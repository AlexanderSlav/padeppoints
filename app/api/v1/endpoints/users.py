from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
import uuid

from app.core.auth import fastapi_users
from app.schemas.user import UserRead, UserUpdate, UserCreate, PlayerSearchResult, UserSearchResponse, GuestUserCreate
from app.core.dependencies import get_current_user, get_current_superuser
from app.core.user_manager import UserManager
from app.db.base import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.tournament_repository import TournamentRepository
from app.models.user import User

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

@router.get("/{user_id}/profile", response_model=dict, summary="Get User Profile with Statistics")
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user profile with tournament statistics. Users can only see their own profile unless they're a superuser."""
    user_repo = UserRepository(db)
    tournament_repo = TournamentRepository(db)
    
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
    
    # Get user statistics
    created_tournaments = await tournament_repo.get_by_user(user_id)
    joined_tournaments = await tournament_repo.get_tournaments_joined_by_user(user_id)
    
    # Count tournaments by status
    created_stats = {
        "total": len(created_tournaments),
        "pending": len([t for t in created_tournaments if t.status == "pending"]),
        "active": len([t for t in created_tournaments if t.status == "active"]),
        "completed": len([t for t in created_tournaments if t.status == "completed"])
    }
    
    joined_stats = {
        "total": len(joined_tournaments),
        "pending": len([t for t in joined_tournaments if t.status == "pending"]),
        "active": len([t for t in joined_tournaments if t.status == "active"]),
        "completed": len([t for t in joined_tournaments if t.status == "completed"])
    }
    
    return {
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "is_guest": user.email is None,
            "is_verified": user.is_verified,
            "is_active": user.is_active
        },
        "statistics": {
            "tournaments_created": created_stats,
            "tournaments_joined": joined_stats
        },
        "recent_tournaments": {
            "created": created_tournaments[:5],  # Last 5 created
            "joined": joined_tournaments[:5]     # Last 5 joined
        }
    }

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

