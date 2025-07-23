from typing import List, Dict, Tuple, Optional
from itertools import combinations
import math
from app.services.base_tournament_format import BaseTournamentFormat
from app.models.round import Round

class AmericanoTournamentService(BaseTournamentFormat):
    """
    Americano tournament format implementation.
    
    Rules:
    - Compete individually but play in pairs
    - Teams change every match
    - Tournament ends when everyone has played against everyone else
    - Each match awards points individually based on team performance
    """
    
    def validate_player_count(self) -> bool:
        """
        Americano tournaments work best with 4, 6, 8, 12, 16 players.
        Must be divisible by 4 for proper round robin.
        """
        return self.total_players >= 4 and self.total_players % 2 == 0
    
    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for Americano tournament.
        Ensures everyone plays with and against everyone else as much as possible.
        """
        if not self.validate_player_count():
            raise ValueError(f"Invalid player count: {self.total_players}. Must be even and >= 4")
        
        player_ids = [player.id for player in self.players]
        rounds = []
        
        # For Americano, we generate rounds where each player plays with different partners
        # and against different opponents as much as possible
        
        # Calculate total rounds needed
        # In ideal Americano, each player should play with every other player once as partner
        # and against every other player at least once
        total_rounds = self._calculate_optimal_rounds()
        
        # Generate round-robin style matches
        rounds = self._generate_round_robin_rounds(player_ids)
        
        return rounds
    
    def _calculate_optimal_rounds(self) -> int:
        """
        Calculate optimal number of rounds for Americano.
        Each round has matches where every player plays once.
        """
        # Each round uses all players (total_players / 4 matches per round)
        matches_per_round = self.total_players // 4
        
        # We want each player to play with every other player once as partner
        # With n players, each player should play with (n-1) other players
        # In each match, a player plays with 1 partner, so needs (n-1) matches
        # But since each match involves 4 players, we need fewer total rounds
        
        # For simplicity, let's use a round-robin approach
        # where we ensure good distribution
        return self.total_players - 1 if self.total_players > 4 else 3
    
    def _generate_round_robin_rounds(self, player_ids: List[str]) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate rounds using a round-robin algorithm optimized for pair rotation.
        """
        rounds = []
        n_players = len(player_ids)
        
        # Create a simple round-robin where we try to rotate partners and opponents
        # For this implementation, we'll use a basic approach that ensures variety
        
        # First, generate all possible unique pairs
        all_pairs = list(combinations(player_ids, 2))
        
        # Track which pairs have played together and against each other
        played_together = set()
        played_against = set()
        
        # Generate rounds
        total_rounds = self._calculate_optimal_rounds()
        
        for round_num in range(total_rounds):
            round_matches = []
            used_players = set()
            
            # Try to create matches for this round
            matches_needed = n_players // 4
            matches_created = 0
            
            # Simple algorithm: take available pairs and match them
            available_pairs = [pair for pair in all_pairs 
                             if not (pair[0] in used_players or pair[1] in used_players)]
            
            while matches_created < matches_needed and len(available_pairs) >= 2:
                # Take first two available pairs
                if len(available_pairs) < 2:
                    break
                    
                team1 = available_pairs[0]
                
                # Find a compatible team2 (no shared players)
                team2 = None
                for i, pair in enumerate(available_pairs[1:], 1):
                    if not (pair[0] in team1 or pair[1] in team1):
                        team2 = pair
                        available_pairs.pop(i)
                        break
                
                if team2:
                    available_pairs.pop(0)  # Remove team1
                    round_matches.append((team1[0], team1[1], team2[0], team2[1]))
                    
                    # Mark players as used
                    used_players.update([team1[0], team1[1], team2[0], team2[1]])
                    
                    # Track what pairs have played together and against each other
                    played_together.add(team1)
                    played_together.add(team2)
                    
                    matches_created += 1
                else:
                    break
            
            if round_matches:
                rounds.append(round_matches)
        
        # If we don't have enough rounds or matches, use a fallback method
        if len(rounds) == 0 or sum(len(round_matches) for round_matches in rounds) < total_rounds:
            return self._generate_simple_rounds(player_ids)
        
        return rounds
    
    def _generate_simple_rounds(self, player_ids: List[str]) -> List[List[Tuple[str, str, str, str]]]:
        """
        Fallback method for generating rounds with simple rotation.
        """
        rounds = []
        n_players = len(player_ids)
        
        # Simple rotation algorithm
        for round_num in range(min(n_players - 1, 6)):  # Limit to reasonable number
            round_matches = []
            
            # Rotate players and create matches
            rotated_players = player_ids[round_num:] + player_ids[:round_num]
            
            # Create matches from rotated list
            for i in range(0, n_players - n_players % 4, 4):
                if i + 3 < len(rotated_players):
                    match = (rotated_players[i], rotated_players[i+1], 
                           rotated_players[i+2], rotated_players[i+3])
                    round_matches.append(match)
            
            if round_matches:
                rounds.append(round_matches)
        
        return rounds
    
    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate individual player scores for Americano.
        Each player gets the points their team scored in each match they played.
        """
        player_scores = {}
        
        # Initialize scores for all players
        for player in self.players:
            player_scores[player.id] = 0
        
        # Add scores from completed rounds
        for round_match in completed_rounds:
            if round_match.is_completed:
                # Team 1 players get team1_score points
                player_scores[round_match.team1_player1_id] += round_match.team1_score
                player_scores[round_match.team1_player2_id] += round_match.team1_score
                
                # Team 2 players get team2_score points
                player_scores[round_match.team2_player1_id] += round_match.team2_score
                player_scores[round_match.team2_player2_id] += round_match.team2_score
        
        return player_scores
    
    def is_tournament_complete(self, current_round: int) -> bool:
        """
        Check if all planned rounds have been completed.
        """
        total_rounds = self.get_total_rounds()
        return current_round > total_rounds
    
    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Get the player with the highest score.
        """
        if not player_scores:
            return None
        
        # Find player with maximum score
        winner_id = max(player_scores.items(), key=lambda x: x[1])[0]
        return winner_id
    
    def get_player_leaderboard(self, player_scores: Dict[str, int]) -> List[Tuple[str, int]]:
        """
        Get leaderboard sorted by scores (highest first).
        """
        return sorted(player_scores.items(), key=lambda x: x[1], reverse=True) 