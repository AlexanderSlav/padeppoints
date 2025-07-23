from typing import List, Dict, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.round import Round
from app.models.user import User
from app.services.base_tournament_format import BaseTournamentFormat
from app.services.americano_service import AmericanoTournamentService
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
    
    def get_format_service(self, tournament: Tournament) -> BaseTournamentFormat:
        """
        Get the appropriate format service for the tournament system.
        """
        format_class = self.FORMAT_SERVICES.get(tournament.system)
        if not format_class:
            raise ValueError(f"Unsupported tournament system: {tournament.system}")
        
        return format_class(tournament)
    
    def validate_tournament_setup(self, tournament: Tournament) -> bool:
        """
        Validate that the tournament is properly configured for its format.
        """
        format_service = self.get_format_service(tournament)
        return format_service.validate_player_count()
    
    async def start_tournament(self, tournament_id: str) -> Tournament:
        """
        Start a tournament by generating all rounds and setting status to active.
        """
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.PENDING.value:
            raise ValueError(f"Tournament {tournament_id} cannot be started. Current status: {tournament.status}")
        
        # Validate tournament setup
        if not self.validate_tournament_setup(tournament):
            raise ValueError("Tournament setup is invalid for the selected format")
        
        # Get format service and generate rounds
        format_service = self.get_format_service(tournament)
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
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
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
        
        if match.is_completed:
            raise ValueError(f"Match {match_id} is already completed")
        
        # Validate scores
        if team1_score < 0 or team2_score < 0:
            raise ValueError("Scores must be non-negative")
        
        # Record the result
        match.team1_score = team1_score
        match.team2_score = team2_score
        match.is_completed = True
        
        await self.db.commit()
        await self.db.refresh(match)
        
        # Check if we should advance to next round
        await self._check_and_advance_round(match.tournament_id)
        
        return match
    
    async def _check_and_advance_round(self, tournament_id: str) -> None:
        """
        Check if all matches in current round are completed and advance to next round.
        """
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
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
            format_service = self.get_format_service(tournament)
            
            # Check if tournament is complete
            if format_service.is_tournament_complete(tournament.current_round + 1):
                tournament.status = TournamentStatus.COMPLETED.value
            else:
                tournament.current_round += 1
            
            await self.db.commit()
    
    async def get_player_scores(self, tournament_id: str) -> Dict[str, int]:
        """
        Get current player scores for a tournament.
        """
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
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
        format_service = self.get_format_service(tournament)
        return format_service.calculate_player_scores(completed_rounds)
    
    async def get_tournament_leaderboard(self, tournament_id: str) -> List[Dict]:
        """
        Get tournament leaderboard with player details and scores.
        """
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        player_scores = await self.get_player_scores(tournament_id)
        format_service = self.get_format_service(tournament)
        
        # Get leaderboard
        if hasattr(format_service, 'get_player_leaderboard'):
            leaderboard = format_service.get_player_leaderboard(player_scores)
        else:
            leaderboard = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Enrich with player details
        result_list = []
        for player_id, score in leaderboard:
            result = await self.db.execute(select(User).filter(User.id == player_id))
            player = result.scalar_one_or_none()
            if player:
                result_list.append({
                    "player_id": player_id,
                    "player_name": f"{player.first_name} {player.last_name}",
                    "email": player.email,
                    "score": score,
                    "rank": len(result_list) + 1
                })
        
        return result_list
    
    async def get_tournament_winner(self, tournament_id: str) -> Optional[Dict]:
        """
        Get the tournament winner (only if tournament is completed).
        """
        result = await self.db.execute(select(Tournament).filter(Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise ValueError(f"Tournament {tournament_id} not found")
        
        if tournament.status != TournamentStatus.COMPLETED.value:
            return None
        
        player_scores = await self.get_player_scores(tournament_id)
        format_service = self.get_format_service(tournament)
        winner_id = format_service.get_tournament_winner(player_scores)
        
        if winner_id:
            result = await self.db.execute(select(User).filter(User.id == winner_id))
            winner = result.scalar_one_or_none()
            if winner:
                return {
                    "player_id": winner_id,
                    "player_name": f"{winner.first_name} {winner.last_name}",
                    "email": winner.email,
                    "score": player_scores.get(winner_id, 0)
                }
        
        return None 