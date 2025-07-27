from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.round import Round

class RoundRepository(BaseRepository[Round]):
    def __init__(self, db: AsyncSession):
        super().__init__(Round, db)
    
    async def get_rounds_by_tournament(self, tournament_id: str) -> List[Round]:
        """Get all rounds for a specific tournament"""
        result = await self.db.execute(
            select(Round)
            .filter(Round.tournament_id == tournament_id)
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .order_by(Round.round_number)
        )
        return result.scalars().all()
    
    async def get_user_rounds_in_tournament(self, user_id: str, tournament_id: str) -> List[Round]:
        """Get all rounds where a user participated in a specific tournament"""
        result = await self.db.execute(
            select(Round)
            .filter(
                Round.tournament_id == tournament_id,
                or_(
                    Round.team1_player1_id == user_id,
                    Round.team1_player2_id == user_id,
                    Round.team2_player1_id == user_id,
                    Round.team2_player2_id == user_id
                )
            )
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .order_by(Round.round_number)
        )
        return result.scalars().all()
    
    async def get_user_rounds_all_tournaments(self, user_id: str) -> List[Round]:
        """Get all rounds where a user has ever participated"""
        result = await self.db.execute(
            select(Round)
            .filter(
                or_(
                    Round.team1_player1_id == user_id,
                    Round.team1_player2_id == user_id,
                    Round.team2_player1_id == user_id,
                    Round.team2_player2_id == user_id
                )
            )
            .options(
                selectinload(Round.tournament),
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .order_by(Round.tournament_id, Round.round_number)
        )
        return result.scalars().all()
    
    async def get_round_by_number(self, tournament_id: str, round_number: int) -> List[Round]:
        """Get all rounds for a specific round number in a tournament"""
        result = await self.db.execute(
            select(Round)
            .filter(
                Round.tournament_id == tournament_id,
                Round.round_number == round_number
            )
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
        )
        return result.scalars().all()
    
    async def get_completed_rounds(self, tournament_id: str) -> List[Round]:
        """Get all completed rounds for a tournament"""
        result = await self.db.execute(
            select(Round)
            .filter(
                Round.tournament_id == tournament_id,
                Round.is_completed == True
            )
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .order_by(Round.round_number)
        )
        return result.scalars().all()