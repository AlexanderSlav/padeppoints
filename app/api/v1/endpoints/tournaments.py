from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.tournament import Tournament
from app.models.user import User
from app.schemas.tournament import TournamentCreate, TournamentResponse, TournamentUpdate
from app.repositories.tournament_repository import TournamentRepository
from app.db.base import get_db
from app.core.dependencies import get_current_user

router = APIRouter()


@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tournament"""
    tournament_data = {
        "id": str(uuid.uuid4()),
        "name": tournament.name,
        "description": tournament.description,
        "location": tournament.location,
        "start_date": tournament.start_date,
        "entry_fee": tournament.entry_fee,
        "max_players": tournament.max_players,
        "system": tournament.system,
        "created_by": current_user.id,
        "status": "pending"
    }
    
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.create(tournament_data)


@router.get("/", response_model=List[TournamentResponse])
async def list_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tournaments for the current user"""
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.get_by_user(current_user.id)


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: str, db: AsyncSession = Depends(get_db)):
    """Get tournament details"""
    tournament_repo = TournamentRepository(db)
    tournament = await tournament_repo.get_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return tournament


@router.post("/{tournament_id}/join")
async def join_tournament(
    tournament_id: str, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a tournament as a player"""
    tournament_repo = TournamentRepository(db)
    success = await tournament_repo.join_tournament(tournament_id, current_user.id)
    if success:
        return {"message": "Successfully joined tournament"}
    raise HTTPException(status_code=400, detail="Failed to join tournament")


@router.get("/{tournament_id}/players")
async def get_tournament_players(tournament_id: str, db: AsyncSession = Depends(get_db)):
    """Get list of player IDs in a tournament"""
    tournament_repo = TournamentRepository(db)
    tournament = await tournament_repo.get_by_id(tournament_id)
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")
    return {"players": await tournament_repo.get_tournament_players(tournament_id)} 