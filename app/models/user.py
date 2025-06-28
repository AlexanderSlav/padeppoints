from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Google OAuth ID
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    picture = Column(String)  # Profile picture URL
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Many-to-many relationship with tournaments
    tournaments = relationship(
        "Tournament",
        secondary="tournament_player",  # Use string reference to avoid circular import
        back_populates="players"
    )
    
    # One-to-many relationship for created tournaments
    created_tournaments = relationship(
        "Tournament", 
        back_populates="creator", 
        foreign_keys="Tournament.created_by"
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"