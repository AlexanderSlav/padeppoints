from sqlalchemy import Column, String, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base


class Round(Base):
    __tablename__ = "rounds"
    
    id = Column(String, primary_key=True)
    tournament_id = Column(String, ForeignKey("tournament.id"), nullable=False)
    team1_player1_id = Column(String, ForeignKey("user.id"), nullable=False)
    team1_player2_id = Column(String, ForeignKey("user.id"), nullable=False)
    team2_player1_id = Column(String, ForeignKey("user.id"), nullable=False)
    team2_player2_id = Column(String, ForeignKey("user.id"), nullable=False)
    team1_score = Column(Integer, default=0)
    team2_score = Column(Integer, default=0)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="rounds")
    team1_player1 = relationship("User", foreign_keys=[team1_player1_id])
    team1_player2 = relationship("User", foreign_keys=[team1_player2_id])
    team2_player1 = relationship("User", foreign_keys=[team2_player1_id])
    team2_player2 = relationship("User", foreign_keys=[team2_player2_id]) 