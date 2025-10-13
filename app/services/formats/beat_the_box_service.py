from typing import List, Dict, Tuple, Optional
import random
from app.services.formats.ranking_based_format import RankingBasedFormat
from app.models.round import Round


class BeatTheBoxTournamentService(RankingBasedFormat):
    """
    Beat the Box tournament format implementation.

    Rules:
    - Players are divided into boxes (groups) of equal size
    - All players in a box play against each other
    - After each round, players move between boxes based on performance
    - Better performers move up, weaker performers move down
    - Creates competitive matches with similarly-skilled opponents
    """

    def __init__(self, *args, box_size: int = 4, **kwargs):
        super().__init__(*args, **kwargs)
        self.box_size = box_size
        self.num_boxes = self.total_players // box_size

    def validate_player_count(self) -> bool:
        """
        Beat the Box requires:
        - At least 8 players
        - Player count must be divisible by box size
        - Box size must be 4, 5, 7, or 8
        """
        valid_box_sizes = [4, 5, 7, 8]

        if self.total_players < 8:
            return False

        if self.box_size not in valid_box_sizes:
            return False

        if self.total_players % self.box_size != 0:
            return False

        return True

    def generate_rounds(self) -> List[List[Tuple[str, str, str, str]]]:
        """
        Generate first round with players in initial boxes.
        Subsequent rounds are generated dynamically based on performance.
        """
        if not self.validate_player_count():
            raise ValueError(
                f"Invalid configuration: {self.total_players} players with box size {self.box_size}. "
                f"Player count must be ≥8 and divisible by box size (4,5,7,8)."
            )

        # Create initial boxes (random or by rating if available)
        boxes = self._create_initial_boxes()

        # Generate first round matches
        first_round = self._generate_round_for_boxes(boxes)

        return [first_round]

    def _create_initial_boxes(self) -> List[List[str]]:
        """
        Create initial player boxes.
        For first tournament, distribute randomly.
        """
        player_ids = [p.id for p in self.players]
        random.shuffle(player_ids)

        boxes = []
        for i in range(0, len(player_ids), self.box_size):
            box = player_ids[i:i + self.box_size]
            boxes.append(box)

        return boxes

    def _generate_round_for_boxes(self, boxes: List[List[str]]) -> List[Tuple[str, str, str, str]]:
        """
        Generate matches within each box.
        Each box plays one round where players are paired to play against each other.
        """
        all_matches = []

        for box in boxes:
            if len(box) < 4:
                continue  # Skip incomplete boxes

            # Shuffle players in box for variety
            box_players = list(box)
            random.shuffle(box_players)

            # Create matches (pair players: 0-1 vs 2-3, 4-5 vs 6-7, etc.)
            for i in range(0, len(box_players), 4):
                if i + 3 < len(box_players):
                    match = (
                        box_players[i],
                        box_players[i + 1],
                        box_players[i + 2],
                        box_players[i + 3]
                    )
                    all_matches.append(match)

        return all_matches

    def generate_next_round(self, completed_rounds: List[Round]) -> List[Tuple[str, str, str, str]]:
        """
        Generate next round after redistributing players into boxes based on performance.
        """
        # Get current standings
        standings = self.get_current_standings(completed_rounds)

        # Redistribute players into boxes based on standings
        new_boxes = self._redistribute_into_boxes(standings)

        # Generate matches for new boxes
        return self._generate_round_for_boxes(new_boxes)

    def _redistribute_into_boxes(self, standings: List[Tuple[str, int]]) -> List[List[str]]:
        """
        Redistribute players into boxes based on their standings.
        Top performers go to top box, bottom performers to bottom box.
        """
        player_ids = [player_id for player_id, _ in standings]

        boxes = []
        for i in range(0, len(player_ids), self.box_size):
            box = player_ids[i:i + self.box_size]
            boxes.append(box)

        return boxes

    def calculate_player_scores(self, completed_rounds: List[Round]) -> Dict[str, int]:
        """
        Calculate individual player scores.
        Each player accumulates points from all their matches.
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
        Beat the Box tournaments are manually completed by organizer.
        """
        return False

    def get_tournament_winner(self, player_scores: Dict[str, int]) -> Optional[str]:
        """
        Winner is the player with highest total score.
        """
        if not player_scores:
            return None

        winner_id = max(player_scores.items(), key=lambda x: x[1])[0]
        return winner_id

    def get_expected_rounds(self) -> int:
        """
        Recommended number of rounds for Beat the Box.
        Typically 3-5 rounds depending on time available.
        """
        return min(5, max(3, self.num_boxes))

    def get_box_standings(self, completed_rounds: List[Round]) -> Dict[int, List[Tuple[str, int]]]:
        """
        Get standings organized by box.
        Returns dict mapping box_number to list of (player_id, score) in that box.
        """
        standings = self.get_current_standings(completed_rounds)
        boxes = self._redistribute_into_boxes(standings)

        box_standings = {}
        for box_num, box_players in enumerate(boxes, 1):
            box_scores = [
                (pid, score) for pid, score in standings
                if pid in box_players
            ]
            box_standings[box_num] = box_scores

        return box_standings
