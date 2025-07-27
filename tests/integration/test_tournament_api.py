import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from app.api.v1.api import api_router
from app.models.tournament import TournamentStatus
from app.models.user import User
from app.models.tournament import Tournament
from app.models.round import Round
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid


@pytest.fixture
def app():
    """Create FastAPI application for testing."""
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    return app


@pytest.mark.asyncio
async def test_create_tournament(app, db_session: AsyncSession, test_organizer: User):
    """Test tournament creation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
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
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        
        response = await client.post("/api/v1/tournaments/", json=tournament_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == tournament_data["name"]
        assert data["status"] == "pending"
        assert data["created_by"] == test_organizer.id


@pytest.mark.asyncio
async def test_start_tournament(app, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
    """Test starting a tournament."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication and tournament access
        from app.core.dependencies import get_current_user, get_tournament_as_organizer
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        app.dependency_overrides[get_tournament_as_organizer] = lambda: test_tournament
        
        response = await client.post(f"/api/v1/tournaments/{test_tournament.id}/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["current_round"] == 1


@pytest.mark.asyncio
async def test_advance_tournament_round(app, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
    """Test advancing tournament to next round."""
    # Set tournament to active status
    test_tournament.status = TournamentStatus.ACTIVE.value
    test_tournament.current_round = 1
    await db_session.commit()
    
    # Create completed matches for current round
    for i in range(2):
        match = Round(
            id=str(uuid.uuid4()),
            tournament_id=test_tournament.id,
            round_number=1,
            team1_player1_id=test_tournament.players[i*2].id,
            team1_player2_id=test_tournament.players[i*2+1].id,
            team2_player1_id=test_tournament.players[i*2+2].id if i*2+2 < len(test_tournament.players) else test_tournament.players[0].id,
            team2_player2_id=test_tournament.players[i*2+3].id if i*2+3 < len(test_tournament.players) else test_tournament.players[1].id,
            team1_score=17,
            team2_score=15,
            is_completed=True
        )
        db_session.add(match)
    
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication and tournament access
        from app.core.dependencies import get_current_user, get_tournament_as_organizer
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        app.dependency_overrides[get_tournament_as_organizer] = lambda: test_tournament
        
        response = await client.post(f"/api/v1/tournaments/{test_tournament.id}/advance-round")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


@pytest.mark.asyncio
async def test_get_tournament_leaderboard(app, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
    """Test getting tournament leaderboard."""
    # Set tournament to active status
    test_tournament.status = TournamentStatus.ACTIVE.value
    await db_session.commit()
    
    # Create some completed matches
    match = Round(
        id=str(uuid.uuid4()),
        tournament_id=test_tournament.id,
        round_number=1,
        team1_player1_id=test_tournament.players[0].id,
        team1_player2_id=test_tournament.players[1].id,
        team2_player1_id=test_tournament.players[2].id,
        team2_player2_id=test_tournament.players[3].id,
        team1_score=17,
        team2_score=15,
        is_completed=True
    )
    db_session.add(match)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication
        from app.core.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        
        response = await client.get(f"/api/v1/tournaments/{test_tournament.id}/leaderboard")
        
        assert response.status_code == 200
        data = response.json()
        assert "entries" in data
        assert "tournament_id" in data
        assert len(data["entries"]) > 0


@pytest.mark.asyncio
async def test_record_match_result(app, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
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
        team1_player1_id=test_tournament.players[0].id,
        team1_player2_id=test_tournament.players[1].id,
        team2_player1_id=test_tournament.players[2].id,
        team2_player2_id=test_tournament.players[3].id,
        is_completed=False
    )
    db_session.add(match)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication
        from app.core.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        
        result_data = {
            "team1_score": 17,
            "team2_score": 15
        }
        
        response = await client.put(f"/api/v1/tournaments/matches/{match.id}/result", json=result_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["team1_score"] == 17
        assert data["team2_score"] == 15


@pytest.mark.asyncio
async def test_get_current_round_matches(app, db_session: AsyncSession, test_tournament: Tournament, test_organizer: User):
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
        team1_player1_id=test_tournament.players[0].id,
        team1_player2_id=test_tournament.players[1].id,
        team2_player1_id=test_tournament.players[2].id,
        team2_player2_id=test_tournament.players[3].id,
        is_completed=False
    )
    db_session.add(match)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication
        from app.core.dependencies import get_current_user
        app.dependency_overrides[get_current_user] = lambda: test_organizer
        
        response = await client.get(f"/api/v1/tournaments/{test_tournament.id}/matches/current")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "team1_player1" in data[0]
        assert "team2_player1" in data[0]


@pytest.mark.asyncio
async def test_join_tournament(app, db_session: AsyncSession, test_tournament: Tournament, test_user: User):
    """Test joining a tournament."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication and tournament access
        from app.core.dependencies import get_current_user, get_tournament_for_user
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_tournament_for_user] = lambda: test_tournament
        
        response = await client.post(f"/api/v1/tournaments/{test_tournament.id}/join")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True


@pytest.mark.asyncio
async def test_leave_tournament(app, db_session: AsyncSession, test_tournament: Tournament, test_user: User):
    """Test leaving a tournament."""
    # Add user to tournament first
    test_tournament.players.append(test_user)
    await db_session.commit()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Mock authentication and tournament access
        from app.core.dependencies import get_current_user, get_tournament_for_user
        app.dependency_overrides[get_current_user] = lambda: test_user
        app.dependency_overrides[get_tournament_for_user] = lambda: test_tournament
        
        response = await client.post(f"/api/v1/tournaments/{test_tournament.id}/leave")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True