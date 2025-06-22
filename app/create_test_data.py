"""Script to create test data for development."""

import asyncio
from app.db.base import AsyncSessionLocal
from app.models.user import User

async def create_test_users():
    """Create test users for development."""
    async with AsyncSessionLocal() as session:
        # Check if users already exist
        from sqlalchemy import select
        result = await session.execute(select(User).filter(User.id == 'me'))
        if result.scalar_one_or_none():
            print("Test users already exist")
            return

        users = [
            User(
                id='me', 
                email='me@example.com', 
                full_name='Test User', 
                is_active=True
            ),
            User(
                id='admin', 
                email='admin@example.com', 
                full_name='Admin User', 
                is_active=True, 
                is_superuser=True
            ),
            User(
                id='player1', 
                email='player1@example.com', 
                full_name='Player One', 
                is_active=True
            ),
            User(
                id='player2', 
                email='player2@example.com', 
                full_name='Player Two', 
                is_active=True
            ),
        ]
        
        for user in users:
            session.add(user)
        
        await session.commit()
        print('Test users created successfully')

if __name__ == "__main__":
    asyncio.run(create_test_users()) 