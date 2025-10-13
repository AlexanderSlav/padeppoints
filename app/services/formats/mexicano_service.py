from typing import List, Dict, Tuple, Optional
import random
from app.services.formats.ranking_based_format import RankingBasedFormat
from app.models.round import Round


class MexicanoTournamentService(RankingBasedFormat):
    """
    Mexicano tournament format implementation.

    Rules:
    - Players compete individually, partners rotate each round
    - First round matchups are random
    - Subsequent rounds use ranking-based matchmaking (1+3 vs 2+4, 5+7 vs 6+8, etc.)
    - The better you play, the harder the opposition
    - Winner is the player with the most accumulated points
    """

    def validate_player_count(self) -> bool:
        """Mexicano tournaments work with 4, 8, 12, 16, ... players (divisible by 4)."""
        return self.total_players >= 4 and self.total_players % 4 == 0

    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for a Mexicano tournament.
        Only the first round is generated upfront (random matchups).
        Subsequent rounds must be generated dynamically based on standings.
        """
        if not self.validate_player_count():
            raise ValueError(
                f"Invalid player count: {self.total_players}. Must be divisible by 4 and ≥4"
            )

        # For Mexicano, we generate the first round only
        # Subsequent rounds will be generated dynamically via generate_next_round()
        first_round = self._generate_first_round()
        return [first_round]

    def _generate_first_round(self) -> List[Tuple[str, str, str, str]]:
        """
        Generate first round with random matchups.
        """
        player_ids = [p.id for p in self.players]
        random.shuffle(player_ids)

        matches = []
        for i in range(0, len(player_ids), 4):
            match = (
                player_ids[i],
                player_ids[i + 1],
                player_ids[i + 2],
                player_ids[i + 3]
            )
            matches.append(match)

        return matches

    def generate_next_round(self, completed_rounds: List[Round]) -> List[Tuple[str, str, str, str]]:
        """
        Generate the next round based on current standings.
        This should be called after each round is completed.
        """
        standings = self.get_current_standings(completed_rounds)
        return self.generate_next_round_matchups(standings)

    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate individual player scores.
        Each player gets points equal to their team's score in each match.
        """
        player_scores: Dict[str, int] = {p.id: 0 for p in self.players}

        for round_match in completed_rounds:
            if round_match.is_completed:
                # Team 1 players get team1_score
                player_scores[round_match.team1_player1_id] += round_match.team1_score or 0
                player_scores[round_match.team1_player2_id] += round_match.team1_score or 0

                # Team 2 players get team2_score
                player_scores[round_match.team2_player1_id] += round_match.team2_score or 0
                player_scores[round_match.team2_player2_id] += round_match.team2_score or 0

        return player_scores

    def calculate_player_statistics(self, completed_rounds: List[Round]) -> Dict[str, Dict]:
        """Calculate comprehensive player statistics including W-L-T records."""
        player_stats = {
            p.id: {
                'total_points': 0,
                'points_earned': 0,
                'points_conceded': 0,
                'points_difference': 0,
                'wins': 0,
                'losses': 0,
                'ties': 0,
                'matches_played': 0,
            }
            for p in self.players
        }

        for round_match in completed_rounds:
            if round_match.is_completed:
                t1, t2 = round_match.team1_score or 0, round_match.team2_score or 0

                # Determine match result
                if t1 > t2:
                    res1, res2 = 'win', 'loss'
                elif t2 > t1:
                    res1, res2 = 'loss', 'win'
                else:
                    res1 = res2 = 'tie'

                # Update team 1 players' stats
                for pid in [round_match.team1_player1_id, round_match.team1_player2_id]:
                    stats = player_stats[pid]
                    stats['total_points'] += t1
                    stats['points_earned'] += t1
                    stats['points_conceded'] += t2
                    stats['points_difference'] += (t1 - t2)
                    stats['matches_played'] += 1
                    stats['wins'] += res1 == 'win'
                    stats['losses'] += res1 == 'loss'
                    stats['ties'] += res1 == 'tie'

                # Update team 2 players' stats
                for pid in [round_match.team2_player1_id, round_match.team2_player2_id]:
                    stats = player_stats[pid]
                    stats['total_points'] += t2
                    stats['points_earned'] += t2
                    stats['points_conceded'] += t1
                    stats['points_difference'] += (t2 - t1)
                    stats['matches_played'] += 1
                    stats['wins'] += res2 == 'win'
                    stats['losses'] += res2 == 'loss'
                    stats['ties'] += res2 == 'tie'

        return player_stats

    def is_tournament_complete(self, current_round: int) -> bool:
        """
        Mexicano tournaments are manually completed by organizer.
        They can run for any number of rounds.
        """
        return False  # Always requires manual completion

    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Determine the winner based on highest total score.
        """
        if not player_scores:
            return None

        winner_id = max(player_scores.items(), key=lambda x: x[1])[0]
        return winner_id

    def get_expected_rounds(self) -> int:
        """
        Get recommended number of rounds for Mexicano.
        Typically n-1 rounds where n is number of players (like Americano).
        """
        return self.total_players - 1
