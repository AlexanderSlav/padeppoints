from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class RoundBase(BaseModel):
    tournament_id: str
    round_number: int
    team1_player1_id: str
    team1_player2_id: str
    team2_player1_id: str
    team2_player2_id: str

class RoundCreate(RoundBase):
    pass

class MatchResultUpdate(BaseModel):
    team1_score: int
    team2_score: int

class PlayerInMatch(BaseModel):
    id: str
    full_name: str
    email: str

class RoundResponse(BaseModel):
    id: str
    tournament_id: str
    round_number: int
    
    # Team 1
    team1_player1: PlayerInMatch
    team1_player2: PlayerInMatch
    team1_score: int
    
    # Team 2
    team2_player1: PlayerInMatch
    team2_player2: PlayerInMatch
    team2_score: int
    
    is_completed: bool
    
    model_config = {"from_attributes": True}

class LeaderboardEntry(BaseModel):
    player_id: str
    player_name: str
    email: str
    score: int
    rank: int

class TournamentLeaderboard(BaseModel):
    tournament_id: str
    tournament_name: str
    entries: list[LeaderboardEntry]
    is_completed: bool
    winner: Optional[LeaderboardEntry] = None 