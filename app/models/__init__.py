# app/models/__init__.py
from app.models.base import Base
from app.models.user import User
from app.models.tournament import Tournament, TournamentSystem, tournament_player
from app.models.round import Round
from app.models.player_rating import PlayerRating, RatingHistory
from app.models.tournament_result import TournamentResult
from app.models.audit_log import AuditLog, ActionType, TargetType

# Export all models for Alembic to detect
__all__ = [
    "Base",
    "User",
    "Tournament",
    "TournamentSystem",
    "tournament_player",
    "Round",
    "PlayerRating",
    "RatingHistory",
    "TournamentResult",
    "AuditLog",
    "ActionType",
    "TargetType"
]