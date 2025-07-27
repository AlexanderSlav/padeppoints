from typing import Optional, Any

from fastapi import Depends
from fastapi_users import BaseUserManager
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.db.base import get_db
from app.core.config import settings


async def get_user_db(session: AsyncSession = Depends(get_db)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(BaseUserManager[User, str]):
    reset_password_token_secret = settings.JWT_SECRET_KEY
    verification_token_secret = settings.JWT_SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Any] = None):
        pass

    def parse_id(self, value: Any) -> str:
        return str(value)


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
