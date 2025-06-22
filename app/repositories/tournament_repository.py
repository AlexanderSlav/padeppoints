from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.base import BaseRepository
from app.models.tournament import Tournament

class TournamentRepository(BaseRepository[Tournament]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tournament, db)
    
    async def get_by_status(self, status: str) -> List[Tournament]:
        result = await self.db.execute(select(Tournament).filter(Tournament.status == status))
        return result.scalars().all()
    
    async def get_by_creator(self, creator_id: str) -> List[Tournament]:
        result = await self.db.execute(select(Tournament).filter(Tournament.created_by == creator_id))
        return result.scalars().all()
    
    async def join_tournament(self, tournament_id: str, player_id: str) -> bool:
        tournament = await self.get_by_id(tournament_id)
        if not tournament:
            return False
            
        # Check if player is already in the tournament
        for player in tournament.players:
            if player.id == player_id:
                return False
        
        # In a real application, you would add the player to the many-to-many relationship
        # For now, this method signature is maintained but implementation would need
        # the User model to be passed or fetched
        await self.db.commit()
        return True
    
    async def get_tournament_players(self, tournament_id: str) -> List[str]:
        tournament = await self.get_by_id(tournament_id)
        if not tournament:
            return []
        return [player.id for player in tournament.players] 