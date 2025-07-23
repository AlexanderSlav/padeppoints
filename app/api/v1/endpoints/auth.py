from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from httpx_oauth.oauth2 import OAuth2Token
import httpx
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
import os
from dotenv import load_dotenv

from app.core.auth import fastapi_users, auth_backend, google_oauth_client
from app.core.config import settings
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.core.user_manager import get_user_manager
from app.db.base import get_db
from app.repositories.user_repository import UserRepository

load_dotenv()

router = APIRouter()

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/reset",
    tags=["auth"],
)

router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/verify",
    tags=["auth"],
)

# Google OAuth endpoints - simplified implementation based on Medium article
@router.get("/google/authorize")
async def google_authorize(request: Request):
    """Get Google OAuth authorization URL - simplified version."""
    try:
        # Build the callback URL dynamically
        callback_url = str(request.url_for('google_callback'))
        logger.info(f"🔍 OAuth: Generated callback URL: {callback_url}")
        
        # Generate authorization URL
        authorization_url = await google_oauth_client.get_authorization_url(
            redirect_uri=callback_url,
            scope=["openid", "email", "profile"],
        )
        
        logger.info(f"🔍 OAuth: Generated authorization URL: {authorization_url}")
        return {"authorization_url": authorization_url}
        
    except Exception as e:
        print(f"❌ OAuth: Error generating authorization URL: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate authorization URL")

@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_manager = Depends(get_user_manager)
):
    """Simplified Google OAuth callback based on Medium article approach."""
    try:
        # Get authorization code from URL parameters
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        
        print(f"🔍 OAuth Callback: Code present: {code is not None}, Error: {error}")
        
        # Handle OAuth errors
        if error:
            print(f"❌ OAuth Callback: OAuth error from Google: {error}")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/callback?error=auth_failed"
            )
        
        if not code:
            print("❌ OAuth Callback: No authorization code received")
            return RedirectResponse(
                url=f"{settings.FRONTEND_URL}/callback?error=auth_failed"
            )
        
        # Exchange authorization code for access token
        callback_url = str(request.url_for('google_callback'))
        print(f"🔍 OAuth Callback: Using callback URL: {callback_url}")
        
        token: OAuth2Token = await google_oauth_client.get_access_token(
            code, callback_url
        )
        print(f"✅ OAuth Callback: Successfully obtained access token")
        
        # Get user information from Google
        user_info = await get_google_user_info(token["access_token"])
        print(f"✅ OAuth Callback: Retrieved user info for: {user_info['email']}")
        
        # Create or update user in database
        user = await create_or_update_user(db, user_info)
        print(f"✅ OAuth Callback: User created/updated: {user.id}")
        
        # Generate JWT token for the user
        jwt_token = await auth_backend.get_strategy().write_token(user)
        print(f"✅ OAuth Callback: JWT token generated successfully")
        
        # Redirect to frontend with success and token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/callback?success=true&token={jwt_token}"
        )
        
    except Exception as e:
        print(f"❌ OAuth Callback: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/callback?error=auth_failed"
        )

# Helper function to get user info from Google - inspired by Medium article
async def get_google_user_info(access_token: str) -> dict:
    """Get user information from Google API using access token."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Failed to get user info from Google: {response.status_code}"
                )
            
            return response.json()
            
    except httpx.HTTPError as e:
        print(f"❌ Google API Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user information")

# Helper function to create or update user - simplified version
async def create_or_update_user(db: AsyncSession, user_info: dict):
    """Create or update user based on Google user info."""
    try:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(user_info["email"])
        
        if user:
            # Update existing user
            logger.info(f"🔄 Updating existing user: {user.email}")
            user.full_name = user_info.get("name", user.full_name)
            user.picture = user_info.get("picture", user.picture)
            user.is_verified = True
            await db.commit()
            return user
        else:
            # Create new user
            print(f"🆕 Creating new user: {user_info['email']}")
            user_data = {
                "email": user_info["email"],
                "full_name": user_info.get("name", ""),
                "picture": user_info.get("picture", ""),
                "is_active": True,
                "is_verified": True,
                "is_superuser": False,
                "hashed_password": None,  # OAuth users don't have passwords
            }
            user = await user_repo.create(user_data)
            return user
            
    except Exception as e:
        print(f"❌ Database Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error during user creation")
