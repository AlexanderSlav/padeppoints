"""
Audit Service

Handles audit logging for all administrative actions. Records who did what,
when, and provides querying capabilities for audit trail review.
"""
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.models.audit_log import AuditLog, ActionType, TargetType
from app.models.user import User
from app.schemas.admin import (
    AuditLogResponse,
    AuditLogListResponse,
    AuditStatsResponse,
)


class AuditService:
    """Service for audit logging and audit trail management."""

    def __init__(self, db: AsyncSession):
        """
        Initialize AuditService.

        Args:
            db: Database session
        """
        self.db = db

    async def log_action(
        self,
        admin_id: str,
        action_type: ActionType,
        target_type: TargetType,
        target_id: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
    ) -> AuditLog:
        """
        Log an administrative action.

        Args:
            admin_id: ID of the admin user performing the action
            action_type: Type of action (from ActionType enum)
            target_type: Type of target entity (from TargetType enum)
            target_id: ID of the target entity
            details: Additional details (old/new values, reason, etc.)
            ip_address: IP address of the admin

        Returns:
            Created AuditLog entry
        """
        audit_log = AuditLog(
            admin_id=admin_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address,
        )

        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)

        return audit_log

    async def get_audit_logs(
        self,
        admin_id: Optional[str] = None,
        action_type: Optional[ActionType] = None,
        target_type: Optional[TargetType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> AuditLogListResponse:
        """
        Retrieve audit logs with filtering and pagination.

        Args:
            admin_id: Filter by admin user ID
            action_type: Filter by action type
            target_type: Filter by target type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            Paginated list of audit logs
        """
        # Build query with filters
        query = select(AuditLog)
        filters = []

        if admin_id:
            filters.append(AuditLog.admin_id == admin_id)
        if action_type:
            filters.append(AuditLog.action_type == action_type)
        if target_type:
            filters.append(AuditLog.target_type == target_type)
        if start_date:
            filters.append(AuditLog.timestamp >= start_date)
        if end_date:
            filters.append(AuditLog.timestamp <= end_date)

        if filters:
            query = query.filter(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(AuditLog)
        if filters:
            count_query = count_query.filter(and_(*filters))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()

        # Get paginated results
        query = query.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        logs = result.scalars().all()

        # Fetch admin names for the logs
        admin_ids = {log.admin_id for log in logs if log.admin_id}
        admin_names = {}
        if admin_ids:
            admin_query = select(User).filter(User.id.in_(admin_ids))
            admin_result = await self.db.execute(admin_query)
            admins = admin_result.scalars().all()
            admin_names = {admin.id: admin.full_name for admin in admins}

        # Convert to response schema
        log_responses = [
            AuditLogResponse(
                id=log.id,
                admin_id=log.admin_id,
                admin_name=admin_names.get(log.admin_id),
                action_type=log.action_type,
                target_type=log.target_type,
                target_id=log.target_id,
                details=log.details,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
            )
            for log in logs
        ]

        return AuditLogListResponse(
            logs=log_responses,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_audit_stats(self) -> AuditStatsResponse:
        """
        Get audit log statistics.

        Returns:
            Statistics about audit logs
        """
        # Total actions
        total_result = await self.db.execute(select(func.count()).select_from(AuditLog))
        total_actions = total_result.scalar_one()

        # Actions by type
        actions_by_type_query = (
            select(AuditLog.action_type, func.count())
            .group_by(AuditLog.action_type)
        )
        result = await self.db.execute(actions_by_type_query)
        actions_by_type = {str(action_type.value): count for action_type, count in result.all()}

        # Actions by admin
        actions_by_admin_query = (
            select(AuditLog.admin_id, func.count())
            .filter(AuditLog.admin_id.isnot(None))
            .group_by(AuditLog.admin_id)
        )
        result = await self.db.execute(actions_by_admin_query)
        admin_action_counts = result.all()

        # Get admin names
        admin_ids = [admin_id for admin_id, _ in admin_action_counts]
        admin_names = {}
        if admin_ids:
            admin_query = select(User).filter(User.id.in_(admin_ids))
            admin_result = await self.db.execute(admin_query)
            admins = admin_result.scalars().all()
            admin_names = {admin.id: admin.full_name or admin.email or admin.id for admin in admins}

        actions_by_admin = {
            admin_names.get(admin_id, admin_id): count
            for admin_id, count in admin_action_counts
        }

        # Recent critical actions (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(hours=24)
        critical_actions = [
            ActionType.USER_DELETE,
            ActionType.TOURNAMENT_DELETE,
        ]
        recent_critical_query = (
            select(func.count())
            .select_from(AuditLog)
            .filter(
                and_(
                    AuditLog.timestamp >= yesterday,
                    AuditLog.action_type.in_(critical_actions),
                )
            )
        )
        result = await self.db.execute(recent_critical_query)
        recent_critical_actions = result.scalar_one()

        return AuditStatsResponse(
            total_actions=total_actions,
            actions_by_type=actions_by_type,
            actions_by_admin=actions_by_admin,
            recent_critical_actions=recent_critical_actions,
        )

    async def get_target_history(
        self,
        target_type: TargetType,
        target_id: str,
    ) -> List[AuditLogResponse]:
        """
        Get complete history of actions for a specific target.

        Args:
            target_type: Type of target entity
            target_id: ID of target entity

        Returns:
            List of audit logs for the target
        """
        query = (
            select(AuditLog)
            .filter(
                and_(
                    AuditLog.target_type == target_type,
                    AuditLog.target_id == target_id,
                )
            )
            .order_by(AuditLog.timestamp.desc())
        )

        result = await self.db.execute(query)
        logs = result.scalars().all()

        # Fetch admin names
        admin_ids = {log.admin_id for log in logs if log.admin_id}
        admin_names = {}
        if admin_ids:
            admin_query = select(User).filter(User.id.in_(admin_ids))
            admin_result = await self.db.execute(admin_query)
            admins = admin_result.scalars().all()
            admin_names = {admin.id: admin.full_name for admin in admins}

        return [
            AuditLogResponse(
                id=log.id,
                admin_id=log.admin_id,
                admin_name=admin_names.get(log.admin_id),
                action_type=log.action_type,
                target_type=log.target_type,
                target_id=log.target_id,
                details=log.details,
                ip_address=log.ip_address,
                timestamp=log.timestamp,
            )
            for log in logs
        ]
