from typing import List, Dict, Tuple, Optional
import random
from app.services.formats.ranking_based_format import RankingBasedFormat
from app.models.round import Round


class TeamMexicanoTournamentService(RankingBasedFormat):
    """
    Team Mexicano tournament format implementation.

    Rules:
    - Players compete in fixed pairs (teams)
    - First round matchups are random
    - Subsequent rounds use ranking-based matchmaking based on team scores
    - Team scoring: both players in a pair accumulate the same points
    - Winner is the team with the most accumulated points
    """

    def validate_player_count(self) -> bool:
        """Team Mexicano requires even number of players (at least 4) to form pairs."""
        return self.total_players >= 4 and self.total_players % 2 == 0

    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate all rounds for Team Mexicano.
        Only the first round is generated upfront (random matchups with fixed teams).
        Subsequent rounds must be generated dynamically based on team standings.
        """
        if not self.validate_player_count():
            raise ValueError(
                f"Invalid player count: {self.total_players}. Must be even and ≥4"
            )

        # Create fixed teams
        self.fixed_teams = self._create_fixed_teams()

        # Generate first round with random team matchups
        first_round = self._generate_first_round()
        return [first_round]

    def _create_fixed_teams(self) -> List[Tuple[str, str]]:
        """
        Create fixed team pairs.
        Pairs players sequentially: [0,1], [2,3], [4,5], etc.
        """
        player_ids = [p.id for p in self.players]
        teams = []

        for i in range(0, len(player_ids), 2):
            team = (player_ids[i], player_ids[i + 1])
            teams.append(team)

        return teams

    def _generate_first_round(self) -> List[Tuple[str, str, str, str]]:
        """
        Generate first round with random team matchups.
        """
        teams = list(self.fixed_teams)
        random.shuffle(teams)

        matches = []
        for i in range(0, len(teams), 2):
            if i + 1 < len(teams):
                team1 = teams[i]
                team2 = teams[i + 1]
                match = (team1[0], team1[1], team2[0], team2[1])
                matches.append(match)

        return matches

    def generate_next_round(self, completed_rounds: List[Round]) -> List[Tuple[str, str, str, str]]:
        """
        Generate the next round based on team standings.
        Teams with similar rankings play against each other.
        """
        # Get team standings
        team_standings = self._get_team_standings(completed_rounds)

        # Use ranking-based matchmaking for teams
        matches = []

        # Pair teams: 1st vs 2nd, 3rd vs 4th, etc.
        for i in range(0, len(team_standings), 2):
            if i + 1 < len(team_standings):
                team1 = team_standings[i][0]  # (player1_id, player2_id)
                team2 = team_standings[i + 1][0]

                match = (team1[0], team1[1], team2[0], team2[1])
                matches.append(match)

        return matches

    def _get_team_standings(self, completed_rounds: List[Round]) -> List[Tuple[Tuple[str, str], int]]:
        """
        Calculate team standings from completed rounds.

        Returns:
            List of ((player1_id, player2_id), team_score) tuples, sorted by score descending
        """
        team_scores: Dict[Tuple[str, str], int] = {team: 0 for team in self.fixed_teams}

        for round_match in completed_rounds:
            if round_match.is_completed:
                # Identify which fixed team each match team belongs to
                match_team1 = self._get_fixed_team_for_players(
                    round_match.team1_player1_id,
                    round_match.team1_player2_id
                )
                match_team2 = self._get_fixed_team_for_players(
                    round_match.team2_player1_id,
                    round_match.team2_player2_id
                )

                if match_team1 in team_scores:
                    team_scores[match_team1] += round_match.team1_score or 0

                if match_team2 in team_scores:
                    team_scores[match_team2] += round_match.team2_score or 0

        # Sort teams by score descending
        standings = sorted(
            team_scores.items(),
            key=lambda x: (-x[1], x[0])
        )

        return standings

    def _get_fixed_team_for_players(self, player1_id: str, player2_id: str) -> Optional[Tuple[str, str]]:
        """
        Find the fixed team that contains these two players.
        """
        player_set = {player1_id, player2_id}

        for team in self.fixed_teams:
            if set(team) == player_set:
                return team

        return None

    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate scores for each player.
        In team format, both players in a team get the same score.
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
        Team Mexicano tournaments are manually completed by organizer.
        """
        return False

    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Determine winning team.
        Returns player_id of one member of the winning team.
        """
        if not player_scores:
            return None

        max_score = max(player_scores.values())
        winners = [pid for pid, score in player_scores.items() if score == max_score]

        return winners[0] if winners else None

    def get_expected_rounds(self) -> int:
        """
        Recommended number of rounds for Team Mexicano.
        Typically (n/2) - 1 where n is number of players.
        """
        num_teams = len(self.fixed_teams)
        return max(num_teams - 1, 3)  # At least 3 rounds
