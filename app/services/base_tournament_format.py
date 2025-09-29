from abc import ABC, abstractmethod
from typing import List, Dict, Tuple, Optional
from app.models.tournament import Tournament
from app.models.round import Round
from app.models.user import User

class BaseTournamentFormat(ABC):
    """
    Abstract base class for tournament format implementations.
    Each format (Americano, Mexicano, etc.) should inherit from this class.
    """
    
    def __init__(self, tournament: Tournament, players: Optional[List[User]] = None):
        self.tournament = tournament
        # If players are explicitly provided, use them; otherwise, access the relationship
        # This allows async callers to pre-load players and avoid greenlet issues
        if players is not None:
            self.players = players
        else:
            self.players = list(tournament.players)
        self.total_players = len(self.players)
    
    @abstractmethod
    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for the tournament.
        Returns a list of rounds, where each round is a list of matches.
        Each match is a tuple of (team1_player1_id, team1_player2_id, team2_player1_id, team2_player2_id).
        """
        pass
    
    @abstractmethod
    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate individual player scores based on completed rounds.
        Returns a dictionary mapping player_id to their total score.
        """
        pass
    
    @abstractmethod
    def is_tournament_complete(self, current_round: int) -> bool:
        """
        Check if the tournament is complete based on the current round.
        """
        pass
    
    @abstractmethod
    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Determine the tournament winner based on player scores.
        Returns player_id of the winner, or None if tournament is not complete.
        """
        pass
    
    @abstractmethod
    def validate_player_count(self) -> bool:
        """
        Validate that the number of players is valid for this tournament format.
        """
        pass
    
    def get_total_rounds(self) -> int:
        """
        Get the total number of rounds needed for the tournament.
        This can be overridden by specific formats if needed.
        """
        return len(self.generate_rounds()) 