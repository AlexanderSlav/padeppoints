"""Tournament operation handlers."""
from typing import List, Optional
from datetime import date
import uuid

from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import TournamentNotFoundError, ValidationError, TournamentError
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.round import Round
from app.models.user import User
from app.repositories.tournament_repository import TournamentRepository
from app.repositories.round_repository import RoundRepository
from app.services.tournament_service import TournamentService
from app.schemas.tournament import (
    TournamentCreate,
    TournamentResponse,
    TournamentUpdate,
    TournamentListResponse,
    TournamentJoinResponse,
    TournamentPlayerResponse,
    TournamentPlayersResponse
)
from app.schemas.responses import OperationResponse


class TournamentHandlers:
    """Handlers for tournament-related operations."""
    
    @staticmethod
    async def create_tournament(
        tournament_data: TournamentCreate,
        current_user: User,
        db: AsyncSession
    ) -> Tournament:
        """Create a new tournament."""
        tournament_dict = {
            "id": str(uuid.uuid4()),
            "name": tournament_data.name,
            "description": tournament_data.description,
            "location": tournament_data.location,
            "start_date": tournament_data.start_date,
            "entry_fee": tournament_data.entry_fee,
            "max_players": tournament_data.max_players,
            "system": tournament_data.system,
            "points_per_match": tournament_data.points_per_match,
            "courts": tournament_data.courts,
            "created_by": current_user.id,
            "status": TournamentStatus.PENDING.value
        }
        
        tournament_repo = TournamentRepository(db)
        return await tournament_repo.create(tournament_dict)
    
    @staticmethod
    async def list_tournaments(
        format_filter: Optional[TournamentSystem],
        status_filter: Optional[str],
        start_date_from: Optional[date],
        start_date_to: Optional[date],
        location_filter: Optional[str],
        created_by_me: bool,
        limit: int,
        offset: int,
        current_user: User,
        db: AsyncSession
    ) -> TournamentListResponse:
        """List tournaments with filtering options."""
        tournament_repo = TournamentRepository(db)
        
        created_by = current_user.id if created_by_me else None
        
        tournaments, total = await tournament_repo.get_tournaments_with_counts_and_total(
            format=format_filter,
            status=status_filter,
            start_date_from=start_date_from,
            start_date_to=start_date_to,
            location=location_filter,
            created_by=created_by,
            limit=limit,
            offset=offset
        )
        
        return TournamentListResponse(tournaments=tournaments, total=total)
    
    @staticmethod
    async def get_tournament_details(
        tournament_id: str,
        db: AsyncSession
    ) -> Tournament:
        """Get tournament details by ID."""
        tournament_repo = TournamentRepository(db)
        tournament = await tournament_repo.get(tournament_id)
        
        if not tournament:
            raise TournamentNotFoundError(tournament_id)
        
        return tournament
    
    @staticmethod
    async def join_tournament(
        tournament_id: str,
        current_user: User,
        db: AsyncSession
    ) -> OperationResponse:
        """Join a tournament."""
        tournament_repo = TournamentRepository(db)
        result = await tournament_repo.join_tournament(tournament_id, current_user.id)
        
        return OperationResponse(
            success=result["success"],
            message=result["message"],
            data={
                "current_players": result.get("current_players"),
                "max_players": result.get("max_players")
            } if result["success"] else None
        )
    
    @staticmethod
    async def leave_tournament(
        tournament_id: str,
        current_user: User,
        db: AsyncSession
    ) -> OperationResponse:
        """Leave a tournament."""
        tournament_repo = TournamentRepository(db)
        result = await tournament_repo.leave_tournament(tournament_id, current_user.id)
        
        return OperationResponse(
            success=result["success"],
            message=result["message"],
            data={
                "current_players": result.get("current_players"),
                "max_players": result.get("max_players")
            } if result["success"] else None
        )
    
    @staticmethod
    async def start_tournament(
        tournament: Tournament,
        db: AsyncSession
    ) -> Tournament:
        """Start a tournament."""
        tournament_service = TournamentService(db)
        
        try:
            return await tournament_service.start_tournament(tournament.id)
        except ValueError as e:
            raise TournamentError(str(e))
    
    @staticmethod
    async def finish_tournament(
        tournament: Tournament,
        db: AsyncSession
    ) -> Tournament:
        """Finish a tournament."""
        if tournament.status != TournamentStatus.ACTIVE.value:
            raise TournamentError(
                f"Tournament cannot be finished. Current status: {tournament.status}. "
                "Only active tournaments can be finished."
            )
        
        tournament.status = TournamentStatus.COMPLETED.value
        await db.commit()
        await db.refresh(tournament)
        
        logger.info(f"Successfully finished tournament {tournament.id}")
        return tournament
    
    @staticmethod
    async def get_tournament_players(
        tournament_id: str,
        db: AsyncSession
    ) -> List[dict]:
        """Get tournament players."""
        tournament_repo = TournamentRepository(db)
        return await tournament_repo.get_tournament_players(tournament_id)
    
    @staticmethod
    async def get_tournament_rounds(
        tournament_id: str,
        db: AsyncSession
    ) -> List[dict]:
        """Get all rounds for a tournament."""
        # Verify tournament exists
        tournament_repo = TournamentRepository(db)
        tournament = await tournament_repo.get(tournament_id)
        
        if not tournament:
            raise TournamentNotFoundError(tournament_id)
        
        # If tournament hasn't started yet, return empty list
        if tournament.status == TournamentStatus.PENDING.value:
            return []
        
        # Get rounds with player relationships loaded
        rounds_result = await db.execute(
            select(Round)
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .filter(Round.tournament_id == tournament_id)
            .order_by(Round.round_number)
        )
        rounds = rounds_result.scalars().all()
        
        # Convert to dict format with player information
        rounds_data = []
        for round_obj in rounds:
            rounds_data.append({
                "id": round_obj.id,
                "tournament_id": round_obj.tournament_id,
                "round_number": round_obj.round_number,
                "team1_player1": {
                    "id": round_obj.team1_player1.id,
                    "full_name": round_obj.team1_player1.full_name,
                    "email": round_obj.team1_player1.email,
                } if round_obj.team1_player1 else None,
                "team1_player2": {
                    "id": round_obj.team1_player2.id,
                    "full_name": round_obj.team1_player2.full_name,
                    "email": round_obj.team1_player2.email,
                } if round_obj.team1_player2 else None,
                "team2_player1": {
                    "id": round_obj.team2_player1.id,
                    "full_name": round_obj.team2_player1.full_name,
                    "email": round_obj.team2_player1.email,
                } if round_obj.team2_player1 else None,
                "team2_player2": {
                    "id": round_obj.team2_player2.id,
                    "full_name": round_obj.team2_player2.full_name,
                    "email": round_obj.team2_player2.email,
                } if round_obj.team2_player2 else None,
                "team1_score": round_obj.team1_score,
                "team2_score": round_obj.team2_score,
                "is_completed": round_obj.is_completed
            })
        
        return rounds_data