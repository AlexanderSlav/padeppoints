from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[str]):
    full_name: Optional[str] = None
    picture: Optional[str] = None

    model_config = {"from_attributes": True}


class UserCreate(schemas.BaseUserCreate):
    full_name: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    picture: Optional[str] = None
