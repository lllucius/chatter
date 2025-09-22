"""Security for workflow execution including tool permissions and audit logging."""

import json

# Simple logger fallback
from datetime import datetime
from enum import Enum
from typing import Any

from chatter.models.base import generate_ulid
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class PermissionLevel(Enum):
    """Permission levels for tool access."""

    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ToolPermission:
    """Represents a permission for a specific tool."""

    def __init__(
        self,
        tool_name: str,
        permission_level: PermissionLevel,
        allowed_methods: set[str] | None = None,
        rate_limit: int | None = None,
        expiry: datetime | None = None,
    ):
        """Initialize tool permission.

        Args:
            tool_name: Name of the tool
            permission_level: Level of permission granted
            allowed_methods: Specific methods allowed (if any)
            rate_limit: Rate limit for tool usage (calls per hour)
            expiry: Expiration time for this permission
        """
        self.tool_name = tool_name
        self.permission_level = permission_level
        self.allowed_methods = allowed_methods or set()
        self.rate_limit = rate_limit
        self.expiry = expiry
        self.usage_count = 0
        self.last_used: datetime | None = None

    def is_valid(self) -> bool:
        """Check if permission is still valid (not expired)."""
        if self.expiry is None:
            return True
        return datetime.now() < self.expiry

    def can_execute(self, method: str | None = None) -> bool:
        """Check if execution is allowed for this permission.

        Args:
            method: Specific method being called (optional)

        Returns:
            True if execution is allowed
        """
        if not self.is_valid():
            return False

        if self.permission_level == PermissionLevel.NONE:
            return False

        if (
            method
            and self.allowed_methods
            and method not in self.allowed_methods
        ):
            return False

        return True

    def record_usage(self) -> bool:
        """Record tool usage and check rate limits.

        Returns:
            True if usage is within limits
        """
        now = datetime.now()

        # Check rate limit
        if self.rate_limit and self.last_used:
            time_since_last = (now - self.last_used).total_seconds()
            if time_since_last < 3600:  # Within 1 hour
                if self.usage_count >= self.rate_limit:
                    return False
            else:
                # Reset usage count after 1 hour
                self.usage_count = 0

        self.usage_count += 1
        self.last_used = now
        return True


class UserPermissions:
    """Manages permissions for a specific user."""

    def __init__(self, user_id: str):
        """Initialize user permissions.

        Args:
            user_id: ID of the user
        """
        self.user_id = user_id
        self.tool_permissions: dict[str, ToolPermission] = {}
        self.global_permission_level = PermissionLevel.NONE
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def add_tool_permission(self, permission: ToolPermission) -> None:
        """Add a tool permission for this user.

        Args:
            permission: Tool permission to add
        """
        self.tool_permissions[permission.tool_name] = permission
        self.updated_at = datetime.now()

        logger.info(
            "Added tool permission",
            user_id=self.user_id,
            tool_name=permission.tool_name,
            permission_level=permission.permission_level.value,
        )

    def remove_tool_permission(self, tool_name: str) -> bool:
        """Remove a tool permission.

        Args:
            tool_name: Name of the tool to remove permission for

        Returns:
            True if permission was removed
        """
        if tool_name in self.tool_permissions:
            del self.tool_permissions[tool_name]
            self.updated_at = datetime.now()

            logger.info(
                "Removed tool permission",
                user_id=self.user_id,
                tool_name=tool_name,
            )
            return True
        return False

    def can_use_tool(
        self, tool_name: str, method: str | None = None
    ) -> bool:
        """Check if user can use a specific tool.

        Args:
            tool_name: Name of the tool
            method: Specific method being called

        Returns:
            True if user can use the tool
        """
        # Check global permission first
        if self.global_permission_level == PermissionLevel.ADMIN:
            return True

        # Check specific tool permission
        if tool_name not in self.tool_permissions:
            return False

        permission = self.tool_permissions[tool_name]
        return permission.can_execute(method)

    def record_tool_usage(
        self, tool_name: str, method: str | None = None
    ) -> bool:
        """Record tool usage and check rate limits.

        Args:
            tool_name: Name of the tool used
            method: Specific method called

        Returns:
            True if usage is within limits
        """
        if tool_name not in self.tool_permissions:
            return False

        permission = self.tool_permissions[tool_name]
        return permission.record_usage()


class AuditLogEntry:
    """Represents a single audit log entry."""

    def __init__(
        self,
        event_type: str,
        user_id: str,
        workflow_id: str,
        workflow_mode: str,
        details: dict[str, Any],
        timestamp: datetime | None = None,
    ):
        """Initialize audit log entry.

        Args:
            event_type: Type of event being logged
            user_id: ID of the user
            workflow_id: ID of the workflow
            workflow_mode: Type of workflow
            details: Additional event details
            timestamp: Timestamp of the event
        """
        self.id = generate_ulid()
        self.event_type = event_type
        self.user_id = user_id
        self.workflow_id = workflow_id
        self.workflow_mode = workflow_mode
        self.details = details
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert audit log entry to dictionary."""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "workflow_id": self.workflow_id,
            "workflow_mode": self.workflow_mode,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class WorkflowSecurityManager:
    """Manages security for workflow execution."""

    def __init__(self) -> None:
        """Initialize workflow security manager."""
        self.user_permissions: dict[str, UserPermissions] = {}
        self.audit_log: list[AuditLogEntry] = []
        self.max_audit_entries = 10000

        # Content filters
        self.blocked_patterns: set[str] = set()
        self.setup_default_filters()

    def setup_default_filters(self) -> None:
        """Setup default content filters."""
        # Add common sensitive patterns
        self.blocked_patterns.update(
            {
                "password",
                "api_key",
                "secret_key",
                "private_key",
                "token",
                "credential",
            }
        )

    def get_user_permissions(self, user_id: str) -> UserPermissions:
        """Get permissions for a user, creating if not exists.

        Args:
            user_id: ID of the user

        Returns:
            User permissions object
        """
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = UserPermissions(user_id)

        return self.user_permissions[user_id]

    def grant_tool_permission(
        self,
        user_id: str,
        tool_name: str,
        permission_level: PermissionLevel,
        allowed_methods: set[str] | None = None,
        rate_limit: int | None = None,
        expiry: datetime | None = None,
    ) -> None:
        """Grant tool permission to a user.

        Args:
            user_id: ID of the user
            tool_name: Name of the tool
            permission_level: Level of permission to grant
            allowed_methods: Specific methods allowed
            rate_limit: Rate limit for tool usage
            expiry: Expiration time for permission
        """
        user_perms = self.get_user_permissions(user_id)

        permission = ToolPermission(
            tool_name=tool_name,
            permission_level=permission_level,
            allowed_methods=allowed_methods,
            rate_limit=rate_limit,
            expiry=expiry,
        )

        user_perms.add_tool_permission(permission)

        # Log the permission grant
        self.log_event(
            "permission_granted",
            user_id,
            "",  # No specific workflow
            "security",
            {
                "tool_name": tool_name,
                "permission_level": permission_level.value,
                "rate_limit": rate_limit,
                "expiry": expiry.isoformat() if expiry else None,
            },
        )

    def revoke_tool_permission(
        self, user_id: str, tool_name: str
    ) -> bool:
        """Revoke tool permission from a user.

        Args:
            user_id: ID of the user
            tool_name: Name of the tool

        Returns:
            True if permission was revoked
        """
        user_perms = self.get_user_permissions(user_id)
        success = user_perms.remove_tool_permission(tool_name)

        if success:
            self.log_event(
                "permission_revoked",
                user_id,
                "",
                "security",
                {"tool_name": tool_name},
            )

        return success

    def authorize_tool_execution(
        self,
        user_id: str,
        workflow_id: str,
        workflow_mode: str,
        tool_name: str,
        method: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> bool:
        """Authorize tool execution for a user.

        Args:
            user_id: ID of the user
            workflow_id: ID of the workflow
            workflow_mode: Type of workflow
            tool_name: Name of the tool
            method: Specific method being called
            parameters: Tool parameters

        Returns:
            True if execution is authorized
        """
        user_perms = self.get_user_permissions(user_id)

        # Check basic permission
        if not user_perms.can_use_tool(tool_name, method):
            self.log_event(
                "tool_access_denied",
                user_id,
                workflow_id,
                workflow_mode,
                {
                    "tool_name": tool_name,
                    "method": method,
                    "reason": "insufficient_permissions",
                },
            )
            return False

        # Check rate limits
        if not user_perms.record_tool_usage(tool_name, method):
            self.log_event(
                "tool_access_denied",
                user_id,
                workflow_id,
                workflow_mode,
                {
                    "tool_name": tool_name,
                    "method": method,
                    "reason": "rate_limit_exceeded",
                },
            )
            return False

        # Content filtering
        if parameters and self.contains_sensitive_content(parameters):
            self.log_event(
                "tool_access_denied",
                user_id,
                workflow_id,
                workflow_mode,
                {
                    "tool_name": tool_name,
                    "method": method,
                    "reason": "sensitive_content_detected",
                },
            )
            return False

        # Log successful authorization
        self.log_event(
            "tool_execution_authorized",
            user_id,
            workflow_id,
            workflow_mode,
            {"tool_name": tool_name, "method": method},
        )

        return True

    def contains_sensitive_content(self, data: Any) -> bool:
        """Check if data contains sensitive content.

        Args:
            data: Data to check

        Returns:
            True if sensitive content is detected
        """
        if isinstance(data, dict):
            data_str = json.dumps(data, default=str).lower()
        elif isinstance(data, list | tuple):
            data_str = " ".join(str(item) for item in data).lower()
        else:
            data_str = str(data).lower()

        return any(
            pattern in data_str for pattern in self.blocked_patterns
        )

    def log_event(
        self,
        event_type: str,
        user_id: str,
        workflow_id: str,
        workflow_mode: str,
        details: dict[str, Any],
    ) -> None:
        """Log a security event.

        Args:
            event_type: Type of event
            user_id: ID of the user
            workflow_id: ID of the workflow
            workflow_mode: Type of workflow
            details: Event details
        """
        entry = AuditLogEntry(
            event_type=event_type,
            user_id=user_id,
            workflow_id=workflow_id,
            workflow_mode=workflow_mode,
            details=details,
        )

        self.audit_log.append(entry)

        # Maintain log size
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log.pop(0)

        logger.info(
            "Security event logged",
            event_type=event_type,
            user_id=user_id,
            workflow_id=workflow_id,
        )

    def get_audit_log(
        self,
        user_id: str | None = None,
        event_type: str | None = None,
        hours: int = 24,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get audit log entries.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            hours: Number of hours to look back
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        filtered_entries = [
            entry
            for entry in reversed(self.audit_log)
            if entry.timestamp.timestamp() > cutoff_time
            and (not user_id or entry.user_id == user_id)
            and (not event_type or entry.event_type == event_type)
        ]

        return [entry.to_dict() for entry in filtered_entries[:limit]]

    def get_security_stats(self, hours: int = 24) -> dict[str, Any]:
        """Get security statistics.

        Args:
            hours: Number of hours to look back

        Returns:
            Dictionary with security statistics
        """
        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        recent_entries = [
            entry
            for entry in self.audit_log
            if entry.timestamp.timestamp() > cutoff_time
        ]

        if not recent_entries:
            return {
                "total_events": 0,
                "denied_attempts": 0,
                "authorized_executions": 0,
                "top_users": [],
                "top_events": [],
            }

        # Count events by type
        event_counts: dict[str, int] = {}
        user_counts: dict[str, int] = {}

        for entry in recent_entries:
            event_counts[entry.event_type] = (
                event_counts.get(entry.event_type, 0) + 1
            )
            user_counts[entry.user_id] = (
                user_counts.get(entry.user_id, 0) + 1
            )

        denied_attempts = sum(
            count
            for event, count in event_counts.items()
            if "denied" in event
        )

        authorized_executions = event_counts.get(
            "tool_execution_authorized", 0
        )

        # Top users and events
        top_users = sorted(
            user_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        top_events = sorted(
            event_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "total_events": len(recent_entries),
            "denied_attempts": denied_attempts,
            "authorized_executions": authorized_executions,
            "top_users": [
                {"user_id": uid, "count": count}
                for uid, count in top_users
            ],
            "top_events": [
                {"event_type": event, "count": count}
                for event, count in top_events
            ],
        }


# Global instance
workflow_security_manager = WorkflowSecurityManager()
