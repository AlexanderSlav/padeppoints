import pytest
from app.services.formats.mexicano_service import MexicanoTournamentService
from app.services.formats.team_americano_service import TeamAmericanoTournamentService
from app.services.formats.team_mexicano_service import TeamMexicanoTournamentService
from app.services.formats.beat_the_box_service import BeatTheBoxTournamentService
from app.models.round import Round
from app.models.tournament import Tournament, TournamentSystem
from app.models.user import User
import uuid


class TestMexicanoTournament:
    """Test suite for Mexicano tournament format."""

    def create_mock_tournament(self, num_players: int):
        """Helper to create mock tournament and players."""
        players = [
            User(id=str(uuid.uuid4()), full_name=f"Player {i}", email=f"player{i}@test.com")
            for i in range(num_players)
        ]
        tournament = Tournament(
            id=str(uuid.uuid4()),
            name="Test Mexicano",
            location="Test Location",
            system=TournamentSystem.MEXICANO,
            points_per_match=32,
            courts=1
        )
        return tournament, players

    def test_player_count_validation(self):
        """Test that Mexicano validates player counts correctly."""
        # Valid counts (divisible by 4, >= 4)
        for count in [4, 8, 12, 16]:
            tournament, players = self.create_mock_tournament(count)
            service = MexicanoTournamentService(tournament, players)
            assert service.validate_player_count(), f"{count} players should be valid"

        # Invalid counts
        for count in [3, 5, 6, 7, 9]:
            tournament, players = self.create_mock_tournament(count)
            service = MexicanoTournamentService(tournament, players)
            assert not service.validate_player_count(), f"{count} players should be invalid"

    def test_first_round_generation(self):
        """Test that first round is generated with random matchups."""
        tournament, players = self.create_mock_tournament(8)
        service = MexicanoTournamentService(tournament, players)

        rounds = service.generate_rounds()
        assert len(rounds) == 1, "Should generate only first round"

        first_round = rounds[0]
        assert len(first_round) == 2, "8 players should create 2 matches"

        # Check all players are included exactly once
        all_players = set()
        for match in first_round:
            all_players.update(match)

        assert len(all_players) == 8, "All 8 players should be in first round"

    def test_ranking_based_matchmaking(self):
        """Test that subsequent rounds use ranking-based matchmaking."""
        tournament, players = self.create_mock_tournament(8)
        service = MexicanoTournamentService(tournament, players)

        # Simulate first round completion with scores
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
            ),
            Round(
                id=str(uuid.uuid4()),
                tournament_id=tournament.id,
                round_number=1,
                team1_player1_id=players[4].id,
                team1_player2_id=players[5].id,
                team2_player1_id=players[6].id,
                team2_player2_id=players[7].id,
                team1_score=18,
                team2_score=14,
                is_completed=True
            )
        ]

        # Generate next round based on standings
        next_round = service.generate_next_round(completed_rounds)

        assert len(next_round) == 2, "Should generate 2 matches for 8 players"

        # Verify ranking-based pairing (1+3 vs 2+4 logic)
        standings = service.get_current_standings(completed_rounds)
        top_4_players = [pid for pid, _ in standings[:4]]

        # Check that top-ranked players are matched together
        match1 = next_round[0]
        assert set(match1).issubset(set(top_4_players)), "Top match should have top-ranked players"


class TestTeamAmericanoTournament:
    """Test suite for Team Americano tournament format."""

    def create_mock_tournament(self, num_players: int):
        """Helper to create mock tournament and players."""
        players = [
            User(id=str(uuid.uuid4()), full_name=f"Player {i}", email=f"player{i}@test.com")
            for i in range(num_players)
        ]
        tournament = Tournament(
            id=str(uuid.uuid4()),
            name="Test Team Americano",
            location="Test Location",
            system=TournamentSystem.TEAM_AMERICANO,
            points_per_match=32,
            courts=1
        )
        return tournament, players

    def test_player_count_validation(self):
        """Test that Team Americano validates even player counts."""
        # Valid counts (even, >= 4)
        for count in [4, 6, 8, 10]:
            tournament, players = self.create_mock_tournament(count)
            service = TeamAmericanoTournamentService(tournament, players)
            assert service.validate_player_count(), f"{count} players should be valid"

        # Invalid counts (odd)
        for count in [3, 5, 7]:
            tournament, players = self.create_mock_tournament(count)
            service = TeamAmericanoTournamentService(tournament, players)
            assert not service.validate_player_count(), f"{count} players should be invalid"

    def test_fixed_team_creation(self):
        """Test that teams are created and remain fixed."""
        tournament, players = self.create_mock_tournament(6)
        service = TeamAmericanoTournamentService(tournament, players)

        teams = service._create_fixed_teams()

        assert len(teams) == 3, "6 players should form 3 teams"
        assert all(len(team) == 2 for team in teams), "Each team should have 2 players"

    def test_round_robin_schedule(self):
        """Test that round-robin schedule is generated correctly."""
        tournament, players = self.create_mock_tournament(6)
        service = TeamAmericanoTournamentService(tournament, players)

        rounds = service.generate_rounds()

        # 3 teams play round-robin: n-1 = 2 rounds needed
        assert len(rounds) >= 2, "At least 2 rounds needed for 3 teams"

        # Each team should play every other team exactly once
        team_matchups = set()
        for round_matches in rounds:
            for match in round_matches:
                team1 = tuple(sorted([match[0], match[1]]))
                team2 = tuple(sorted([match[2], match[3]]))
                matchup = tuple(sorted([team1, team2]))
                team_matchups.add(matchup)

        # With 3 teams, should have 3 unique matchups
        assert len(team_matchups) >= 3, "Should have at least 3 unique team matchups"


class TestTeamMexicanoTournament:
    """Test suite for Team Mexicano tournament format."""

    def create_mock_tournament(self, num_players: int):
        """Helper to create mock tournament and players."""
        players = [
            User(id=str(uuid.uuid4()), full_name=f"Player {i}", email=f"player{i}@test.com")
            for i in range(num_players)
        ]
        tournament = Tournament(
            id=str(uuid.uuid4()),
            name="Test Team Mexicano",
            location="Test Location",
            system=TournamentSystem.TEAM_MEXICANO,
            points_per_match=32,
            courts=1
        )
        return tournament, players

    def test_player_count_validation(self):
        """Test validation for Team Mexicano."""
        # Valid counts (even, >= 4)
        for count in [4, 6, 8]:
            tournament, players = self.create_mock_tournament(count)
            service = TeamMexicanoTournamentService(tournament, players)
            assert service.validate_player_count(), f"{count} players should be valid"

    def test_team_based_ranking(self):
        """Test that teams are ranked and matched based on performance."""
        tournament, players = self.create_mock_tournament(6)
        service = TeamMexicanoTournamentService(tournament, players)

        # Generate first round
        rounds = service.generate_rounds()
        assert len(rounds) == 1, "Should generate first round only"

        # Simulate completion with different team scores
        completed_rounds = [
            Round(
                id=str(uuid.uuid4()),
                tournament_id=tournament.id,
                round_number=1,
                team1_player1_id=players[0].id,
                team1_player2_id=players[1].id,
                team2_player1_id=players[2].id,
                team2_player2_id=players[3].id,
                team1_score=25,
                team2_score=7,
                is_completed=True
            )
        ]

        # Generate next round
        next_round = service.generate_next_round(completed_rounds)
        assert len(next_round) >= 1, "Should generate matches for next round"


class TestBeatTheBoxTournament:
    """Test suite for Beat the Box tournament format."""

    def create_mock_tournament(self, num_players: int, box_size: int = 4):
        """Helper to create mock tournament and players."""
        players = [
            User(id=str(uuid.uuid4()), full_name=f"Player {i}", email=f"player{i}@test.com")
            for i in range(num_players)
        ]
        tournament = Tournament(
            id=str(uuid.uuid4()),
            name="Test Beat the Box",
            location="Test Location",
            system=TournamentSystem.BEAT_THE_BOX,
            points_per_match=32,
            courts=1
        )
        return tournament, players, box_size

    def test_player_count_validation(self):
        """Test that Beat the Box validates player counts correctly."""
        # Valid: 8 players, box size 4 (2 boxes)
        tournament, players, box_size = self.create_mock_tournament(8, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)
        assert service.validate_player_count(), "8 players with box size 4 should be valid"

        # Valid: 12 players, box size 4 (3 boxes)
        tournament, players, box_size = self.create_mock_tournament(12, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)
        assert service.validate_player_count(), "12 players with box size 4 should be valid"

        # Invalid: 10 players, box size 4 (not divisible)
        tournament, players, box_size = self.create_mock_tournament(10, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)
        assert not service.validate_player_count(), "10 players with box size 4 should be invalid"

        # Invalid: 6 players (less than minimum 8)
        tournament, players, box_size = self.create_mock_tournament(6, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)
        assert not service.validate_player_count(), "6 players should be invalid (minimum 8)"

    def test_box_creation(self):
        """Test that players are correctly divided into boxes."""
        tournament, players, box_size = self.create_mock_tournament(12, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)

        boxes = service._create_initial_boxes()

        assert len(boxes) == 3, "12 players with box size 4 should create 3 boxes"
        assert all(len(box) == 4 for box in boxes), "Each box should have 4 players"

        # Check all players are assigned
        all_box_players = set()
        for box in boxes:
            all_box_players.update(box)
        assert len(all_box_players) == 12, "All 12 players should be in boxes"

    def test_performance_based_redistribution(self):
        """Test that players are redistributed based on performance."""
        tournament, players, box_size = self.create_mock_tournament(8, 4)
        service = BeatTheBoxTournamentService(tournament, players, box_size=box_size)

        # Simulate completed round with clear performance differences
        completed_rounds = [
            Round(
                id=str(uuid.uuid4()),
                tournament_id=tournament.id,
                round_number=1,
                team1_player1_id=players[0].id,
                team1_player2_id=players[1].id,
                team2_player1_id=players[2].id,
                team2_player2_id=players[3].id,
                team1_score=30,
                team2_score=2,
                is_completed=True
            ),
            Round(
                id=str(uuid.uuid4()),
                tournament_id=tournament.id,
                round_number=1,
                team1_player1_id=players[4].id,
                team1_player2_id=players[5].id,
                team2_player1_id=players[6].id,
                team2_player2_id=players[7].id,
                team1_score=20,
                team2_score=12,
                is_completed=True
            )
        ]

        # Generate next round (should redistribute based on performance)
        next_round = service.generate_next_round(completed_rounds)
        assert len(next_round) >= 1, "Should generate matches for next round"

        # Verify standings are calculated
        standings = service.get_current_standings(completed_rounds)
        assert len(standings) == 8, "Should have standings for all 8 players"

        # Top scorer should be players[0] or players[1] with 30 points
        top_player_id = standings[0][0]
        assert top_player_id in [players[0].id, players[1].id], "Top player should be from winning team"
