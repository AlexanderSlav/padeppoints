"""ELO rating calculation service for padel tournaments."""
import math
import json
from typing import List, Tuple, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.player_rating import PlayerRating, RatingHistory
from app.models.user import User
from app.models.round import Round
import logging

logger = logging.getLogger(__name__)


class ELOService:
    """Service for calculating and updating ELO ratings."""
    
    # ELO constants
    K_FACTOR_NEW_PLAYER = 40  # Higher K for players with < 30 matches
    K_FACTOR_NORMAL = 20      # Normal K factor
    K_FACTOR_EXPERIENCED = 10  # Lower K for players with > 100 matches
    INITIAL_RATING = 1000
    SCALING_FACTOR = 400  # Traditional ELO scaling
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @staticmethod
    def calculate_expected_score(rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for player/team A against player/team B.
        
        Args:
            rating_a: Rating of player/team A
            rating_b: Rating of player/team B
            
        Returns:
            Expected score between 0 and 1
        """
        return 1 / (1 + math.pow(10, (rating_b - rating_a) / ELOService.SCALING_FACTOR))
    
    @staticmethod
    def get_k_factor(matches_played: int) -> float:
        """
        Get K factor based on player experience.
        
        Args:
            matches_played: Number of matches the player has played
            
        Returns:
            K factor for rating adjustment
        """
        if matches_played < 30:
            return ELOService.K_FACTOR_NEW_PLAYER
        elif matches_played > 100:
            return ELOService.K_FACTOR_EXPERIENCED
        else:
            return ELOService.K_FACTOR_NORMAL
    
    async def get_or_create_rating(self, user_id: str) -> PlayerRating:
        """
        Get existing player rating or create new one.
        
        Args:
            user_id: User ID
            
        Returns:
            PlayerRating object
        """
        result = await self.db.execute(
            select(PlayerRating).filter(PlayerRating.user_id == user_id)
        )
        rating = result.scalar_one_or_none()
        
        if not rating:
            rating = PlayerRating(
                user_id=user_id,
                current_rating=self.INITIAL_RATING,
                peak_rating=self.INITIAL_RATING,
                lowest_rating=self.INITIAL_RATING
            )
            self.db.add(rating)
            await self.db.flush()
        
        return rating
    
    async def update_match_ratings(self, match: Round) -> Dict[str, float]:
        """
        Update ELO ratings based on a completed doubles match with personalized deltas.

        Strategy:
          1) Compute team expected/actual scores (same as before).
          2) Compute ONE team delta: Δ_team = K_eff * (A_team - E_team).
          3) Split Δ_team across teammates with rating-aware weights that
             give slightly more credit to the lower-rated player on over-performance
             (and protect them more on under-performance).
          4) Apply deltas, update stats, and persist rating histories using
             pre-update partner/opponent ratings.

        Returns:
            Dict[user_id, rating_change]
        """
        if not match.is_completed or match.team1_score is None or match.team2_score is None:
            raise ValueError("Match must be completed with scores")

        # ---- Helpers (kept local to avoid changing class API) --------------------
        def effective_k(base_k: float, total_points: int, score_diff: int, team_matches_played_min: int) -> float:
            """Scale K by margin-of-victory and uncertainty (few matches → bigger moves)."""
            # Margin-of-victory scaling
            margin = (abs(score_diff) / max(1, total_points)) if total_points > 0 else 0.0
            lambda_margin = 0.75  # tune 0.5–1.0 as desired

            # Uncertainty scaling (conservative: use min matches played on the team)
            if team_matches_played_min < 5:
                u = 1.25
            elif team_matches_played_min < 15:
                u = 1.10
            else:
                u = 1.00

            return base_k * (1 + lambda_margin * margin) * u

        def split_weights(r_a: float, r_b: float, alpha: float = 0.25, gap_cap: float = 200.0) -> Tuple[float, float]:
            """
            Rating-aware split around 50/50.
            If A is lower-rated than B, A gets a slightly larger share on positive team delta.
            """
            # Clamp the gap to avoid extreme tilts
            g_ab = max(-gap_cap, min(gap_cap, r_b - r_a))  # positive if A is lower-rated
            w_a_raw = 0.5 + alpha * (g_ab / (2 * gap_cap))
            w_b_raw = 1.0 - w_a_raw
            s = w_a_raw + w_b_raw
            return (w_a_raw / s, w_b_raw / s)

        def expected_score(r_team: float, r_opp_team: float) -> float:
            """Classic Elo expectation using average team ratings."""
            return 1.0 / (1.0 + math.pow(10.0, (r_opp_team - r_team) / 400.0))

        # ---- Load player ratings -------------------------------------------------
        t1p1 = await self.get_or_create_rating(match.team1_player1_id)
        t1p2 = await self.get_or_create_rating(match.team1_player2_id)
        t2p1 = await self.get_or_create_rating(match.team2_player1_id)
        t2p2 = await self.get_or_create_rating(match.team2_player2_id)

        # Pre-update snapshots for history payloads (avoid order effects)
        pre = {
            "t1p1": t1p1.current_rating,
            "t1p2": t1p2.current_rating,
            "t2p1": t2p1.current_rating,
            "t2p2": t2p2.current_rating,
        }

        # ---- Team ratings (average; you can switch to sum if you prefer) --------
        team1_rating = (pre["t1p1"] + pre["t1p2"]) / 2.0
        team2_rating = (pre["t2p1"] + pre["t2p2"]) / 2.0

        # ---- Expected & actual team scores --------------------------------------
        team1_expected = expected_score(team1_rating, team2_rating)
        team2_expected = 1.0 - team1_expected

        total_points = match.team1_score + match.team2_score
        if total_points > 0:
            team1_actual = match.team1_score / total_points
            team2_actual = 1.0 - team1_actual
        else:
            # Fallback to W/L if no points recorded
            team1_actual = 1.0 if match.team1_score > match.team2_score else 0.0
            team2_actual = 1.0 - team1_actual

        # ---- Team delta (conserved) ---------------------------------------------
        score_diff = match.team1_score - match.team2_score

        # Base K for the team: conservative choice uses the min matches played of teammates
        team1_min_matches = min(t1p1.matches_played, t1p2.matches_played)
        team2_min_matches = min(t2p1.matches_played, t2p2.matches_played)

        # Derive a base K from your current per-player policy (any teammate; we'll scale it)
        k1_base = self.get_k_factor(team1_min_matches)
        k2_base = self.get_k_factor(team2_min_matches)

        # Effective K adds margin + uncertainty scaling
        k1_eff = effective_k(k1_base, total_points, score_diff, team1_min_matches)
        # We keep a single Δ_team for conservation; you could compute k2_eff too for diagnostics
        delta_team1 = k1_eff * (team1_actual - team1_expected)
        delta_team2 = -delta_team1  # conservation

        # ---- Split team deltas between teammates --------------------------------
        w11, w12 = split_weights(pre["t1p1"], pre["t1p2"])
        w21, w22 = split_weights(pre["t2p1"], pre["t2p2"])

        delta_11 = w11 * delta_team1
        delta_12 = w12 * delta_team1
        delta_21 = w21 * delta_team2
        delta_22 = w22 * delta_team2

        rating_changes: Dict[str, float] = {}

        # ---- Apply updates: Team 1 ----------------------------------------------
        for player_rating, partner_pre, opps_pre, delta, team_points in [
            (t1p1, pre["t1p2"], [pre["t2p1"], pre["t2p2"]], delta_11, match.team1_score),
            (t1p2, pre["t1p1"], [pre["t2p1"], pre["t2p2"]], delta_12, match.team1_score),
        ]:
            old_rating = player_rating.current_rating
            new_rating = old_rating + delta

            player_rating.current_rating = new_rating
            player_rating.peak_rating = max(player_rating.peak_rating, new_rating)
            player_rating.lowest_rating = min(player_rating.lowest_rating, new_rating)
            player_rating.matches_played += 1
            if match.team1_score > match.team2_score:
                player_rating.matches_won += 1
            player_rating.total_points_scored += match.team1_score
            player_rating.total_points_possible += total_points

            history = RatingHistory(
                player_rating_id=player_rating.id,
                match_id=match.id,
                tournament_id=match.tournament_id,
                old_rating=old_rating,
                new_rating=new_rating,
                rating_change=delta,
                opponent_ratings=json.dumps({
                    "team_partner": partner_pre,
                    "opponents": opps_pre,
                }),
                match_result=f"{match.team1_score}-{match.team2_score}",
            )
            self.db.add(history)
            rating_changes[player_rating.user_id] = delta

        # ---- Apply updates: Team 2 ----------------------------------------------
        for player_rating, partner_pre, opps_pre, delta, team_points in [
            (t2p1, pre["t2p2"], [pre["t1p1"], pre["t1p2"]], delta_21, match.team2_score),
            (t2p2, pre["t2p1"], [pre["t1p1"], pre["t1p2"]], delta_22, match.team2_score),
        ]:
            old_rating = player_rating.current_rating
            new_rating = old_rating + delta

            player_rating.current_rating = new_rating
            player_rating.peak_rating = max(player_rating.peak_rating, new_rating)
            player_rating.lowest_rating = min(player_rating.lowest_rating, new_rating)
            player_rating.matches_played += 1
            if match.team2_score > match.team1_score:
                player_rating.matches_won += 1
            player_rating.total_points_scored += match.team2_score
            player_rating.total_points_possible += total_points

            history = RatingHistory(
                player_rating_id=player_rating.id,
                match_id=match.id,
                tournament_id=match.tournament_id,
                old_rating=old_rating,
                new_rating=new_rating,
                rating_change=delta,
                opponent_ratings=json.dumps({
                    "team_partner": partner_pre,
                    "opponents": opps_pre,
                }),
                match_result=f"{match.team2_score}-{match.team1_score}",
            )
            self.db.add(history)
            rating_changes[player_rating.user_id] = delta

        await self.db.flush()

        logger.info(f"Updated ELO ratings for match {match.id}: {rating_changes}")
        return rating_changes
    
    async def update_tournament_podium(self, tournament_id: str, leaderboard: List[Dict]) -> None:
        """
        Update podium finishes based on tournament results.
        
        Args:
            tournament_id: Tournament ID
            leaderboard: List of leaderboard entries with player_id and position
        """
        for entry in leaderboard[:3]:  # Top 3 only
            player_rating = await self.get_or_create_rating(entry['player_id'])
            
            if entry.get('position') == 1:
                player_rating.first_place_finishes += 1
            elif entry.get('position') == 2:
                player_rating.second_place_finishes += 1
            elif entry.get('position') == 3:
                player_rating.third_place_finishes += 1
            
            player_rating.tournaments_played += 1
        
        # Update tournament count for all participants
        for entry in leaderboard[3:]:
            player_rating = await self.get_or_create_rating(entry['player_id'])
            player_rating.tournaments_played += 1
        
        await self.db.flush()
    
    async def get_player_statistics(self, user_id: str) -> Dict:
        """
        Get comprehensive player statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with player statistics
        """
        rating = await self.get_or_create_rating(user_id)
        
        # Get user info
        result = await self.db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        # Get recent rating history
        history_result = await self.db.execute(
            select(RatingHistory)
            .filter(RatingHistory.player_rating_id == rating.id)
            .order_by(RatingHistory.timestamp.desc())
            .limit(10)
        )
        recent_history = history_result.scalars().all()
        
        return {
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email,
                "picture": user.picture
            } if user else None,
            "rating": {
                "current": round(rating.current_rating, 1),
                "peak": round(rating.peak_rating, 1),
                "lowest": round(rating.lowest_rating, 1)
            },
            "statistics": {
                "matches_played": rating.matches_played,
                "matches_won": rating.matches_won,
                "win_rate": round(rating.win_rate, 1),
                "average_point_percentage": round(rating.average_point_percentage, 1),
                "tournaments_played": rating.tournaments_played
            },
            "podium": {
                "first": rating.first_place_finishes,
                "second": rating.second_place_finishes,
                "third": rating.third_place_finishes,
                "total": rating.podium_count
            },
            "recent_history": [
                {
                    "date": entry.timestamp.isoformat(),
                    "old_rating": round(entry.old_rating, 1),
                    "new_rating": round(entry.new_rating, 1),
                    "change": round(entry.rating_change, 1),
                    "match_result": entry.match_result
                }
                for entry in recent_history
            ]
        }
    
    async def get_leaderboard(self, limit: int = 50) -> List[Dict]:
        """
        Get ELO rating leaderboard.
        
        Args:
            limit: Maximum number of players to return
            
        Returns:
            List of players with ratings
        """
        result = await self.db.execute(
            select(PlayerRating, User)
            .join(User, PlayerRating.user_id == User.id)
            .filter(PlayerRating.matches_played >= 5)  # Minimum matches for ranking
            .order_by(PlayerRating.current_rating.desc())
            .limit(limit)
        )
        
        leaderboard = []
        for rank, (rating, user) in enumerate(result.all(), 1):
            leaderboard.append({
                "rank": rank,
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "picture": user.picture
                },
                "rating": round(rating.current_rating, 1),
                "matches_played": rating.matches_played,
                "win_rate": round(rating.win_rate, 1),
                "trend": "up" if len(rating.rating_history) > 0 and rating.rating_history[-1].rating_change > 0 else "down"
            })
        
        return leaderboard