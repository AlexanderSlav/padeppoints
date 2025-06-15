from typing import Dict, List, Optional
from app.models.tournament import Tournament, TournamentSystem
from app.models.user import User

# In-memory storage
tournaments: Dict[str, Tournament] = {}
users: Dict[str, User] = {}
tournament_player_ids: Dict[str, List[str]] = {}  # tournament_id -> list of player_ids


class MockDB:
    @staticmethod
    def create_tournament(tournament: Tournament) -> Tournament:
        tournaments[tournament.id] = tournament
        tournament_player_ids[tournament.id] = []
        return tournament

    @staticmethod
    def get_tournament(tournament_id: str) -> Optional[Tournament]:
        return tournaments.get(tournament_id)

    @staticmethod
    def list_tournaments() -> List[Tournament]:
        return list(tournaments.values())

    @staticmethod
    def join_tournament(tournament_id: str, player_id: str) -> bool:
        if tournament_id not in tournaments:
            return False
        if player_id not in tournament_player_ids[tournament_id]:
            tournament_player_ids[tournament_id].append(player_id)
            return True
        return False

    @staticmethod
    def get_tournament_players(tournament_id: str) -> List[str]:
        return tournament_player_ids.get(tournament_id, []) 