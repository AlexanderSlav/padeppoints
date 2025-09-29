"""Player profile and ELO rating endpoints."""
from typing import List, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.services.elo_service import ELOService
from pydantic import BaseModel


router = APIRouter()


class PlayerStatistics(BaseModel):
    """Player statistics response model."""
    user: Dict
    rating: Dict
    statistics: Dict
    podium: Dict
    recent_history: List[Dict]


class LeaderboardEntry(BaseModel):
    """Leaderboard entry model."""
    rank: int
    user: Dict
    rating: float
    matches_played: int
    win_rate: float
    trend: str


@router.get("/profile/{user_id}", response_model=PlayerStatistics)
async def get_player_profile(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive player profile with ELO rating and statistics."""
    elo_service = ELOService(db)
    
    try:
        statistics = await elo_service.get_player_statistics(user_id)
        if not statistics.get("user"):
            raise HTTPException(status_code=404, detail="Player not found")
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profile", response_model=PlayerStatistics)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile with ELO rating and statistics."""
    elo_service = ELOService(db)
    
    try:
        statistics = await elo_service.get_player_statistics(current_user.id)
        return statistics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ELO rating leaderboard."""
    elo_service = ELOService(db)
    
    try:
        leaderboard = await elo_service.get_leaderboard(limit=limit)
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_players(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search for players by name or email."""
    from sqlalchemy import select, or_
    
    search_term = f"%{query}%"
    
    result = await db.execute(
        select(User)
        .filter(
            or_(
                User.full_name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )
        .limit(limit)
    )
    
    players = result.scalars().all()
    
    return [
        {
            "id": player.id,
            "full_name": player.full_name,
            "email": player.email,
            "picture": player.picture
        }
        for player in players
    ]