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
        Update ELO ratings based on a completed match.
        
        Args:
            match: Completed match (Round object)
            
        Returns:
            Dictionary of user_id -> rating_change
        
        TODO: Check this, is rating change only depends on total stregth of the team ?
              It should be more personal up to player rating.
        """
        if not match.is_completed or match.team1_score is None or match.team2_score is None:
            raise ValueError("Match must be completed with scores")
        
        # Get all player ratings
        team1_p1_rating = await self.get_or_create_rating(match.team1_player1_id)
        team1_p2_rating = await self.get_or_create_rating(match.team1_player2_id)
        team2_p1_rating = await self.get_or_create_rating(match.team2_player1_id)
        team2_p2_rating = await self.get_or_create_rating(match.team2_player2_id)
        
        # Calculate team ratings (average of players)
        team1_rating = (team1_p1_rating.current_rating + team1_p2_rating.current_rating) / 2
        team2_rating = (team2_p1_rating.current_rating + team2_p2_rating.current_rating) / 2
        
        # Calculate expected scores
        team1_expected = self.calculate_expected_score(team1_rating, team2_rating)
        team2_expected = 1 - team1_expected
        
        # Calculate actual scores based on points
        total_points = match.team1_score + match.team2_score
        if total_points > 0:
            team1_actual = match.team1_score / total_points
            team2_actual = match.team2_score / total_points
        else:
            # Fallback to win/loss if no points
            team1_actual = 1.0 if match.team1_score > match.team2_score else 0.0
            team2_actual = 1.0 - team1_actual
        
        # Update ratings for all players
        rating_changes = {}
        
        # Team 1 players
        for player_rating in [team1_p1_rating, team1_p2_rating]:
            k_factor = self.get_k_factor(player_rating.matches_played)
            rating_change = k_factor * (team1_actual - team1_expected)
            
            old_rating = player_rating.current_rating
            new_rating = old_rating + rating_change
            
            # Update rating
            player_rating.current_rating = new_rating
            player_rating.peak_rating = max(player_rating.peak_rating, new_rating)
            player_rating.lowest_rating = min(player_rating.lowest_rating, new_rating)
            
            # Update statistics
            player_rating.matches_played += 1
            if match.team1_score > match.team2_score:
                player_rating.matches_won += 1
            player_rating.total_points_scored += match.team1_score
            player_rating.total_points_possible += total_points
            
            # Create history entry
            history = RatingHistory(
                player_rating_id=player_rating.id,
                match_id=match.id,
                tournament_id=match.tournament_id,
                old_rating=old_rating,
                new_rating=new_rating,
                rating_change=rating_change,
                opponent_ratings=json.dumps({
                    "team_partner": team1_p2_rating.current_rating if player_rating.user_id != team1_p2_rating.user_id else team1_p1_rating.current_rating,
                    "opponents": [team2_p1_rating.current_rating, team2_p2_rating.current_rating]
                }),
                match_result=f"{match.team1_score}-{match.team2_score}"
            )
            self.db.add(history)
            
            rating_changes[player_rating.user_id] = rating_change
        
        # Team 2 players
        for player_rating in [team2_p1_rating, team2_p2_rating]:
            k_factor = self.get_k_factor(player_rating.matches_played)
            rating_change = k_factor * (team2_actual - team2_expected)
            
            old_rating = player_rating.current_rating
            new_rating = old_rating + rating_change
            
            # Update rating
            player_rating.current_rating = new_rating
            player_rating.peak_rating = max(player_rating.peak_rating, new_rating)
            player_rating.lowest_rating = min(player_rating.lowest_rating, new_rating)
            
            # Update statistics
            player_rating.matches_played += 1
            if match.team2_score > match.team1_score:
                player_rating.matches_won += 1
            player_rating.total_points_scored += match.team2_score
            player_rating.total_points_possible += total_points
            
            # Create history entry
            history = RatingHistory(
                player_rating_id=player_rating.id,
                match_id=match.id,
                tournament_id=match.tournament_id,
                old_rating=old_rating,
                new_rating=new_rating,
                rating_change=rating_change,
                opponent_ratings=json.dumps({
                    "team_partner": team2_p2_rating.current_rating if player_rating.user_id != team2_p2_rating.user_id else team2_p1_rating.current_rating,
                    "opponents": [team1_p1_rating.current_rating, team1_p2_rating.current_rating]
                }),
                match_result=f"{match.team2_score}-{match.team1_score}"
            )
            self.db.add(history)
            
            rating_changes[player_rating.user_id] = rating_change
        
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