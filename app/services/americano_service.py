from typing import List, Dict, Tuple, Optional
from app.services.base_tournament_format import BaseTournamentFormat
from app.models.round import Round

class AmericanoTournamentService(BaseTournamentFormat):
    """
    Americano tournament format implementation.

    Rules:
    - Players compete individually but play in pairs.
    - Teams change every match.
    - Over the tournament each player partners with every other player once and
      also faces every other player at least once.
    - Each match awards points individually based on team performance.
    """

    def validate_player_count(self) -> bool:
        """ Americano tournaments work with 4, 8, 12, 16, … players. """
        return self.total_players >= 4 and self.total_players % 4 == 0

    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for an Americano tournament.
        Each round consists of matches where 4 players (2 pairs) compete per court.
        This implementation ensures each pair of players partners exactly once and
        faces each other at least once.
        """
        if not self.validate_player_count():
            raise ValueError(
                f"Invalid player count: {self.total_players}. Must be divisible by 4 and ≥4"
            )
        n = self.total_players
        player_ids = [p.id for p in self.players]

        # Compute one‑factorization of the complete graph on n vertices.
        # This partitions all possible pairs into n−1 perfect matchings,
        # giving the number of rounds needed.
        factorization = self._one_factorization(n)

        # Use a greedy pairing algorithm to convert each perfect matching into
        # matches of four players (two pairs) while maximising new opponent pairs.
        rounds = self._generate_balanced_americano_rounds(player_ids, factorization)
        return rounds

    @staticmethod
    def _one_factorization(n: int) -> List[List[Tuple[int, int]]]:
        """
        Generate a list of (n−1) perfect matchings (1‑factorization) for an even n.
        Each perfect matching consists of n/2 unordered pairs of vertex indices.
        """
        # Round‑robin algorithm to generate a 1‑factorization
        top = list(range(1, n))
        rounds = []
        for _ in range(n - 1):
            pairs = []
            arrangement = [0] + top
            for i in range(n // 2):
                a = arrangement[i]
                b = arrangement[n - 1 - i]
                pairs.append((a, b))
            rounds.append(pairs)
            # rotate the top list
            top = [top[-1]] + top[:-1]
        return rounds

    @staticmethod
    def _pairings_of_edges(edges: List[Tuple[int, int]]) -> List[List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Enumerate all ways to pair up the list of edges into unordered pairs.
        Used to split a perfect matching (n/2 edges) into n/4 matches.
        """
        if not edges:
            return [[]]
        first = edges[0]
        rest = edges[1:]
        result = []
        for i, e in enumerate(rest):
            pair = (first, e)
            remaining = rest[:i] + rest[i + 1:]
            for sub in AmericanoTournamentService._pairings_of_edges(remaining):
                result.append([pair] + sub)
        return result

    def _generate_balanced_americano_rounds(
        self, player_ids: List[str], factorization: List[List[Tuple[int, int]]]
    ) -> List[List[Tuple[str, str, str, str]]]:
        """
        Given a 1‑factorization, greedily pair edges in each round to maximise new
        opponent pairs.  Returns a list of rounds, where each round is a list of
        matches represented as (playerA, playerB, playerC, playerD).
        """
        n = len(player_ids)
        cross_covered = set()  # track opponent pairs already used
        rounds: List[List[Tuple[str, str, str, str]]] = []

        for round_pairs in factorization:
            # enumerate all ways to pair the n/2 edges into n/4 matches
            pairings = self._pairings_of_edges(round_pairs)
            best_pairing = None
            max_new_cross = -1

            # choose the pairing that introduces the most new opponent pairs
            for pairing in pairings:
                new_cross = 0
                for (a, b), (c, d) in pairing:
                    for u in (a, b):
                        for v in (c, d):
                            cp = (min(u, v), max(u, v))
                            if cp not in cross_covered:
                                new_cross += 1
                if new_cross > max_new_cross:
                    max_new_cross = new_cross
                    best_pairing = pairing
                    # early exit if this pairing covers all remaining cross pairs
                    if max_new_cross == (n * (n - 1) // 2) - len(cross_covered):
                        break

            # record opponent pairs and build matches for this round
            round_matches: List[Tuple[str, str, str, str]] = []
            for (a, b), (c, d) in best_pairing:
                # update opponent coverage
                for u in (a, b):
                    for v in (c, d):
                        cross_covered.add((min(u, v), max(u, v)))
                # convert indices to player IDs and record match
                round_matches.append((player_ids[a], player_ids[b], player_ids[c], player_ids[d]))
            rounds.append(round_matches)
        return rounds

    def _calculate_optimal_rounds(self) -> int:
        """Each player partners with every other player once, so need (P − 1) rounds."""
        return max(self.total_players - 1, 3)

    @staticmethod
    def calculate_total_rounds(num_players: int) -> int:
        return num_players - 1

    @staticmethod
    def calculate_optimal_points_per_match(
        num_players: int,
        courts: int,
        available_hours: float,
        seconds_per_point: int = 25,
        resting_between_matches_seconds: int = 60,
    ) -> int:
        """
        Calculate optimal points per match based on time constraints.
        Returns the highest point target that fits within the available time.
        """
        if num_players < 4 or num_players % 2 != 0 or courts < 1 or available_hours <= 0:
            raise ValueError("Invalid parameters")

        total_rounds = num_players - 1
        matches_per_round = num_players // 4
        total_matches = total_rounds * matches_per_round
        available_minutes = available_hours * 60

        for points in range(48, 15, -4):
            seconds_per_match = (points * seconds_per_point) + resting_between_matches_seconds
            minutes_per_match = seconds_per_match / 60
            total_minutes_needed = (total_matches * minutes_per_match) / courts
            if total_minutes_needed <= available_minutes:
                return points
        return 16

    @staticmethod
    def estimate_duration(
        num_players: int,
        courts: int,
        points_per_game: int = 21,
        seconds_per_point: int = 25,
        resting_between_matches_seconds: int = 60,
        minutes_per_match: int = 10,
    ) -> tuple[int, int]:
        """Estimate tournament duration in minutes and return total rounds."""
        if num_players < 4 or num_players % 2 != 0 or courts < 1:
            raise ValueError("Invalid players or courts")
        total_rounds = num_players - 1
        matches_per_round = num_players // 4
        total_matches = total_rounds * matches_per_round
        seconds_per_match = points_per_game * seconds_per_point + resting_between_matches_seconds
        minutes_per_match = seconds_per_match / 60
        total_minutes = (total_matches * minutes_per_match) / courts
        return int(total_minutes), total_rounds

    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """Compute individual scores for players based on completed matches."""
        player_scores = {p.id: 0 for p in self.players}
        for round_match in completed_rounds:
            if round_match.is_completed:
                player_scores[round_match.team1_player1_id] += round_match.team1_score
                player_scores[round_match.team1_player2_id] += round_match.team1_score
                player_scores[round_match.team2_player1_id] += round_match.team2_score
                player_scores[round_match.team2_player2_id] += round_match.team2_score
        return player_scores

    def calculate_player_statistics(self, completed_rounds: List[Round]) -> Dict[str, Dict]:
        """Calculate comprehensive player statistics including W‑L‑T records."""
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
                t1, t2 = round_match.team1_score, round_match.team2_score
                if t1 > t2:
                    res1, res2 = 'win', 'loss'
                elif t2 > t1:
                    res1, res2 = 'loss', 'win'
                else:
                    res1 = res2 = 'tie'
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

    def get_total_rounds(self) -> int:
        return self._calculate_optimal_rounds()

    def is_tournament_complete(self, current_round: int) -> bool:
        return current_round > self.get_total_rounds()

    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        return max(player_scores, key=player_scores.get) if player_scores else None

    def get_player_leaderboard(self, player_scores: Dict[str, int]) -> List[Tuple[str, int]]:
        return sorted(player_scores.items(), key=lambda x: x[1], reverse=True)