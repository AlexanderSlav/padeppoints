from sqlalchemy import Column, String, DateTime, Enum, Integer, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.base import Base

tournament_player = Table(
    "tournament_player",
    Base.metadata,
    Column("tournament_id", String, ForeignKey("tournament.id"), primary_key=True),
    Column("player_id", String, ForeignKey("user.id"), primary_key=True),
)

class TournamentSystem(str, enum.Enum):
    AMERICANO = "americano"
    MEXICANO = "mexicano"


class Tournament(Base):
    __tablename__ = "tournament"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    system = Column(Enum(TournamentSystem), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, ForeignKey("user.id"), nullable=False)
    status = Column(String, default="pending")  # pending, active, completed
    current_round = Column(Integer, default=1)
    
    # Relationships
    players = relationship(
        "User",
        secondary="tournament_player",
        back_populates="tournaments"
    )
    rounds = relationship("Round", back_populates="tournament")
    creator = relationship("User", back_populates="created_tournaments")

    def __repr__(self):
        return f"<Tournament(id={self.id}, name={self.name}, system={self.system}, status={self.status})>" 