"""Schemas for SSE events API."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from chatter.models.base import generate_ulid


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

    id: str = Field(default_factory=generate_ulid)
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
    message: str | None = Field(
        default=None, description="Status message"
    )
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
    health_status: str | None = Field(
        default=None, description="Health status"
    )
    details: dict[str, Any] | None = Field(
        None, description="Additional details"
    )
    error: str | None = Field(
        None, description="Error message if failed"
    )


class DocumentEvent(BaseModel):
    """Document event data."""

    document_id: str = Field(..., description="Document ID")
    filename: str | None = Field(
        default=None, description="Document filename"
    )
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
    status: str | None = Field(
        default=None, description="System status"
    )
    details: dict[str, Any] | None = Field(
        None, description="Additional details"
    )


# =============================================================================
# INPUT VALIDATION SCHEMAS
# =============================================================================


class ValidatedEventData(BaseModel):
    """Base class for validated event data."""

    class Config:
        extra = "forbid"  # Forbid extra fields for security


class BackupEventData(ValidatedEventData):
    """Validated data for backup events."""

    backup_id: str = Field(..., min_length=1, max_length=255)
    status: str | None = Field(default=None, max_length=100)
    progress: float | None = Field(default=None, ge=0.0, le=100.0)
    backup_path: str | None = Field(default=None, max_length=1000)
    error: str | None = Field(default=None, max_length=1000)
    updated_at: str | None = Field(
        None, description="Last update timestamp"
    )


class JobEventData(ValidatedEventData):
    """Validated data for job events."""

    job_id: str = Field(..., min_length=1, max_length=255)
    job_name: str = Field(..., min_length=1, max_length=255)
    status: str | None = Field(default=None, max_length=100)
    result: dict[str, Any] | None = None
    error: str | None = Field(default=None, max_length=1000)


class DocumentEventData(ValidatedEventData):
    """Validated data for document events."""

    document_id: str = Field(..., min_length=1, max_length=255)
    filename: str | None = Field(default=None, max_length=500)
    status: str = Field(..., max_length=100)
    progress: float | None = Field(default=None, ge=0.0, le=100.0)
    result: dict[str, Any] | None = None
    error: str | None = Field(default=None, max_length=1000)


class SystemEventData(ValidatedEventData):
    """Validated data for system events."""

    message: str = Field(..., min_length=1, max_length=1000)
    severity: str | None = Field(
        None, pattern=r"^(info|warning|error|critical)$"
    )
    details: dict[str, Any] | None = None
    test: bool | None = None
    broadcast: bool | None = None
    triggered_by: str | None = Field(default=None, max_length=255)


class ToolServerEventData(ValidatedEventData):
    """Validated data for tool server events."""

    server_id: str = Field(..., min_length=1, max_length=255)
    server_name: str = Field(..., min_length=1, max_length=255)
    health_status: str | None = Field(default=None, max_length=100)
    details: dict[str, Any] | None = None
    error: str | None = Field(default=None, max_length=1000)
    checked_at: str | None = Field(
        None, description="Health check timestamp"
    )
    started_at: str | None = Field(
        None, description="Server start timestamp"
    )
    stopped_at: str | None = Field(
        None, description="Server stop timestamp"
    )


class UserEventData(ValidatedEventData):
    """Validated data for user events."""

    user_id: str = Field(..., min_length=1, max_length=255)
    status: str | None = Field(default=None, max_length=100)
    details: dict[str, Any] | None = None


# Mapping of event types to their validation schemas
EVENT_DATA_VALIDATORS = {
    # Backup events
    EventType.BACKUP_STARTED: BackupEventData,
    EventType.BACKUP_COMPLETED: BackupEventData,
    EventType.BACKUP_FAILED: BackupEventData,
    EventType.BACKUP_PROGRESS: BackupEventData,
    # Job events
    EventType.JOB_STARTED: JobEventData,
    EventType.JOB_COMPLETED: JobEventData,
    EventType.JOB_FAILED: JobEventData,
    EventType.JOB_PROGRESS: JobEventData,
    # Document events
    EventType.DOCUMENT_UPLOADED: DocumentEventData,
    EventType.DOCUMENT_PROCESSING_STARTED: DocumentEventData,
    EventType.DOCUMENT_PROCESSING_COMPLETED: DocumentEventData,
    EventType.DOCUMENT_PROCESSING_FAILED: DocumentEventData,
    EventType.DOCUMENT_PROCESSING_PROGRESS: DocumentEventData,
    # Tool server events
    EventType.TOOL_SERVER_STARTED: ToolServerEventData,
    EventType.TOOL_SERVER_STOPPED: ToolServerEventData,
    EventType.TOOL_SERVER_HEALTH_CHANGED: ToolServerEventData,
    EventType.TOOL_SERVER_ERROR: ToolServerEventData,
    # System events
    EventType.SYSTEM_ALERT: SystemEventData,
    EventType.SYSTEM_STATUS: SystemEventData,
    # User events
    EventType.USER_REGISTERED: UserEventData,
    EventType.USER_UPDATED: UserEventData,
    EventType.USER_CONNECTED: UserEventData,
    EventType.USER_DISCONNECTED: UserEventData,
    EventType.USER_STATUS_CHANGED: UserEventData,
}


def validate_event_data(
    event_type: EventType, data: dict[str, Any]
) -> dict[str, Any]:
    """Validate event data against the appropriate schema.

    Args:
        event_type: Type of event
        data: Event data to validate

    Returns:
        Validated and sanitized event data

    Raises:
        ValidationError: If data is invalid
    """
    validator_class = EVENT_DATA_VALIDATORS.get(event_type)

    if validator_class:
        # Validate using the specific schema
        validated_data = validator_class(**data)
        return validated_data.model_dump(exclude_none=True)
    else:
        # For event types without specific validators, do basic validation
        if not isinstance(data, dict):
            raise ValueError("Event data must be a dictionary")

        # Sanitize string values to prevent injection attacks
        sanitized_data = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic sanitization - remove potentially dangerous characters
                import re

                if len(value) > 2000:  # Limit string length
                    value = value[:2000]
                # Remove control characters except newlines and tabs
                value = re.sub(
                    r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value
                )
            sanitized_data[key] = value

        return sanitized_data
