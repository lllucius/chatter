"""Tool server models for MCP server management and analytics."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base, Keys


class ServerStatus(str, Enum):
    """Enumeration for server status."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"


class ToolStatus(str, Enum):
    """Enumeration for tool status."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class ToolServer(Base):
    """Tool server model for MCP server configurations."""

    # Server identification
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Remote server configuration
    base_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    transport_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="http"  # "http" or "sse"
    )

    # Built-in server configuration (for local servers)
    command: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    args: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    env: Mapped[dict[str, str] | None] = mapped_column(
        JSON, nullable=True
    )

    # OAuth configuration
    oauth_client_id: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )
    oauth_client_secret: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    oauth_token_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    oauth_scope: Mapped[str | None] = mapped_column(
        String(200), nullable=True
    )

    # Additional headers and configuration
    headers: Mapped[dict[str, str] | None] = mapped_column(
        JSON, nullable=True
    )
    timeout: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )

    # Management fields
    status: Mapped[ServerStatus] = mapped_column(
        SQLEnum(ServerStatus),
        default=ServerStatus.DISABLED,
        nullable=False,
        index=True,
    )
    is_builtin: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    auto_start: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    auto_update: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Health and availability
    last_health_check: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_startup_success: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_startup_error: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    consecutive_failures: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    max_failures: Mapped[int] = mapped_column(
        Integer, default=3, nullable=False
    )

    # Metadata
    created_by: Mapped[str | None] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=True, index=True
    )

    # Relationships
    tools: Mapped[list["ServerTool"]] = relationship(
        "ServerTool",
        back_populates="server",
        cascade="all, delete-orphan",
    )
    usage_records: Mapped[list["ToolUsage"]] = relationship(
        "ToolUsage",
        back_populates="server",
        cascade="all, delete-orphan",
    )


class ServerTool(Base):
    """Individual tool model for tools provided by servers."""

    # Foreign keys
    server_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey("tool_servers.id"),
        nullable=False,
        index=True,
    )

    # Tool identification
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tool configuration
    args_schema: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Management fields
    status: Mapped[ToolStatus] = mapped_column(
        SQLEnum(ToolStatus),
        default=ToolStatus.ENABLED,
        nullable=False,
        index=True,
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    bypass_when_unavailable: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Usage tracking
    total_calls: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_errors: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_called: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    avg_response_time_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Relationships
    server: Mapped["ToolServer"] = relationship(
        "ToolServer", back_populates="tools"
    )
    usage_records: Mapped[list["ToolUsage"]] = relationship(
        "ToolUsage", back_populates="tool", cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "server_id", "name", name="uix_server_tool_name"
        ),
    )


class ToolUsage(Base):
    """Tool usage tracking model for analytics."""

    # Foreign keys
    server_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey(Keys.TOOL_SERVERS),
        nullable=False,
        index=True,
    )
    tool_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey(Keys.SERVER_TOOLS),
        nullable=False,
        index=True,
    )
    user_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=True, index=True
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey(Keys.CONVERSATIONS),
        nullable=True,
        index=True,
    )

    # Usage details
    tool_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    arguments: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    # Performance metrics
    response_time_ms: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    success: Mapped[bool] = mapped_column(
        Boolean, nullable=False, index=True
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Timing
    called_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    # Relationships
    server: Mapped["ToolServer"] = relationship(
        "ToolServer", back_populates="usage_records"
    )
    tool: Mapped["ServerTool"] = relationship(
        "ServerTool", back_populates="usage_records"
    )


class ToolAccessLevel(str, Enum):
    """Access levels for tools."""

    NONE = "none"
    READ = "read"  # Can view tool info
    EXECUTE = "execute"  # Can execute tools
    ADMIN = "admin"  # Can manage tool settings


class ToolPermission(Base):
    """Role-based access control for tools."""

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )
    tool_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey(Keys.SERVER_TOOLS),
        nullable=True,
        index=True,
    )
    server_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey(Keys.TOOL_SERVERS),
        nullable=True,
        index=True,
    )

    # Permission configuration
    access_level: Mapped[ToolAccessLevel] = mapped_column(
        SQLEnum(ToolAccessLevel),
        default=ToolAccessLevel.NONE,
        nullable=False,
        index=True,
    )

    # Rate limiting
    rate_limit_per_hour: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    rate_limit_per_day: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Time restrictions
    allowed_hours: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True  # [0-23] list of allowed hours
    )
    allowed_days: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True  # [0-6] list of allowed weekdays (0=Monday)
    )

    # Permission metadata
    granted_by: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Usage tracking for this permission
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Constraints - either tool_id or server_id must be set
    __table_args__ = (
        UniqueConstraint(
            "user_id", "tool_id", name="uix_user_tool_permission"
        ),
        UniqueConstraint(
            "user_id", "server_id", name="uix_user_server_permission"
        ),
    )


class UserRole(str, Enum):
    """User roles for tool access."""

    GUEST = "guest"
    USER = "user"
    POWER_USER = "power_user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class RoleToolAccess(Base):
    """Default tool access by role."""

    # Role configuration
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        nullable=False,
        index=True,
    )

    # Tool access pattern (tool name pattern or server pattern)
    tool_pattern: Mapped[str | None] = mapped_column(
        String(200), nullable=True, index=True
    )
    server_pattern: Mapped[str | None] = mapped_column(
        String(200), nullable=True, index=True
    )

    # Access configuration
    access_level: Mapped[ToolAccessLevel] = mapped_column(
        SQLEnum(ToolAccessLevel),
        default=ToolAccessLevel.NONE,
        nullable=False,
    )

    # Rate limits for this role
    default_rate_limit_per_hour: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    default_rate_limit_per_day: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Time restrictions
    allowed_hours: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True
    )
    allowed_days: Mapped[list[int] | None] = mapped_column(
        JSON, nullable=True
    )

    # Metadata
    created_by: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            "role",
            "tool_pattern",
            "server_pattern",
            name="uix_role_tool_access",
        ),
    )
