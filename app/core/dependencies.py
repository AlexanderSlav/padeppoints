from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.auth import fastapi_users
from app.models.user import User
from app.models.tournament import Tournament
from app.db.base import get_db

get_current_user = fastapi_users.current_user(active=True)
get_current_superuser = fastapi_users.current_user(active=True, superuser=True)
get_optional_current_user = fastapi_users.current_user(optional=True)
get_current_verified_user = fastapi_users.current_user(active=True, verified=True)

async def get_tournament_as_organizer(
    tournament_id: str = Path(..., description="Tournament ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tournament:
    """
    Dependency that checks if the current user is the organizer of the tournament.
    Returns the tournament if the user is the organizer, raises 403 otherwise.
    """
    # Get tournament from database with players loaded
    result = await db.execute(
        select(Tournament)
        .options(selectinload(Tournament.players))
        .filter(Tournament.id == tournament_id)
    )
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    # Check if current user is the tournament organizer
    if tournament.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tournament organizers can perform this action"
        )
    
    return tournament

async def get_tournament_for_user(
    tournament_id: str = Path(..., description="Tournament ID"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Tournament:
    """
    Dependency that gets a tournament for any authenticated user.
    Returns the tournament if it exists, raises 404 otherwise.
    """
    # Get tournament from database with players loaded
    result = await db.execute(
        select(Tournament)
        .options(selectinload(Tournament.players))
        .filter(Tournament.id == tournament_id)
    )
    tournament = result.scalar_one_or_none()
    
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )
    
    return tournament
