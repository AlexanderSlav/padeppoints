"""Service for managing tournament results and final positions."""
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.tournament import Tournament
from app.models.tournament_result import TournamentResult
from app.models.round import Round
from app.models.user import User
from app.services.base_tournament_format import BaseTournamentFormat
from app.services.americano_service import AmericanoTournamentService


class TournamentResultService:
    """Service for calculating and storing tournament results."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _get_format_service(self, tournament: Tournament, players: List[User]) -> BaseTournamentFormat:
        """Get the appropriate tournament format service."""
        if tournament.system.value == "AMERICANO":
            return AmericanoTournamentService(tournament, players)
        else:
            raise ValueError(f"Unsupported tournament system: {tournament.system}")
    
    async def calculate_and_store_final_results(self, tournament_id: str) -> List[TournamentResult]:
        """Calculate final results and store them in the database."""
        # Get tournament with players
        result = await self.db.execute(
            select(Tournament)
            .where(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        # Get all players in the tournament
        players_result = await self.db.execute(
            select(User)
            .join(Tournament.players)
            .where(Tournament.id == tournament_id)
        )
        players = list(players_result.scalars().all())
        
        if not players:
            raise ValueError(f"No players found for tournament {tournament_id}")
        
        # Get all completed rounds
        rounds_result = await self.db.execute(
            select(Round)
            .where(Round.tournament_id == tournament_id)
            .where(Round.is_completed == True)
        )
        completed_rounds = list(rounds_result.scalars().all())
        
        # Get format service and calculate comprehensive statistics
        format_service = self._get_format_service(tournament, players)
        
        if hasattr(format_service, 'calculate_player_statistics'):
            player_stats = format_service.calculate_player_statistics(completed_rounds)
        else:
            # Fallback to basic scores
            player_scores = format_service.calculate_player_scores(completed_rounds)
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
        
        # Sort players by total points and points difference to determine final positions
        sorted_players = sorted(
            player_stats.items(),
            key=lambda x: (x[1]['total_points'], x[1]['points_difference']),
            reverse=True
        )
        
        # Delete existing results for this tournament (in case of recalculation)
        delete_query = TournamentResult.__table__.delete().where(
            TournamentResult.tournament_id == tournament_id
        )
        await self.db.execute(delete_query)
        
        # Create and store tournament results
        tournament_results = []
        for position, (player_id, stats) in enumerate(sorted_players, 1):
            result = TournamentResult(
                tournament_id=tournament_id,
                player_id=player_id,
                final_position=position,
                total_score=stats['total_points'],
                points_difference=stats.get('points_difference', 0),
                matches_played=stats.get('matches_played', 0),
                matches_won=stats.get('wins', 0),
                matches_lost=stats.get('losses', 0),
                matches_tied=stats.get('ties', 0)
            )
            tournament_results.append(result)
        
        # Bulk insert results
        self.db.add_all(tournament_results)
        await self.db.commit()
        
        # Refresh to get IDs
        for result in tournament_results:
            await self.db.refresh(result)
        
        return tournament_results
    
    async def get_tournament_results(self, tournament_id: str) -> List[TournamentResult]:
        """Get stored tournament results."""
        result = await self.db.execute(
            select(TournamentResult)
            .where(TournamentResult.tournament_id == tournament_id)
            .order_by(TournamentResult.final_position.asc())
        )
        return list(result.scalars().all())
    
    async def get_player_result_in_tournament(self, tournament_id: str, player_id: str) -> Optional[TournamentResult]:
        """Get a specific player's result in a tournament."""
        result = await self.db.execute(
            select(TournamentResult)
            .where(
                and_(
                    TournamentResult.tournament_id == tournament_id,
                    TournamentResult.player_id == player_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def has_stored_results(self, tournament_id: str) -> bool:
        """Check if tournament has stored results."""
        result = await self.db.execute(
            select(TournamentResult)
            .where(TournamentResult.tournament_id == tournament_id)
            .limit(1)
        )
        return result.scalar_one_or_none() is not None
