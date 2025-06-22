"""Authentication schemas for API requests and responses."""

from typing import Optional
from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """User information response model."""
    id: str
    email: str
    full_name: Optional[str] = None
    picture: Optional[str] = None
    is_active: bool
    is_superuser: bool
    
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class GoogleAuthUrlResponse(BaseModel):
    """Google OAuth authorization URL response."""
    auth_url: str
    state: Optional[str] = None


class GoogleCallbackRequest(BaseModel):
    """Google OAuth callback request model."""
    code: str
    state: Optional[str] = None


class AuthErrorResponse(BaseModel):
    """Authentication error response model."""
    detail: str
    error_code: Optional[str] = None 