from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator
from enum import Enum

class TournamentSystem(str, Enum):
    AMERICANO = "americano"
    MEXICANO = "mexicano"

class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    start_date: date
    entry_fee: float
    max_players: int = 16
    system: TournamentSystem = TournamentSystem.AMERICANO

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
        if v not in [8, 16, 32, 64]:
            raise ValueError('Max players must be 8, 16, 32, or 64')
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

class TournamentListResponse(BaseModel):
    tournaments: List[TournamentResponse]
    total: int 