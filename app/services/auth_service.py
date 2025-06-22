"""Authentication service for Google OAuth and JWT tokens."""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from fastapi import HTTPException, status
from loguru import logger

from app.core.config import settings


class AuthService:
    """Authentication service for handling OAuth and JWT operations."""
    
    def __init__(self):
        self.google_client_id = settings.GOOGLE_CLIENT_ID
        self.google_client_secret = settings.GOOGLE_CLIENT_SECRET
        self.google_redirect_uri = settings.GOOGLE_REDIRECT_URI
        self.jwt_secret = settings.JWT_SECRET_KEY
        self.jwt_algorithm = settings.JWT_ALGORITHM
        self.jwt_expire_minutes = settings.JWT_EXPIRE_MINUTES
        
        # Google OAuth URLs
        self.google_auth_url = "https://accounts.google.com/o/oauth2/auth"
        self.google_token_url = "https://oauth2.googleapis.com/token"
        self.google_user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    
    def get_google_auth_url(self, state: Optional[str] = None) -> str:
        """Generate Google OAuth authorization URL."""
        client = AsyncOAuth2Client(
            client_id=self.google_client_id,
            redirect_uri=self.google_redirect_uri
        )
        
        auth_url, _ = client.create_authorization_url(
            self.google_auth_url,
            scope="openid email profile",
            state=state
        )
        return auth_url
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        client = AsyncOAuth2Client(
            client_id=self.google_client_id,
            client_secret=self.google_client_secret,
            redirect_uri=self.google_redirect_uri
        )
        
        try:
            token = await client.fetch_token(
                self.google_token_url,
                code=code,
                grant_type="authorization_code"
            )
            return token
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )
    
    async def get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google using access token."""
        client = AsyncOAuth2Client(token={"access_token": access_token})
        
        try:
            response = await client.get(self.google_user_info_url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching user info: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fetch user information"
            )
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.jwt_expire_minutes)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        try:
            encoded_jwt = jwt.encode(
                to_encode, 
                self.jwt_secret, 
                algorithm=self.jwt_algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create access token"
            )
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token."""
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.jwt_algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def extract_user_data(self, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize user data from Google user info."""
        return {
            "id": google_user_info.get("id"),
            "email": google_user_info.get("email"),
            "full_name": google_user_info.get("name"),
            "picture": google_user_info.get("picture"),
            "is_active": True,
            "is_superuser": False
        }


# Global auth service instance
auth_service = AuthService() 