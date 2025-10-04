"""
Admin Tournament Service

Handles tournament management operations for administrators including viewing,
editing results, recalculating scores, and forcing status changes.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.tournament import Tournament, TournamentStatus, TournamentSystem
from app.models.round import Round
from app.models.user import User
from app.models.audit_log import ActionType, TargetType
from app.schemas.admin import (
    AdminTournamentListItem,
    TournamentListResponse,
    MatchResultUpdate,
    TournamentStatusUpdate,
    RecalculateScoresRequest,
    AdminActionResponse,
)
from app.services.admin.audit_service import AuditService
from app.services.americano_service import AmericanoTournamentService
from app.services.tournament_result_service import TournamentResultService


class AdminTournamentService:
    """Service for administrative tournament management operations."""

    def __init__(
        self,
        db: AsyncSession,
        audit_service: AuditService,
        result_service: TournamentResultService,
    ):
        """
        Initialize AdminTournamentService.

        Args:
            db: Database session
            audit_service: Audit logging service
            result_service: Tournament result service
        """
        self.db = db
        self.audit_service = audit_service
        self.result_service = result_service

    async def get_tournaments(
        self,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        tournament_system: Optional[str] = None,
        creator_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> TournamentListResponse:
        """
        Get paginated list of tournaments with filtering.

        Args:
            search: Search term for tournament name
            status_filter: Filter by status (pending, active, completed)
            tournament_system: Filter by tournament system
            creator_id: Filter by creator user ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Paginated list of tournaments
        """
        query = select(Tournament).options(
            selectinload(Tournament.players),
            selectinload(Tournament.creator),
            selectinload(Tournament.rounds),
        )
        filters = []

        # Apply filters
        if search:
            search_term = f"%{search}%"
            filters.append(Tournament.name.ilike(search_term))
        if status_filter:
            filters.append(Tournament.status == status_filter)
        if tournament_system:
            filters.append(Tournament.system == TournamentSystem(tournament_system))
        if creator_id:
            filters.append(Tournament.created_by == creator_id)

        if filters:
            query = query.filter(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Tournament)
        if filters:
            count_query = count_query.filter(and_(*filters))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(Tournament.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        tournaments = result.scalars().all()

        # Build response
        tournament_items = []
        for t in tournaments:
            # Count completed rounds
            completed_rounds = sum(1 for r in t.rounds if r.is_completed)
            total_rounds = len(t.rounds)

            tournament_items.append(
                AdminTournamentListItem(
                    id=t.id,
                    name=t.name,
                    created_by=t.created_by,
                    creator_name=t.creator.full_name if t.creator else None,
                    status=t.status,
                    tournament_system=t.system.value,
                    player_count=len(t.players),
                    rounds_completed=completed_rounds,
                    rounds_total=total_rounds,
                    created_at=t.created_at,
                )
            )

        return TournamentListResponse(
            tournaments=tournament_items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_match_result(
        self,
        tournament_id: str,
        round_id: str,
        result_update: MatchResultUpdate,
        admin_id: str,
        ip_address: Optional[str] = None,
    ) -> AdminActionResponse:
        """
        Update a match result.

        Args:
            tournament_id: Tournament ID
            round_id: Round/Match ID
            result_update: New scores and reason
            admin_id: ID of admin performing the update
            ip_address: IP address of admin

        Returns:
            Action response

        Raises:
            HTTPException: If tournament or round not found, or validation fails
        """
        # Get tournament
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.rounds))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()

        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found",
            )

        # Get round
        round_result = await self.db.execute(
            select(Round).filter(Round.id == round_id)
        )
        round_match = round_result.scalar_one_or_none()

        if not round_match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )

        if round_match.tournament_id != tournament_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Match does not belong to this tournament",
            )

        # Validate scores sum to points_per_match
        total_points = result_update.team1_score + result_update.team2_score
        if total_points != tournament.points_per_match:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scores must sum to {tournament.points_per_match}",
            )

        # Store old values for audit
        old_values = {
            "team1_score": round_match.team1_score,
            "team2_score": round_match.team2_score,
            "is_completed": round_match.is_completed,
        }

        # Update scores
        round_match.team1_score = result_update.team1_score
        round_match.team2_score = result_update.team2_score
        round_match.is_completed = True

        await self.db.commit()
        await self.db.refresh(round_match)

        # Log to audit
        await self.audit_service.log_action(
            admin_id=admin_id,
            action_type=ActionType.TOURNAMENT_RESULT_EDIT,
            target_type=TargetType.MATCH,
            target_id=round_id,
            details={
                "tournament_id": tournament_id,
                "old_values": old_values,
                "new_values": {
                    "team1_score": result_update.team1_score,
                    "team2_score": result_update.team2_score,
                    "is_completed": True,
                },
                "reason": result_update.reason,
            },
            ip_address=ip_address,
        )

        return AdminActionResponse(
            success=True,
            message="Match result updated successfully",
            details={
                "tournament_id": tournament_id,
                "round_id": round_id,
                "new_scores": {
                    "team1": result_update.team1_score,
                    "team2": result_update.team2_score,
                },
            },
        )

    async def recalculate_tournament_scores(
        self,
        tournament_id: str,
        request: RecalculateScoresRequest,
        admin_id: str,
        ip_address: Optional[str] = None,
    ) -> AdminActionResponse:
        """
        Recalculate all scores for a tournament.

        Args:
            tournament_id: Tournament ID
            request: Recalculation request with reason
            admin_id: ID of admin performing the recalculation
            ip_address: IP address of admin

        Returns:
            Action response

        Raises:
            HTTPException: If tournament not found
        """
        # Get tournament with all data
        result = await self.db.execute(
            select(Tournament)
            .options(
                selectinload(Tournament.rounds),
                selectinload(Tournament.players),
            )
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()

        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found",
            )

        # Get old scores before recalculation
        old_scores_result = await self.db.execute(
            select(User.id, User.full_name)
            .join(Tournament.players)
            .filter(Tournament.id == tournament_id)
        )
        players = old_scores_result.all()
        old_scores = {player.id: 0 for player in players}  # Simplified, would need actual scores

        # Recalculate using tournament format service
        if tournament.system == TournamentSystem.AMERICANO:
            format_service = AmericanoTournamentService(
                tournament=tournament,
                players=list(tournament.players),
            )
            completed_rounds = [r for r in tournament.rounds if r.is_completed]
            new_scores = format_service.calculate_player_scores(completed_rounds)
        else:
            # Add other formats as needed
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Recalculation not implemented for {tournament.system.value}",
            )

        # Update tournament results in database
        await self.result_service.update_tournament_results(
            tournament_id=tournament_id,
            player_scores=new_scores,
        )

        # Log to audit
        await self.audit_service.log_action(
            admin_id=admin_id,
            action_type=ActionType.TOURNAMENT_SCORE_RECALC,
            target_type=TargetType.TOURNAMENT,
            target_id=tournament_id,
            details={
                "old_scores": old_scores,
                "new_scores": new_scores,
                "reason": request.reason,
            },
            ip_address=ip_address,
        )

        return AdminActionResponse(
            success=True,
            message="Tournament scores recalculated successfully",
            details={
                "tournament_id": tournament_id,
                "player_count": len(new_scores),
            },
        )

    async def force_status_change(
        self,
        tournament_id: str,
        status_update: TournamentStatusUpdate,
        admin_id: str,
        ip_address: Optional[str] = None,
    ) -> AdminActionResponse:
        """
        Force a tournament status change.

        Args:
            tournament_id: Tournament ID
            status_update: New status and reason
            admin_id: ID of admin performing the change
            ip_address: IP address of admin

        Returns:
            Action response

        Raises:
            HTTPException: If tournament not found or invalid status
        """
        # Get tournament
        result = await self.db.execute(
            select(Tournament).filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()

        if not tournament:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tournament not found",
            )

        # Validate new status
        valid_statuses = [s.value for s in TournamentStatus]
        if status_update.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        # Store old status for audit
        old_status = tournament.status

        # Update status
        tournament.status = status_update.status
        await self.db.commit()
        await self.db.refresh(tournament)

        # Log to audit
        await self.audit_service.log_action(
            admin_id=admin_id,
            action_type=ActionType.TOURNAMENT_STATUS_CHANGE,
            target_type=TargetType.TOURNAMENT,
            target_id=tournament_id,
            details={
                "old_status": old_status,
                "new_status": status_update.status,
                "reason": status_update.reason,
            },
            ip_address=ip_address,
        )

        return AdminActionResponse(
            success=True,
            message=f"Tournament status changed to {status_update.status}",
            details={
                "tournament_id": tournament_id,
                "old_status": old_status,
                "new_status": status_update.status,
            },
        )
