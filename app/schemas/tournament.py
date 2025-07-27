from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from enum import Enum
from app.models.tournament import TournamentStatus

class TournamentSystem(str, Enum):
    AMERICANO = "AMERICANO"
    MEXICANO = "MEXICANO"

class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    start_date: date
    entry_fee: float
    max_players: int = 16
    system: TournamentSystem = TournamentSystem.AMERICANO
    points_per_match: int = 32  # Points needed to win a match
    courts: int = 1  # Number of courts available

class TournamentCreate(TournamentBase):
    @field_validator('entry_fee')
    @classmethod
    def validate_entry_fee(cls, v):
        if v < 0:
            raise ValueError('Entry fee must be non-negative')
        return v
    
    @field_validator('max_players')
    @classmethod
    def validate_max_players(cls, v):
        if v not in [4, 8, 12, 16, 20, 24, 32]:
            raise ValueError('Max players must be 4, 8, 12, 16, 20, or 24')
        return v
    
    @field_validator('points_per_match')
    @classmethod
    def validate_points_per_match(cls, v):
        if v < 1:
            raise ValueError('Points per match must be at least 1')
        return v
    
    @field_validator('courts')
    @classmethod
    def validate_courts(cls, v):
        if v < 1:
            raise ValueError('Courts must be at least 1')
        return v

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[date] = None
    entry_fee: Optional[float] = None
    max_players: Optional[int] = None
    system: Optional[TournamentSystem] = None
    status: Optional[str] = None

class TournamentResponse(TournamentBase):
    id: str
    created_at: datetime
    created_by: str
    status: str
    current_round: int
    
    model_config = {"from_attributes": True}

class TournamentFilter(BaseModel):
    """Query parameters for filtering tournaments"""
    format: Optional[TournamentSystem] = None
    status: Optional[str] = None  # pending, active, completed
    start_date_from: Optional[date] = None
    start_date_to: Optional[date] = None
    location: Optional[str] = None
    created_by_me: Optional[bool] = False  # Filter to show only user's tournaments

class TournamentJoinResponse(BaseModel):
    success: bool
    message: str
    current_players: Optional[int] = None
    max_players: Optional[int] = None

class TournamentPlayerResponse(BaseModel):
    id: str
    full_name: str
    email: Optional[str] = None

class TournamentPlayersResponse(BaseModel):
    tournament_id: str
    tournament_name: str
    current_players: int
    max_players: int
    is_full: bool
    can_join: bool
    players: List[TournamentPlayerResponse]

class TournamentListResponse(BaseModel):
    tournaments: List[TournamentResponse]
    total: int 