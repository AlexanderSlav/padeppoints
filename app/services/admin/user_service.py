"""
Admin User Service

Handles user management operations for administrators including viewing,
updating, and deleting users with proper audit logging.
"""
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.user import User
from app.models.tournament import Tournament, tournament_player
from app.models.audit_log import ActionType, TargetType
from app.schemas.admin import (
    AdminUserDetail,
    UserActivityStats,
    AdminUserDetails,
    UserListResponse,
    UserStatusUpdate,
)
from app.services.admin.audit_service import AuditService


class AdminUserService:
    """Service for administrative user management operations."""

    def __init__(self, db: AsyncSession, audit_service: AuditService):
        """
        Initialize AdminUserService.

        Args:
            db: Database session
            audit_service: Audit logging service
        """
        self.db = db
        self.audit_service = audit_service

    async def get_users(
        self,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_superuser: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> UserListResponse:
        """
        Get paginated list of users with filtering.

        Args:
            search: Search term for name or email
            is_active: Filter by active status
            is_verified: Filter by verified status
            is_superuser: Filter by superuser status
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Paginated list of users
        """
        query = select(User)
        filters = []

        # Apply filters
        if search:
            search_term = f"%{search}%"
            filters.append(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term),
                )
            )
        if is_active is not None:
            filters.append(User.is_active == is_active)
        if is_verified is not None:
            filters.append(User.is_verified == is_verified)
        if is_superuser is not None:
            filters.append(User.is_superuser == is_superuser)

        if filters:
            query = query.filter(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(User)
        if filters:
            count_query = count_query.filter(and_(*filters))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(User.full_name).limit(limit).offset(offset)
        result = await self.db.execute(query)
        users = result.scalars().all()

        return UserListResponse(
            users=[AdminUserDetail.model_validate(user) for user in users],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_user_details(self, user_id: str) -> AdminUserDetails:
        """
        Get detailed information about a specific user.

        Args:
            user_id: User ID

        Returns:
            Detailed user information with statistics

        Raises:
            HTTPException: If user not found
        """
        # Get user
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Get user statistics
        # Tournaments created
        created_count_result = await self.db.execute(
            select(func.count())
            .select_from(Tournament)
            .filter(Tournament.created_by == user_id)
        )
        tournaments_created = created_count_result.scalar_one()

        # Tournaments played
        played_count_result = await self.db.execute(
            select(func.count())
            .select_from(tournament_player)
            .filter(tournament_player.c.player_id == user_id)
        )
        tournaments_played = played_count_result.scalar_one()

        # Matches played (approximate from rounds in tournaments)
        # This is a simplified count
        matches_played = tournaments_played * 5  # Rough estimate

        # Account age (if we had created_at field)
        account_age_days = 0  # Placeholder

        # Last activity (most recent tournament)
        last_tournament_result = await self.db.execute(
            select(Tournament.created_at)
            .select_from(Tournament)
            .join(tournament_player, Tournament.id == tournament_player.c.tournament_id)
            .filter(tournament_player.c.player_id == user_id)
            .order_by(Tournament.created_at.desc())
            .limit(1)
        )
        last_activity = last_tournament_result.scalar_one_or_none()

        statistics = UserActivityStats(
            tournaments_created=tournaments_created,
            tournaments_played=tournaments_played,
            matches_played=matches_played,
            account_age_days=account_age_days,
            last_activity=last_activity,
        )

        return AdminUserDetails(
            user=AdminUserDetail.model_validate(user),
            statistics=statistics,
        )

    async def update_user_status(
        self,
        user_id: str,
        updates: UserStatusUpdate,
        admin_id: str,
        ip_address: Optional[str] = None,
    ) -> AdminUserDetail:
        """
        Update user status fields.

        Args:
            user_id: User ID
            updates: Status updates to apply
            admin_id: ID of admin performing the update
            ip_address: IP address of admin

        Returns:
            Updated user

        Raises:
            HTTPException: If user not found
        """
        # Get user
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Store old values for audit
        old_values = {
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
        }

        # Apply updates
        if updates.is_active is not None:
            user.is_active = updates.is_active
        if updates.is_verified is not None:
            user.is_verified = updates.is_verified
        if updates.is_superuser is not None:
            user.is_superuser = updates.is_superuser

        # Store new values
        new_values = {
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "is_superuser": user.is_superuser,
        }

        await self.db.commit()
        await self.db.refresh(user)

        # Log to audit
        await self.audit_service.log_action(
            admin_id=admin_id,
            action_type=ActionType.USER_STATUS_CHANGE,
            target_type=TargetType.USER,
            target_id=user_id,
            details={
                "old_values": old_values,
                "new_values": new_values,
                "reason": updates.reason,
            },
            ip_address=ip_address,
        )

        return AdminUserDetail.model_validate(user)

    async def delete_user(
        self,
        user_id: str,
        admin_id: str,
        permanent: bool = False,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """
        Delete a user (soft or hard delete).

        Args:
            user_id: User ID
            admin_id: ID of admin performing the deletion
            permanent: If True, hard delete. Otherwise soft delete.
            reason: Reason for deletion
            ip_address: IP address of admin

        Raises:
            HTTPException: If user not found or is last superuser
        """
        # Get user
        result = await self.db.execute(select(User).filter(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        # Prevent deleting the last superuser
        if user.is_superuser:
            superuser_count_result = await self.db.execute(
                select(func.count())
                .select_from(User)
                .filter(User.is_superuser == True)
            )
            superuser_count = superuser_count_result.scalar_one()

            if superuser_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot delete the last superuser",
                )

        # Store user info for audit
        user_info = {
            "email": user.email,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
        }

        if permanent:
            # Hard delete - cascade will handle related records
            await self.db.delete(user)
        else:
            # Soft delete - just mark as inactive
            user.is_active = False

        await self.db.commit()

        # Log to audit
        await self.audit_service.log_action(
            admin_id=admin_id,
            action_type=ActionType.USER_DELETE,
            target_type=TargetType.USER,
            target_id=user_id,
            details={
                "permanent": permanent,
                "reason": reason,
                "user_info": user_info,
            },
            ip_address=ip_address,
        )

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID (helper method).

        Args:
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
