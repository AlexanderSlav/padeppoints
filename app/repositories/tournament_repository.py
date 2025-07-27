from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from app.repositories.base import BaseRepository
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.user import User

class TournamentRepository(BaseRepository[Tournament]):
    def __init__(self, db: AsyncSession):
        super().__init__(Tournament, db)
    
    async def get_by_status(self, status: str) -> List[Tournament]:
        result = await self.db.execute(select(Tournament).filter(Tournament.status == status))
        return result.scalars().all()
    
    async def get_by_creator(self, creator_id: str) -> List[Tournament]:
        result = await self.db.execute(select(Tournament).filter(Tournament.created_by == creator_id))
        return result.scalars().all()
    
    async def get_by_user(self, user_id: str) -> List[Tournament]:
        """Get tournaments created by the user"""
        result = await self.db.execute(select(Tournament).filter(Tournament.created_by == user_id))
        return result.scalars().all()
    
    async def join_tournament(self, tournament_id: str, player_id: str) -> dict:
        """
        Join a tournament with proper validation
        Returns dict with success status and message
        """
        # Get tournament with players loaded
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return {"success": False, "message": "Tournament not found"}
        
        # Check if tournament is still accepting players
        if tournament.status != TournamentStatus.PENDING.value:
            return {"success": False, "message": "Tournament is not accepting new players"}
        
        # Check if tournament is full
        current_players = len(tournament.players)
        if current_players >= tournament.max_players:
            return {"success": False, "message": "Tournament is full"}
            
        # Check if player is already in the tournament
        for player in tournament.players:
            if player.id == player_id:
                return {"success": False, "message": "Player is already in this tournament"}
        
        # Get the user/player
        user_result = await self.db.execute(select(User).filter(User.id == player_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        # Add player to tournament
        tournament.players.append(user)
        await self.db.commit()
        
        # Calculate player count before refresh to avoid relationship loading issues
        new_player_count = len(tournament.players)
        
        await self.db.refresh(tournament)
        
        return {
            "success": True, 
            "message": f"Successfully joined tournament '{tournament.name}'",
            "current_players": new_player_count,
            "max_players": tournament.max_players
        }
    
    async def leave_tournament(self, tournament_id: str, player_id: str) -> dict:
        """
        Leave a tournament with proper validation
        """
        # Get tournament with players loaded
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return {"success": False, "message": "Tournament not found"}
        
        # Check if tournament allows leaving (only pending tournaments)
        if tournament.status != TournamentStatus.PENDING.value:
            return {"success": False, "message": "Cannot leave tournament that has already started"}
        
        # Check if player is in the tournament
        player_to_remove = None
        for player in tournament.players:
            if player.id == player_id:
                player_to_remove = player
                break
        
        if not player_to_remove:
            return {"success": False, "message": "Player is not in this tournament"}
        
        # Remove player from tournament
        tournament.players.remove(player_to_remove)
        await self.db.commit()
        
        # Calculate player count before refresh to avoid relationship loading issues
        new_player_count = len(tournament.players)
        
        await self.db.refresh(tournament)
        
        return {
            "success": True, 
            "message": f"Successfully left tournament '{tournament.name}'",
            "current_players": new_player_count,
            "max_players": tournament.max_players
        }
    
    async def get_tournament_players(self, tournament_id: str) -> List[dict]:
        """Get tournament players with their details"""
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return []
        
        return [
            {
                "id": player.id,
                "full_name": player.full_name,
                "email": player.email
            }
            for player in tournament.players
        ]
    
    async def is_player_in_tournament(self, tournament_id: str, player_id: str) -> bool:
        """Check if a player is already in a tournament"""
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return False
        
        return any(player.id == player_id for player in tournament.players)
    
    async def get_tournament_with_player_count(self, tournament_id: str) -> Optional[dict]:
        """Get tournament with current player count and availability"""
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return None
        
        current_players = len(tournament.players)
        
        return {
            "tournament": tournament,
            "current_players": current_players,
            "max_players": tournament.max_players,
            "is_full": current_players >= tournament.max_players,
            "can_join": tournament.status == TournamentStatus.PENDING.value and current_players < tournament.max_players
        }
    
    async def get_all_tournaments(
        self,
        format: Optional[TournamentSystem] = None,
        status: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        location: Optional[str] = None,
        created_by: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Tournament]:
        """Get tournaments with filtering options"""
        query = select(Tournament)
        
        filters = []
        
        if format:
            filters.append(Tournament.system == format)
        
        if status:
            filters.append(Tournament.status == status)
            
        if start_date_from:
            filters.append(Tournament.start_date >= start_date_from)
            
        if start_date_to:
            filters.append(Tournament.start_date <= start_date_to)
            
        if location:
            filters.append(Tournament.location.ilike(f"%{location}%"))
            
        if created_by:
            filters.append(Tournament.created_by == created_by)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by start date (upcoming first, then by creation date)
        query = query.order_by(Tournament.start_date.asc(), Tournament.created_at.desc())
        
        # Apply pagination
        query = query.offset(offset).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def count_tournaments(
        self,
        format: Optional[TournamentSystem] = None,
        status: Optional[str] = None,
        start_date_from: Optional[date] = None,
        start_date_to: Optional[date] = None,
        location: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> int:
        """Count tournaments matching the filters"""
        query = select(Tournament)
        
        filters = []
        
        if format:
            filters.append(Tournament.system == format)
        
        if status:
            filters.append(Tournament.status == status)
            
        if start_date_from:
            filters.append(Tournament.start_date >= start_date_from)
            
        if start_date_to:
            filters.append(Tournament.start_date <= start_date_to)
            
        if location:
            filters.append(Tournament.location.ilike(f"%{location}%"))
            
        if created_by:
            filters.append(Tournament.created_by == created_by)
        
        if filters:
            query = query.filter(and_(*filters))
        
        count_query = select(func.count(Tournament.id)).select_from(query.subquery())
        result = await self.db.execute(count_query)
        return result.scalar()
    
    async def get_upcoming_tournaments(self, limit: int = 10) -> List[Tournament]:
        """Get upcoming tournaments (not yet started)"""
        query = select(Tournament).filter(
            and_(
                Tournament.start_date >= datetime.now().date(),
                Tournament.status.in_([TournamentStatus.PENDING.value, TournamentStatus.ACTIVE.value])
            )
        ).order_by(Tournament.start_date.asc()).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_tournaments_joined_by_user(self, user_id: str) -> List[Tournament]:
        """Get tournaments that the user has joined as a player"""
        query = select(Tournament).options(
            selectinload(Tournament.players)
        ).join(
            Tournament.players
        ).filter(
            User.id == user_id
        ).order_by(Tournament.start_date.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def add_player_to_tournament(self, tournament_id: str, player_id: str, organizer_id: str) -> dict:
        """
        Add a player to tournament (organizer only)
        """
        # Get tournament with players loaded
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return {"success": False, "message": "Tournament not found"}
        
        # Check if user is the tournament organizer
        if tournament.created_by != organizer_id:
            return {"success": False, "message": "Only tournament organizers can add players"}
        
        # Check if tournament is still accepting players
        if tournament.status != TournamentStatus.PENDING.value:
            return {"success": False, "message": "Cannot add players to tournament that has already started"}
        
        # Check if tournament is full
        current_players = len(tournament.players)
        if current_players >= tournament.max_players:
            return {"success": False, "message": "Tournament is full"}
        
        # Check if player is already in the tournament
        for player in tournament.players:
            if player.id == player_id:
                return {"success": False, "message": "Player is already in this tournament"}
        
        # Get the user/player
        user_result = await self.db.execute(select(User).filter(User.id == player_id))
        user = user_result.scalar_one_or_none()
        
        if not user:
            return {"success": False, "message": "Player not found"}
        
        # Add player to tournament
        tournament.players.append(user)
        await self.db.commit()
        
        # Calculate player count before refresh to avoid relationship loading issues
        new_player_count = len(tournament.players)
        
        await self.db.refresh(tournament)
        
        return {
            "success": True, 
            "message": f"Successfully added {user.full_name or user.email} to tournament '{tournament.name}'",
            "current_players": new_player_count,
            "max_players": tournament.max_players,
            "added_player": {
                "id": user.id,
                "full_name": user.full_name,
                "email": user.email
            }
        }
    
    async def remove_player_from_tournament(self, tournament_id: str, player_id: str, organizer_id: str) -> dict:
        """
        Remove a player from tournament (organizer only)
        """
        # Get tournament with players loaded
        result = await self.db.execute(
            select(Tournament)
            .options(selectinload(Tournament.players))
            .filter(Tournament.id == tournament_id)
        )
        tournament = result.scalar_one_or_none()
        
        if not tournament:
            return {"success": False, "message": "Tournament not found"}
        
        # Check if user is the tournament organizer
        if tournament.created_by != organizer_id:
            return {"success": False, "message": "Only tournament organizers can remove players"}
        
        # Check if tournament allows removing players (only pending tournaments)
        if tournament.status != TournamentStatus.PENDING.value:
            return {"success": False, "message": "Cannot remove players from tournament that has already started"}
        
        # Check if player is in the tournament
        player_to_remove = None
        for player in tournament.players:
            if player.id == player_id:
                player_to_remove = player
                break
        
        if not player_to_remove:
            return {"success": False, "message": "Player is not in this tournament"}
        
        # Remove player from tournament
        tournament.players.remove(player_to_remove)
        await self.db.commit()
        
        # Calculate player count before refresh to avoid relationship loading issues
        new_player_count = len(tournament.players)
        
        await self.db.refresh(tournament)
        
        return {
            "success": True, 
            "message": f"Successfully removed {player_to_remove.full_name or player_to_remove.email} from tournament '{tournament.name}'",
            "current_players": new_player_count,
            "max_players": tournament.max_players
        } 