from typing import Optional
from pydantic import EmailStr
from fastapi_users import schemas as fu_schemas


class UserRead(fu_schemas.BaseUser[str]):
    full_name: Optional[str] = None
    picture: Optional[str] = None

    model_config = {"from_attributes": True}


class UserCreate(fu_schemas.BaseUserCreate):
    full_name: Optional[str] = None


class UserUpdate(fu_schemas.BaseUserUpdate):
    full_name: Optional[str] = None
    picture: Optional[str] = None
