from typing import List, Dict, Tuple, Optional
from app.services.base_tournament_format import BaseTournamentFormat
from app.models.round import Round


class TeamAmericanoTournamentService(BaseTournamentFormat):
    """
    Team Americano tournament format implementation.

    Rules:
    - Players compete in fixed pairs (teams)
    - Each team plays against every other team once (round-robin for teams)
    - Scoring is cumulative for the team across all matches
    - Winner is the team with the most accumulated points
    """

    def validate_player_count(self) -> bool:
        """Team Americano requires even number of players (at least 4) to form pairs."""
        return self.total_players >= 4 and self.total_players % 2 == 0

    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for Team Americano.
        Uses round-robin scheduling for fixed teams.
        """
        if not self.validate_player_count():
            raise ValueError(
                f"Invalid player count: {self.total_players}. Must be even and ≥4"
            )

        # Create fixed teams (pairs)
        teams = self._create_fixed_teams()

        # Generate round-robin schedule for teams
        rounds = self._generate_round_robin_for_teams(teams)

        return rounds

    def _create_fixed_teams(self) -> List[Tuple[str, str]]:
        """
        Create fixed team pairs.
        For now, pairs players sequentially: [0,1], [2,3], [4,5], etc.
        In a real implementation, this could be customizable.
        """
        player_ids = [p.id for p in self.players]
        teams = []

        for i in range(0, len(player_ids), 2):
            team = (player_ids[i], player_ids[i + 1])
            teams.append(team)

        return teams

    def _generate_round_robin_for_teams(
        self,
        teams: List[Tuple[str, str]]
    ) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate round-robin schedule where each team plays every other team once.

        Uses circle method algorithm for round-robin scheduling.
        """
        num_teams = len(teams)

        if num_teams < 2:
            return []

        # If odd number of teams, add a "bye" team
        if num_teams % 2 == 1:
            teams = teams + [None]  # type: ignore
            num_teams += 1

        rounds = []

        # Generate rounds using circle method
        for round_num in range(num_teams - 1):
            round_matches = []

            for i in range(num_teams // 2):
                team1_idx = i
                team2_idx = num_teams - 1 - i

                team1 = teams[team1_idx]
                team2 = teams[team2_idx]

                # Skip if either team is a "bye"
                if team1 is not None and team2 is not None:
                    match = (team1[0], team1[1], team2[0], team2[1])
                    round_matches.append(match)

            if round_matches:
                rounds.append(round_matches)

            # Rotate teams (keep first team fixed, rotate others)
            teams = [teams[0]] + [teams[-1]] + teams[1:-1]

        return rounds

    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate team scores (sum of points for each pair).
        Returns scores per player (both players in a team get the same score).
        """
        player_scores: Dict[str, int] = {p.id: 0 for p in self.players}

        for round_match in completed_rounds:
            if round_match.is_completed:
                # Team 1 players
                player_scores[round_match.team1_player1_id] += round_match.team1_score or 0
                player_scores[round_match.team1_player2_id] += round_match.team1_score or 0

                # Team 2 players
                player_scores[round_match.team2_player1_id] += round_match.team2_score or 0
                player_scores[round_match.team2_player2_id] += round_match.team2_score or 0

        return player_scores

    def is_tournament_complete(self, current_round: int) -> bool:
        """
        Tournament is complete when all rounds have been played.
        """
        total_rounds = len(self.generate_rounds())
        return current_round >= total_rounds

    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Determine winning team.
        Returns the player_id of one member of the winning team.
        """
        if not player_scores:
            return None

        # Find the player(s) with highest score
        max_score = max(player_scores.values())
        winners = [pid for pid, score in player_scores.items() if score == max_score]

        # Return first winner (in a team, both players have same score)
        return winners[0] if winners else None

    def get_team_scores(self, player_scores: Dict[str, int]) -> Dict[Tuple[str, str], int]:
        """
        Get scores organized by team (pair).
        Returns dict mapping (player1_id, player2_id) to team score.
        """
        teams = self._create_fixed_teams()
        team_scores = {}

        for team in teams:
            # Both players should have the same score
            team_score = player_scores.get(team[0], 0)
            team_scores[team] = team_score

        return team_scores
