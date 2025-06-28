from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class Round(Base):
    __tablename__ = "rounds"
    
    id = Column(String, primary_key=True)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=False)
    round_number = Column(Integer, nullable=False, default=1)  # Added round number
    
    # Team 1 players
    team1_player1_id = Column(String, ForeignKey("users.id"), nullable=False)
    team1_player2_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Team 2 players
    team2_player1_id = Column(String, ForeignKey("users.id"), nullable=False)
    team2_player2_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Scores
    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)
    
    # Match status
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="rounds")
    
    # Player relationships - simplified without back_populates
    team1_player1 = relationship("User", foreign_keys=[team1_player1_id])
    team1_player2 = relationship("User", foreign_keys=[team1_player2_id])
    team2_player1 = relationship("User", foreign_keys=[team2_player1_id])
    team2_player2 = relationship("User", foreign_keys=[team2_player2_id])

    def __repr__(self):
        return f"<Round(id={self.id}, tournament_id={self.tournament_id}, round_number={self.round_number})>"