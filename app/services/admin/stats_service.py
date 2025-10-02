"""
Admin Statistics Service

Provides analytics and statistics for the admin dashboard including user metrics,
tournament metrics, activity tracking, and growth data.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.tournament import Tournament, TournamentSystem, TournamentStatus
from app.models.round import Round
from app.schemas.admin import (
    OverviewStats,
    UserStatistics,
    TournamentStatistics,
    ActivityStatistics,
    SystemHealth,
    GrowthData,
    GrowthDataPoint,
    EngagementMetrics,
    TopUser,
)


class AdminStatsService:
    """Service for generating admin dashboard statistics and analytics."""

    def __init__(self, db: AsyncSession):
        """
        Initialize AdminStatsService.

        Args:
            db: Database session
        """
        self.db = db

    async def get_overview_stats(self) -> OverviewStats:
        """
        Get complete overview statistics for admin dashboard.

        Returns:
            Overview statistics including users, tournaments, activity, and system health
        """
        # Run all stat queries concurrently
        user_stats = await self._get_user_stats()
        tournament_stats = await self._get_tournament_stats()
        activity_stats = await self._get_activity_stats()
        system_health = await self._get_system_health()

        return OverviewStats(
            users=user_stats,
            tournaments=tournament_stats,
            activity=activity_stats,
            system=system_health,
        )

    async def _get_user_stats(self) -> UserStatistics:
        """Get user-related statistics."""
        # Total users
        total_result = await self.db.execute(select(func.count()).select_from(User))
        total = total_result.scalar_one()

        # Active vs inactive users
        active_result = await self.db.execute(
            select(func.count()).select_from(User).filter(User.is_active == True)
        )
        active = active_result.scalar_one()
        inactive = total - active

        # Verified vs unverified
        verified_result = await self.db.execute(
            select(func.count()).select_from(User).filter(User.is_verified == True)
        )
        verified = verified_result.scalar_one()
        unverified = total - verified

        # New users this week/month
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)

        # Note: User model doesn't have created_at field by default in fastapi-users
        # We'll return 0 for now, can be added later if needed
        new_this_week = 0
        new_this_month = 0

        return UserStatistics(
            total=total,
            active=active,
            inactive=inactive,
            verified=verified,
            unverified=unverified,
            new_this_week=new_this_week,
            new_this_month=new_this_month,
        )

    async def _get_tournament_stats(self) -> TournamentStatistics:
        """Get tournament-related statistics."""
        # Total tournaments
        total_result = await self.db.execute(select(func.count()).select_from(Tournament))
        total = total_result.scalar_one()

        # By status
        active_result = await self.db.execute(
            select(func.count())
            .select_from(Tournament)
            .filter(Tournament.status == TournamentStatus.ACTIVE.value)
        )
        active = active_result.scalar_one()

        pending_result = await self.db.execute(
            select(func.count())
            .select_from(Tournament)
            .filter(Tournament.status == TournamentStatus.PENDING.value)
        )
        pending = pending_result.scalar_one()

        completed_result = await self.db.execute(
            select(func.count())
            .select_from(Tournament)
            .filter(Tournament.status == TournamentStatus.COMPLETED.value)
        )
        completed = completed_result.scalar_one()

        # By format
        by_format_query = (
            select(Tournament.system, func.count())
            .group_by(Tournament.system)
        )
        result = await self.db.execute(by_format_query)
        by_format = {str(system.value): count for system, count in result.all()}

        return TournamentStatistics(
            total=total,
            active=active,
            pending=pending,
            completed=completed,
            by_format=by_format,
        )

    async def _get_activity_stats(self) -> ActivityStatistics:
        """Get activity metrics."""
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)

        # Matches today
        # Note: Round model represents rounds, need to count matches within rounds
        # For simplicity, we'll count rounds for now
        matches_today_result = await self.db.execute(
            select(func.count())
            .select_from(Round)
            .join(Tournament)
            .filter(Tournament.created_at >= today_start)
        )
        matches_today = matches_today_result.scalar_one()

        # Matches this week
        matches_week_result = await self.db.execute(
            select(func.count())
            .select_from(Round)
            .join(Tournament)
            .filter(Tournament.created_at >= week_ago)
        )
        matches_this_week = matches_week_result.scalar_one()

        # Average players per tournament
        # Query tournaments with player count using a subquery
        from app.models.tournament import tournament_player
        from sqlalchemy import literal_column

        # Use a subquery to count players per tournament, then average
        subquery = (
            select(
                Tournament.id,
                func.count(tournament_player.c.player_id).label('player_count')
            )
            .select_from(Tournament)
            .outerjoin(tournament_player, Tournament.id == tournament_player.c.tournament_id)
            .group_by(Tournament.id)
            .subquery()
        )

        avg_query = select(func.avg(subquery.c.player_count))
        avg_result = await self.db.execute(avg_query)
        avg_players = avg_result.scalar() or 0.0

        # Peak concurrent tournaments (tournaments active at the same time)
        # This is complex to calculate historically, we'll use current active count
        peak_result = await self.db.execute(
            select(func.count())
            .select_from(Tournament)
            .filter(Tournament.status == TournamentStatus.ACTIVE.value)
        )
        peak_concurrent = peak_result.scalar_one()

        return ActivityStatistics(
            matches_today=matches_today,
            matches_this_week=matches_this_week,
            avg_players_per_tournament=round(avg_players, 1),
            peak_concurrent_tournaments=peak_concurrent,
        )

    async def _get_system_health(self) -> SystemHealth:
        """Get system health information."""
        # Get total counts
        user_count = await self.db.execute(select(func.count()).select_from(User))
        total_users = user_count.scalar_one()

        tournament_count = await self.db.execute(select(func.count()).select_from(Tournament))
        total_tournaments = tournament_count.scalar_one()

        return SystemHealth(
            database_status="healthy",
            total_users=total_users,
            total_tournaments=total_tournaments,
            api_version="1.0.0",
        )

    async def get_user_growth(self, period: str = "daily") -> GrowthData:
        """
        Get user signup growth data.

        Args:
            period: Period for grouping (daily, weekly, monthly)

        Returns:
            Growth data for charts
        """
        # Note: User model doesn't have created_at by default
        # Returning empty data for now, can be implemented when field is added
        user_signups: List[GrowthDataPoint] = []
        tournament_creation: List[GrowthDataPoint] = []

        # Get tournament creation data (Tournament has created_at)
        now = datetime.utcnow()
        days_back = 30 if period == "daily" else 90

        for i in range(days_back, -1, -1):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)

            result = await self.db.execute(
                select(func.count())
                .select_from(Tournament)
                .filter(
                    and_(
                        Tournament.created_at >= date_start,
                        Tournament.created_at < date_end,
                    )
                )
            )
            count = result.scalar_one()

            tournament_creation.append(
                GrowthDataPoint(
                    date=date_start.strftime("%Y-%m-%d"),
                    count=count,
                )
            )

        return GrowthData(
            user_signups=user_signups,
            tournament_creation=tournament_creation,
            period=period,
        )

    async def get_engagement_metrics(self) -> EngagementMetrics:
        """
        Get user engagement metrics.

        Returns:
            Engagement metrics including top users and organizers
        """
        from app.models.tournament import tournament_player

        # Most active users (by tournaments played)
        most_active_query = (
            select(
                User.id,
                User.full_name,
                User.email,
                func.count(tournament_player.c.tournament_id).label("tournament_count"),
            )
            .select_from(User)
            .join(tournament_player, User.id == tournament_player.c.player_id)
            .group_by(User.id, User.full_name, User.email)
            .order_by(func.count(tournament_player.c.tournament_id).desc())
            .limit(10)
        )
        result = await self.db.execute(most_active_query)
        rows = result.all()

        most_active_users = [
            TopUser(
                user_id=row.id,
                full_name=row.full_name,
                email=row.email,
                tournaments_played=row.tournament_count,
                tournaments_created=0,  # Will fetch separately
            )
            for row in rows
        ]

        # Top organizers (by tournaments created)
        top_organizers_query = (
            select(
                User.id,
                User.full_name,
                User.email,
                func.count(Tournament.id).label("tournament_count"),
            )
            .select_from(User)
            .join(Tournament, User.id == Tournament.created_by)
            .group_by(User.id, User.full_name, User.email)
            .order_by(func.count(Tournament.id).desc())
            .limit(10)
        )
        result = await self.db.execute(top_organizers_query)
        rows = result.all()

        top_organizers = [
            TopUser(
                user_id=row.id,
                full_name=row.full_name,
                email=row.email,
                tournaments_played=0,  # Will fetch separately
                tournaments_created=row.tournament_count,
            )
            for row in rows
        ]

        # Average tournaments per user
        total_users = await self.db.execute(select(func.count()).select_from(User))
        user_count = total_users.scalar_one()

        total_participations = await self.db.execute(
            select(func.count()).select_from(tournament_player)
        )
        participation_count = total_participations.scalar_one()

        avg_tournaments_per_user = (
            round(participation_count / user_count, 2) if user_count > 0 else 0.0
        )

        # Retention rate (users who played in last 30 days / total active users)
        # Simplified version: percentage of users who have participated in tournaments
        users_with_tournaments = await self.db.execute(
            select(func.count(func.distinct(tournament_player.c.player_id)))
            .select_from(tournament_player)
        )
        active_player_count = users_with_tournaments.scalar_one()

        retention_rate = (
            round(active_player_count / user_count * 100, 1) if user_count > 0 else 0.0
        )

        return EngagementMetrics(
            most_active_users=most_active_users,
            top_organizers=top_organizers,
            avg_tournaments_per_user=avg_tournaments_per_user,
            retention_rate=retention_rate,
        )
