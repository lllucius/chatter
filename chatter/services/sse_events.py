"""Server-Sent Events (SSE) service for real-time updates."""

import asyncio
import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from chatter.schemas.events import Event, EventType
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SSEConnection:
    """Represents an active SSE connection."""

    def __init__(self, connection_id: str, user_id: str | None = None):
        self.connection_id = connection_id
        self.user_id = user_id
        self.connected_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)
        self._queue: asyncio.Queue[Event] = asyncio.Queue()
        self._closed = False

    async def send_event(self, event: Event) -> None:
        """Queue an event to be sent to this connection."""
        if not self._closed:
            try:
                await self._queue.put(event)
                self.last_activity = datetime.now(UTC)
            except Exception as e:
                logger.error(
                    "Failed to queue event for connection",
                    connection_id=self.connection_id,
                    error=str(e)
                )

    async def get_events(self) -> AsyncGenerator[Event, None]:
        """Get events from the queue as they arrive."""
        while not self._closed:
            try:
                # Wait for an event with a timeout to allow periodic checks
                event = await asyncio.wait_for(self._queue.get(), timeout=30.0)
                yield event
            except asyncio.TimeoutError:
                # Send keepalive/heartbeat
                yield Event(
                    type=EventType.SYSTEM_STATUS,
                    data={"status": "connected", "keepalive": True}
                )
            except Exception as e:
                logger.error(
                    "Error getting events for connection",
                    connection_id=self.connection_id,
                    error=str(e)
                )
                break

    def close(self) -> None:
        """Close the connection."""
        self._closed = True
        logger.info(
            "SSE connection closed",
            connection_id=self.connection_id,
            user_id=self.user_id
        )


class SSEEventService:
    """Service for managing Server-Sent Events connections and broadcasting."""

    def __init__(self):
        self.connections: dict[str, SSEConnection] = {}
        self.user_connections: dict[str, set[str]] = {}  # user_id -> connection_ids
        self._cleanup_task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the SSE service."""
        logger.info("Starting SSE event service")
        self._cleanup_task = asyncio.create_task(self._cleanup_inactive_connections())

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
        connection_id = str(uuid.uuid4())
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
            total_connections=len(self.connections)
        )

        return connection_id

    def get_connection(self, connection_id: str) -> SSEConnection | None:
        """Get an SSE connection by ID."""
        return self.connections.get(connection_id)

    def close_connection(self, connection_id: str) -> None:
        """Close and remove an SSE connection."""
        connection = self.connections.pop(connection_id, None)
        if connection:
            # Remove from user connections
            if connection.user_id and connection.user_id in self.user_connections:
                self.user_connections[connection.user_id].discard(connection_id)
                if not self.user_connections[connection.user_id]:
                    del self.user_connections[connection.user_id]

            connection.close()
            logger.info(
                "Closed SSE connection",
                connection_id=connection_id,
                user_id=connection.user_id,
                total_connections=len(self.connections)
            )

    async def broadcast_event(self, event: Event) -> None:
        """Broadcast an event to all relevant connections."""
        logger.info(
            "Broadcasting event",
            event_type=event.type.value,
            event_id=event.id,
            user_specific=event.user_id is not None
        )

        target_connections = []

        if event.user_id:
            # Send to specific user's connections
            if event.user_id in self.user_connections:
                for connection_id in self.user_connections[event.user_id]:
                    if connection_id in self.connections:
                        target_connections.append(self.connections[connection_id])
        else:
            # Broadcast to all connections
            target_connections = list(self.connections.values())

        # Send event to all target connections
        send_tasks = []
        for connection in target_connections:
            send_tasks.append(connection.send_event(event))

        if send_tasks:
            try:
                await asyncio.gather(*send_tasks, return_exceptions=True)
            except Exception as e:
                logger.error("Error broadcasting event", error=str(e))

    async def trigger_event(
        self,
        event_type: EventType,
        data: dict[str, Any],
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Trigger a new event and broadcast it."""
        event = Event(
            type=event_type,
            data=data,
            user_id=user_id,
            metadata=metadata or {}
        )

        await self.broadcast_event(event)
        return event.id

    async def _cleanup_inactive_connections(self) -> None:
        """Periodically clean up inactive connections."""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                now = datetime.now(UTC)
                inactive_connections = []

                for connection_id, connection in self.connections.items():
                    # Consider connections inactive if no activity for 1 hour
                    if (now - connection.last_activity).total_seconds() > 3600:
                        inactive_connections.append(connection_id)

                for connection_id in inactive_connections:
                    self.close_connection(connection_id)

                if inactive_connections:
                    logger.info(
                        "Cleaned up inactive SSE connections",
                        count=len(inactive_connections)
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Error during SSE connection cleanup", error=str(e))

    def get_stats(self) -> dict[str, Any]:
        """Get service statistics."""
        return {
            "total_connections": len(self.connections),
            "user_connections": len(self.user_connections),
            "connections_by_user": {
                user_id: len(connection_ids)
                for user_id, connection_ids in self.user_connections.items()
            }
        }


# Global SSE service instance
sse_service = SSEEventService()


# Helper functions for common events
async def trigger_backup_started(backup_id: str, user_id: str | None = None) -> str:
    """Trigger backup started event."""
    return await sse_service.trigger_event(
        EventType.BACKUP_STARTED,
        {
            "backup_id": backup_id,
            "started_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
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
        user_id=user_id
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
        user_id=user_id
    )


async def trigger_backup_progress(
    backup_id: str, progress: float, status: str, user_id: str | None = None
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
        user_id=user_id
    )


async def trigger_job_started(job_id: str, job_name: str, user_id: str | None = None) -> str:
    """Trigger job started event."""
    return await sse_service.trigger_event(
        EventType.JOB_STARTED,
        {
            "job_id": job_id,
            "job_name": job_name,
            "started_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
    )


async def trigger_job_completed(
    job_id: str, job_name: str, result: dict[str, Any], user_id: str | None = None
) -> str:
    """Trigger job completed event."""
    return await sse_service.trigger_event(
        EventType.JOB_COMPLETED,
        {
            "job_id": job_id,
            "job_name": job_name,
            "result": result,
            "completed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
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
            "error": error,
            "failed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
    )


async def trigger_tool_server_started(server_id: str, server_name: str) -> str:
    """Trigger tool server started event."""
    return await sse_service.trigger_event(
        EventType.TOOL_SERVER_STARTED,
        {
            "server_id": server_id,
            "server_name": server_name,
            "started_at": datetime.now(UTC).isoformat(),
        }
    )


async def trigger_tool_server_stopped(server_id: str, server_name: str) -> str:
    """Trigger tool server stopped event."""
    return await sse_service.trigger_event(
        EventType.TOOL_SERVER_STOPPED,
        {
            "server_id": server_id,
            "server_name": server_name,
            "stopped_at": datetime.now(UTC).isoformat(),
        }
    )


async def trigger_tool_server_health_changed(
    server_id: str, server_name: str, health_status: str, details: dict[str, Any]
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
        }
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
            "uploaded_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
    )


async def trigger_document_processing_completed(
    document_id: str, result: dict[str, Any], user_id: str
) -> str:
    """Trigger document processing completed event."""
    return await sse_service.trigger_event(
        EventType.DOCUMENT_PROCESSING_COMPLETED,
        {
            "document_id": document_id,
            "result": result,
            "completed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
    )


async def trigger_document_processing_failed(
    document_id: str, error: str, user_id: str
) -> str:
    """Trigger document processing failed event."""
    return await sse_service.trigger_event(
        EventType.DOCUMENT_PROCESSING_FAILED,
        {
            "document_id": document_id,
            "error": error,
            "failed_at": datetime.now(UTC).isoformat(),
        },
        user_id=user_id
    )
