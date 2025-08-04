from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
import uuid

from app.core.auth import fastapi_users
from app.schemas.user import (
    UserRead, UserUpdate, UserCreate, PlayerSearchResult, UserSearchResponse, 
    GuestUserCreate, UserProfileResponse, UserProfileInfo, UserProfileStatistics,
    TournamentStatistics, EloRatingInfo, EloRatingPoint
)
from app.schemas.tournament import TournamentResponse
from app.core.dependencies import get_current_user, get_current_superuser
from app.core.user_manager import UserManager
from app.db.base import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.tournament_repository import TournamentRepository
from app.models.user import User
from app.models.player_rating import PlayerRating, RatingHistory
from app.models.round import Round
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload


def get_skill_level_from_rating(rating: float) -> tuple[str, float]:
    """
    Determine skill level and Playtomic level based on ELO rating.
    Returns tuple of (skill_level, playtomic_level)
    """
    skill_levels = [
        (1100, "Beginner", 1.0),
        (1200, "Novice", 2.0),
        (1300, "Improver", 2.5),
        (1400, "Weak Intermediate", 3.0),
        (1500, "Intermediate", 3.5),
        (1600, "Strong Intermediate", 4.0),
        (1700, "Weak Advanced", 4.5),
        (1800, "Advanced", 5.0),
        (1900, "Strong Advanced", 5.5),
        (2000, "Weak Expert", 6.0),
        (float('inf'), "Expert", 6.5),
    ]
    
    for threshold, level, playtomic in skill_levels:
        if rating < threshold:
            return level, playtomic
    
    return "Expert", 6.5  # Default for very high ratings


# Regular user router (public endpoints)
router = APIRouter()

# Admin-only router - visible in Swagger with proper protection
admin_router = APIRouter(
    prefix="/admin",
    tags=["🔒 Admin Only"],  # Clear visual indicator in Swagger
    dependencies=[Depends(get_current_superuser)],
    responses={
        403: {"description": "❌ Not enough permissions - Superuser required"},
        401: {"description": "❌ Not authenticated - Login required"},
    }
)

# Custom user endpoints with proper security instead of FastAPI-Users defaults
@router.get("/me", response_model=UserRead, summary="Get Current User")
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get information about the currently authenticated user."""
    return current_user

@router.patch("/me", response_model=UserRead, summary="Update Current User")
async def update_current_user_info(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update information for the currently authenticated user."""
    user_repo = UserRepository(db)
    
    # Only allow updating own profile
    update_data = user_update.model_dump(exclude_unset=True)
    updated_user = await user_repo.update(current_user.id, update_data)
    return updated_user

@router.delete("/me", summary="Delete Own Account")
async def delete_own_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete your own user account. This action cannot be undone."""
    user_repo = UserRepository(db)
    
    success = await user_repo.delete(current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
    
    return {"message": "Account deleted successfully"}

@router.get("/{user_id}", response_model=UserRead, summary="Get User by ID")
async def get_user_by_id(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user information by ID. Users can only see their own profile unless they're a superuser."""
    user_repo = UserRepository(db)
    
    # Allow superusers to see any user, regular users only see themselves
    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this user"
        )
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/{user_id}/profile", response_model=UserProfileResponse, summary="Get User Profile with Statistics")
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile with tournament statistics and ELO rating. Any authenticated user can view profiles."""
    user_repo = UserRepository(db)
    tournament_repo = TournamentRepository(db)
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get user's rating info
    rating_query = select(PlayerRating).where(PlayerRating.user_id == user_id)
    rating_result = await db.execute(rating_query)
    player_rating = rating_result.scalar_one_or_none()
    
    # Get rating history (last 10 tournaments - only final rating per tournament)
    rating_history = []
    if player_rating:
        # First get unique tournament IDs with their final ratings
        history_query = (
            select(RatingHistory)
            .where(RatingHistory.player_rating_id == player_rating.id)
            .order_by(desc(RatingHistory.timestamp))
        )
        history_result = await db.execute(history_query)
        all_entries = history_result.scalars().all()
        
        # Group by tournament and take only the last rating for each tournament
        tournament_final_ratings = {}
        for entry in all_entries:
            if entry.tournament_id:
                # Keep only the latest entry for each tournament
                if entry.tournament_id not in tournament_final_ratings:
                    tournament_final_ratings[entry.tournament_id] = entry
                elif entry.timestamp > tournament_final_ratings[entry.tournament_id].timestamp:
                    tournament_final_ratings[entry.tournament_id] = entry
        
        # Sort by timestamp and take last 10 tournaments
        sorted_entries = sorted(tournament_final_ratings.values(), key=lambda x: x.timestamp)[-10:]
        
        # Fetch tournament names
        tournament_ids = [e.tournament_id for e in sorted_entries if e.tournament_id]
        tournaments_dict = {}
        if tournament_ids:
            tournaments = await tournament_repo.get_by_ids(tournament_ids)
            tournaments_dict = {t.id: t.name for t in tournaments}
        
        # Convert to EloRatingPoint objects (round ratings to 2 decimal places)
        for entry in sorted_entries:
            rating_history.append(EloRatingPoint(
                tournament_id=entry.tournament_id,
                rating=round(entry.new_rating, 2),
                timestamp=entry.timestamp,
                tournament_name=tournaments_dict.get(entry.tournament_id, "Unknown")
            ))
    
    # Get user statistics
    joined_tournaments = await tournament_repo.get_tournaments_joined_by_user(user_id)
    completed_tournaments = [t for t in joined_tournaments if t.status == "completed"]
    
    # Calculate actual wins and podium finishes from tournament results
    tournaments_won = 0
    podium_finishes = 0
    
    for tournament in completed_tournaments:
        # Calculate player positions for this tournament
        player_scores = {}
        rounds_query = select(Round).where(Round.tournament_id == tournament.id)
        rounds_result = await db.execute(rounds_query)
        rounds = rounds_result.scalars().all()
        
        # Calculate total scores for each player
        for match_round in rounds:
            # Team 1 scores
            if match_round.team1_player1_id not in player_scores:
                player_scores[match_round.team1_player1_id] = 0
            if match_round.team1_player2_id not in player_scores:
                player_scores[match_round.team1_player2_id] = 0
            player_scores[match_round.team1_player1_id] += match_round.team1_score or 0
            player_scores[match_round.team1_player2_id] += match_round.team1_score or 0
            
            # Team 2 scores
            if match_round.team2_player1_id not in player_scores:
                player_scores[match_round.team2_player1_id] = 0
            if match_round.team2_player2_id not in player_scores:
                player_scores[match_round.team2_player2_id] = 0
            player_scores[match_round.team2_player1_id] += match_round.team2_score or 0
            player_scores[match_round.team2_player2_id] += match_round.team2_score or 0
        
        # Sort players by score to get positions
        sorted_players = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Find user's position
        for position, (player_id, score) in enumerate(sorted_players, 1):
            if player_id == user_id:
                if position == 1:
                    tournaments_won += 1
                    podium_finishes += 1  # 1st place is also a podium finish
                elif position <= 3:
                    podium_finishes += 1  # 2nd or 3rd place
                break
    
    # Calculate tournament statistics
    tournament_stats = TournamentStatistics(
        total_played=len(completed_tournaments),
        tournaments_won=tournaments_won,
        podium_finishes=podium_finishes,
        average_points_percentage=player_rating.average_point_percentage if player_rating else 0.0
    )
    
    # Determine skill level and Playtomic level based on rating
    current_rating = player_rating.current_rating if player_rating else 1000.0
    skill_level, playtomic_level = get_skill_level_from_rating(current_rating)
    
    # Calculate recent change
    recent_change = 0.0
    if len(rating_history) >= 2:
        # Difference between last two tournaments
        recent_change = rating_history[-1].rating - rating_history[-2].rating
    elif len(rating_history) == 1:
        # Difference from initial rating (1000) for first tournament
        recent_change = rating_history[0].rating - 1000.0
    
    # Build ELO rating info (round ratings to 2 decimal places)
    elo_info = EloRatingInfo(
        current_rating=round(current_rating, 2),
        peak_rating=round(player_rating.peak_rating if player_rating else 1000.0, 2),
        recent_change=round(recent_change, 2),
        percentile=None,  # TODO: Calculate percentile among all players
        skill_level=skill_level,
        playtomic_level=playtomic_level,
        rating_history=rating_history
    )
    
    # Build user profile info
    user_info = UserProfileInfo(
        id=user.id,
        full_name=user.full_name,
        email=user.email,
        is_guest=user.email is None,
        is_verified=user.is_verified,
        is_active=user.is_active
    )
    
    # Build profile statistics
    profile_stats = UserProfileStatistics(
        tournament_stats=tournament_stats,
        elo_rating=elo_info,
        member_since=user.created_at if hasattr(user, 'created_at') else None
    )
    
    # Build recent tournaments with user placement
    recent_tournaments_list = []
    for t in joined_tournaments[:5]:
        tournament_dict = TournamentResponse.model_validate(t).model_dump()
        
        # Get actual user placement from tournament results
        if t.status == "completed":
            # Calculate all players' total scores from rounds
            player_scores = {}
            
            # Get all rounds for this tournament
            rounds_query = select(Round).where(Round.tournament_id == t.id)
            rounds_result = await db.execute(rounds_query)
            rounds = rounds_result.scalars().all()
            
            # Calculate total scores for each player
            for match_round in rounds:
                # Team 1 scores
                if match_round.team1_player1_id not in player_scores:
                    player_scores[match_round.team1_player1_id] = 0
                if match_round.team1_player2_id not in player_scores:
                    player_scores[match_round.team1_player2_id] = 0
                player_scores[match_round.team1_player1_id] += match_round.team1_score or 0
                player_scores[match_round.team1_player2_id] += match_round.team1_score or 0
                
                # Team 2 scores
                if match_round.team2_player1_id not in player_scores:
                    player_scores[match_round.team2_player1_id] = 0
                if match_round.team2_player2_id not in player_scores:
                    player_scores[match_round.team2_player2_id] = 0
                player_scores[match_round.team2_player1_id] += match_round.team2_score or 0
                player_scores[match_round.team2_player2_id] += match_round.team2_score or 0
            
            # Sort players by score (descending) to get positions
            sorted_players = sorted(player_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Find user's position (1-indexed)
            for position, (player_id, score) in enumerate(sorted_players, 1):
                if player_id == user_id:
                    tournament_dict["user_placement"] = position
                    break
        
        recent_tournaments_list.append(tournament_dict)
    
    recent_tournaments = {
        "created": [],  # Not showing created tournaments in this view
        "joined": recent_tournaments_list
    }
    
    return UserProfileResponse(
        user=user_info,
        statistics=profile_stats,
        recent_tournaments=recent_tournaments
    )

@router.get("/", response_model=UserSearchResponse, summary="Search Players")
async def search_users(
    search: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search for players by name or email.
    
    - **search**: Search term (case-insensitive, supports partial matching)
    - **limit**: Maximum number of results (default: 50, max: 100)
    - **offset**: Skip this many results for pagination (default: 0)
    
    Returns players with basic information (id, name, picture) for privacy.
    """
    # Validate limits
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    if offset < 0:
        offset = 0
    
    user_repo = UserRepository(db)
    
    # Get users and total count
    users = await user_repo.search_users(
        search_query=search,
        limit=limit,
        offset=offset
    )
    total = await user_repo.count_users(search_query=search)
    
    return UserSearchResponse(
        users=[PlayerSearchResult.model_validate(user) for user in users],
        total=total,
        limit=limit,
        offset=offset
    )

@router.post("/guest", response_model=UserRead, summary="Create Guest User")
async def create_guest_user(
    guest_data: GuestUserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a guest user with just a name (no email required).
    
    This is useful for adding players to tournaments who don't have accounts.
    Guest users will have empty email and cannot log in.
    """
    from loguru import logger
    
    logger.info(f"Creating guest user: {guest_data.full_name}")
    
    user_repo = UserRepository(db)
    
    # Check if a user with this name already exists (case-insensitive)
    existing_user = await user_repo.get_by_name_exact(guest_data.full_name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A user with the name '{guest_data.full_name}' already exists"
        )
    
    # Create guest user data
    guest_user_data = {
        "id": str(uuid.uuid4()),
        "full_name": guest_data.full_name,
        "email": None,  # Empty email for guest users
        "is_active": True,
        "is_verified": True,  # Guest users are considered "verified" since they're created by authenticated users
        "is_superuser": False,
        "hashed_password": None
    }
    
    logger.info(f"Guest user data: {guest_user_data}")
    
    try:
        guest_user = await user_repo.create(guest_user_data)
        logger.info(f"Successfully created guest user: {guest_user.id}")
        return guest_user
    except Exception as e:
        logger.error(f"Failed to create guest user: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create guest user: {str(e)}"
        )

# Admin-only endpoints
@admin_router.get("/", response_model=List[UserRead], summary="🔍 List All Users (Admin)")
async def list_all_users_admin(
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    **🔒 SUPERUSER ONLY** - Get detailed list of all users with full information.
    
    Unlike the public search endpoint, this returns complete user details including email,
    superuser status, verification status, etc.
    """
    user_repo = UserRepository(db)
    
    # Get users (admin version shows all details)
    users = await user_repo.search_users(
        search_query=search,
        limit=min(limit, 500),  # Higher limit for admins
        offset=max(offset, 0)
    )
    
    return users

@admin_router.post("/create-superuser", 
                  response_model=UserRead,
                  summary="🛡️ Create Superuser",
                  description="**🔒 SUPERUSER ONLY** - Create a new user with superuser privileges.")
async def create_superuser(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new superuser.
    
    This endpoint is only available to existing superusers.
    The created user will have full administrative privileges.
    """
    from app.core.user_manager import get_user_manager
    
    # Get user manager
    user_db = SQLAlchemyUserDatabase(db, User)
    user_manager = UserManager(user_db)
    
    # Check if user already exists
    existing_user = await user_manager.get_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Use FastAPI-Users built-in create method
    try:
        # Create user with superuser privileges
        superuser = await user_manager.create(
            user_data,
            safe=False,  # Allow creation without email verification
            request=None
        )
        
        # Promote to superuser (FastAPI-Users doesn't allow this in create directly)
        superuser.is_superuser = True
        superuser.is_verified = True
        await user_db.update(superuser)
        
        return superuser
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create superuser: {str(e)}"
        )

@admin_router.delete("/{user_id}",
                    summary="🗑️ Delete User",
                    description="**🔒 SUPERUSER ONLY** - Delete a user by ID. Includes safety checks.")
async def delete_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """
    Delete a user by ID.
    
    This endpoint is only available to superusers and includes safety checks:
    - User must exist
    - Cannot delete your own account
    """
    user_repo = UserRepository(db)
    
    # Check if user exists first
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent superuser from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    # Delete the user
    success = await user_repo.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )
    
    return {"message": "User deleted successfully"}

@admin_router.patch("/{user_id}/promote",
                   response_model=UserRead,
                   summary="⬆️ Promote to Superuser",
                   description="**🔒 SUPERUSER ONLY** - Promote an existing user to superuser status.")
async def promote_user_to_superuser(
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Promote an existing user to superuser status.
    
    Useful for upgrading regular users to administrators.
    """
    user_repo = UserRepository(db)
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a superuser"
        )
    
    # Promote user
    updated_user = await user_repo.update(user_id, {"is_superuser": True})
    return updated_user

