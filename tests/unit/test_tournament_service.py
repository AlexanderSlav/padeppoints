import pytest
from unittest.mock import Mock, AsyncMock
from app.services.tournament_service import TournamentService
from app.services.americano_service import AmericanoTournamentService
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.user import User
from app.models.round import Round
import uuid


class TestTournamentService:
    """Test cases for TournamentService."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return AsyncMock()

    @pytest.fixture
    def tournament_service(self, mock_db):
        """Create TournamentService instance."""
        return TournamentService(mock_db)

    @pytest.fixture
    def mock_tournament(self):
        """Create mock tournament."""
        tournament = Mock(spec=Tournament)
        tournament.id = str(uuid.uuid4())
        tournament.name = "Test Tournament"
        tournament.system = TournamentSystem.AMERICANO
        tournament.status = TournamentStatus.PENDING.value
        tournament.current_round = 1
        tournament.points_per_match = 32
        tournament.courts = 2
        tournament.max_players = 8
        return tournament

    @pytest.fixture
    def mock_players(self):
        """Create mock players."""
        players = []
        for i in range(8):
            player = Mock(spec=User)
            player.id = str(uuid.uuid4())
            player.full_name = f"Player {i+1}"
            player.email = f"player{i+1}@example.com"
            players.append(player)
        return players

    def test_get_format_service_americano(self, tournament_service, mock_tournament, mock_players):
        """Test getting Americano format service."""
        mock_tournament.system = TournamentSystem.AMERICANO
        mock_tournament.players = mock_players
        service = tournament_service.get_format_service(mock_tournament)
        assert isinstance(service, AmericanoTournamentService)

    def test_get_format_service_unsupported(self, tournament_service):
        """Test getting unsupported format service raises error."""
        mock_tournament = Mock()
        mock_tournament.system = "UNSUPPORTED"
        
        with pytest.raises(ValueError, match="Unsupported tournament system"):
            tournament_service.get_format_service(mock_tournament)

    @pytest.mark.asyncio
    async def test_start_tournament_success(self, tournament_service, mock_tournament, mock_players):
        """Test successful tournament start."""
        # Setup mock
        mock_tournament.players = mock_players
        tournament_service.db.execute = AsyncMock()
        tournament_service.db.commit = AsyncMock()
        tournament_service.db.refresh = AsyncMock()
        
        # Mock database query result
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_tournament
        tournament_service.db.execute.return_value = mock_result
        
        # Mock format service
        mock_format_service = Mock()
        mock_format_service.validate_player_count.return_value = True
        mock_format_service.generate_rounds.return_value = [
            [(mock_players[0].id, mock_players[1].id, mock_players[2].id, mock_players[3].id)],
            [(mock_players[4].id, mock_players[5].id, mock_players[6].id, mock_players[7].id)]
        ]
        tournament_service.get_format_service = Mock(return_value=mock_format_service)
        
        result = await tournament_service.start_tournament(mock_tournament.id)
        
        assert result.status == TournamentStatus.ACTIVE.value
        assert result.current_round == 1
        tournament_service.db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_tournament_not_found(self, tournament_service):
        """Test starting non-existent tournament."""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        tournament_service.db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="Tournament .* not found"):
            await tournament_service.start_tournament("nonexistent-id")

    @pytest.mark.asyncio
    async def test_start_tournament_wrong_status(self, tournament_service, mock_tournament):
        """Test starting tournament with wrong status."""
        mock_tournament.status = TournamentStatus.ACTIVE.value
        
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = mock_tournament
        tournament_service.db.execute = AsyncMock(return_value=mock_result)
        
        with pytest.raises(ValueError, match="Tournament .* cannot be started"):
            await tournament_service.start_tournament(mock_tournament.id)

    @pytest.mark.asyncio
    async def test_record_match_result_success(self, tournament_service, mock_tournament):
        """Test recording match result successfully."""
        # Setup mock match
        mock_match = Mock(spec=Round)
        mock_match.id = str(uuid.uuid4())
        mock_match.tournament_id = mock_tournament.id
        mock_match.is_completed = False
        mock_match.team1_score = None
        mock_match.team2_score = None
        
        # Setup mock database responses
        match_result = Mock()
        match_result.scalar_one_or_none.return_value = mock_match
        
        tournament_result = Mock()
        tournament_result.scalar_one_or_none.return_value = mock_tournament
        
        tournament_service.db.execute = AsyncMock(side_effect=[match_result, tournament_result])
        tournament_service.db.commit = AsyncMock()
        tournament_service.db.refresh = AsyncMock()
        tournament_service._check_and_advance_round = AsyncMock()
        
        result = await tournament_service.record_match_result(mock_match.id, 17, 15)
        
        assert result.team1_score == 17
        assert result.team2_score == 15
        assert result.is_completed == True
        tournament_service.db.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_match_result_invalid_scores(self, tournament_service, mock_tournament):
        """Test recording match result with invalid scores."""
        mock_match = Mock(spec=Round)
        mock_match.id = str(uuid.uuid4())
        mock_match.tournament_id = mock_tournament.id
        mock_match.is_completed = False
        
        match_result = Mock()
        match_result.scalar_one_or_none.return_value = mock_match
        
        tournament_result = Mock()
        tournament_result.scalar_one_or_none.return_value = mock_tournament
        
        # Test negative scores - need fresh mock for each test
        tournament_service.db.execute = AsyncMock(side_effect=[match_result, tournament_result])
        with pytest.raises(ValueError, match="Scores must be non-negative"):
            await tournament_service.record_match_result(mock_match.id, -1, 15)
        
        # Test invalid Americano scores (don't sum to points_per_match) - reset mock side_effect
        tournament_service.db.execute = AsyncMock(side_effect=[match_result, tournament_result])
        with pytest.raises(ValueError, match="Invalid score for Americano format"):
            await tournament_service.record_match_result(mock_match.id, 10, 15)

    @pytest.mark.asyncio
    async def test_get_player_scores(self, tournament_service, mock_tournament, mock_players):
        """Test getting player scores."""
        # Setup mock completed rounds
        mock_rounds = []
        for i in range(2):
            round_match = Mock(spec=Round)
            round_match.is_completed = True
            round_match.team1_player1_id = mock_players[0].id
            round_match.team1_player2_id = mock_players[1].id
            round_match.team2_player1_id = mock_players[2].id
            round_match.team2_player2_id = mock_players[3].id
            round_match.team1_score = 17
            round_match.team2_score = 15
            mock_rounds.append(round_match)
        
        # Setup database mocks
        tournament_result = Mock()
        tournament_result.scalar_one_or_none.return_value = mock_tournament
        
        rounds_result = Mock()
        rounds_result.scalars.return_value.all.return_value = mock_rounds
        
        tournament_service.db.execute = AsyncMock(side_effect=[tournament_result, rounds_result])
        
        # Mock format service
        mock_format_service = Mock()
        expected_scores = {player.id: 34 if i < 2 else 30 for i, player in enumerate(mock_players[:4])}
        mock_format_service.calculate_player_scores.return_value = expected_scores
        tournament_service.get_format_service = Mock(return_value=mock_format_service)
        
        scores = await tournament_service.get_player_scores(mock_tournament.id)
        
        assert scores == expected_scores

    @pytest.mark.asyncio
    async def test_get_tournament_leaderboard(self, tournament_service, mock_tournament, mock_players):
        """Test getting tournament leaderboard with comprehensive statistics."""
        # Setup mock tournament and rounds query results
        tournament_result = Mock()
        tournament_result.scalar_one_or_none.return_value = mock_tournament
        
        # Mock completed rounds
        rounds_result = Mock()
        rounds_result.scalars.return_value.all.return_value = []
        
        # Mock users query
        users_result = Mock()
        users_result.scalars.return_value.all.return_value = mock_players[:3]
        
        tournament_service.db.execute = AsyncMock(side_effect=[tournament_result, rounds_result, users_result])
        
        # Mock format service with comprehensive statistics
        mock_format_service = Mock()
        mock_player_stats = {
            mock_players[0].id: {
                'total_points': 100,
                'points_difference': 15,
                'wins': 3,
                'losses': 1,
                'ties': 0,
                'matches_played': 4
            },
            mock_players[1].id: {
                'total_points': 90,
                'points_difference': 5,
                'wins': 2,
                'losses': 1,
                'ties': 1,
                'matches_played': 4
            },
            mock_players[2].id: {
                'total_points': 80,
                'points_difference': -10,
                'wins': 1,
                'losses': 2,
                'ties': 1,
                'matches_played': 4
            }
        }
        mock_format_service.calculate_player_statistics.return_value = mock_player_stats
        tournament_service.get_format_service = Mock(return_value=mock_format_service)
        
        leaderboard = await tournament_service.get_tournament_leaderboard(mock_tournament.id)
        
        assert len(leaderboard) == 3
        # Check first place (highest total points)
        assert leaderboard[0]["player_name"] == "Player 1"
        assert leaderboard[0]["score"] == 100
        assert leaderboard[0]["points_difference"] == 15
        assert leaderboard[0]["wins"] == 3
        assert leaderboard[0]["losses"] == 1
        assert leaderboard[0]["ties"] == 0
        assert leaderboard[0]["matches_played"] == 4
        assert leaderboard[0]["rank"] == 1
        
        # Check second place
        assert leaderboard[1]["player_name"] == "Player 2"
        assert leaderboard[1]["score"] == 90
        assert leaderboard[1]["rank"] == 2
        
        # Check third place
        assert leaderboard[2]["player_name"] == "Player 3"
        assert leaderboard[2]["score"] == 80
        assert leaderboard[2]["points_difference"] == -10
        assert leaderboard[2]["rank"] == 3