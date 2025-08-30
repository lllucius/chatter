"""Tool access control service for role-based permissions."""

import re
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.toolserver import (
    RoleToolAccess,
    ServerTool,
    ToolAccessLevel,
    ToolPermission,
    ToolServer,
    UserRole,
)
from chatter.models.user import User
from chatter.schemas.toolserver import (
    RoleToolAccessCreate,
    RoleToolAccessResponse,
    ToolAccessResult,
    ToolPermissionCreate,
    ToolPermissionResponse,
    ToolPermissionUpdate,
    UserToolAccessCheck,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ToolAccessServiceError(Exception):
    """Tool access service error."""

    pass


class ToolAccessService:
    """Service for managing tool access permissions and role-based access control."""

    def __init__(self, session: AsyncSession):
        """Initialize tool access service.

        Args:
            session: Database session
        """
        self.session = session

    # Permission management methods

    async def grant_tool_permission(
        self, 
        permission_data: ToolPermissionCreate,
        granted_by: str,
    ) -> ToolPermissionResponse:
        """Grant tool permission to a user.

        Args:
            permission_data: Permission data
            granted_by: ID of user granting permission

        Returns:
            Created permission response
        """
        # Validate that either tool_id or server_id is provided
        if not permission_data.tool_id and not permission_data.server_id:
            raise ToolAccessServiceError("Either tool_id or server_id must be provided")

        if permission_data.tool_id and permission_data.server_id:
            raise ToolAccessServiceError("Cannot specify both tool_id and server_id")

        # Check if permission already exists
        existing = await self._get_existing_permission(
            permission_data.user_id, 
            permission_data.tool_id, 
            permission_data.server_id
        )
        
        if existing:
            raise ToolAccessServiceError("Permission already exists")

        # Create permission
        permission = ToolPermission(
            user_id=permission_data.user_id,
            tool_id=permission_data.tool_id,
            server_id=permission_data.server_id,
            access_level=permission_data.access_level,
            rate_limit_per_hour=permission_data.rate_limit_per_hour,
            rate_limit_per_day=permission_data.rate_limit_per_day,
            allowed_hours=permission_data.allowed_hours,
            allowed_days=permission_data.allowed_days,
            expires_at=permission_data.expires_at,
            granted_by=granted_by,
        )

        self.session.add(permission)
        await self.session.commit()
        await self.session.refresh(permission)

        logger.info(
            "Tool permission granted",
            user_id=permission_data.user_id,
            tool_id=permission_data.tool_id,
            server_id=permission_data.server_id,
            access_level=permission_data.access_level.value,
        )

        return ToolPermissionResponse.model_validate(permission)

    async def update_tool_permission(
        self,
        permission_id: str,
        update_data: ToolPermissionUpdate,
    ) -> ToolPermissionResponse:
        """Update tool permission.

        Args:
            permission_id: Permission ID
            update_data: Update data

        Returns:
            Updated permission response
        """
        permission = await self._get_permission_by_id(permission_id)
        if not permission:
            raise ToolAccessServiceError("Permission not found")

        # Update fields if provided
        if update_data.access_level is not None:
            permission.access_level = update_data.access_level
        if update_data.rate_limit_per_hour is not None:
            permission.rate_limit_per_hour = update_data.rate_limit_per_hour
        if update_data.rate_limit_per_day is not None:
            permission.rate_limit_per_day = update_data.rate_limit_per_day
        if update_data.allowed_hours is not None:
            permission.allowed_hours = update_data.allowed_hours
        if update_data.allowed_days is not None:
            permission.allowed_days = update_data.allowed_days
        if update_data.expires_at is not None:
            permission.expires_at = update_data.expires_at

        permission.updated_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(permission)

        return ToolPermissionResponse.model_validate(permission)

    async def revoke_tool_permission(self, permission_id: str) -> bool:
        """Revoke tool permission.

        Args:
            permission_id: Permission ID

        Returns:
            True if revoked successfully
        """
        permission = await self._get_permission_by_id(permission_id)
        if not permission:
            return False

        await self.session.delete(permission)
        await self.session.commit()

        logger.info("Tool permission revoked", permission_id=permission_id)
        return True

    async def get_user_permissions(
        self, user_id: str
    ) -> list[ToolPermissionResponse]:
        """Get all permissions for a user.

        Args:
            user_id: User ID

        Returns:
            List of user permissions
        """
        result = await self.session.execute(
            select(ToolPermission).where(
                ToolPermission.user_id == user_id
            )
        )
        permissions = result.scalars().all()

        return [
            ToolPermissionResponse.model_validate(p) for p in permissions
        ]

    # Role-based access methods

    async def create_role_access_rule(
        self,
        rule_data: RoleToolAccessCreate,
        created_by: str,
    ) -> RoleToolAccessResponse:
        """Create role-based access rule.

        Args:
            rule_data: Rule data
            created_by: ID of user creating rule

        Returns:
            Created rule response
        """
        rule = RoleToolAccess(
            role=rule_data.role,
            tool_pattern=rule_data.tool_pattern,
            server_pattern=rule_data.server_pattern,
            access_level=rule_data.access_level,
            default_rate_limit_per_hour=rule_data.default_rate_limit_per_hour,
            default_rate_limit_per_day=rule_data.default_rate_limit_per_day,
            allowed_hours=rule_data.allowed_hours,
            allowed_days=rule_data.allowed_days,
            created_by=created_by,
        )

        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)

        logger.info(
            "Role access rule created",
            role=rule_data.role.value,
            tool_pattern=rule_data.tool_pattern,
            server_pattern=rule_data.server_pattern,
        )

        return RoleToolAccessResponse.model_validate(rule)

    async def get_role_access_rules(
        self, role: UserRole | None = None
    ) -> list[RoleToolAccessResponse]:
        """Get role-based access rules.

        Args:
            role: Optional role filter

        Returns:
            List of access rules
        """
        query = select(RoleToolAccess)
        if role:
            query = query.where(RoleToolAccess.role == role)

        result = await self.session.execute(query)
        rules = result.scalars().all()

        return [RoleToolAccessResponse.model_validate(rule) for rule in rules]

    # Access checking methods

    async def check_tool_access(
        self, check_data: UserToolAccessCheck
    ) -> ToolAccessResult:
        """Check if user has access to a tool.

        Args:
            check_data: Access check data

        Returns:
            Access check result
        """
        user_id = check_data.user_id
        tool_name = check_data.tool_name
        server_name = check_data.server_name

        # Get user information
        user = await self._get_user(user_id)
        if not user:
            return ToolAccessResult(
                allowed=False,
                access_level=ToolAccessLevel.NONE,
                restriction_reason="User not found",
            )

        # Get tool and server information
        tool, server = await self._get_tool_and_server(tool_name, server_name)
        
        # Check explicit permissions first
        permission = await self._get_user_tool_permission(user_id, tool, server)
        if permission:
            return await self._check_permission_access(permission, tool_name)

        # Check role-based access
        user_role = getattr(user, 'role', UserRole.USER)  # Default to USER role
        role_access = await self._get_role_access(user_role, tool_name, server_name)
        if role_access:
            return await self._check_role_access(role_access, user_id, tool_name)

        # Default deny
        return ToolAccessResult(
            allowed=False,
            access_level=ToolAccessLevel.NONE,
            restriction_reason="No access permission found",
        )

    async def record_tool_usage(
        self, user_id: str, tool_name: str, server_name: str | None = None
    ) -> bool:
        """Record tool usage for rate limiting.

        Args:
            user_id: User ID
            tool_name: Tool name
            server_name: Server name

        Returns:
            True if recorded successfully
        """
        # Get tool and server information
        tool, server = await self._get_tool_and_server(tool_name, server_name)
        
        # Update usage for explicit permissions
        permission = await self._get_user_tool_permission(user_id, tool, server)
        if permission:
            permission.usage_count += 1
            permission.last_used = datetime.now(UTC)
            await self.session.commit()
            return True

        return False

    # Helper methods

    async def _get_existing_permission(
        self, 
        user_id: str, 
        tool_id: str | None, 
        server_id: str | None
    ) -> ToolPermission | None:
        """Get existing permission."""
        query = select(ToolPermission).where(
            ToolPermission.user_id == user_id
        )
        
        if tool_id:
            query = query.where(ToolPermission.tool_id == tool_id)
        elif server_id:
            query = query.where(ToolPermission.server_id == server_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_permission_by_id(self, permission_id: str) -> ToolPermission | None:
        """Get permission by ID."""
        result = await self.session.execute(
            select(ToolPermission).where(ToolPermission.id == permission_id)
        )
        return result.scalar_one_or_none()

    async def _get_user(self, user_id: str) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_tool_and_server(
        self, tool_name: str, server_name: str | None
    ) -> tuple[ServerTool | None, ToolServer | None]:
        """Get tool and server information."""
        tool = None
        server = None

        if server_name:
            # Get server first
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.name == server_name)
            )
            server = result.scalar_one_or_none()

            if server:
                # Get tool from this server
                result = await self.session.execute(
                    select(ServerTool).where(
                        and_(
                            ServerTool.server_id == server.id,
                            ServerTool.name == tool_name,
                        )
                    )
                )
                tool = result.scalar_one_or_none()
        else:
            # Search for tool across all servers
            result = await self.session.execute(
                select(ServerTool).where(ServerTool.name == tool_name)
            )
            tool = result.scalar_one_or_none()
            
            if tool:
                result = await self.session.execute(
                    select(ToolServer).where(ToolServer.id == tool.server_id)
                )
                server = result.scalar_one_or_none()

        return tool, server

    async def _get_user_tool_permission(
        self, 
        user_id: str, 
        tool: ServerTool | None, 
        server: ToolServer | None
    ) -> ToolPermission | None:
        """Get user permission for specific tool or server."""
        if not tool and not server:
            return None

        query = select(ToolPermission).where(
            ToolPermission.user_id == user_id
        )

        # Check for specific tool permission first
        if tool:
            tool_result = await self.session.execute(
                query.where(ToolPermission.tool_id == tool.id)
            )
            tool_permission = tool_result.scalar_one_or_none()
            if tool_permission:
                return tool_permission

        # Check for server-wide permission
        if server:
            server_result = await self.session.execute(
                query.where(ToolPermission.server_id == server.id)
            )
            server_permission = server_result.scalar_one_or_none()
            if server_permission:
                return server_permission

        return None

    async def _get_role_access(
        self, role: UserRole, tool_name: str, server_name: str | None
    ) -> RoleToolAccess | None:
        """Get role-based access for tool."""
        result = await self.session.execute(
            select(RoleToolAccess).where(RoleToolAccess.role == role)
        )
        rules = result.scalars().all()

        # Check each rule for pattern match
        for rule in rules:
            if self._matches_pattern(tool_name, rule.tool_pattern):
                return rule
            if server_name and self._matches_pattern(server_name, rule.server_pattern):
                return rule

        return None

    def _matches_pattern(self, name: str, pattern: str | None) -> bool:
        """Check if name matches pattern."""
        if not pattern:
            return False
        
        # Simple wildcard pattern matching
        pattern = pattern.replace('*', '.*')
        return bool(re.match(f"^{pattern}$", name))

    async def _check_permission_access(
        self, permission: ToolPermission, tool_name: str
    ) -> ToolAccessResult:
        """Check access based on explicit permission."""
        now = datetime.now(UTC)

        # Check if permission has expired
        if permission.expires_at and permission.expires_at <= now:
            return ToolAccessResult(
                allowed=False,
                access_level=ToolAccessLevel.NONE,
                restriction_reason="Permission expired",
                expires_at=permission.expires_at,
            )

        # Check time restrictions
        if not self._check_time_restrictions(permission.allowed_hours, permission.allowed_days):
            return ToolAccessResult(
                allowed=False,
                access_level=permission.access_level,
                restriction_reason="Access not allowed at this time",
            )

        # Check rate limits
        rate_limit_result = await self._check_rate_limits(permission)
        if not rate_limit_result["allowed"]:
            return ToolAccessResult(
                allowed=False,
                access_level=permission.access_level,
                rate_limit_remaining_hour=rate_limit_result["remaining_hour"],
                rate_limit_remaining_day=rate_limit_result["remaining_day"],
                restriction_reason="Rate limit exceeded",
            )

        return ToolAccessResult(
            allowed=True,
            access_level=permission.access_level,
            rate_limit_remaining_hour=rate_limit_result["remaining_hour"],
            rate_limit_remaining_day=rate_limit_result["remaining_day"],
            expires_at=permission.expires_at,
        )

    async def _check_role_access(
        self, role_access: RoleToolAccess, user_id: str, tool_name: str
    ) -> ToolAccessResult:
        """Check access based on role."""
        # Check time restrictions
        if not self._check_time_restrictions(role_access.allowed_hours, role_access.allowed_days):
            return ToolAccessResult(
                allowed=False,
                access_level=role_access.access_level,
                restriction_reason="Access not allowed at this time",
            )

        # For role-based access, we don't track individual usage
        # Rate limits would be applied at the application level
        return ToolAccessResult(
            allowed=True,
            access_level=role_access.access_level,
        )

    def _check_time_restrictions(
        self, allowed_hours: list[int] | None, allowed_days: list[int] | None
    ) -> bool:
        """Check if current time is within allowed restrictions."""
        now = datetime.now(UTC)

        # Check allowed hours (0-23)
        if allowed_hours and now.hour not in allowed_hours:
            return False

        # Check allowed days (0=Monday, 6=Sunday)
        if allowed_days and now.weekday() not in allowed_days:
            return False

        return True

    async def _check_rate_limits(
        self, permission: ToolPermission
    ) -> dict[str, Any]:
        """Check rate limits for permission."""
        now = datetime.now(UTC)
        
        # Default to no limits
        result = {
            "allowed": True,
            "remaining_hour": None,
            "remaining_day": None,
        }

        # Check hourly limit
        if permission.rate_limit_per_hour:
            hour_ago = now - timedelta(hours=1)
            # This would need additional tracking table in real implementation
            # For now, use the usage_count as approximation
            if permission.last_used and permission.last_used > hour_ago:
                # Simplified check - in real implementation would need hourly usage tracking
                result["remaining_hour"] = max(0, permission.rate_limit_per_hour - 1)
                if result["remaining_hour"] <= 0:
                    result["allowed"] = False

        # Check daily limit
        if permission.rate_limit_per_day:
            day_ago = now - timedelta(days=1)
            # Similar simplification for daily limits
            if permission.last_used and permission.last_used > day_ago:
                result["remaining_day"] = max(0, permission.rate_limit_per_day - permission.usage_count)
                if result["remaining_day"] <= 0:
                    result["allowed"] = False

        return result