"""Tournament result model for storing final positions and scores."""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class TournamentResult(Base):
    """Store final tournament results and player positions."""
    __tablename__ = "tournament_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    player_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Final results
    final_position = Column(Integer, nullable=False)  # 1st, 2nd, 3rd, etc.
    total_score = Column(Integer, nullable=False)     # Total points scored
    points_difference = Column(Integer, default=0)    # Points for - points against
    matches_played = Column(Integer, default=0)
    matches_won = Column(Integer, default=0)
    matches_lost = Column(Integer, default=0)
    matches_tied = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    tournament = relationship("Tournament")
    player = relationship("User")
    
    # Ensure one result per player per tournament
    __table_args__ = (
        UniqueConstraint('tournament_id', 'player_id', name='unique_tournament_player_result'),
    )
    
    def __repr__(self):
        return f"<TournamentResult(tournament_id={self.tournament_id}, player_id={self.player_id}, position={self.final_position})>"
