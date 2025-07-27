"""Simple integration test to verify basic functionality."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.tournament import Tournament
from app.models.round import Round
from app.services.tournament_service import TournamentService
from app.services.americano_service import AmericanoTournamentService
import uuid


@pytest.mark.asyncio
async def test_basic_flow():
    """Test basic flow without database."""
    # Create mock tournament
    tournament = Tournament(
        id=str(uuid.uuid4()),
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        max_players=8,
        current_round=1,
        status="active"
    )
    
    # Create mock players
    players = []
    for i in range(8):
        player = User(
            id=str(uuid.uuid4()),
            full_name=f"Player {i+1}",
            email=f"player{i+1}@example.com"
        )
        players.append(player)
    
    tournament.players = players
    
    # Test Americano service
    service = AmericanoTournamentService(tournament)
    assert service.validate_player_count() == True
    
    # Test round generation
    rounds = service.generate_rounds()
    assert len(rounds) > 0
    
    # Test statistics calculation
    completed_rounds = []
    round1 = Round(
        id=str(uuid.uuid4()),
        tournament_id=tournament.id,
        round_number=1,
        team1_player1_id=players[0].id,
        team1_player2_id=players[1].id,
        team2_player1_id=players[2].id,
        team2_player2_id=players[3].id,
        team1_score=17,
        team2_score=15,
        is_completed=True
    )
    completed_rounds.append(round1)
    
    stats = service.calculate_player_statistics(completed_rounds)
    
    # Verify statistics
    assert players[0].id in stats
    assert stats[players[0].id]['total_points'] == 17
    assert stats[players[0].id]['wins'] == 1
    assert stats[players[0].id]['losses'] == 0
    assert stats[players[0].id]['ties'] == 0
    assert stats[players[0].id]['points_difference'] == 2


@pytest.mark.asyncio 
async def test_leaderboard_format():
    """Test leaderboard data format."""
    # Create tournament with completed matches
    tournament = Tournament(
        id=str(uuid.uuid4()),
        system="AMERICANO",
        points_per_match=32,
        courts=2,
        max_players=4,
        current_round=1,
        status="active"
    )
    
    players = []
    for i in range(4):
        player = User(
            id=str(uuid.uuid4()),
            full_name=f"Player {i+1}",
            email=f"player{i+1}@example.com"
        )
        players.append(player)
    
    tournament.players = players
    service = AmericanoTournamentService(tournament)
    
    # Create match data
    completed_rounds = [
        Round(
            id=str(uuid.uuid4()),
            tournament_id=tournament.id,
            round_number=1,
            team1_player1_id=players[0].id,
            team1_player2_id=players[1].id,
            team2_player1_id=players[2].id,
            team2_player2_id=players[3].id,
            team1_score=20,
            team2_score=12,
            is_completed=True
        )
    ]
    
    stats = service.calculate_player_statistics(completed_rounds)
    
    # Check all required fields exist
    for player_id, player_stats in stats.items():
        assert 'total_points' in player_stats
        assert 'points_difference' in player_stats
        assert 'wins' in player_stats
        assert 'losses' in player_stats
        assert 'ties' in player_stats
        assert 'matches_played' in player_stats
    
    # Verify calculations
    assert stats[players[0].id]['points_difference'] == 8  # 20-12
    assert stats[players[2].id]['points_difference'] == -8  # 12-20