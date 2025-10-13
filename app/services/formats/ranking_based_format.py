from abc import abstractmethod
from typing import List, Dict, Tuple
from app.services.base_tournament_format import BaseTournamentFormat
from app.models.round import Round


class RankingBasedFormat(BaseTournamentFormat):
    """
    Base class for ranking-based formats (Mexicano variants).
    These formats use current standings to determine matchmaking.
    """

    def generate_next_round_matchups(
        self,
        current_standings: List[Tuple[str, int]]
    ) -> List[Tuple[str, str, str, str]]:
        """
        Generate matchups for the next round based on current standings.
        Pairs players by ranking: 1+3 vs 2+4, 5+7 vs 6+8, etc.

        Args:
            current_standings: List of (player_id, score) tuples, sorted by score descending

        Returns:
            List of matches (team1_p1, team1_p2, team2_p1, team2_p2)
        """
        player_ids = [player_id for player_id, _ in current_standings]
        matches = []

        # Pair players: 1+3 vs 2+4, 5+7 vs 6+8, etc.
        for i in range(0, len(player_ids), 4):
            if i + 3 < len(player_ids):
                match = (
                    player_ids[i],      # Rank 1
                    player_ids[i + 2],  # Rank 3
                    player_ids[i + 1],  # Rank 2
                    player_ids[i + 3]   # Rank 4
                )
                matches.append(match)

        return matches

    def get_current_standings(self, completed_rounds: List[Round]) -> List[Tuple[str, int]]:
        """
        Calculate current player standings from completed rounds.

        Returns:
            List of (player_id, total_score) tuples, sorted by score descending
        """
        player_scores = self.calculate_player_scores(completed_rounds)

        # Sort by score descending, then by player_id for consistency
        standings = sorted(
            player_scores.items(),
            key=lambda x: (-x[1], x[0])
        )

        return standings
