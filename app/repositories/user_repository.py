"""User repository for database operations."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user-related database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        result = await self.db.execute(
            select(self.model).filter(self.model.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_user(self, user_data: dict) -> User:
        """Create new user or update existing one based on email."""
        existing_user = await self.get_by_email(user_data["email"])
        
        if existing_user:
            # Update existing user
            for key, value in user_data.items():
                if key != "id":  # Don't update the ID
                    setattr(existing_user, key, value)
            await self.db.commit()
            await self.db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            return await self.create(user_data)
    
    async def deactivate_user(self, user_id: str) -> bool:
        """Deactivate a user account."""
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = False
            await self.db.commit()
            return True
        return False
    
    async def activate_user(self, user_id: str) -> bool:
        """Activate a user account."""
        user = await self.get_by_id(user_id)
        if user:
            user.is_active = True
            await self.db.commit()
            return True
        return False 