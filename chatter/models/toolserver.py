"""Tool server models for MCP server management and analytics."""

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base


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
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Server configuration
    command: Mapped[str] = mapped_column(String(500), nullable=False)
    args: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    env: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)

    # Management fields
    status: Mapped[ServerStatus] = mapped_column(
        SQLEnum(ServerStatus),
        default=ServerStatus.DISABLED,
        nullable=False,
        index=True
    )
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_start: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_update: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Health and availability
    last_health_check: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_startup_success: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_startup_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_failures: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Metadata
    created_by: Mapped[str | None] = mapped_column(
        String(12),
        ForeignKey("User.id"),
        nullable=True,
        index=True
    )

    # Relationships
    tools: Mapped[list["ServerTool"]] = relationship(
        "ServerTool",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    usage_records: Mapped[list["ToolUsage"]] = relationship(
        "ToolUsage",
        back_populates="server",
        cascade="all, delete-orphan"
    )


class ServerTool(Base):
    """Individual tool model for tools provided by servers."""

    # Foreign keys
    server_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("tool_servers.id"),
        nullable=False,
        index=True
    )

    # Tool identification
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Tool configuration
    args_schema: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Management fields
    status: Mapped[ToolStatus] = mapped_column(
        SQLEnum(ToolStatus),
        default=ToolStatus.ENABLED,
        nullable=False,
        index=True
    )
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    bypass_when_unavailable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Usage tracking
    total_calls: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_errors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_called: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    avg_response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    server: Mapped["ToolServer"] = relationship("ToolServer", back_populates="tools")
    usage_records: Mapped[list["ToolUsage"]] = relationship(
        "ToolUsage",
        back_populates="tool",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint('server_id', 'name', name='uix_server_tool_name'),
    )


class ToolUsage(Base):
    """Tool usage tracking model for analytics."""

    # Foreign keys
    server_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("tool_servers.id"),
        nullable=False,
        index=True
    )
    tool_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey("server_tools.id"),
        nullable=False,
        index=True
    )
    user_id: Mapped[str | None] = mapped_column(
        String(12),
        ForeignKey("User.id"),
        nullable=True,
        index=True
    )
    conversation_id: Mapped[str | None] = mapped_column(
        String(12),
        ForeignKey("conversations.id"),
        nullable=True,
        index=True
    )

    # Usage details
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    arguments: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    # Performance metrics
    response_time_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timing
    called_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True
    )

    # Relationships
    server: Mapped["ToolServer"] = relationship("ToolServer", back_populates="usage_records")
    tool: Mapped["ServerTool"] = relationship("ServerTool", back_populates="usage_records")
