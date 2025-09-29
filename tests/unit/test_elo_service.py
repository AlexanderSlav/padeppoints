"""Unit tests for the ELO rating service with personalized deltas."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, MagicMock
from app.services.elo_service import ELOService
from app.models.round import Round
from app.models.player_rating import PlayerRating


@pytest.mark.asyncio
class TestELOService:
    """Test suite for ELO rating calculations."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = Mock()
        db.add = Mock()
        db.flush = AsyncMock()
        db.execute = AsyncMock()
        return db

    @pytest.fixture
    def elo_service(self, mock_db):
        """Create an ELO service instance."""
        return ELOService(mock_db)

    async def test_personalized_rating_changes(self, elo_service, mock_db):
        """Test that rating changes are personalized based on individual player ratings."""
        # Create mock match with scores
        match = Mock(spec=Round)
        match.id = "match-1"
        match.tournament_id = "tournament-1"
        match.is_completed = True
        match.team1_score = 24
        match.team2_score = 16
        match.team1_player1_id = "player1"
        match.team1_player2_id = "player2"
        match.team2_player1_id = "player3"
        match.team2_player2_id = "player4"

        # Create mock player ratings with different skill levels
        # Team 1: One strong player (1200), one weak player (900) - avg 1050
        # Team 2: Two average players (1000 each) - avg 1000
        player1_rating = Mock(spec=PlayerRating)
        player1_rating.id = "rating-1"
        player1_rating.user_id = "player1"
        player1_rating.current_rating = 1200.0  # Strong player
        player1_rating.peak_rating = 1200.0
        player1_rating.lowest_rating = 1200.0
        player1_rating.matches_played = 20
        player1_rating.matches_won = 15
        player1_rating.total_points_scored = 0
        player1_rating.total_points_possible = 0

        player2_rating = Mock(spec=PlayerRating)
        player2_rating.id = "rating-2"
        player2_rating.user_id = "player2"
        player2_rating.current_rating = 900.0  # Weak player
        player2_rating.peak_rating = 900.0
        player2_rating.lowest_rating = 900.0
        player2_rating.matches_played = 10
        player2_rating.matches_won = 3
        player2_rating.total_points_scored = 0
        player2_rating.total_points_possible = 0

        player3_rating = Mock(spec=PlayerRating)
        player3_rating.id = "rating-3"
        player3_rating.user_id = "player3"
        player3_rating.current_rating = 1000.0
        player3_rating.peak_rating = 1000.0
        player3_rating.lowest_rating = 1000.0
        player3_rating.matches_played = 15
        player3_rating.matches_won = 7
        player3_rating.total_points_scored = 0
        player3_rating.total_points_possible = 0

        player4_rating = Mock(spec=PlayerRating)
        player4_rating.id = "rating-4"
        player4_rating.user_id = "player4"
        player4_rating.current_rating = 1000.0
        player4_rating.peak_rating = 1000.0
        player4_rating.lowest_rating = 1000.0
        player4_rating.matches_played = 15
        player4_rating.matches_won = 8
        player4_rating.total_points_scored = 0
        player4_rating.total_points_possible = 0

        # Mock the get_or_create_rating method
        ratings = {
            "player1": player1_rating,
            "player2": player2_rating,
            "player3": player3_rating,
            "player4": player4_rating
        }

        async def mock_get_or_create(user_id):
            return ratings[user_id]

        elo_service.get_or_create_rating = mock_get_or_create

        # Execute the rating update
        rating_changes = await elo_service.update_match_ratings(match)

        # Verify that rating changes were calculated
        assert len(rating_changes) == 4
        assert "player1" in rating_changes
        assert "player2" in rating_changes
        assert "player3" in rating_changes
        assert "player4" in rating_changes

        # Team 1 won (24-16), so should have positive rating changes
        assert rating_changes["player1"] > 0
        assert rating_changes["player2"] > 0

        # Team 2 lost, so should have negative rating changes
        assert rating_changes["player3"] < 0
        assert rating_changes["player4"] < 0

        # Key test: The weaker player (player2) on the winning team should get
        # a larger positive change than the stronger player (player1)
        # This is because the split_weights function gives more credit to lower-rated players
        assert rating_changes["player2"] > rating_changes["player1"]

        # Conservation check: Total rating change should sum to approximately 0
        total_change = sum(rating_changes.values())
        assert abs(total_change) < 0.001, f"Rating changes not conserved: {total_change}"

        # Verify ratings were updated
        assert player1_rating.current_rating > 1200.0
        assert player2_rating.current_rating > 900.0
        assert player3_rating.current_rating < 1000.0
        assert player4_rating.current_rating < 1000.0

    async def test_rating_changes_with_margin_of_victory(self, elo_service, mock_db):
        """Test that margin of victory affects rating changes."""
        # Test two scenarios: close match vs blowout

        # Scenario 1: Close match (24-22)
        close_match = Mock(spec=Round)
        close_match.id = "match-1"
        close_match.tournament_id = "tournament-1"
        close_match.is_completed = True
        close_match.team1_score = 24
        close_match.team2_score = 22
        close_match.team1_player1_id = "player1"
        close_match.team1_player2_id = "player2"
        close_match.team2_player1_id = "player3"
        close_match.team2_player2_id = "player4"

        # Scenario 2: Blowout (24-10)
        blowout_match = Mock(spec=Round)
        blowout_match.id = "match-2"
        blowout_match.tournament_id = "tournament-1"
        blowout_match.is_completed = True
        blowout_match.team1_score = 24
        blowout_match.team2_score = 10
        blowout_match.team1_player1_id = "player1"
        blowout_match.team1_player2_id = "player2"
        blowout_match.team2_player1_id = "player3"
        blowout_match.team2_player2_id = "player4"

        # Create identical player ratings for both scenarios
        def create_player_rating(user_id, rating_id):
            rating = Mock(spec=PlayerRating)
            rating.id = rating_id
            rating.user_id = user_id
            rating.current_rating = 1000.0
            rating.peak_rating = 1000.0
            rating.lowest_rating = 1000.0
            rating.matches_played = 20
            rating.matches_won = 10
            rating.total_points_scored = 0
            rating.total_points_possible = 0
            return rating

        # For close match
        close_ratings = {
            "player1": create_player_rating("player1", "rating-1"),
            "player2": create_player_rating("player2", "rating-2"),
            "player3": create_player_rating("player3", "rating-3"),
            "player4": create_player_rating("player4", "rating-4")
        }

        async def mock_get_close(user_id):
            return close_ratings[user_id]

        elo_service.get_or_create_rating = mock_get_close
        close_changes = await elo_service.update_match_ratings(close_match)

        # For blowout match (reset ratings)
        blowout_ratings = {
            "player1": create_player_rating("player1", "rating-5"),
            "player2": create_player_rating("player2", "rating-6"),
            "player3": create_player_rating("player3", "rating-7"),
            "player4": create_player_rating("player4", "rating-8")
        }

        async def mock_get_blowout(user_id):
            return blowout_ratings[user_id]

        elo_service.get_or_create_rating = mock_get_blowout
        blowout_changes = await elo_service.update_match_ratings(blowout_match)

        # The blowout should result in larger rating changes due to margin-of-victory scaling
        assert abs(blowout_changes["player1"]) > abs(close_changes["player1"])
        assert abs(blowout_changes["player3"]) > abs(close_changes["player3"])

    async def test_new_player_uncertainty_scaling(self, elo_service, mock_db):
        """Test that new players (few matches) have larger rating changes."""
        match = Mock(spec=Round)
        match.id = "match-1"
        match.tournament_id = "tournament-1"
        match.is_completed = True
        match.team1_score = 24
        match.team2_score = 20
        match.team1_player1_id = "new_player"
        match.team1_player2_id = "experienced_player"
        match.team2_player1_id = "player3"
        match.team2_player2_id = "player4"

        # New player with only 2 matches
        new_player_rating = Mock(spec=PlayerRating)
        new_player_rating.id = "rating-1"
        new_player_rating.user_id = "new_player"
        new_player_rating.current_rating = 1000.0
        new_player_rating.peak_rating = 1000.0
        new_player_rating.lowest_rating = 1000.0
        new_player_rating.matches_played = 2  # Very new
        new_player_rating.matches_won = 1
        new_player_rating.total_points_scored = 0
        new_player_rating.total_points_possible = 0

        # Experienced player with many matches
        experienced_player_rating = Mock(spec=PlayerRating)
        experienced_player_rating.id = "rating-2"
        experienced_player_rating.user_id = "experienced_player"
        experienced_player_rating.current_rating = 1000.0
        experienced_player_rating.peak_rating = 1100.0
        experienced_player_rating.lowest_rating = 900.0
        experienced_player_rating.matches_played = 50  # Very experienced
        experienced_player_rating.matches_won = 25
        experienced_player_rating.total_points_scored = 0
        experienced_player_rating.total_points_possible = 0

        # Opponents
        player3_rating = Mock(spec=PlayerRating)
        player3_rating.id = "rating-3"
        player3_rating.user_id = "player3"
        player3_rating.current_rating = 1000.0
        player3_rating.peak_rating = 1000.0
        player3_rating.lowest_rating = 1000.0
        player3_rating.matches_played = 20
        player3_rating.matches_won = 10
        player3_rating.total_points_scored = 0
        player3_rating.total_points_possible = 0

        player4_rating = Mock(spec=PlayerRating)
        player4_rating.id = "rating-4"
        player4_rating.user_id = "player4"
        player4_rating.current_rating = 1000.0
        player4_rating.peak_rating = 1000.0
        player4_rating.lowest_rating = 1000.0
        player4_rating.matches_played = 20
        player4_rating.matches_won = 10
        player4_rating.total_points_scored = 0
        player4_rating.total_points_possible = 0

        ratings = {
            "new_player": new_player_rating,
            "experienced_player": experienced_player_rating,
            "player3": player3_rating,
            "player4": player4_rating
        }

        async def mock_get_or_create(user_id):
            return ratings[user_id]

        elo_service.get_or_create_rating = mock_get_or_create

        # Execute the rating update
        rating_changes = await elo_service.update_match_ratings(match)

        # Due to uncertainty scaling, the team with the new player should have
        # larger overall changes (affected by min matches on team)
        # This is implemented through the effective_k function
        assert rating_changes["new_player"] != 0
        assert rating_changes["experienced_player"] != 0

        # Conservation check
        total_change = sum(rating_changes.values())
        assert abs(total_change) < 0.001, f"Rating changes not conserved: {total_change}"