from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String)
    picture = Column(String)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

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