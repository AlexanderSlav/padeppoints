import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.base import Base
from app.core.config import settings
from app.db.base import get_db
from app.models.user import User
from app.models.tournament import Tournament
from app.models.round import Round
import uuid
from datetime import date
from fastapi.testclient import TestClient
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests with proper settings
    test_database_url = "sqlite+aiosqlite:///:memory:"
    engine = create_async_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """Create a database session for testing."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override the get_db dependency for testing."""
    def _override_get_db():
        return db_session
    return _override_get_db


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def test_tournament(db_session: AsyncSession, test_organizer: User, test_players: list[User]) -> Tournament:
    """Create a test tournament with players."""
    tournament = Tournament(
        id=str(uuid.uuid4()),
        name="Test Tournament",
        description="A test tournament",
        location="Test Location",
        start_date=date(2024, 12, 1),
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


@pytest.fixture
def test_app(override_get_db):
    """Create test FastAPI app with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(test_app):
    """Create async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
def americano_tournament_factory(mocker):
    """
    Shared factory fixture for creating Americano tournaments with mock data.
    This replaces duplicate fixtures across test files.
    """
    def _create(num_players, courts=None, points_per_match=32):
        from app.models.tournament import Tournament, TournamentSystem
        from app.models.user import User
        
        tournament = mocker.Mock(spec=Tournament)
        tournament.id = str(uuid.uuid4())
        tournament.system = TournamentSystem.AMERICANO
        tournament.points_per_match = points_per_match
        tournament.courts = courts or max(1, num_players // 8)
        tournament.max_players = num_players
        
        # Create mock players with consistent IDs
        players = []
        for i in range(num_players):
            player = mocker.Mock(spec=User)
            player.id = f"P{i}"  # Short, consistent IDs
            player.full_name = f"Player {i+1}"
            player.email = f"player{i+1}@test.com"
            players.append(player)
        
        tournament.players = players
        return tournament, players
    
    return _create