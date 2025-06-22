"""Base module for the database."""

import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create an async engine
engine = create_async_engine(
    settings.db.dsn,
    echo=False,
)

# Create async session factory
AsyncSessionLocal = async_scoped_session(
    sessionmaker(engine, class_=AsyncSession, expire_on_commit=False),
    scopefunc=asyncio.current_task,
)

async def get_db() -> AsyncSession:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()