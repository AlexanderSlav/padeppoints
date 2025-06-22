from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.models.base import Base

# Association table for many-to-many relationship
tournament_player = Table(
    "tournament_player",
    Base.metadata,
    Column("tournament_id", String, ForeignKey("tournament.id"), primary_key=True),
    Column("player_id", String, ForeignKey("users.id"), primary_key=True),
)

class TournamentSystem(enum.Enum):  # Fixed: removed str inheritance
    AMERICANO = "americano"
    MEXICANO = "mexicano"

class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    system = Column(Enum(TournamentSystem), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, active, completed
    current_round = Column(Integer, default=1)
    
    # Relationships
    players = relationship(
        "User",
        secondary=tournament_player,
        back_populates="tournaments"
    )
    rounds = relationship("Round", back_populates="tournament", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_tournaments")

    def __repr__(self):
        return f"<Tournament(id={self.id}, name={self.name}, system={self.system}, status={self.status})>"