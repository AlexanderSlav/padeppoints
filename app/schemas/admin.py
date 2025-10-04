"""
Admin Panel Schemas

Request and response schemas for admin endpoints including statistics,
user management, tournament management, and audit logging.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.audit_log import ActionType, TargetType


# ============================================================================
# Statistics Schemas
# ============================================================================

class UserStatistics(BaseModel):
    """User-related statistics."""
    total: int
    active: int
    inactive: int
    verified: int
    unverified: int
    new_this_week: int
    new_this_month: int


class TournamentStatistics(BaseModel):
    """Tournament-related statistics."""
    total: int
    active: int
    pending: int
    completed: int
    by_format: Dict[str, int]


class ActivityStatistics(BaseModel):
    """Activity metrics."""
    matches_today: int
    matches_this_week: int
    avg_players_per_tournament: float
    peak_concurrent_tournaments: int


class SystemHealth(BaseModel):
    """System health information."""
    database_status: str
    total_users: int
    total_tournaments: int
    api_version: str


class OverviewStats(BaseModel):
    """Complete overview statistics for admin dashboard."""
    users: UserStatistics
    tournaments: TournamentStatistics
    activity: ActivityStatistics
    system: SystemHealth


class GrowthDataPoint(BaseModel):
    """Single data point for growth charts."""
    date: str
    count: int


class GrowthData(BaseModel):
    """Growth data for charts."""
    user_signups: List[GrowthDataPoint]
    tournament_creation: List[GrowthDataPoint]
    period: str  # daily, weekly, monthly


class TopUser(BaseModel):
    """Top user information for engagement metrics."""
    user_id: str
    full_name: Optional[str]
    email: Optional[str]
    tournaments_played: int
    tournaments_created: int


class EngagementMetrics(BaseModel):
    """User engagement metrics."""
    most_active_users: List[TopUser]
    top_organizers: List[TopUser]
    avg_tournaments_per_user: float
    retention_rate: float


# ============================================================================
# User Management Schemas
# ============================================================================

class AdminUserDetail(BaseModel):
    """Extended user details for admin view."""
    id: str
    email: Optional[str]
    full_name: Optional[str]
    picture: Optional[str]
    is_active: bool
    is_verified: bool
    is_superuser: bool
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class UserActivityStats(BaseModel):
    """User activity statistics."""
    tournaments_created: int
    tournaments_played: int
    matches_played: int
    account_age_days: int
    last_activity: Optional[datetime] = None


class AdminUserDetails(BaseModel):
    """Complete user details with statistics for admin."""
    user: AdminUserDetail
    statistics: UserActivityStats


class UserListResponse(BaseModel):
    """Paginated user list response."""
    users: List[AdminUserDetail]
    total: int
    limit: int
    offset: int


class UserStatusUpdate(BaseModel):
    """Request to update user status."""
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
    reason: Optional[str] = Field(None, description="Reason for status change (for audit log)")


class UserDeleteRequest(BaseModel):
    """Request to delete a user."""
    permanent: bool = Field(False, description="If true, hard delete. Otherwise soft delete.")
    reason: Optional[str] = Field(None, description="Reason for deletion (for audit log)")


# ============================================================================
# Tournament Management Schemas
# ============================================================================

class AdminTournamentListItem(BaseModel):
    """Tournament item in admin list view."""
    id: str
    name: str
    created_by: str
    creator_name: Optional[str]
    status: str
    tournament_system: str
    player_count: int
    rounds_completed: int
    rounds_total: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TournamentListResponse(BaseModel):
    """Paginated tournament list response."""
    tournaments: List[AdminTournamentListItem]
    total: int
    limit: int
    offset: int


class MatchResultUpdate(BaseModel):
    """Request to update match result."""
    team1_score: int = Field(..., ge=0, description="Team 1 score")
    team2_score: int = Field(..., ge=0, description="Team 2 score")
    reason: str = Field(..., min_length=1, description="Reason for result change (required for audit)")


class TournamentStatusUpdate(BaseModel):
    """Request to change tournament status."""
    status: str = Field(..., description="New status: PENDING, ACTIVE, or COMPLETED")
    reason: str = Field(..., min_length=1, description="Reason for status change (required for audit)")


class RecalculateScoresRequest(BaseModel):
    """Request to recalculate tournament scores."""
    reason: str = Field(..., min_length=1, description="Reason for recalculation (required for audit)")


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogResponse(BaseModel):
    """Audit log entry response."""
    id: str
    admin_id: Optional[str]
    admin_name: Optional[str] = None
    action_type: ActionType
    target_type: TargetType
    target_id: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    logs: List[AuditLogResponse]
    total: int
    limit: int
    offset: int


class AuditStatsResponse(BaseModel):
    """Audit log statistics."""
    total_actions: int
    actions_by_type: Dict[str, int]
    actions_by_admin: Dict[str, int]
    recent_critical_actions: int  # Last 24 hours


# ============================================================================
# Common Responses
# ============================================================================

class AdminActionResponse(BaseModel):
    """Generic response for admin actions."""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None
