import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.models.tournament import Tournament
from app.models.round import Round
import uuid


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests
    test_database_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(test_database_url, echo=False)
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create a database session for testing."""
    async_session = sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency for testing."""
    def _override_get_db():
        return db_session
    return _override_get_db


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        id=str(uuid.uuid4()),
        email="test@example.com",
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_organizer(db_session: AsyncSession) -> User:
    """Create a test tournament organizer."""
    organizer = User(
        id=str(uuid.uuid4()),
        email="organizer@example.com",
        full_name="Tournament Organizer",
        is_active=True,
        is_verified=True
    )
    db_session.add(organizer)
    await db_session.commit()
    await db_session.refresh(organizer)
    return organizer


@pytest.fixture
async def test_players(db_session: AsyncSession) -> list[User]:
    """Create test players for tournaments."""
    players = []
    for i in range(8):  # Create 8 players for Americano
        player = User(
            id=str(uuid.uuid4()),
            email=f"player{i+1}@example.com",
            full_name=f"Player {i+1}",
            is_active=True,
            is_verified=True
        )
        db_session.add(player)
        players.append(player)
    
    await db_session.commit()
    for player in players:
        await db_session.refresh(player)
    
    return players


@pytest.fixture
async def test_tournament(db_session: AsyncSession, test_organizer: User, test_players: list[User]) -> Tournament:
    """Create a test tournament with players."""
    tournament = Tournament(
        id=str(uuid.uuid4()),
        name="Test Tournament",
        description="A test tournament",
        location="Test Location",
        start_date="2024-12-01",
        entry_fee=50.0,
        max_players=8,
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        created_by=test_organizer.id,
        status="pending"
    )
    
    # Add players to tournament
    tournament.players = test_players
    
    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)
    
    return tournament