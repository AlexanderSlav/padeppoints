import pytest
from app.services.americano_service import AmericanoTournamentService
from app.models.round import Round
from collections import defaultdict
from math import comb
import time


class TestAmericanoTournament:
    """
    Comprehensive test suite for Americano tournament algorithm.
    Tests the refactored 1-factorization based implementation.
    """

    def test_basic_validation(self, americano_tournament_factory):
        """Test basic player count validation."""
        # Valid counts
        for count in [4, 8, 12, 16, 20, 24]:
            tournament, _ = americano_tournament_factory(count)
            service = AmericanoTournamentService(tournament)
            assert service.validate_player_count(), f"{count} players should be valid"
        
        # Invalid counts
        for count in [3, 5, 6, 7, 9, 10, 11]:
            tournament, _ = americano_tournament_factory(count)
            service = AmericanoTournamentService(tournament)
            assert not service.validate_player_count(), f"{count} players should be invalid"

    def test_round_generation_fails_for_invalid_counts(self, americano_tournament_factory):
        """Test that round generation raises ValueError for invalid player counts."""
        for count in [3, 5, 7]:
            tournament, _ = americano_tournament_factory(count)
            service = AmericanoTournamentService(tournament)
            
            with pytest.raises(ValueError, match="Invalid player count"):
                service.generate_rounds()

    def test_no_repeated_partnerships_guarantee(self, americano_tournament_factory):
        """
        Core test: Verify no partnerships are ever repeated.
        This is the fundamental Americano tournament requirement.
        """
        for num_players in [4, 8, 12, 16, 20]:
            tournament, players = americano_tournament_factory(num_players)
            service = AmericanoTournamentService(tournament)
            
            rounds = service.generate_rounds()
            
            # Track all partnerships
            partnerships_seen = set()
            repeated_partnerships = []
            
            for round_idx, round_matches in enumerate(rounds):
                for match_idx, match in enumerate(round_matches):
                    # Extract partnerships from match
                    team1 = tuple(sorted([match[0], match[1]]))
                    team2 = tuple(sorted([match[2], match[3]]))
                    
                    # Check for repeats
                    if team1 in partnerships_seen:
                        repeated_partnerships.append(f"Partnership {team1} repeated in R{round_idx+1}M{match_idx+1}")
                    if team2 in partnerships_seen:
                        repeated_partnerships.append(f"Partnership {team2} repeated in R{round_idx+1}M{match_idx+1}")
                    
                    partnerships_seen.add(team1)
                    partnerships_seen.add(team2)
            
            assert len(repeated_partnerships) == 0, \
                f"Found repeated partnerships for {num_players} players: {repeated_partnerships}"
            
            # Verify we use exactly C(n,2) partnerships
            expected_partnerships = comb(num_players, 2)
            assert len(partnerships_seen) == expected_partnerships, \
                f"Expected {expected_partnerships} partnerships, got {len(partnerships_seen)}"

    def test_complete_partnership_coverage(self, americano_tournament_factory):
        """Test that every player partners with every other player exactly once."""
        for num_players in [4, 8, 12, 16]:
            tournament, players = americano_tournament_factory(num_players)
            service = AmericanoTournamentService(tournament)
            
            rounds = service.generate_rounds()
            
            # Track partnerships for each player
            player_partners = defaultdict(set)
            
            for round_matches in rounds:
                for match in round_matches:
                    team1_p1, team1_p2, team2_p1, team2_p2 = match
                    
                    # Record partnerships
                    player_partners[team1_p1].add(team1_p2)
                    player_partners[team1_p2].add(team1_p1)
                    player_partners[team2_p1].add(team2_p2)
                    player_partners[team2_p2].add(team2_p1)
            
            # Verify completeness
            for player_id in [p.id for p in players]:
                expected_partners = num_players - 1
                actual_partners = len(player_partners[player_id])
                
                assert actual_partners == expected_partners, \
                    f"Player {player_id} partnered with {actual_partners}/{expected_partners} others"

    def test_complete_opposition_coverage(self, americano_tournament_factory):
        """Test that every player faces every other player at least once."""
        for num_players in [4, 8, 12]:
            tournament, players = americano_tournament_factory(num_players)
            service = AmericanoTournamentService(tournament)
            
            rounds = service.generate_rounds()
            
            # Track opponents for each player
            player_opponents = defaultdict(set)
            
            for round_matches in rounds:
                for match in round_matches:
                    team1_p1, team1_p2, team2_p1, team2_p2 = match
                    
                    # Record oppositions
                    for t1_player in [team1_p1, team1_p2]:
                        for t2_player in [team2_p1, team2_p2]:
                            player_opponents[t1_player].add(t2_player)
                            player_opponents[t2_player].add(t1_player)
            
            # Verify completeness
            for player_id in [p.id for p in players]:
                expected_opponents = num_players - 1
                actual_opponents = len(player_opponents[player_id])
                
                assert actual_opponents == expected_opponents, \
                    f"Player {player_id} faced {actual_opponents}/{expected_opponents} opponents"

    def test_tournament_structure_properties(self, americano_tournament_factory):
        """Test mathematical properties of tournament structure."""
        test_cases = [
            (4, 3),   # 4 players = 3 rounds
            (8, 7),   # 8 players = 7 rounds  
            (12, 11), # 12 players = 11 rounds
            (16, 15), # 16 players = 15 rounds
        ]
        
        for num_players, expected_rounds in test_cases:
            tournament, players = americano_tournament_factory(num_players)
            service = AmericanoTournamentService(tournament)
            
            rounds = service.generate_rounds()
            
            # Correct number of rounds
            assert len(rounds) == expected_rounds, \
                f"Expected {expected_rounds} rounds for {num_players} players, got {len(rounds)}"
            
            # Each round uses all players exactly once
            for round_idx, round_matches in enumerate(rounds):
                players_in_round = set()
                for match in round_matches:
                    players_in_round.update(match)
                
                assert len(players_in_round) == num_players, \
                    f"Round {round_idx+1} uses {len(players_in_round)} players, expected {num_players}"
                assert players_in_round == {p.id for p in players}, \
                    f"Round {round_idx+1} missing players"
            
            # Correct number of matches per round
            expected_matches_per_round = num_players // 4
            for round_idx, round_matches in enumerate(rounds):
                assert len(round_matches) == expected_matches_per_round, \
                    f"Round {round_idx+1} has {len(round_matches)} matches, expected {expected_matches_per_round}"

    def test_one_factorization_algorithm(self, americano_tournament_factory):
        """Test the underlying 1-factorization algorithm."""
        for n in [4, 8, 12, 16]:
            factorization = AmericanoTournamentService._one_factorization(n)
            
            # Should have n-1 perfect matchings
            assert len(factorization) == n - 1
            
            # Each perfect matching should have n/2 pairs
            for round_pairs in factorization:
                assert len(round_pairs) == n // 2
                
                # Each vertex appears exactly once in each matching
                vertices_in_round = []
                for a, b in round_pairs:
                    vertices_in_round.extend([a, b])
                
                assert len(vertices_in_round) == n
                assert len(set(vertices_in_round)) == n
                assert set(vertices_in_round) == set(range(n))

    def test_edge_pairing_algorithm(self, americano_tournament_factory):
        """Test the edge pairing algorithm for converting matchings to matches."""
        # Simple case: 2 edges
        edges = [(0, 1), (2, 3)]
        pairings = AmericanoTournamentService._pairings_of_edges(edges)
        assert len(pairings) == 1
        assert pairings[0] == [((0, 1), (2, 3))]
        
        # More complex: 4 edges (should have 3 ways to pair)
        edges = [(0, 1), (2, 3), (4, 5), (6, 7)]
        pairings = AmericanoTournamentService._pairings_of_edges(edges)
        assert len(pairings) == 3

    def test_algorithm_determinism(self, americano_tournament_factory):
        """Test that algorithm produces consistent results."""
        tournament, players = americano_tournament_factory(8)
        service = AmericanoTournamentService(tournament)
        
        # Generate multiple times
        results = []
        for _ in range(3):
            rounds = service.generate_rounds()
            
            # Convert to comparable format
            partnerships = set()
            for round_matches in rounds:
                for match in round_matches:
                    partnerships.add(tuple(sorted([match[0], match[1]])))
                    partnerships.add(tuple(sorted([match[2], match[3]])))
            
            results.append(partnerships)
        
        # All results should be identical
        first_result = results[0]
        for i, result in enumerate(results[1:], 1):
            assert result == first_result, f"Run {i+1} differs from run 1"

    def test_score_calculation(self, americano_tournament_factory, mocker):
        """Test player score calculations."""
        tournament, players = americano_tournament_factory(4)
        service = AmericanoTournamentService(tournament)
        
        # Create mock rounds with specific scores
        rounds = []
        
        # Round 1: P0,P1 vs P2,P3 -> 20-12
        round1 = mocker.Mock(spec=Round)
        round1.is_completed = True
        round1.team1_player1_id = "P0"
        round1.team1_player2_id = "P1"
        round1.team2_player1_id = "P2"
        round1.team2_player2_id = "P3"
        round1.team1_score = 20
        round1.team2_score = 12
        rounds.append(round1)
        
        # Round 2: P0,P2 vs P1,P3 -> 16-16
        round2 = mocker.Mock(spec=Round)
        round2.is_completed = True
        round2.team1_player1_id = "P0"
        round2.team1_player2_id = "P2"
        round2.team2_player1_id = "P1"
        round2.team2_player2_id = "P3"
        round2.team1_score = 16
        round2.team2_score = 16
        rounds.append(round2)
        
        scores = service.calculate_player_scores(rounds)
        
        # Verify scores
        assert scores["P0"] == 36  # 20 + 16
        assert scores["P1"] == 36  # 20 + 16
        assert scores["P2"] == 28  # 12 + 16
        assert scores["P3"] == 28  # 12 + 16

    def test_static_methods(self, americano_tournament_factory):
        """Test static utility methods."""
        # Test calculate_total_rounds
        assert AmericanoTournamentService.calculate_total_rounds(4) == 3
        assert AmericanoTournamentService.calculate_total_rounds(8) == 7
        assert AmericanoTournamentService.calculate_total_rounds(12) == 11
        
        # Test estimate_duration
        duration, rounds = AmericanoTournamentService.estimate_duration(
            num_players=8, courts=2, points_per_game=21
        )
        assert isinstance(duration, int)
        assert isinstance(rounds, int)
        assert rounds == 7
        assert duration > 0

    def test_performance_scalability(self, americano_tournament_factory):
        """Test algorithm performance for different tournament sizes."""
        performance_data = []
        
        for num_players in [4, 8, 12, 16, 20, 24]:
            tournament, players = americano_tournament_factory(num_players)
            service = AmericanoTournamentService(tournament)
            
            start = time.time()
            rounds = service.generate_rounds()
            duration = time.time() - start
            
            performance_data.append((num_players, duration))
            
            # Verify correctness
            assert len(rounds) == num_players - 1
            
            # Count partnerships
            partnerships = set()
            for round_matches in rounds:
                for match in round_matches:
                    partnerships.add(tuple(sorted([match[0], match[1]])))
                    partnerships.add(tuple(sorted([match[2], match[3]])))
            
            expected = comb(num_players, 2)
            assert len(partnerships) == expected
        
        # Performance should be reasonable
        for num_players, duration in performance_data:
            assert duration < 5.0, f"{num_players} players took {duration:.3f}s - too slow"

    @pytest.mark.parametrize("num_players,expected_rounds,expected_partnerships", [
        (4, 3, 6),     # C(4,2) = 6
        (8, 7, 28),    # C(8,2) = 28
        (12, 11, 66),  # C(12,2) = 66
        (16, 15, 120), # C(16,2) = 120
    ])
    def test_parametrized_tournament_properties(self, americano_tournament_factory, 
                                               num_players, expected_rounds, expected_partnerships):
        """Test tournament properties using parametrization."""
        tournament, players = americano_tournament_factory(num_players)
        service = AmericanoTournamentService(tournament)
        
        rounds = service.generate_rounds()
        
        # Verify rounds
        assert len(rounds) == expected_rounds
        
        # Count partnerships
        partnerships = set()
        for round_matches in rounds:
            for match in round_matches:
                partnerships.add(tuple(sorted([match[0], match[1]])))
                partnerships.add(tuple(sorted([match[2], match[3]])))
        
        assert len(partnerships) == expected_partnerships

    def test_tournament_winner_and_leaderboard(self, americano_tournament_factory):
        """Test winner determination and leaderboard generation."""
        tournament, players = americano_tournament_factory(4)
        service = AmericanoTournamentService(tournament)
        
        player_scores = {
            "P0": 100,
            "P1": 120,  # Winner
            "P2": 90,
            "P3": 85
        }
        
        # Test winner
        winner = service.get_tournament_winner(player_scores)
        assert winner == "P1"
        
        # Test empty scores
        assert service.get_tournament_winner({}) is None
        
        # Test leaderboard
        leaderboard = service.get_player_leaderboard(player_scores)
        expected = [("P1", 120), ("P0", 100), ("P2", 90), ("P3", 85)]
        assert leaderboard == expected