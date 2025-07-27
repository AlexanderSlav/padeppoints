from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, Table, Text, Float, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base

# Association table for many-to-many relationship
tournament_player = Table(
    "tournament_player",
    Base.metadata,
    Column("tournament_id", String, ForeignKey("tournaments.id"), primary_key=True),
    Column("player_id", String, ForeignKey("users.id"), primary_key=True),
)

class TournamentSystem(enum.Enum):  # Fixed: removed str inheritance
    AMERICANO = "AMERICANO"
    MEXICANO = "MEXICANO"

class TournamentStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

class Tournament(Base):
    __tablename__ = "tournaments"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    entry_fee = Column(Float, nullable=False, default=0.0)
    max_players = Column(Integer, nullable=False, default=16)
    system = Column(Enum(TournamentSystem, name='tournamentsystem', create_type=False), nullable=False, default=TournamentSystem.AMERICANO)
    points_per_match = Column(Integer, nullable=False, default=32)
    courts = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String, default=TournamentStatus.PENDING.value)
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