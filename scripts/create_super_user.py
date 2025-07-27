#!/usr/bin/env python3
"""Script to create the first superuser directly in the database."""

import asyncio
import uuid
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi_users.password import PasswordHelper
from dotenv import load_dotenv

from app.models.user import User
from app.core.config import settings

load_dotenv()

async def create_first_superuser():
    """Create the first superuser directly in the database."""
    
    print("🚀 Creating first superuser...")
    print("-" * 40)
    
    # Get superuser details
    email = input("Enter superuser email: ").strip()
    if not email:
        print("❌ Email is required!")
        return
        
    password = input("Enter superuser password: ").strip()
    if not password:
        print("❌ Password is required!")
        return
        
    full_name = input("Enter full name (optional): ").strip() or None
    
    # Create async engine
    engine = create_async_engine(settings.db.dsn, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Check if user already exists
            from sqlalchemy import select
            result = await session.execute(select(User).filter(User.email == email))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User with email {email} already exists!")
                if existing_user.is_superuser:
                    print(f"✅ This user is already a superuser.")
                else:
                    print(f"🔄 Making existing user a superuser...")
                    existing_user.is_superuser = True
                    await session.commit()
                    print(f"✅ User {email} is now a superuser!")
                return
            
            # Hash password
            password_helper = PasswordHelper()
            hashed_password = password_helper.hash(password)
            
            # Create superuser
            superuser = User(
                id=str(uuid.uuid4()),
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                is_superuser=True,
                is_active=True,
                is_verified=True
            )
            
            session.add(superuser)
            await session.commit()
            await session.refresh(superuser)
            
            print(f"✅ First superuser created successfully!")
            print(f"   📧 Email: {email}")
            print(f"   👤 Name: {full_name or 'Not provided'}")
            print(f"   🔑 ID: {superuser.id}")
            print(f"   🛡️  Superuser: {superuser.is_superuser}")
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_first_superuser()) 