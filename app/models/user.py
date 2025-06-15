from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)  # Google OAuth ID
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String)
    picture = Column(String)  # Profile picture URL
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    tournaments = relationship(
        "Tournament",
        secondary="tournament_player",
        back_populates="players"
    )
    created_tournaments = relationship("Tournament", back_populates="creator") 