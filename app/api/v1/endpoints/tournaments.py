from datetime import date
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import (
    get_current_user,
    get_tournament_as_organizer,
    get_tournament_for_user,
)
from app.db.base import get_db
from app.models.player_rating import PlayerRating
from app.models.round import Round
from app.models.tournament import (
    Tournament,
    TournamentStatus,
    TournamentSystem,
    tournament_player,
)
from app.models.user import User
from app.repositories.round_repository import RoundRepository
from app.repositories.tournament_repository import TournamentRepository
from app.schemas.round import MatchResultUpdate, RoundResponse
from app.schemas.tournament import (
    TournamentCreate,
    TournamentJoinResponse,
    TournamentListResponse,
    TournamentPlayerResponse,
    TournamentPlayersResponse,
    TournamentResponse,
    TournamentUpdate,
)
from app.services.americano_service import AmericanoTournamentService
from app.services.tournament_result_service import TournamentResultService
from app.services.tournament_service import TournamentService

router = APIRouter()


@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tournament"""
    tournament_data = {
        "id": str(uuid.uuid4()),
        "name": tournament.name,
        "description": tournament.description,
        "location": tournament.location,
        "start_date": tournament.start_date,
        "entry_fee": tournament.entry_fee,
        "max_players": tournament.max_players,
        "system": tournament.system,
        "points_per_match": tournament.points_per_match,
        "courts": tournament.courts,
        "created_by": current_user.id,
        "status": TournamentStatus.PENDING.value
    }
    
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.create(tournament_data)


@router.get("/", response_model=TournamentListResponse)
async def list_tournaments(
    format: Optional[TournamentSystem] = Query(None, description="Filter by tournament format"),
    status: Optional[str] = Query(None, description="Filter by tournament status (pending, active, completed)"),
    start_date_from: Optional[date] = Query(None, description="Filter tournaments starting from this date"),
    start_date_to: Optional[date] = Query(None, description="Filter tournaments starting until this date"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    created_by_me: Optional[bool] = Query(False, description="Show only tournaments created by current user"),
    min_avg_rating: Optional[float] = Query(None, ge=0, description="Minimum average player ELO rating"),
    max_avg_rating: Optional[float] = Query(None, ge=0, description="Maximum average player ELO rating"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of tournaments to return"),
    offset: int = Query(0, ge=0, description="Number of tournaments to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tournaments with filtering options"""
    tournament_repo = TournamentRepository(db)
    
    # Determine created_by filter
    created_by = current_user.id if created_by_me else None

    # Get tournaments and total count in a single efficient operation
    tournaments, total = await tournament_repo.get_tournaments_with_counts_and_total(
        format=format,
        status=status,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        location=location,
        created_by=created_by,
        min_avg_rating=min_avg_rating,
        max_avg_rating=max_avg_rating,
        limit=limit,
        offset=offset
    )
    
    return TournamentListResponse(tournaments=tournaments, total=total)

@router.get("/my", response_model=List[TournamentResponse])
async def list_my_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tournaments created by the current user"""
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.get_by_user(current_user.id)

@router.get("/joined", response_model=List[TournamentResponse])
async def list_joined_tournaments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List tournaments the current user has joined as a player"""
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.get_tournaments_joined_by_user(current_user.id)

@router.get("/upcoming", response_model=List[TournamentResponse])
async def list_upcoming_tournaments(
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tournaments to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List upcoming tournaments (not yet started)"""
    tournament_repo = TournamentRepository(db)
    return await tournament_repo.get_upcoming_tournaments(limit=limit)

@router.get("/formats")
async def get_tournament_formats():
    """Get available tournament formats"""
    return {
        "formats": [
            {"value": TournamentSystem.AMERICANO.value, "name": "Americano"},
            {"value": TournamentSystem.MEXICANO.value, "name": "Mexicano"},
        ]
    }

@router.get("/statuses")
async def get_tournament_statuses():
    """Get available tournament statuses"""
    return {
        "statuses": [
            {"value": TournamentStatus.PENDING.value, "name": "Pending"},
            {"value": TournamentStatus.ACTIVE.value, "name": "Active"},
            {"value": TournamentStatus.COMPLETED.value, "name": "Completed"},
        ]
    }


@router.get("/estimate-duration")
async def estimate_tournament_duration(
    players: int = Query(..., ge=4),
    courts: int = Query(1, ge=1),
    system: TournamentSystem = Query(TournamentSystem.AMERICANO),
    points_per_game: int = Query(21, ge=1),
    seconds_per_point: int = Query(25, ge=10),
    rest_seconds: int = Query(60, ge=0),
    current_user: User = Depends(get_current_user)
):
    """Estimate tournament duration for given settings."""
    if system != TournamentSystem.AMERICANO:
        raise HTTPException(status_code=400, detail="Only Americano supported")

    minutes, rounds = AmericanoTournamentService.estimate_duration(
        num_players=players, 
        courts=courts, 
        points_per_game=points_per_game,
        seconds_per_point=seconds_per_point,
        resting_between_matches_seconds=rest_seconds
    )
    return {
        "system": system.value,
        "players": players,
        "courts": courts,
        "points_per_game": points_per_game,
        "seconds_per_point": seconds_per_point,
        "rest_seconds": rest_seconds,
        "total_rounds": rounds,
        "estimated_minutes": minutes
    }

@router.get("/calculate-optimal-points")
async def calculate_optimal_points(
    players: int = Query(..., ge=4),
    courts: int = Query(1, ge=1),
    hours: float = Query(..., gt=0),
    seconds_per_point: int = Query(25, ge=10),
    rest_seconds: int = Query(60, ge=0),
    system: TournamentSystem = Query(TournamentSystem.AMERICANO),
    current_user: User = Depends(get_current_user)
):
    """Calculate optimal points per match based on time constraints."""
    if system != TournamentSystem.AMERICANO:
        raise HTTPException(status_code=400, detail="Only Americano supported")
    
    try:
        optimal_points = AmericanoTournamentService.calculate_optimal_points_per_match(
            num_players=players, 
            courts=courts, 
            available_hours=hours,
            seconds_per_point=seconds_per_point,
            resting_between_matches_seconds=rest_seconds
        )
        
        # Also calculate duration with these optimal points
        minutes, rounds = AmericanoTournamentService.estimate_duration(
            num_players=players, 
            courts=courts, 
            points_per_game=optimal_points,
            seconds_per_point=seconds_per_point,
            resting_between_matches_seconds=rest_seconds
        )
        
        return {
            "system": system.value,
            "players": players,
            "courts": courts,
            "hours": hours,
            "seconds_per_point": seconds_per_point,
            "rest_seconds": rest_seconds,
            "optimal_points_per_match": optimal_points,
            "total_rounds": rounds,
            "estimated_minutes": minutes
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tournament-planning-advice")
async def get_tournament_planning_advice(
    players: int = Query(..., ge=4),
    courts: int = Query(1, ge=1),
    hours: float = Query(..., gt=0),
    points_per_match: Optional[int] = Query(None, ge=1),
    seconds_per_point: int = Query(25, ge=10),
    rest_seconds: int = Query(60, ge=0),
    system: TournamentSystem = Query(TournamentSystem.AMERICANO),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive tournament planning advice with all calculations done backend."""
    if system != TournamentSystem.AMERICANO:
        raise HTTPException(status_code=400, detail="Only Americano format is currently supported")
    
    if players % 4 != 0:
        raise HTTPException(
            status_code=400, 
            detail="Number of players must be divisible by 4 for Americano format"
        )
    
    try:
        # If points not specified, calculate optimal
        if points_per_match is None:
            points_per_match = AmericanoTournamentService.calculate_optimal_points_per_match(
                num_players=players,
                courts=courts,
                available_hours=hours,
                seconds_per_point=seconds_per_point,
                resting_between_matches_seconds=rest_seconds
            )
            was_calculated = True
        else:
            was_calculated = False
        
        # Calculate duration with chosen points
        estimated_minutes, total_rounds = AmericanoTournamentService.estimate_duration(
            num_players=players,
            courts=courts,
            points_per_game=points_per_match,
            seconds_per_point=seconds_per_point,
            resting_between_matches_seconds=rest_seconds
        )
        
        # Calculate tournament metrics
        available_minutes = hours * 60
        matches_per_round = players // 4  # Always players/4, courts only affect scheduling
        total_matches = total_rounds * matches_per_round
        
        # Calculate completable rounds
        if estimated_minutes <= available_minutes:
            # Can complete all rounds
            completable_rounds = total_rounds
            actual_time_used = estimated_minutes
            efficiency = round((estimated_minutes / available_minutes) * 100)
            status = "complete"
        else:
            # Can only complete partial rounds
            minutes_per_round = estimated_minutes / total_rounds
            completable_rounds = int(available_minutes / minutes_per_round)
            actual_time_used = available_minutes
            efficiency = 100  # Using all available time
            status = "partial"
        
        # Calculate total points
        total_points = completable_rounds * matches_per_round * points_per_match
        
        # Generate recommendation message
        if status == "complete":
            recommendation = (
                f"✅ Perfect! You can complete all {total_rounds} rounds "
                f"in {hours} hours with {courts} courts."
            )
            if was_calculated:
                recommendation += f" Maximum points per match: {points_per_match}"
        else:
            # Calculate precise time needed
            hours_needed = estimated_minutes / 60
            hours_int = int(hours_needed)
            minutes_remainder = int((hours_needed - hours_int) * 60)
            
            if minutes_remainder > 0:
                time_needed_str = f"{hours_int}h {minutes_remainder}m"
            else:
                time_needed_str = f"{hours_int} hours"
            
            recommendation = (
                f"⚠️ You can complete {completable_rounds} of {total_rounds} rounds "
                f"in {hours} hours. "
                f"Need {time_needed_str} for full tournament."
            )
            if was_calculated:
                recommendation += f" Maximum points per match: {points_per_match}"
        
        return {
            "system": system.value,
            "input": {
                "players": players,
                "courts": courts,
                "available_hours": hours,
                "seconds_per_point": seconds_per_point,
                "rest_seconds": rest_seconds,
                "points_per_match": points_per_match,
                "was_calculated": was_calculated
            },
            "tournament_structure": {
                "total_rounds": total_rounds,
                "matches_per_round": matches_per_round,
                "total_matches": total_matches,
                "completable_rounds": completable_rounds,
                "completable_matches": completable_rounds * matches_per_round
            },
            "time_analysis": {
                "estimated_total_minutes": round(estimated_minutes, 1),
                "available_minutes": available_minutes,
                "actual_time_used": round(actual_time_used, 1),
                "minutes_per_round": round(estimated_minutes / total_rounds, 1),
                "efficiency_percentage": efficiency,
                "status": status
            },
            "points_analysis": {
                "points_per_match": points_per_match,
                "total_possible_points": total_rounds * matches_per_round * points_per_match,
                "achievable_points": total_points
            },
            "recommendation": recommendation
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(
    tournament: Tournament = Depends(get_tournament_for_user)
):
    """Get tournament details"""
    return tournament


@router.post("/{tournament_id}/join", response_model=TournamentJoinResponse)
async def join_tournament(
    tournament: Tournament = Depends(get_tournament_for_user),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Join a tournament"""
    tournament_repo = TournamentRepository(db)
    
    result = await tournament_repo.join_tournament(tournament.id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return TournamentJoinResponse(**result)

@router.post("/{tournament_id}/leave", response_model=TournamentJoinResponse)
async def leave_tournament(
    tournament: Tournament = Depends(get_tournament_for_user),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Leave a tournament"""
    tournament_repo = TournamentRepository(db)
    
    result = await tournament_repo.leave_tournament(tournament.id, current_user.id)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return TournamentJoinResponse(**result)

@router.get("/{tournament_id}/players", response_model=TournamentPlayersResponse)
async def get_tournament_players(
    tournament: Tournament = Depends(get_tournament_for_user),
    db: AsyncSession = Depends(get_db)
):
    """Get players in a tournament with availability info"""
    tournament_repo = TournamentRepository(db)
    
    # Get tournament with player count info
    tournament_info = await tournament_repo.get_tournament_with_player_count(tournament.id)
    if not tournament_info:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Get players list
    players = await tournament_repo.get_tournament_players(tournament.id)
    
    return TournamentPlayersResponse(
        tournament_id=tournament.id,
        tournament_name=tournament_info["tournament"].name,
        current_players=tournament_info["current_players"],
        max_players=tournament_info["max_players"],
        is_full=tournament_info["is_full"],
        can_join=tournament_info["can_join"],
        players=[TournamentPlayerResponse(**player) for player in players]
    )

@router.get("/{tournament_id}/can-join")
async def can_join_tournament(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if current user can join a tournament"""
    tournament_repo = TournamentRepository(db)
    
    # Check if tournament exists and get info
    tournament_info = await tournament_repo.get_tournament_with_player_count(tournament_id)
    if not tournament_info:
        raise HTTPException(status_code=404, detail="Tournament not found")
    
    # Check if user is already in tournament
    is_already_joined = await tournament_repo.is_player_in_tournament(tournament_id, current_user.id)
    
    return {
        "can_join": tournament_info["can_join"] and not is_already_joined,
        "is_already_joined": is_already_joined,
        "is_full": tournament_info["is_full"],
        "current_players": tournament_info["current_players"],
        "max_players": tournament_info["max_players"],
        "tournament_status": tournament_info["tournament"].status,
        "reason": (
            "Already joined" if is_already_joined else
            "Tournament is full" if tournament_info["is_full"] else
            "Tournament has already started" if tournament_info["tournament"].status != TournamentStatus.PENDING.value else
            "Can join"
        )
    }

@router.post("/{tournament_id}/add-player")
async def add_player_to_tournament(
    player_data: dict,  # Expected format: {"player_id": "user-id"}
    tournament: Tournament = Depends(get_tournament_as_organizer),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a player to tournament (organizer only)"""
    tournament_repo = TournamentRepository(db)
    
    player_id = player_data.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="player_id is required")
    
    result = await tournament_repo.add_player_to_tournament(
        tournament.id, player_id, current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@router.post("/{tournament_id}/remove-player")
async def remove_player_from_tournament(
    player_data: dict,  # Expected format: {"player_id": "user-id"}
    tournament: Tournament = Depends(get_tournament_as_organizer),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a player from tournament (organizer only)"""
    tournament_repo = TournamentRepository(db)
    
    player_id = player_data.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="player_id is required")
    
    result = await tournament_repo.remove_player_from_tournament(
        tournament.id, player_id, current_user.id
    )
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result


@router.post("/{tournament_id}/start", response_model=TournamentResponse)
async def start_tournament(
    tournament: Tournament = Depends(get_tournament_as_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Start a tournament by generating all rounds."""
    logger.info(f"Starting tournament {tournament.id} by user")
    
    try:
        # Validate tournament state before starting
        if tournament.status != TournamentStatus.PENDING.value:
            logger.warning(f"Attempt to start tournament {tournament.id} with status {tournament.status}")
            raise HTTPException(
                status_code=400, 
                detail=f"Tournament cannot be started. Current status: {tournament.status}"
            )
        
        # Check if tournament has enough players
        tournament_repo = TournamentRepository(db)
        tournament_info = await tournament_repo.get_tournament_with_player_count(tournament.id)
        
        if not tournament_info:
            logger.error(f"Tournament {tournament.id} not found in database")
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        current_players = tournament_info.get("current_players", 0)
        if current_players < 4:  # Minimum players for a tournament
            logger.warning(f"Tournament {tournament.id} has insufficient players: {current_players}")
            raise HTTPException(
                status_code=400,
                detail=f"Cannot start tournament with {current_players} players. Minimum 4 players required."
            )

        # Calculate average player rating before starting
        # Get all players with their ratings
        players_result = await db.execute(
            select(User, PlayerRating.current_rating)
            .join(tournament_player, User.id == tournament_player.c.player_id)
            .outerjoin(PlayerRating, User.id == PlayerRating.user_id)
            .filter(tournament_player.c.tournament_id == tournament.id)
        )
        players_with_ratings = players_result.all()

        if players_with_ratings:
            # Calculate average rating (default to 1000 if player has no rating)
            total_rating = sum(rating if rating else 1000.0 for _, rating in players_with_ratings)
            average_rating = total_rating / len(players_with_ratings)
            tournament.average_player_rating = average_rating
            await db.commit()
            logger.info(f"Calculated average player rating for tournament {tournament.id}: {average_rating:.2f}")

        # Initialize tournament service
        tournament_service = TournamentService(db)
        logger.info(f"Initializing tournament service for tournament {tournament.id}")
        
        # Start the tournament
        started_tournament = await tournament_service.start_tournament(tournament.id)
        logger.info(f"Successfully started tournament {tournament.id}")
        
        return started_tournament
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValueError as e:
        logger.error(f"Validation error starting tournament {tournament.id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error starting tournament {tournament.id}: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while starting the tournament"
        )

@router.get("/{tournament_id}/matches/current")
async def get_current_round_matches(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all matches for the current round of a tournament."""
    tournament_service = TournamentService(db)
    
    try:
        # Get matches with player relationships loaded
        result = await db.execute(
            select(Round)
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .join(Tournament, Round.tournament_id == Tournament.id)
            .filter(Tournament.id == tournament_id)
            .filter(Round.round_number == Tournament.current_round)
        )
        matches = result.scalars().all()
        
        # Convert to response format with player details
        response_matches = []
        for match in matches:
            response_matches.append({
                "id": match.id,
                "tournament_id": match.tournament_id,
                "round_number": match.round_number,
                "team1_player1": {
                    "id": match.team1_player1.id,
                    "full_name": match.team1_player1.full_name,
                    "email": match.team1_player1.email,
                },
                "team1_player2": {
                    "id": match.team1_player2.id,
                    "full_name": match.team1_player2.full_name,
                    "email": match.team1_player2.email,
                },
                "team2_player1": {
                    "id": match.team2_player1.id,
                    "full_name": match.team2_player1.full_name,
                    "email": match.team2_player1.email,
                },
                "team2_player2": {
                    "id": match.team2_player2.id,
                    "full_name": match.team2_player2.full_name,
                    "email": match.team2_player2.email,
                },
                "team1_score": match.team1_score,
                "team2_score": match.team2_score,
                "is_completed": match.is_completed
            })
        
        return response_matches
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/matches/{match_id}/result")
async def record_match_result(
    match_id: str,
    result: MatchResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record the result of a match."""
    tournament_service = TournamentService(db)
    
    try:
        match = await tournament_service.record_match_result(
            match_id, result.team1_score, result.team2_score
        )
        return {
            "message": "Match result recorded successfully",
            "match_id": match.id,
            "team1_score": match.team1_score,
            "team2_score": match.team2_score
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{tournament_id}/leaderboard")
async def get_tournament_leaderboard(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tournament leaderboard with current scores."""
    tournament_service = TournamentService(db)
    
    try:
        result = await db.execute(select(Tournament).filter(Tournament.id == tournament_id))
        tournament = result.scalar_one_or_none()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        leaderboard_data = await tournament_service.get_tournament_leaderboard(tournament_id)
        winner_data = await tournament_service.get_tournament_winner(tournament_id)
        
        return {
            "tournament_id": tournament_id,
            "tournament_name": tournament.name,
            "entries": leaderboard_data,
            "is_completed": tournament.status == TournamentStatus.COMPLETED.value,
            "winner": winner_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{tournament_id}/scores")
async def get_player_scores(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current player scores for a tournament."""
    tournament_service = TournamentService(db)
    
    try:
        scores = await tournament_service.get_player_scores(tournament_id)
        return {"tournament_id": tournament_id, "scores": scores}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{tournament_id}/rounds")
async def get_all_rounds(
    tournament_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all scheduled rounds for a tournament."""
    try:
        # Check if tournament exists first
        tournament_result = await db.execute(
            select(Tournament).filter(Tournament.id == tournament_id)
        )
        tournament = tournament_result.scalar_one_or_none()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")
        
        # If tournament hasn't started yet, return empty list
        if tournament.status == TournamentStatus.PENDING.value:
            return []
        
        # Try to get rounds with player relationships loaded
        rounds_result = await db.execute(
            select(Round)
            .options(
                selectinload(Round.team1_player1),
                selectinload(Round.team1_player2),
                selectinload(Round.team2_player1),
                selectinload(Round.team2_player2)
            )
            .filter(Round.tournament_id == tournament_id)
            .order_by(Round.round_number)
        )
        rounds = rounds_result.scalars().all()
        
        # Convert to dict format with player information
        rounds_data = []
        for round in rounds:
            rounds_data.append({
                "id": round.id,
                "tournament_id": round.tournament_id,
                "round_number": round.round_number,
                "team1_player1": {
                    "id": round.team1_player1.id,
                    "full_name": round.team1_player1.full_name,
                    "email": round.team1_player1.email,
                } if round.team1_player1 else None,
                "team1_player2": {
                    "id": round.team1_player2.id,
                    "full_name": round.team1_player2.full_name,
                    "email": round.team1_player2.email,
                } if round.team1_player2 else None,
                "team2_player1": {
                    "id": round.team2_player1.id,
                    "full_name": round.team2_player1.full_name,
                    "email": round.team2_player1.email,
                } if round.team2_player1 else None,
                "team2_player2": {
                    "id": round.team2_player2.id,
                    "full_name": round.team2_player2.full_name,
                    "email": round.team2_player2.email,
                } if round.team2_player2 else None,
                "team1_score": round.team1_score,
                "team2_score": round.team2_score,
                "is_completed": round.is_completed
            })
        
        return rounds_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_all_rounds: {str(e)}")
        # Return empty list instead of crashing
        return []


@router.post("/{tournament_id}/finish", response_model=TournamentResponse)
async def finish_tournament(
    tournament: Tournament = Depends(get_tournament_as_organizer),
    db: AsyncSession = Depends(get_db)
):
    """Finish/complete a tournament by setting status to completed."""
    logger.info(f"Finishing tournament {tournament.id}")

    try:
        # Validate tournament state before finishing
        if tournament.status != TournamentStatus.ACTIVE.value:
            logger.warning(f"Attempt to finish tournament {tournament.id} with status {tournament.status}")
            raise HTTPException(
                status_code=400,
                detail=f"Tournament cannot be finished. Current status: {tournament.status}. Only active tournaments can be finished."
            )

        # Update tournament status to completed
        tournament.status = TournamentStatus.COMPLETED.value
        await db.commit()
        await db.refresh(tournament)

        # Store final tournament results
        try:
            result_service = TournamentResultService(db)
            await result_service.calculate_and_store_final_results(tournament.id)
            logger.info(f"Successfully stored final results for tournament {tournament.id}")
        except Exception as result_error:
            # Log error but don't fail the tournament completion
            logger.error(f"Failed to store tournament results for {tournament.id}: {str(result_error)}")

        logger.info(f"Successfully finished tournament {tournament.id}")
        return tournament
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error finishing tournament {tournament.id}: {str(e)}")
        logger.exception("Full exception details:")
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred while finishing the tournament"
        )


