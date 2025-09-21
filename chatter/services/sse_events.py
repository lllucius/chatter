"""Server-Sent Events (SSE) service for real-time updates."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from chatter.config import settings
from chatter.models.base import generate_ulid
from chatter.schemas.events import Event, EventType, validate_event_data
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Import unified event system


class SSEConnection:
    """Represents an active SSE connection."""

    def __init__(self, connection_id: str, user_id: str | None = None):
        self.connection_id = connection_id
        self.user_id = user_id
        self.connected_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)
        # Bounded queue to prevent memory issues with slow clients
        self._queue: asyncio.Queue[Event] = asyncio.Queue(
            maxsize=settings.sse_queue_maxsize
        )
        self._closed = False
        self._dropped_events = 0

    async def send_event(self, event: Event) -> None:
        """Queue an event to be sent to this connection."""
        if not self._closed:
            try:
                # Try to put event in queue without blocking
                self._queue.put_nowait(event)
                self.last_activity = datetime.now(UTC)
            except asyncio.QueueFull:
                # Queue is full, drop the event and track it
                self._dropped_events += 1
                logger.warning(
                    "Event queue full, dropping event",
                    connection_id=self.connection_id,
                    event_type=event.type.value,
                    dropped_events=self._dropped_events,
                )
                # Optionally, we could drop oldest events instead
                if (
                    self._dropped_events % 10 == 0
                ):  # Log every 10th drop
                    logger.error(
                        "Client appears to be slow, many events dropped",
                        connection_id=self.connection_id,
                        total_dropped=self._dropped_events,
                    )
            except Exception as e:
                logger.error(
                    "Failed to queue event for connection",
                    connection_id=self.connection_id,
                    error=str(e),
                )

    async def get_events(self) -> AsyncGenerator[Event, None]:
        """Get events from the queue as they arrive."""
        while not self._closed:
            try:
                # Wait for an event with configurable timeout
                event = await asyncio.wait_for(
                    self._queue.get(),
                    timeout=float(settings.sse_keepalive_timeout),
                )
                yield event
            except TimeoutError:
                # Send keepalive/heartbeat
                yield Event(
                    type=EventType.SYSTEM_STATUS,
                    data={"status": "connected", "keepalive": True},
                )
            except Exception as e:
                logger.error(
                    "Error getting events for connection",
                    connection_id=self.connection_id,
                    error=str(e),
                )
                break

    def close(self) -> None:
        """Close the connection."""
        self._closed = True
        logger.info(
            "SSE connection closed",
            connection_id=self.connection_id,
            user_id=self.user_id,
        )


class SSEEventService:
    """Service for managing Server-Sent Events connections and broadcasting."""

    def __init__(self):
        self.connections: dict[str, SSEConnection] = {}
        self.user_connections: dict[
            str, set[str]
        ] = {}  # user_id -> connection_ids
        self._cleanup_task: asyncio.Task | None = None
        # Connection limits from configuration
        self.max_connections_per_user = (
            settings.sse_max_connections_per_user
        )
        self.max_total_connections = settings.sse_max_total_connections

    async def start(self) -> None:
        """Start the SSE service."""
        logger.info("Starting SSE event service")
        self._cleanup_task = asyncio.create_task(
            self._cleanup_inactive_connections()
        )

    async def stop(self) -> None:
        """Stop the SSE service."""
        logger.info("Stopping SSE event service")
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Close all connections
        for connection in list(self.connections.values()):
            connection.close()
        self.connections.clear()
        self.user_connections.clear()

    def create_connection(self, user_id: str | None = None) -> str:
        """Create a new SSE connection."""
        # Check global connection limit
        if len(self.connections) >= self.max_total_connections:
            logger.warning(
                "Maximum total connections reached",
                total_connections=len(self.connections),
                max_connections=self.max_total_connections,
            )
            raise ValueError("Maximum number of connections reached")

        # Check per-user connection limit
        if user_id and user_id in self.user_connections:
            user_connection_count = len(self.user_connections[user_id])
            if user_connection_count >= self.max_connections_per_user:
                logger.warning(
                    "Maximum connections per user reached",
                    user_id=user_id,
                    user_connections=user_connection_count,
                    max_per_user=self.max_connections_per_user,
                )
                raise ValueError(
                    "Maximum number of connections per user reached"
                )

        connection_id = generate_ulid()
        connection = SSEConnection(connection_id, user_id)

        self.connections[connection_id] = connection

        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)

        logger.info(
            "Created SSE connection",
            connection_id=connection_id,
            user_id=user_id,
            total_connections=len(self.connections),
            user_connections=(
                len(self.user_connections.get(user_id, []))
                if user_id
                else 0
            ),
        )

        return connection_id

    def get_connection(
        self, connection_id: str
    ) -> SSEConnection | None:
        """Get an SSE connection by ID."""
        return self.connections.get(connection_id)

    def close_connection(self, connection_id: str) -> None:
        """Close and remove an SSE connection."""
        connection = self.connections.pop(connection_id, None)
        if connection:
            # Remove from user connections
            if (
                connection.user_id
                and connection.user_id in self.user_connections
            ):
                self.user_connections[connection.user_id].discard(
                    connection_id
                )
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            connection.close()
            logger.info(
                "Closed SSE connection",
                connection_id=connection_id,
                user_id=connection.user_id,
                total_connections=len(self.connections),
            )

    async def broadcast_event(self, event: Event) -> None:
        """Broadcast an event to all relevant connections."""
        logger.info(
            "Broadcasting event",
            event_type=event.type.value,
            event_id=event.id,
            user_specific=event.user_id is not None,
        )

        # Send event to connections efficiently without building lists
        send_count = 0
        error_count = 0

        if event.user_id:
            # Send to specific user's connections
            if event.user_id in self.user_connections:
                connection_ids = list(
                    self.user_connections[event.user_id]
                )  # Create snapshot
                for connection_id in connection_ids:
                    connection = self.connections.get(connection_id)
                    if connection:
                        try:
                            await connection.send_event(event)
                            send_count += 1
                        except Exception as e:
                            error_count += 1
                            logger.warning(
                                "Failed to send event to connection",
                                connection_id=connection_id,
                                event_type=event.type.value,
                                error=str(e),
                            )
        else:
            # Broadcast to all connections (stream without building list)
            connection_items = list(
                self.connections.items()
            )  # Snapshot for safety
            for connection_id, connection in connection_items:
                try:
                    await connection.send_event(event)
                    send_count += 1
                except Exception as e:
                    error_count += 1
                    logger.warning(
                        "Failed to send event to connection",
                        connection_id=connection_id,
                        event_type=event.type.value,
                        error=str(e),
                    )

        if send_count > 0 or error_count > 0:
            logger.debug(
                "Event broadcast complete",
                event_type=event.type.value,
                sent=send_count,
                errors=error_count,
            )

    async def trigger_event(
        self,
        event_type: EventType,
        data: dict[str, Any],
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Trigger a new event and broadcast it."""
        try:
            # Validate and sanitize event data
            validated_data = validate_event_data(event_type, data)

            event = Event(
                type=event_type,
                data=validated_data,
                user_id=user_id,
                metadata=metadata or {},
            )

            await self.broadcast_event(event)

            return event.id
        except Exception as e:
            logger.error(
                "Failed to trigger event",
                event_type=event_type.value,
                error=str(e),
                user_id=user_id,
            )
            # Still create event but with error info
            event = Event(
                type=EventType.SYSTEM_ALERT,
                data={
                    "message": f"Failed to process {event_type.value} event",
                    "error": "Event validation failed",
                    "severity": "error",
                },
                user_id=user_id,
                metadata=metadata or {},
            )
            await self.broadcast_event(event)
            return event.id

    async def _cleanup_inactive_connections(self) -> None:
        """Periodically clean up inactive connections."""
        while True:
            try:
                await asyncio.sleep(
                    settings.sse_connection_cleanup_interval
                )

                now = datetime.now(UTC)
                inactive_connections = []

                for (
                    connection_id,
                    connection,
                ) in self.connections.items():
                    # Consider connections inactive based on configuration
                    if (
                        now - connection.last_activity
                    ).total_seconds() > settings.sse_inactive_timeout:
                        inactive_connections.append(connection_id)

                for connection_id in inactive_connections:
                    self.close_connection(connection_id)

                if inactive_connections:
                    logger.info(
                        "Cleaned up inactive SSE connections",
                        count=len(inactive_connections),
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(
                    "Error during SSE connection cleanup", error=str(e)
                )

    def get_stats(self) -> dict[str, Any]:
        """Get service statistics."""
        return {
            "total_connections": len(self.connections),
            "user_connections": len(self.user_connections),
            "connections_by_user": {
                user_id: len(connection_ids)
                for user_id, connection_ids in self.user_connections.items()
            },
        }


# Global SSE service instance
sse_service = SSEEventService()


# Helper functions for common events
async def trigger_backup_started(
    backup_id: str, user_id: str | None = None
) -> str:
    """Trigger backup started event."""
    return await sse_service.trigger_event(
        EventType.BACKUP_STARTED,
        {
            "backup_id": backup_id,
            "started_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id,
    )


async def trigger_backup_completed(
    backup_id: str, backup_path: str, user_id: str | None = None
) -> str:
    """Trigger backup completed event."""
    return await sse_service.trigger_event(
        EventType.BACKUP_COMPLETED,
        {
            "backup_id": backup_id,
            "backup_path": backup_path,
            "completed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id,
    )


async def trigger_backup_failed(
    backup_id: str, error: str, user_id: str | None = None
) -> str:
    """Trigger backup failed event."""
    return await sse_service.trigger_event(
        EventType.BACKUP_FAILED,
        {
            "backup_id": backup_id,
            "error": error,
            "failed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id,
    )


async def trigger_backup_progress(
    backup_id: str,
    progress: float,
    status: str,
    user_id: str | None = None,
) -> str:
    """Trigger backup progress event."""
    return await sse_service.trigger_event(
        EventType.BACKUP_PROGRESS,
        {
            "backup_id": backup_id,
            "progress": progress,
            "status": status,
            "updated_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id,
    )


async def trigger_job_started(
    job_id: str, job_name: str, user_id: str | None = None
) -> str:
    """Trigger job started event."""
    return await sse_service.trigger_event(
        EventType.JOB_STARTED,
        {
            "job_id": job_id,
            "job_name": job_name,
            "status": "started",
        },
        user_id=user_id,
    )


async def trigger_job_completed(
    job_id: str,
    job_name: str,
    result: dict[str, Any],
    user_id: str | None = None,
) -> str:
    """Trigger job completed event."""
    return await sse_service.trigger_event(
        EventType.JOB_COMPLETED,
        {
            "job_id": job_id,
            "job_name": job_name,
            "status": "completed",
            "result": result,
        },
        user_id=user_id,
    )


async def trigger_job_failed(
    job_id: str, job_name: str, error: str, user_id: str | None = None
) -> str:
    """Trigger job failed event."""
    return await sse_service.trigger_event(
        EventType.JOB_FAILED,
        {
            "job_id": job_id,
            "job_name": job_name,
            "status": "failed",
            "error": error,
        },
        user_id=user_id,
    )


async def trigger_tool_server_started(
    server_id: str, server_name: str
) -> str:
    """Trigger tool server started event."""
    return await sse_service.trigger_event(
        EventType.TOOL_SERVER_STARTED,
        {
            "server_id": server_id,
            "server_name": server_name,
            "started_at": datetime.now(UTC).isoformat(),
        },
    )


async def trigger_tool_server_stopped(
    server_id: str, server_name: str
) -> str:
    """Trigger tool server stopped event."""
    return await sse_service.trigger_event(
        EventType.TOOL_SERVER_STOPPED,
        {
            "server_id": server_id,
            "server_name": server_name,
            "stopped_at": datetime.now(UTC).isoformat(),
        },
    )


async def trigger_tool_server_health_changed(
    server_id: str,
    server_name: str,
    health_status: str,
    details: dict[str, Any],
) -> str:
    """Trigger tool server health changed event."""
    return await sse_service.trigger_event(
        EventType.TOOL_SERVER_HEALTH_CHANGED,
        {
            "server_id": server_id,
            "server_name": server_name,
            "health_status": health_status,
            "details": details,
            "checked_at": datetime.now(UTC).isoformat(),
        },
    )


async def trigger_document_uploaded(
    document_id: str, filename: str, user_id: str
) -> str:
    """Trigger document uploaded event."""
    return await sse_service.trigger_event(
        EventType.DOCUMENT_UPLOADED,
        {
            "document_id": document_id,
            "filename": filename,
            "status": "uploaded",
        },
        user_id=user_id,
    )


async def trigger_document_processing_completed(
    document_id: str, result: dict[str, Any], user_id: str
) -> str:
    """Trigger document processing completed event."""
    return await sse_service.trigger_event(
        EventType.DOCUMENT_PROCESSING_COMPLETED,
        {
            "document_id": document_id,
            "status": "completed",
            "result": result,
        },
        user_id=user_id,
    )


async def trigger_document_processing_failed(
    document_id: str, error: str, user_id: str
) -> str:
    """Trigger document processing failed event."""
    return await sse_service.trigger_event(
        EventType.DOCUMENT_PROCESSING_FAILED,
        {
            "document_id": document_id,
            "status": "failed",
            "error": error,
        },
        user_id=user_id,
    )
