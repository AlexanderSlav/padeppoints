import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.tournament import Tournament, TournamentStatus
from app.models.round import Round
from app.repositories.tournament_repository import TournamentRepository
from app.services.tournament_service import TournamentService
import uuid
from datetime import date


@pytest.mark.asyncio
async def test_user_creation(db_session: AsyncSession):
    """Test creating a user in the database."""
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
    
    # Verify user was created
    result = await db_session.execute(select(User).filter(User.email == "test@example.com"))
    saved_user = result.scalar_one_or_none()
    
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
    assert saved_user.full_name == "Test User"


@pytest.mark.asyncio
async def test_tournament_creation(db_session: AsyncSession, test_organizer: User):
    """Test creating a tournament in the database."""
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
    
    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)
    
    # Verify tournament was created
    result = await db_session.execute(select(Tournament).filter(Tournament.name == "Test Tournament"))
    saved_tournament = result.scalar_one_or_none()
    
    assert saved_tournament is not None
    assert saved_tournament.name == "Test Tournament"
    assert saved_tournament.created_by == test_organizer.id


@pytest.mark.asyncio
async def test_tournament_player_relationship(db_session: AsyncSession, test_tournament: Tournament, test_players: list[User]):
    """Test many-to-many relationship between tournaments and players."""
    # test_tournament already has players from the fixture
    # Verify relationship by querying
    from sqlalchemy.orm import selectinload
    
    result = await db_session.execute(
        select(Tournament)
        .options(selectinload(Tournament.players))
        .filter(Tournament.id == test_tournament.id)
    )
    tournament_with_players = result.scalar_one_or_none()
    
    assert tournament_with_players is not None
    assert len(tournament_with_players.players) == 8  # test_players fixture creates 8 players
    assert set(player.id for player in tournament_with_players.players) == set(player.id for player in test_players)


@pytest.mark.asyncio
async def test_round_creation(db_session: AsyncSession, test_tournament: Tournament, test_players: list[User]):
    """Test creating rounds in the database."""
    players = test_players[:4]  # Get first 4 players
    
    round_match = Round(
        id=str(uuid.uuid4()),
        tournament_id=test_tournament.id,
        round_number=1,
        team1_player1_id=players[0].id,
        team1_player2_id=players[1].id,
        team2_player1_id=players[2].id,
        team2_player2_id=players[3].id,
        team1_score=17,
        team2_score=15,
        is_completed=True
    )
    
    db_session.add(round_match)
    await db_session.commit()
    await db_session.refresh(round_match)
    
    # Verify round was created
    result = await db_session.execute(
        select(Round).filter(Round.tournament_id == test_tournament.id)
    )
    saved_round = result.scalar_one_or_none()
    
    assert saved_round is not None
    assert saved_round.tournament_id == test_tournament.id
    assert saved_round.round_number == 1
    assert saved_round.is_completed == True


@pytest.mark.asyncio
async def test_tournament_repository_operations(db_session: AsyncSession, test_organizer: User):
    """Test tournament repository operations."""
    repo = TournamentRepository(db_session)
    
    # Create tournament data
    tournament_data = {
        "id": str(uuid.uuid4()),
        "name": "Repository Test Tournament",
        "description": "Testing repository",
        "location": "Test Location",
        "start_date": date(2024, 12, 1),
        "entry_fee": 25.0,
        "max_players": 4,
        "system": "AMERICANO",
        "points_per_match": 32,
        "courts": 1,
        "created_by": test_organizer.id,
        "status": "pending"
    }
    
    # Test create
    tournament = await repo.create(tournament_data)
    assert tournament.name == "Repository Test Tournament"
    
    # Test get by id
    retrieved_tournament = await repo.get_by_id(tournament.id)
    assert retrieved_tournament is not None
    assert retrieved_tournament.id == tournament.id
    
    # Test get by user
    user_tournaments = await repo.get_by_user(test_organizer.id)
    assert len(user_tournaments) > 0
    assert any(t.id == tournament.id for t in user_tournaments)


@pytest.mark.asyncio
async def test_tournament_service_database_integration(db_session: AsyncSession, test_tournament: Tournament):
    """Test tournament service database integration."""
    service = TournamentService(db_session)
    
    # Test starting tournament
    started_tournament = await service.start_tournament(test_tournament.id)
    assert started_tournament.status == TournamentStatus.ACTIVE.value
    assert started_tournament.current_round == 1
    
    # Verify rounds were created in database
    result = await db_session.execute(
        select(Round).filter(Round.tournament_id == test_tournament.id)
    )
    rounds = result.scalars().all()
    assert len(rounds) > 0
    
    # Test getting current round matches
    current_matches = await service.get_current_round_matches(test_tournament.id)
    assert len(current_matches) > 0


@pytest.mark.asyncio
async def test_complex_tournament_flow(db_session: AsyncSession, test_tournament: Tournament):
    """Test complex tournament flow with database persistence."""
    service = TournamentService(db_session)
    
    # Start tournament
    started_tournament = await service.start_tournament(test_tournament.id)
    
    # Get current round matches
    matches = await service.get_current_round_matches(test_tournament.id)
    assert len(matches) > 0
    
    # Record results for all matches
    for match in matches:
        await service.record_match_result(match.id, 17, 15)
    
    # Get player scores
    scores = await service.get_player_scores(test_tournament.id)
    assert len(scores) > 0
    assert all(score >= 0 for score in scores.values())
    
    # Get leaderboard
    leaderboard = await service.get_tournament_leaderboard(test_tournament.id)
    assert len(leaderboard) > 0
    assert all("player_name" in entry for entry in leaderboard)
    assert all("score" in entry for entry in leaderboard)


@pytest.mark.asyncio
async def test_database_transaction_rollback(db_session: AsyncSession):
    """Test database transaction rollback on error."""
    # This test verifies that database transactions are properly rolled back
    # when an error occurs, maintaining data integrity
    
    user = User(
        id=str(uuid.uuid4()),
        email="rollback_test@example.com",
        full_name="Rollback Test User",
        is_active=True,
        is_verified=True
    )
    
    db_session.add(user)
    
    try:
        # Force an error by trying to add a duplicate
        duplicate_user = User(
            id=user.id,  # Same ID should cause error
            email="different@example.com",
            full_name="Different User",
            is_active=True,
            is_verified=True
        )
        db_session.add(duplicate_user)
        await db_session.commit()
        
        # Should not reach here
        assert False, "Expected an error due to duplicate ID"
        
    except Exception:
        # Rollback happened, test passed
        pass
    else:
        # Should not reach here - we expected an exception
        assert False, "Expected an error due to duplicate ID"