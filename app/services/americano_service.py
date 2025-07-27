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
        Americano tournaments work with 4, 8, 12, 16, 20, 24 players.
        Each court can handle 4 players per match.
        """
        return self.total_players >= 4 and self.total_players % 4 == 0
    
    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for Americano tournament.
        Each round has matches where 4 players compete per court.
        """
        if not self.validate_player_count():
            raise ValueError(f"Invalid player count: {self.total_players}. Must be divisible by 4 and >= 4")
        
        player_ids = [player.id for player in self.players]
        
        # Calculate matches per round based on available courts
        matches_per_round = self.tournament.courts
        
        # Calculate total rounds needed
        # Each player should play with and against every other player
        # For n players, we need approximately (n-1) rounds
        total_rounds = self._calculate_optimal_rounds()
        
        # Generate rounds using proper Americano logic
        rounds = self._generate_americano_rounds(player_ids, matches_per_round, total_rounds)
        
        return rounds
    
    def _calculate_optimal_rounds(self) -> int:
        """
        Calculate optimal number of rounds for Americano.
        Each player should play with and against every other player.
        """
        # For Americano, we want each player to play with every other player
        # With n players, each player needs to play with (n-1) other players
        # Since each match involves 4 players, we need fewer rounds
        # A good approximation is (n-1) rounds for n players
        return max(self.total_players - 1, 3)  # Minimum 3 rounds

    @staticmethod
    def calculate_total_rounds(num_players: int) -> int:
        """Calculate total rounds for a given player count."""
        # Each player should play with and against every other player
        # For a balanced tournament, use (P - 1) rounds
        return num_players - 1

    @staticmethod
    def estimate_duration(num_players: int, courts: int, points_per_game: int = 21, seconds_per_point: int = 25) -> tuple[int, int]:
        """
        Estimate tournament duration in minutes and return total rounds.
        
        Args:
            num_players: Number of players in tournament
            courts: Number of courts available
            points_per_game: Points needed to win a game (default: 21)
            seconds_per_point: Average time per point in seconds (default: 25)
        
        Returns:
            tuple: (total_minutes, total_rounds)
        """
        if num_players < 4 or num_players % 2 != 0 or courts < 1:
            raise ValueError("Invalid players or courts")
        
        # Calculate total rounds based on Americano format
        # Each player should play with and against every other player
        # For a balanced tournament, use (P - 1) rounds
        total_rounds = num_players - 1
        
        # Calculate total matches
        # Each round has P/4 matches (since 4 players per match)
        matches_per_round = num_players // 4
        total_matches = total_rounds * matches_per_round
        
        # Calculate time per match
        # T_m = G * T_p (points per game * seconds per point)
        seconds_per_match = points_per_game * seconds_per_point
        minutes_per_match = seconds_per_match / 60
        
        # Calculate total time needed
        # T_t = (M * T_m) / C (total matches * minutes per match / courts)
        total_minutes = (total_matches * minutes_per_match) / courts
        
        return int(total_minutes), total_rounds
    
    def _generate_americano_rounds(self, player_ids: List[str], matches_per_round: int, total_rounds: int) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate rounds using proper Americano logic.
        Each round has exactly matches_per_round matches (one per court).
        """
        rounds = []
        n_players = len(player_ids)
        
        # For Americano, we want to ensure good partner rotation
        # Each player should play with different partners across rounds
        
        for round_num in range(total_rounds):
            round_matches = []
            used_players = set()
            
            # Create matches for this round (one per court)
            for match_num in range(matches_per_round):
                if len(used_players) >= n_players:
                    break
                
                # Get available players for this match
                available_players = [p for p in player_ids if p not in used_players]
                
                if len(available_players) < 4:
                    # Not enough players for a full match, skip
                    break
                
                # Select 4 players for this match
                # Use round number to ensure good rotation
                match_players = []
                for i in range(4):
                    if i < len(available_players):
                        # Use round number to rotate player selection
                        player_index = (round_num + i) % len(available_players)
                        match_players.append(available_players[player_index])
                
                # Remove selected players from available list
                for player in match_players:
                    available_players.remove(player)
                    used_players.add(player)
                
                # Create match: (team1_player1, team1_player2, team2_player1, team2_player2)
                if len(match_players) == 4:
                    match = (match_players[0], match_players[1], match_players[2], match_players[3])
                    round_matches.append(match)
            
            if round_matches:
                rounds.append(round_matches)
        
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