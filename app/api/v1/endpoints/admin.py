"""
Admin API Endpoints

REST API endpoints for administrative operations including statistics,
user management, tournament management, and audit logging.

All endpoints require superuser authentication.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_superuser
from app.models.user import User
from app.models.audit_log import ActionType, TargetType
from app.db.base import get_db
from app.schemas.admin import (
    # Statistics
    OverviewStats,
    GrowthData,
    EngagementMetrics,
    # User Management
    AdminUserDetails,
    UserListResponse,
    UserStatusUpdate,
    UserDeleteRequest,
    AdminUserDetail,
    # Tournament Management
    TournamentListResponse,
    MatchResultUpdate,
    TournamentStatusUpdate,
    RecalculateScoresRequest,
    AdminActionResponse,
    # Audit
    AuditLogListResponse,
    AuditStatsResponse,
    AuditLogResponse,
)
from app.services.admin import (
    AuditService,
    AdminStatsService,
    AdminUserService,
    AdminTournamentService,
)
from app.services.tournament_result_service import TournamentResultService


router = APIRouter(prefix="/admin", tags=["admin"])


def get_client_ip(request: Request) -> Optional[str]:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ============================================================================
# Statistics Endpoints
# ============================================================================

@router.get("/stats/overview", response_model=OverviewStats)
async def get_overview_stats(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get overview statistics for admin dashboard.

    Returns user stats, tournament stats, activity metrics, and system health.
    """
    stats_service = AdminStatsService(db)
    return await stats_service.get_overview_stats()


@router.get("/stats/growth", response_model=GrowthData)
async def get_growth_stats(
    period: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user growth and tournament creation trends.

    Args:
        period: Grouping period (daily, weekly, monthly)
    """
    stats_service = AdminStatsService(db)
    return await stats_service.get_user_growth(period)


@router.get("/stats/engagement", response_model=EngagementMetrics)
async def get_engagement_metrics(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get user engagement metrics.

    Returns most active users, top organizers, and retention metrics.
    """
    stats_service = AdminStatsService(db)
    return await stats_service.get_engagement_metrics()


# ============================================================================
# User Management Endpoints
# ============================================================================

@router.get("/users", response_model=UserListResponse)
async def get_users(
    search: Optional[str] = Query(None, description="Search by name or email"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    is_superuser: Optional[bool] = Query(None, description="Filter by superuser status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of users with filtering options.
    """
    audit_service = AuditService(db)
    user_service = AdminUserService(db, audit_service)
    return await user_service.get_users(
        search=search,
        is_active=is_active,
        is_verified=is_verified,
        is_superuser=is_superuser,
        limit=limit,
        offset=offset,
    )


@router.get("/users/{user_id}", response_model=AdminUserDetails)
async def get_user_details(
    user_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific user.
    """
    audit_service = AuditService(db)
    user_service = AdminUserService(db, audit_service)
    return await user_service.get_user_details(user_id)


@router.patch("/users/{user_id}", response_model=AdminUserDetail)
async def update_user_status(
    user_id: str,
    updates: UserStatusUpdate,
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Update user status (active, verified, superuser).

    Requires reason for audit trail.
    """
    audit_service = AuditService(db)
    user_service = AdminUserService(db, audit_service)
    return await user_service.update_user_status(
        user_id=user_id,
        updates=updates,
        admin_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.delete("/users/{user_id}", response_model=AdminActionResponse)
async def delete_user(
    user_id: str,
    delete_request: UserDeleteRequest,
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user (soft or hard delete).

    Soft delete (default): Sets is_active to False
    Hard delete: Permanently removes user and related data
    """
    audit_service = AuditService(db)
    user_service = AdminUserService(db, audit_service)
    await user_service.delete_user(
        user_id=user_id,
        admin_id=current_user.id,
        permanent=delete_request.permanent,
        reason=delete_request.reason,
        ip_address=get_client_ip(request),
    )
    return AdminActionResponse(
        success=True,
        message=f"User {'permanently deleted' if delete_request.permanent else 'deactivated'}",
        details={"user_id": user_id, "permanent": delete_request.permanent},
    )


# ============================================================================
# Tournament Management Endpoints
# ============================================================================

@router.get("/tournaments", response_model=TournamentListResponse)
async def get_tournaments(
    search: Optional[str] = Query(None, description="Search by tournament name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tournament_system: Optional[str] = Query(None, description="Filter by system"),
    creator_id: Optional[str] = Query(None, description="Filter by creator"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated list of tournaments with filtering options.
    """
    audit_service = AuditService(db)
    result_service = TournamentResultService(db)
    tournament_service = AdminTournamentService(db, audit_service, result_service)
    return await tournament_service.get_tournaments(
        search=search,
        status_filter=status,
        tournament_system=tournament_system,
        creator_id=creator_id,
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/tournaments/{tournament_id}/results/{round_id}",
    response_model=AdminActionResponse,
)
async def update_match_result(
    tournament_id: str,
    round_id: str,
    result_update: MatchResultUpdate,
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a match result.

    Requires reason for audit trail.
    Scores must sum to tournament's points_per_match.
    """
    audit_service = AuditService(db)
    result_service = TournamentResultService(db)
    tournament_service = AdminTournamentService(db, audit_service, result_service)
    return await tournament_service.update_match_result(
        tournament_id=tournament_id,
        round_id=round_id,
        result_update=result_update,
        admin_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.post(
    "/tournaments/{tournament_id}/recalculate",
    response_model=AdminActionResponse,
)
async def recalculate_tournament_scores(
    tournament_id: str,
    recalc_request: RecalculateScoresRequest,
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Recalculate all scores for a tournament.

    Requires reason for audit trail.
    """
    audit_service = AuditService(db)
    result_service = TournamentResultService(db)
    tournament_service = AdminTournamentService(db, audit_service, result_service)
    return await tournament_service.recalculate_tournament_scores(
        tournament_id=tournament_id,
        request=recalc_request,
        admin_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.patch(
    "/tournaments/{tournament_id}/status",
    response_model=AdminActionResponse,
)
async def force_tournament_status_change(
    tournament_id: str,
    status_update: TournamentStatusUpdate,
    request: Request,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Force a tournament status change.

    Requires reason for audit trail.
    Valid statuses: PENDING, ACTIVE, COMPLETED
    """
    audit_service = AuditService(db)
    result_service = TournamentResultService(db)
    tournament_service = AdminTournamentService(db, audit_service, result_service)
    return await tournament_service.force_status_change(
        tournament_id=tournament_id,
        status_update=status_update,
        admin_id=current_user.id,
        ip_address=get_client_ip(request),
    )


# ============================================================================
# Audit Log Endpoints
# ============================================================================

@router.get("/audit/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    admin_id: Optional[str] = Query(None, description="Filter by admin user ID"),
    action_type: Optional[ActionType] = Query(None, description="Filter by action type"),
    target_type: Optional[TargetType] = Query(None, description="Filter by target type"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get paginated audit logs with filtering options.
    """
    audit_service = AuditService(db)
    return await audit_service.get_audit_logs(
        admin_id=admin_id,
        action_type=action_type,
        target_type=target_type,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )


@router.get("/audit/stats", response_model=AuditStatsResponse)
async def get_audit_stats(
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get audit log statistics.

    Returns total actions, actions by type, actions by admin, and recent critical actions.
    """
    audit_service = AuditService(db)
    return await audit_service.get_audit_stats()


@router.get(
    "/audit/target/{target_type}/{target_id}",
    response_model=list[AuditLogResponse],
)
async def get_target_history(
    target_type: TargetType,
    target_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db),
):
    """
    Get complete audit history for a specific target entity.

    Useful for viewing all changes made to a user, tournament, etc.
    """
    audit_service = AuditService(db)
    return await audit_service.get_target_history(target_type, target_id)
