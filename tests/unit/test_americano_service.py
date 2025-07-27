import pytest
from unittest.mock import Mock
from app.services.americano_service import AmericanoTournamentService
from app.models.tournament import Tournament, TournamentSystem
from app.models.user import User
from app.models.round import Round
import uuid


class TestAmericanoTournamentService:
    """Test cases for AmericanoTournamentService."""

    @pytest.fixture
    def mock_tournament(self):
        """Create mock tournament."""
        tournament = Mock(spec=Tournament)
        tournament.id = str(uuid.uuid4())
        tournament.system = TournamentSystem.AMERICANO
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

    @pytest.fixture
    def americano_service(self, mock_tournament, mock_players):
        """Create AmericanoTournamentService instance."""
        mock_tournament.players = mock_players
        return AmericanoTournamentService(mock_tournament)

    def test_validate_player_count_valid(self, americano_service):
        """Test player count validation with valid counts."""
        assert americano_service.validate_player_count() == True

    def test_validate_player_count_invalid(self, mock_tournament):
        """Test player count validation with invalid counts."""
        # Test with 3 players (not divisible by 4)
        players = [Mock(spec=User) for _ in range(3)]
        mock_tournament.players = players
        service = AmericanoTournamentService(mock_tournament)
        assert service.validate_player_count() == False

    def test_generate_rounds_success(self, americano_service):
        """Test successful round generation."""
        rounds = americano_service.generate_rounds()
        
        assert len(rounds) > 0
        # Each round should have matches
        for round_matches in rounds:
            assert len(round_matches) > 0
            # Each match should have 4 players
            for match in round_matches:
                assert len(match) == 4

    def test_generate_rounds_invalid_player_count(self, mock_tournament):
        """Test round generation with invalid player count."""
        players = [Mock(spec=User) for _ in range(3)]
        mock_tournament.players = players
        service = AmericanoTournamentService(mock_tournament)
        
        with pytest.raises(ValueError, match="Invalid player count"):
            service.generate_rounds()

    def test_calculate_optimal_rounds(self, americano_service):
        """Test optimal rounds calculation."""
        rounds = americano_service._calculate_optimal_rounds()
        # For 8 players, should be 7 rounds (n-1)
        assert rounds == 7

    def test_estimate_duration(self):
        """Test tournament duration estimation."""
        minutes, rounds = AmericanoTournamentService.estimate_duration(
            num_players=8, courts=2, points_per_game=21
        )
        
        assert isinstance(minutes, int)
        assert isinstance(rounds, int)
        assert minutes > 0
        assert rounds > 0

    def test_estimate_duration_invalid_params(self):
        """Test duration estimation with invalid parameters."""
        with pytest.raises(ValueError):
            AmericanoTournamentService.estimate_duration(
                num_players=3, courts=1  # Invalid player count
            )

    def test_calculate_player_scores(self, americano_service, mock_players):
        """Test player score calculation."""
        # Create mock completed rounds
        completed_rounds = []
        
        # Round 1: Players 0,1 vs Players 2,3 -> 17-15
        round1 = Mock(spec=Round)
        round1.is_completed = True
        round1.team1_player1_id = mock_players[0].id
        round1.team1_player2_id = mock_players[1].id
        round1.team2_player1_id = mock_players[2].id
        round1.team2_player2_id = mock_players[3].id
        round1.team1_score = 17
        round1.team2_score = 15
        completed_rounds.append(round1)
        
        # Round 2: Players 0,2 vs Players 1,3 -> 20-12
        round2 = Mock(spec=Round)
        round2.is_completed = True
        round2.team1_player1_id = mock_players[0].id
        round2.team1_player2_id = mock_players[2].id
        round2.team2_player1_id = mock_players[1].id
        round2.team2_player2_id = mock_players[3].id
        round2.team1_score = 20
        round2.team2_score = 12
        completed_rounds.append(round2)
        
        scores = americano_service.calculate_player_scores(completed_rounds)
        
        # Player 0: 17 + 20 = 37
        # Player 1: 17 + 12 = 29
        # Player 2: 15 + 20 = 35
        # Player 3: 15 + 12 = 27
        assert scores[mock_players[0].id] == 37
        assert scores[mock_players[1].id] == 29
        assert scores[mock_players[2].id] == 35
        assert scores[mock_players[3].id] == 27

    def test_is_tournament_complete(self, americano_service):
        """Test tournament completion check."""
        # For 8 players, tournament should complete after 7 rounds
        assert americano_service.is_tournament_complete(8) == True
        assert americano_service.is_tournament_complete(6) == False

    def test_get_tournament_winner(self, americano_service):
        """Test getting tournament winner."""
        player_scores = {
            "player1": 100,
            "player2": 90,
            "player3": 110,  # Winner
            "player4": 85
        }
        
        winner = americano_service.get_tournament_winner(player_scores)
        assert winner == "player3"

    def test_get_tournament_winner_empty_scores(self, americano_service):
        """Test getting winner with empty scores."""
        winner = americano_service.get_tournament_winner({})
        assert winner is None

    def test_get_player_leaderboard(self, americano_service):
        """Test getting player leaderboard."""
        player_scores = {
            "player1": 100,
            "player2": 90,
            "player3": 110,
            "player4": 85
        }
        
        leaderboard = americano_service.get_player_leaderboard(player_scores)
        
        # Should be sorted by score (highest first)
        assert len(leaderboard) == 4
        assert leaderboard[0] == ("player3", 110)
        assert leaderboard[1] == ("player1", 100)
        assert leaderboard[2] == ("player2", 90)
        assert leaderboard[3] == ("player4", 85)

    def test_calculate_total_rounds(self):
        """Test static method for calculating total rounds."""
        assert AmericanoTournamentService.calculate_total_rounds(8) == 7
        assert AmericanoTournamentService.calculate_total_rounds(4) == 3

    def test_calculate_player_statistics(self, americano_service, mock_players):
        """Test comprehensive player statistics calculation."""
        # Create mock completed rounds
        completed_rounds = []
        
        # Round 1: Players 0,1 vs Players 2,3 -> 17-15 (Team 1 wins)
        round1 = Mock(spec=Round)
        round1.is_completed = True
        round1.team1_player1_id = mock_players[0].id
        round1.team1_player2_id = mock_players[1].id
        round1.team2_player1_id = mock_players[2].id
        round1.team2_player2_id = mock_players[3].id
        round1.team1_score = 17
        round1.team2_score = 15
        completed_rounds.append(round1)
        
        # Round 2: Players 0,2 vs Players 1,3 -> 16-16 (Tie)
        round2 = Mock(spec=Round)
        round2.is_completed = True
        round2.team1_player1_id = mock_players[0].id
        round2.team1_player2_id = mock_players[2].id
        round2.team2_player1_id = mock_players[1].id
        round2.team2_player2_id = mock_players[3].id
        round2.team1_score = 16
        round2.team2_score = 16
        completed_rounds.append(round2)
        
        # Round 3: Players 0,3 vs Players 1,2 -> 12-20 (Team 2 wins)
        round3 = Mock(spec=Round)
        round3.is_completed = True
        round3.team1_player1_id = mock_players[0].id
        round3.team1_player2_id = mock_players[3].id
        round3.team2_player1_id = mock_players[1].id
        round3.team2_player2_id = mock_players[2].id
        round3.team1_score = 12
        round3.team2_score = 20
        completed_rounds.append(round3)
        
        stats = americano_service.calculate_player_statistics(completed_rounds)
        
        # Player 0: 17 + 16 + 12 = 45 points, W-L-T: 1-1-1, Diff: (17-15) + (16-16) + (12-20) = +2+0-8 = -6
        assert stats[mock_players[0].id]['total_points'] == 45
        assert stats[mock_players[0].id]['points_difference'] == -6
        assert stats[mock_players[0].id]['wins'] == 1
        assert stats[mock_players[0].id]['losses'] == 1
        assert stats[mock_players[0].id]['ties'] == 1
        assert stats[mock_players[0].id]['matches_played'] == 3
        
        # Player 1: 17 + 16 + 20 = 53 points, W-L-T: 2-1-0, Diff: (17-15) + (16-16) + (20-12) = +2+0+8 = +10
        assert stats[mock_players[1].id]['total_points'] == 53
        assert stats[mock_players[1].id]['points_difference'] == 10
        assert stats[mock_players[1].id]['wins'] == 2
        assert stats[mock_players[1].id]['losses'] == 0
        assert stats[mock_players[1].id]['ties'] == 1
        assert stats[mock_players[1].id]['matches_played'] == 3