from typing import List, Dict, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.round import Round
from app.models.user import User
from app.services.base_tournament_format import BaseTournamentFormat
from app.services.americano_service import AmericanoTournamentService
from app.services.elo_service import ELOService
import uuid

class TournamentService:
    """
    Main tournament service that coordinates tournament operations
    and delegates format-specific logic to appropriate format services.
    """
    
    # Registry of format services
    FORMAT_SERVICES: Dict[TournamentSystem, Type[BaseTournamentFormat]] = {
        TournamentSystem.AMERICANO: AmericanoTournamentService,
        # TournamentSystem.MEXICANO: MexicanoTournamentService,  # To be implemented later
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def get_format_service(self, tournament: Tournament, players: Optional[List[User]] = None) -> BaseTournamentFormat:
        """
        Get the appropriate format service for the tournament system.
        """
        format_class = self.FORMAT_SERVICES.get(tournament.system)
        if not format_class:
            raise ValueError(f"Unsupported tournament system: {tournament.system}")
        
        return format_class(tournament, players)
    
    def validate_tournament_setup(self, tournament: Tournament, players: Optional[List[User]] = None) -> bool:
        """
        Validate that the tournament is properly configured for its format.
        """
        format_service = self.get_format_service(tournament, players)
        return format_service.validate_player_count()
    
    async def start_tournament(self, tournament_id: str) -> Tournament:
        """
        Start a tournament by generating all rounds and setting status to active.
        """
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.PENDING.value:
            raise ValueError(f"Tournament {tournament_id} cannot be started. Current status: {tournament.status}")
        
        # Validate tournament setup
        if not self.validate_tournament_setup(tournament, list(tournament.players)):
            raise ValueError("Tournament setup is invalid for the selected format")
        
        # Get format service and generate rounds
        format_service = self.get_format_service(tournament, list(tournament.players))
        rounds_data = format_service.generate_rounds()
        
        # Create Round objects in database
        created_rounds = []
        for round_number, round_matches in enumerate(rounds_data, 1):
            for match in round_matches:
                round_obj = Round(
                    id=str(uuid.uuid4()),
                    tournament_id=tournament.id,
                    round_number=round_number,
                    team1_player1_id=match[0],
                    team1_player2_id=match[1],
                    team2_player1_id=match[2],
                    team2_player2_id=match[3]
                )
                self.db.add(round_obj)
                created_rounds.append(round_obj)
        
        # Update tournament status
        tournament.status = TournamentStatus.ACTIVE.value
        tournament.current_round = 1
        
        await self.db.commit()
        await self.db.refresh(tournament)
        
        return tournament
    
    async def get_current_round_matches(self, tournament_id: str) -> List[Round]:
        """
        Get all matches for the current round of a tournament.
        """
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        result = await self.db.execute(
            select(Round)
            .filter(Round.tournament_id == tournament_id)
            .filter(Round.round_number == tournament.current_round)
        )
        return result.scalars().all()
    
    async def record_match_result(self, match_id: str, team1_score: int, team2_score: int) -> Round:
        """
        Record the result of a match.
        """
        result = await self.db.execute(select(Round).filter(Round.id == match_id))
        match = result.scalar_one_or_none()
        if not match:
            raise ValueError(f"Match {match_id} not found")
        
        # Get tournament to validate points_per_match
        tournament_result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == match.tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {match.tournament_id} not found")
        
        # Prevent editing results if tournament is completed
        if tournament.status == TournamentStatus.COMPLETED.value:
            raise ValueError(f"Cannot edit results - tournament {tournament.id} is already completed")
        
        # Validate scores
        if team1_score < 0 or team2_score < 0:
            raise ValueError("Scores must be non-negative")
        
        # Validate Americano scoring rule: sum must equal points_per_match
        if tournament.system == TournamentSystem.AMERICANO:
            total_points = team1_score + team2_score
            if total_points != tournament.points_per_match:
                raise ValueError(
                    f"Invalid score for Americano format. "
                    f"Team scores must sum to {tournament.points_per_match} points. "
                    f"Current sum: {total_points} ({team1_score} + {team2_score})"
                )
        
        # Record the result
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.is_completed = True
        
        # Update ELO ratings
        elo_service = ELOService(self.db)
        try:
            rating_changes = await elo_service.update_match_ratings(match)
        except Exception as e:
            # Log but don't fail the match recording if ELO update fails
            print(f"Failed to update ELO ratings: {e}")
            rating_changes = {}
        
        await self.db.commit()
        await self.db.refresh(match)
        
        # Check if we should advance to next round
        await self._check_and_advance_round(match.tournament_id)
        
        return match
    
    async def _check_and_advance_round(self, tournament_id: str) -> None:
        """
        Check if all matches in current round are completed and advance to next round.
        """
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            return
        
        # Check if all matches in current round are completed
        result = await self.db.execute(
            select(Round)
            .filter(Round.tournament_id == tournament_id)
            .filter(Round.round_number == tournament.current_round)
        )
        current_round_matches = result.scalars().all()
        
        if all(match.is_completed for match in current_round_matches):
            # All matches in current round completed
            format_service = self.get_format_service(tournament, list(tournament.players))
            
            # Check if tournament is complete - advance to next round if not the last round
            if not format_service.is_tournament_complete(tournament.current_round + 1):
                tournament.current_round += 1
            # Note: Tournament will only be finished manually by organizer via finish button
            
            await self.db.commit()
    
    async def get_player_scores(self, tournament_id: str, tournament: Tournament = None) -> Dict[str, int]:
        """
        Get current player scores for a tournament.
        If tournament object is already available, pass it to avoid duplicate database queries.
        """
        if tournament is None:
            result = await self.db.execute(
                select(Tournament)
                .options(selectinload(Tournament.players))
                .filter(Tournament.id == tournament_id)
            )
            tournament = result.scalar_one_or_none()
            if not tournament:
                raise ValueError(f"Tournament {tournament_id} not found")
        
        # Get all completed rounds
        result = await self.db.execute(
            select(Round)
            .filter(Round.tournament_id == tournament_id)
            .filter(Round.is_completed == True)
        )
        completed_rounds = result.scalars().all()
        
        # Calculate scores using format service
        format_service = self.get_format_service(tournament, list(tournament.players))
        return format_service.calculate_player_scores(completed_rounds)
    
    async def get_tournament_leaderboard(self, tournament_id: str) -> List[Dict]:
        """
        Get tournament leaderboard with player details and comprehensive statistics.
        """
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        # Get all completed rounds for statistics calculation
        result = await self.db.execute(
            select(Round)
            .filter(Round.tournament_id == tournament_id)
            .filter(Round.is_completed == True)
        )
        completed_rounds = result.scalars().all()
        
        format_service = self.get_format_service(tournament, list(tournament.players))
        
        # Get comprehensive player statistics if available
        if hasattr(format_service, 'calculate_player_statistics'):
            player_stats = format_service.calculate_player_statistics(completed_rounds)
        else:
            # Fallback to basic scores
            player_scores = await self.get_player_scores(tournament_id, tournament)
            player_stats = {
                pid: {
                    'total_points': score,
                    'points_difference': 0,
                    'wins': 0,
                    'losses': 0,
                    'ties': 0,
                    'matches_played': 0
                } for pid, score in player_scores.items()
            }
        
        # Sort by total points (descending), then by points difference (descending)
        leaderboard = sorted(
            player_stats.items(), 
            key=lambda x: (x[1]['total_points'], x[1]['points_difference']), 
            reverse=True
        )
        
        # Enrich with player details - bulk load all users
        player_ids = [player_id for player_id, _ in leaderboard]
        result = await self.db.execute(select(User).filter(User.id.in_(player_ids)))
        users_dict = {user.id: user for user in result.scalars().all()}
        
        result_list = []
        for player_id, stats in leaderboard:
            player = users_dict.get(player_id)
            if player:
                result_list.append({
                    "player_id": player_id,
                    "player_name": player.full_name or player.email or "Unknown Player",
                    "email": player.email,
                    "score": stats['total_points'],
                    "points_difference": stats['points_difference'],
                    "wins": stats['wins'],
                    "losses": stats['losses'],
                    "ties": stats['ties'],
                    "matches_played": stats['matches_played'],
                    "rank": len(result_list) + 1
                })
        
        return result_list
    
    async def get_tournament_winner(self, tournament_id: str) -> Optional[Dict]:
        """
        Get the tournament winner (only if tournament is completed).
        """
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.COMPLETED.value:
            return None
        
        player_scores = await self.get_player_scores(tournament_id, tournament)
        format_service = self.get_format_service(tournament, list(tournament.players))
        winner_id = format_service.get_tournament_winner(player_scores)
        
        if winner_id:
            # Find winner in tournament players (already loaded)
            winner = next((player for player in tournament.players if player.id == winner_id), None)
            if winner:
                return {
                    "player_id": winner_id,
                    "player_name": winner.full_name or winner.email or "Unknown Player",
                    "email": winner.email,
                    "score": player_scores.get(winner_id, 0)
                }
        
        return None 