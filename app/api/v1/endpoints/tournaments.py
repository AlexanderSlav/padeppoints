from typing import List
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid

from app.models.tournament import Tournament, TournamentSystem
from app.services.mock_db import MockDB

router = APIRouter()


class TournamentCreate(BaseModel):
    name: str
    system: TournamentSystem
    created_by: str  # In real app, this would come from authenticated user


class TournamentResponse(BaseModel):
    id: str
    name: str
    system: TournamentSystem
    created_by: str
    status: str

    class Config:
        from_attributes = True


@router.post("/", response_model=TournamentResponse)
def create_tournament(tournament: TournamentCreate):
    """Create a new tournament"""
    new_tournament = Tournament(
        id=str(uuid.uuid4()),
        name=tournament.name,
        system=tournament.system,
        created_by=tournament.created_by,
        status="pending"
    )
    return MockDB.create_tournament(new_tournament)


@router.get("/", response_model=List[TournamentResponse])
def list_tournaments():
    """List all tournaments"""
    return MockDB.list_tournaments()


@router.get("/{tournament_id}", response_model=TournamentResponse)
def get_tournament(tournament_id: str):
    """Get tournament details"""
    tournament = MockDB.get_tournament(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("/{tournament_id}/join")
def join_tournament(tournament_id: str, player_id: str):
    """Join a tournament as a player"""
    if not MockDB.get_tournament(tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    if MockDB.join_tournament(tournament_id, player_id):
        return {"message": "Successfully joined tournament"}
    raise HTTPException(status_code=400, detail="Already joined tournament")


@router.get("/{tournament_id}/players")
def get_tournament_players(tournament_id: str):
    """Get list of player IDs in a tournament"""
    if not MockDB.get_tournament(tournament_id):
        raise HTTPException(status_code=404, detail="Tournament not found")
    return {"players": MockDB.get_tournament_players(tournament_id)} 