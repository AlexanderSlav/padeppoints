import pytest
from app.models.tournament import Tournament, TournamentStatus, tournament_player
from app.models.user import User
from app.models.round import Round
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid


@pytest.mark.asyncio
async def test_create_tournament(async_client, db_session: AsyncSession, test_organizer: User):
    """Test tournament creation."""
    tournament_data = {
        "name": "Test Tournament",
        "description": "A test tournament",
        "location": "Test Location",
        "start_date": "2024-12-01",
        "entry_fee": 50.0,
        "max_players": 8,
        "system": "AMERICANO",
        "points_per_match": 32,
        "courts": 2
    }
    
    # Mock authentication
    from app.core.dependencies import get_current_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    
    response = await async_client.post("/api/v1/tournaments/", json=tournament_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == tournament_data["name"]
    assert data["status"] == "pending"
    assert data["created_by"] == test_organizer.id


@pytest.mark.asyncio
async def test_start_tournament(async_client, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
    """Test starting a tournament."""
    # Mock authentication and tournament access
    from app.core.dependencies import get_current_user, get_tournament_as_organizer
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    async_client._transport.app.dependency_overrides[get_tournament_as_organizer] = lambda: test_tournament
    
    response = await async_client.post(f"/api/v1/tournaments/{test_tournament.id}/start")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["current_round"] == 1



@pytest.mark.asyncio
async def test_get_tournament_leaderboard(async_client, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User, test_players: list[User]):
    """Test getting tournament leaderboard."""
    # Set tournament to active status
    test_tournament.status = TournamentStatus.ACTIVE.value
    await db_session.commit()
    
    # Create some completed matches
    match = Round(
        id=str(uuid.uuid4()),
        tournament_id=test_tournament.id,
        round_number=1,
        team1_player1_id=test_players[0].id,
        team1_player2_id=test_players[1].id,
        team2_player1_id=test_players[2].id,
        team2_player2_id=test_players[3].id,
        team1_score=17,
        team2_score=15,
        is_completed=True
    )
    db_session.add(match)
    await db_session.commit()
    
    # Mock authentication
    from app.core.dependencies import get_current_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    
    response = await async_client.get(f"/api/v1/tournaments/{test_tournament.id}/leaderboard")
    
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert "tournament_id" in data
    assert len(data["entries"]) > 0
    # Check new fields
    first_entry = data["entries"][0]
    assert "points_difference" in first_entry
    assert "wins" in first_entry
    assert "losses" in first_entry
    assert "ties" in first_entry


@pytest.mark.asyncio
async def test_record_match_result(async_client, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User, test_players: list[User]):
    """Test recording match result."""
    # Set tournament to active status
    test_tournament.status = TournamentStatus.ACTIVE.value
    test_tournament.current_round = 1
    await db_session.commit()
    
    # Create a match
    match = Round(
        id=str(uuid.uuid4()),
        tournament_id=test_tournament.id,
        round_number=1,
        team1_player1_id=test_players[0].id,
        team1_player2_id=test_players[1].id,
        team2_player1_id=test_players[2].id,
        team2_player2_id=test_players[3].id,
        is_completed=False
    )
    db_session.add(match)
    await db_session.commit()
    
    # Mock authentication
    from app.core.dependencies import get_current_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    
    result_data = {
        "team1_score": 17,
        "team2_score": 15
    }
    
    response = await async_client.put(f"/api/v1/tournaments/matches/{match.id}/result", json=result_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["team1_score"] == 17
    assert data["team2_score"] == 15


@pytest.mark.asyncio
async def test_get_current_round_matches(async_client, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User, test_players: list[User]):
    """Test getting current round matches."""
    # Set tournament to active status
    test_tournament.status = TournamentStatus.ACTIVE.value
    test_tournament.current_round = 1
    await db_session.commit()
    
    # Create matches for current round
    match = Round(
        id=str(uuid.uuid4()),
        tournament_id=test_tournament.id,
        round_number=1,
        team1_player1_id=test_players[0].id,
        team1_player2_id=test_players[1].id,
        team2_player1_id=test_players[2].id,
        team2_player2_id=test_players[3].id,
        is_completed=False
    )
    db_session.add(match)
    await db_session.commit()
    
    # Mock authentication
    from app.core.dependencies import get_current_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    
    response = await async_client.get(f"/api/v1/tournaments/{test_tournament.id}/matches/current")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "team1_player1" in data[0]
    assert "team2_player1" in data[0]


@pytest.mark.asyncio
async def test_join_tournament(async_client, db_session: AsyncSession, test_user: User, test_organizer: User):
    """Test joining a tournament."""
    # Create a new tournament specifically for this test with space for more players
    from datetime import date
    tournament = Tournament(
        id=str(uuid.uuid4()),
        name="Join Test Tournament",
        description="A test tournament for joining",
        location="Test Location",
        start_date=date(2024, 12, 1),
        entry_fee=50.0,
        max_players=16,  # More space for joining
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        created_by=test_organizer.id,
        status="pending"
    )
    
    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)
    
    # Mock authentication and tournament access
    from app.core.dependencies import get_current_user, get_tournament_for_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_user
    async_client._transport.app.dependency_overrides[get_tournament_for_user] = lambda: tournament
    
    response = await async_client.post(f"/api/v1/tournaments/{tournament.id}/join")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


@pytest.mark.asyncio
async def test_get_share_link(async_client, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
    """Share link is created only once and returned."""
    from app.core.dependencies import get_current_user, get_tournament_as_organizer

    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_organizer
    async_client._transport.app.dependency_overrides[get_tournament_as_organizer] = lambda: test_tournament

    response1 = await async_client.get(f"/api/v1/tournaments/{test_tournament.id}/share-link")
    assert response1.status_code == 200
    link1 = response1.json()["join_link"]

    response2 = await async_client.get(f"/api/v1/tournaments/{test_tournament.id}/share-link")
    assert response2.status_code == 200
    link2 = response2.json()["join_link"]

    assert link1 == link2

    result = await db_session.execute(select(Tournament).filter(Tournament.id == test_tournament.id))
    tournament = result.scalar_one()
    assert tournament.join_code is not None
    assert tournament.join_code in link1


@pytest.mark.asyncio
async def test_join_tournament_by_code(async_client, db_session: AsyncSession, test_players: list[User], test_organizer: User):
    """A player can join a tournament using its join code."""
    from datetime import date
    from app.core.dependencies import get_current_user
    from app.repositories.tournament_repository import TournamentRepository

    tournament = Tournament(
        id=str(uuid.uuid4()),
        name="Join Code Tournament",
        description="Tournament join via code",
        location="Test Location",
        start_date=date(2024, 12, 1),
        entry_fee=50.0,
        max_players=8,
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        created_by=test_organizer.id,
        status="pending",
    )

    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)

    repo = TournamentRepository(db_session)
    join_code = await repo.get_or_create_join_code(tournament.id)

    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_players[0]

    response = await async_client.post(f"/api/v1/tournaments/join/{join_code}")
    assert response.status_code == 200

    result = await db_session.execute(
        select(tournament_player).where(
            tournament_player.c.tournament_id == tournament.id,
            tournament_player.c.player_id == test_players[0].id,
        )
    )
    assert result.first() is not None


@pytest.mark.asyncio
async def test_leave_tournament(async_client, db_session: AsyncSession, test_organizer: User, test_players: list[User]):
    """Test leaving a tournament."""
    # Create a tournament with the user already in it
    from datetime import date
    tournament = Tournament(
        id=str(uuid.uuid4()),
        name="Leave Test Tournament",
        description="A test tournament for leaving",
        location="Test Location",
        start_date=date(2024, 12, 1),
        entry_fee=50.0,
        max_players=16,
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        created_by=test_organizer.id,
        status="pending"
    )
    
    # Add the first player to the tournament
    tournament.players = [test_players[0]]
    
    db_session.add(tournament)
    await db_session.commit()
    await db_session.refresh(tournament)
    
    # Mock authentication and tournament access
    from app.core.dependencies import get_current_user, get_tournament_for_user
    async_client._transport.app.dependency_overrides[get_current_user] = lambda: test_players[0]
    async_client._transport.app.dependency_overrides[get_tournament_for_user] = lambda: tournament
    
    response = await async_client.post(f"/api/v1/tournaments/{tournament.id}/leave")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
