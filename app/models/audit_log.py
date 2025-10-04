"""
Audit Log Model

Tracks all administrative actions for accountability and audit trail purposes.
Records who performed what action, when, and what changed.
"""
from sqlalchemy import Column, String, DateTime, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
import uuid
import enum
from app.models.base import Base


class ActionType(str, enum.Enum):
    """Types of administrative actions that can be logged."""
    USER_DELETE = "user_delete"
    USER_UPDATE = "user_update"
    USER_STATUS_CHANGE = "user_status_change"
    TOURNAMENT_RESULT_EDIT = "tournament_result_edit"
    TOURNAMENT_SCORE_RECALC = "tournament_score_recalc"
    TOURNAMENT_STATUS_CHANGE = "tournament_status_change"
    TOURNAMENT_DELETE = "tournament_delete"
    SYSTEM_CONFIG_CHANGE = "system_config_change"


class TargetType(str, enum.Enum):
    """Types of entities that can be targeted by admin actions."""
    USER = "user"
    TOURNAMENT = "tournament"
    MATCH = "match"
    ROUND = "round"
    SYSTEM = "system"


class AuditLog(Base):
    """
    Audit log for tracking all administrative actions.

    Attributes:
        id: Unique identifier for the audit log entry
        admin_id: ID of the admin user who performed the action
        action_type: Type of action performed (from ActionType enum)
        target_type: Type of entity that was modified (from TargetType enum)
        target_id: ID of the entity that was modified
        details: JSON object containing action details:
            - old_values: Previous state (for updates)
            - new_values: New state (for updates)
            - reason: Admin's reason for the action
            - cascade_effects: List of related entities affected
        ip_address: IP address of the admin when action was performed
        timestamp: When the action occurred (auto-generated)
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    admin_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action_type = Column(SQLEnum(ActionType), nullable=False, index=True)
    target_type = Column(SQLEnum(TargetType), nullable=False, index=True)
    target_id = Column(String, nullable=False, index=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    def __repr__(self):
        return (
            f"<AuditLog(id={self.id}, admin_id={self.admin_id}, "
            f"action={self.action_type}, target={self.target_type}:{self.target_id})>"
        )
