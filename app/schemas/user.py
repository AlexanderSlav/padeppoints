from typing import Optional, List

from fastapi_users import schemas
from pydantic import BaseModel, EmailStr


class UserRead(schemas.BaseUser[str]):
    full_name: Optional[str] = None
    picture: Optional[str] = None
    email: Optional[str] = None  # Override to allow None for guest users

    model_config = {"from_attributes": True}


class UserCreate(schemas.BaseUserCreate):
    full_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    picture: Optional[str] = None


class PlayerSearchResult(BaseModel):
    """Simplified user info for player search results."""
    id: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    picture: Optional[str] = None
    
    model_config = {"from_attributes": True}


class UserSearchResponse(BaseModel):
    """Response schema for user search with pagination info."""
    users: List[PlayerSearchResult]
    total: int
    limit: int
    offset: int
    
    model_config = {"from_attributes": True}


class GuestUserCreate(BaseModel):
    """Schema for creating guest users (no email required)."""
    full_name: str
    
    model_config = {"from_attributes": True}
