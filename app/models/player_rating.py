"""Player rating model for ELO tracking."""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base
import uuid


class PlayerRating(Base):
    """Player ELO rating and statistics."""
    __tablename__ = "player_ratings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    
    # ELO Rating
    current_rating = Column(Float, default=1000.0, nullable=False)
    peak_rating = Column(Float, default=1000.0, nullable=False)
    lowest_rating = Column(Float, default=1000.0, nullable=False)
    
    # Statistics
    matches_played = Column(Integer, default=0, nullable=False)
    matches_won = Column(Integer, default=0, nullable=False)
    total_points_scored = Column(Integer, default=0, nullable=False)
    total_points_possible = Column(Integer, default=0, nullable=False)
    tournaments_played = Column(Integer, default=0, nullable=False)
    
    # Podium finishes
    first_place_finishes = Column(Integer, default=0, nullable=False)
    second_place_finishes = Column(Integer, default=0, nullable=False)
    third_place_finishes = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="rating")
    rating_history = relationship("RatingHistory", back_populates="player_rating", cascade="all, delete-orphan")
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.matches_played == 0:
            return 0.0
        return (self.matches_won / self.matches_played) * 100
    
    @property
    def average_point_percentage(self) -> float:
        """Calculate average point scoring percentage."""
        if self.total_points_possible == 0:
            return 0.0
        return (self.total_points_scored / self.total_points_possible) * 100
    
    @property
    def podium_count(self) -> int:
        """Total podium finishes."""
        return self.first_place_finishes + self.second_place_finishes + self.third_place_finishes


class RatingHistory(Base):
    """Track rating changes over time."""
    __tablename__ = "rating_history"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    player_rating_id = Column(String, ForeignKey("player_ratings.id"), nullable=False)
    tournament_id = Column(String, ForeignKey("tournaments.id"), nullable=True)
    match_id = Column(String, ForeignKey("rounds.id"), nullable=True)
    
    # Rating change
    old_rating = Column(Float, nullable=False)
    new_rating = Column(Float, nullable=False)
    rating_change = Column(Float, nullable=False)
    
    # Match details for context
    opponent_ratings = Column(Text, nullable=True)  # JSON string of opponent ratings
    match_result = Column(String, nullable=True)  # "win", "loss", or points ratio
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    player_rating = relationship("PlayerRating", back_populates="rating_history")