"""Authentication endpoints for Google OAuth."""

import secrets
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.config import settings
from app.core.dependencies import get_current_user, get_optional_current_user
from app.db.base import get_db
from app.schemas.auth import (
    TokenResponse, 
    GoogleAuthUrlResponse, 
    GoogleCallbackRequest,
    UserResponse
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth_service import auth_service


router = APIRouter()


@router.get("/google/login", response_model=GoogleAuthUrlResponse)
async def google_login():
    """Initiate Google OAuth login flow."""
    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Get Google authorization URL
    auth_url = auth_service.get_google_auth_url(state=state)
    
    return GoogleAuthUrlResponse(auth_url=auth_url, state=state)


@router.get("/google/callback")
async def google_callback_redirect(
    code: str,
    state: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback redirect (GET request from Google)."""
    
    try:
        # Exchange authorization code for access token
        token_data = await auth_service.exchange_code_for_token(code)
        access_token = token_data.get("access_token")
        
        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google"
            )
        
        # Get user information from Google
        google_user_info = await auth_service.get_google_user_info(access_token)
        
        # Extract user data
        user_data = auth_service.extract_user_data(google_user_info)
        
        # Create or update user in database
        user_repo = UserRepository(db)
        user = await user_repo.create_or_update_user(user_data)
        
        # Create JWT token
        jwt_payload = {
            "sub": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
        jwt_token = auth_service.create_access_token(jwt_payload)
        
        # Return token response (or redirect to frontend with token)
        return {
            "message": "Authentication successful",
            "access_token": jwt_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "picture": user.picture,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser
            }
        }
        
    except Exception as e:
        logger.error(f"Google OAuth callback error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/logout")
async def logout(response: Response):
    """Logout user (client should discard the token)."""
    # Since we're using JWT tokens, we can't invalidate them server-side
    # The client should discard the token
    # In a production app, you might want to implement a token blacklist
    
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """Refresh user's access token."""
    
    # Create new JWT token
    jwt_payload = {
        "sub": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }
    jwt_token = auth_service.create_access_token(jwt_payload)
    
    return TokenResponse(
        access_token=jwt_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(current_user)
    )


@router.get("/status")
async def auth_status(
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Check authentication status."""
    if current_user:
        return {
            "authenticated": True,
            "user": UserResponse.model_validate(current_user)
        }
    else:
        return {"authenticated": False, "user": None}

