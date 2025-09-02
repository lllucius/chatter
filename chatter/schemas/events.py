"""Schemas for SSE events API."""

import uuid
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of real-time events."""

    # Backup events
    BACKUP_STARTED = "backup.started"
    BACKUP_COMPLETED = "backup.completed"
    BACKUP_FAILED = "backup.failed"
    BACKUP_PROGRESS = "backup.progress"

    # Job events
    JOB_STARTED = "job.started"
    JOB_COMPLETED = "job.completed"
    JOB_FAILED = "job.failed"
    JOB_PROGRESS = "job.progress"

    # Tool server events
    TOOL_SERVER_STARTED = "tool_server.started"
    TOOL_SERVER_STOPPED = "tool_server.stopped"
    TOOL_SERVER_HEALTH_CHANGED = "tool_server.health_changed"
    TOOL_SERVER_ERROR = "tool_server.error"

    # Document events
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSING_STARTED = "document.processing_started"
    DOCUMENT_PROCESSING_COMPLETED = "document.processing_completed"
    DOCUMENT_PROCESSING_FAILED = "document.processing_failed"
    DOCUMENT_PROCESSING_PROGRESS = "document.processing_progress"

    # Chat events
    CONVERSATION_STARTED = "conversation.started"
    CONVERSATION_ENDED = "conversation.ended"
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"

    # User events
    USER_REGISTERED = "user.registered"
    USER_UPDATED = "user.updated"
    USER_CONNECTED = "user.connected"
    USER_DISCONNECTED = "user.disconnected"
    USER_STATUS_CHANGED = "user.status_changed"

    # Plugin events
    PLUGIN_INSTALLED = "plugin.installed"
    PLUGIN_ACTIVATED = "plugin.activated"
    PLUGIN_DEACTIVATED = "plugin.deactivated"
    PLUGIN_ERROR = "plugin.error"

    # Agent events
    AGENT_CREATED = "agent.created"
    AGENT_UPDATED = "agent.updated"

    # System events
    SYSTEM_ALERT = "system.alert"
    SYSTEM_STATUS = "system.status"


class Event(BaseModel):
    """Real-time event data."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType
    data: dict[str, Any]
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    user_id: str | None = None  # If event is user-specific
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventResponse(BaseModel):
    """Response schema for SSE event data."""

    id: str = Field(..., description="Event ID")
    type: EventType = Field(..., description="Event type")
    data: dict[str, Any] = Field(..., description="Event data")
    timestamp: datetime = Field(..., description="Event timestamp")
    user_id: str | None = Field(
        None, description="User ID (if user-specific event)"
    )
    metadata: dict[str, Any] = Field(..., description="Event metadata")


class ConnectionEstablishedEvent(BaseModel):
    """Initial connection event data."""

    type: str = Field(
        "connection.established", description="Event type"
    )
    data: dict[str, Any] = Field(..., description="Connection data")
    timestamp: str = Field(..., description="Connection timestamp")


class TestEventRequest(BaseModel):
    """Request schema for test event."""

    message: str = Field("Test event", description="Test message")


class TestEventResponse(BaseModel):
    """Response schema for test event."""

    message: str = Field(..., description="Response message")
    event_id: str = Field(..., description="Generated event ID")


class SSEStatsResponse(BaseModel):
    """Response schema for SSE service statistics."""

    total_connections: int = Field(
        ..., description="Total active connections"
    )
    your_connections: int = Field(
        ..., description="Your active connections"
    )


class AdminSSEStatsResponse(BaseModel):
    """Response schema for admin SSE service statistics."""

    total_connections: int = Field(
        ..., description="Total active connections"
    )
    user_connections: int = Field(
        ..., description="Number of users with connections"
    )
    connections_by_user: dict[str, int] = Field(
        ..., description="Connections count per user"
    )


class BackupEvent(BaseModel):
    """Backup event data."""

    backup_id: str = Field(..., description="Backup operation ID")
    status: str = Field(..., description="Backup status")
    progress: float | None = Field(
        None, description="Progress percentage"
    )
    message: str | None = Field(None, description="Status message")
    backup_path: str | None = Field(
        None, description="Backup file path"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class JobEvent(BaseModel):
    """Job event data."""

    job_id: str = Field(..., description="Job ID")
    job_name: str = Field(..., description="Job name")
    status: str = Field(..., description="Job status")
    result: dict[str, Any] | None = Field(
        None, description="Job result"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class ToolServerEvent(BaseModel):
    """Tool server event data."""

    server_id: str = Field(..., description="Tool server ID")
    server_name: str = Field(..., description="Tool server name")
    status: str = Field(..., description="Server status")
    health_status: str | None = Field(None, description="Health status")
    details: dict[str, Any] | None = Field(
        None, description="Additional details"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class DocumentEvent(BaseModel):
    """Document event data."""

    document_id: str = Field(..., description="Document ID")
    filename: str | None = Field(None, description="Document filename")
    status: str = Field(..., description="Document processing status")
    progress: float | None = Field(
        None, description="Processing progress"
    )
    result: dict[str, Any] | None = Field(
        None, description="Processing result"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class SystemEvent(BaseModel):
    """System event data."""

    message: str = Field(..., description="System message")
    status: str | None = Field(None, description="System status")
    details: dict[str, Any] | None = Field(
        None, description="Additional details"
    )
