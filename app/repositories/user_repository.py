"""User repository for database operations."""

from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for user-related database operations."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        if email is None:
            return None
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
    
    async def search_users(
        self, 
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """
        Search users by name or email with optional pagination.
        
        Args:
            search_query: Search term for name or email (case-insensitive, prefix matching)
            limit: Maximum number of results to return
            offset: Number of results to skip for pagination
        
        Returns:
            List of matching active users
        """
        query = select(self.model).filter(self.model.is_active == True)
        
        if search_query:
            search_pattern = f"%{search_query.lower()}%"
            query = query.filter(
                or_(
                    func.lower(self.model.full_name).like(search_pattern),
                    func.lower(self.model.email).like(search_pattern)
                )
            )
        
        if search_query:
            search_lower = search_query.lower()
            query = query.order_by(
                func.lower(self.model.full_name) == search_lower,
                func.lower(self.model.full_name).like(f"{search_lower}%"),
                self.model.full_name
            )
        else:
            query = query.order_by(self.model.full_name)
            
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_users(self, search_query: Optional[str] = None) -> int:
        """
        Count users matching search criteria.
        
        Args:
            search_query: Search term for name or email
            
        Returns:
            Total count of matching active users
        """
        query = select(func.count(self.model.id)).filter(self.model.is_active == True)
        
        if search_query:
            search_pattern = f"%{search_query.lower()}%"
            query = query.filter(
                or_(
                    func.lower(self.model.full_name).like(search_pattern),
                    func.lower(self.model.email).like(search_pattern)
                )
            )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_by_name_exact(self, full_name: str) -> Optional[User]:
        """Get user by exact name match (case-insensitive)."""
        result = await self.db.execute(
            select(self.model).filter(
                func.lower(self.model.full_name) == full_name.lower()
            )
        )
        return result.scalar_one_or_none() 