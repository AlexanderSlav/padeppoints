from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr
from app.schemas.tournament import TournamentResponse


class UserRead(schemas.BaseUser[str]):
    full_name: Optional[str] = None
    picture: Optional[str] = None
    email: Optional[str] = None  # Override to allow None for guest users

    model_config = {"from_attributes": True}


class UserCreate(schemas.BaseUserCreate):
    full_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    picture: Optional[str] = None


class PlayerSearchResult(BaseModel):
    """Simplified user info for player search results."""
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None
    
    model_config = {"from_attributes": True}


class UserSearchResponse(BaseModel):
    """Response schema for user search with pagination info."""
    users: List[PlayerSearchResult]
    total: int
    limit: int
    offset: int
    
    model_config = {"from_attributes": True}


class GuestUserCreate(BaseModel):
    """Schema for creating guest users (no email required)."""
    full_name: str
    
    model_config = {"from_attributes": True}


class UserProfileInfo(BaseModel):
    """Basic user information for profile display."""
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    is_guest: bool
    is_verified: bool
    is_active: bool
    
    model_config = {"from_attributes": True}


class TournamentStatistics(BaseModel):
    """Tournament statistics for a user."""
    total_played: int = 0
    tournaments_won: int = 0
    podium_finishes: int = 0
    average_points_percentage: float = 0.0


class EloRatingPoint(BaseModel):
    """Single point in ELO rating history."""
    tournament_id: Optional[str] = None
    rating: float
    timestamp: datetime
    tournament_name: Optional[str] = None


class EloRatingInfo(BaseModel):
    """ELO rating information."""
    current_rating: float = 1000.0
    peak_rating: float = 1000.0
    recent_change: float = 0.0
    percentile: Optional[float] = None
    skill_level: str = "Beginner"  # Beginner, Novice, Improver, Intermediate, Advanced, Expert
    playtomic_level: Optional[float] = None  # Maps to Playtomic rating system (1.0-7.0)
    rating_history: List[EloRatingPoint] = []


class UserProfileStatistics(BaseModel):
    """User's complete profile statistics."""
    tournament_stats: TournamentStatistics
    elo_rating: EloRatingInfo
    member_since: Optional[datetime] = None


class UserProfileResponse(BaseModel):
    """Complete user profile response with statistics and recent tournaments."""
    user: UserProfileInfo
    statistics: UserProfileStatistics
    recent_tournaments: Dict[str, List[TournamentResponse]]
    
    model_config = {"from_attributes": True}
