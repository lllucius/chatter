"""Server-Sent Events (SSE) API endpoints for real-time updates."""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.events import (
    SSEStatsResponse,
    TestEventResponse,
)
from chatter.services.sse_events import EventType, sse_service
from chatter.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/stream", responses={
    200: {
        "content": {"text/event-stream": {"schema": {"type": "string"}}},
        "description": "Server-Sent Events stream for real-time updates"
    }
})
async def events_stream(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Stream real-time events via Server-Sent Events.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user

    Returns:
        StreamingResponse with SSE format
    """

    async def generate_events():
        """Generate SSE formatted events."""
        # Create connection for this user
        connection_id = sse_service.create_connection(user_id=current_user.id)
        connection = sse_service.get_connection(connection_id)

        if not connection:
            logger.error("Failed to create SSE connection", user_id=current_user.id)
            return

        try:
            # Send initial connection event
            initial_event = {
                "type": "connection.established",
                "data": {
                    "connection_id": connection_id,
                    "user_id": current_user.id,
                    "connected_at": connection.connected_at.isoformat(),
                },
                "timestamp": connection.connected_at.isoformat(),
            }
            yield f"data: {json.dumps(initial_event)}\n\n"

            # Stream events as they arrive
            async for event in connection.get_events():
                # Skip keepalive events for the client unless explicitly requested
                if (event.type == EventType.SYSTEM_STATUS and
                        event.data.get("keepalive", False)):
                    yield ": keepalive\n\n"  # SSE comment format for keepalive
                    continue

                event_data = {
                    "id": event.id,
                    "type": event.type.value,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "metadata": event.metadata,
                }

                yield f"id: {event.id}\n"
                yield f"event: {event.type.value}\n"
                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            logger.error(
                "Error in SSE stream",
                connection_id=connection_id,
                user_id=current_user.id,
                error=str(e)
            )
            error_event = {
                "type": "error",
                "data": {"error": "Stream connection error"},
                "timestamp": connection.connected_at.isoformat(),
            }
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            # Clean up connection
            sse_service.close_connection(connection_id)

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )


@router.get("/admin/stream", responses={
    200: {
        "content": {"text/event-stream": {"schema": {"type": "string"}}},
        "description": "Admin SSE stream for all system events"
    }
})
async def admin_events_stream(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """Stream all system events for admin users.

    Args:
        request: FastAPI request object
        current_user: Current authenticated user (must be admin)

    Returns:
        StreamingResponse with SSE format for all events
    """
    # Check admin role - only superusers can access admin event stream
    from chatter.core.auth import AuthService
    from chatter.utils.database import get_session
    
    async with get_session() as session:
        auth_service = AuthService(session)
        is_admin = await auth_service.is_admin(current_user.id)
        if not is_admin:
            from chatter.utils.problem import AuthorizationProblem
            raise AuthorizationProblem(
                detail="Admin privileges required for system event stream"
            )

    async def generate_admin_events():
        """Generate SSE formatted events for admin stream."""
        # Create connection without user filter to receive all events
        connection_id = sse_service.create_connection(user_id=None)
        connection = sse_service.get_connection(connection_id)

        if not connection:
            logger.error("Failed to create admin SSE connection", user_id=current_user.id)
            return

        try:
            # Send initial connection event
            initial_event = {
                "type": "admin.connection.established",
                "data": {
                    "connection_id": connection_id,
                    "admin_user_id": current_user.id,
                    "connected_at": connection.connected_at.isoformat(),
                },
                "timestamp": connection.connected_at.isoformat(),
            }
            yield f"data: {json.dumps(initial_event)}\n\n"

            # Stream all system events
            async for event in connection.get_events():
                # Skip keepalive events for admin stream too
                if (event.type == EventType.SYSTEM_STATUS and
                        event.data.get("keepalive", False)):
                    yield ": admin-keepalive\n\n"
                    continue

                event_data = {
                    "id": event.id,
                    "type": event.type.value,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "user_id": event.user_id,  # Include user_id for admin
                    "metadata": event.metadata,
                }

                yield f"id: {event.id}\n"
                yield f"event: {event.type.value}\n"
                yield f"data: {json.dumps(event_data)}\n\n"

        except Exception as e:
            logger.error(
                "Error in admin SSE stream",
                connection_id=connection_id,
                admin_user_id=current_user.id,
                error=str(e)
            )
            error_event = {
                "type": "error",
                "data": {"error": "Admin stream connection error"},
                "timestamp": connection.connected_at.isoformat(),
            }
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            # Clean up connection
            sse_service.close_connection(connection_id)

    return StreamingResponse(
        generate_admin_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )


@router.get("/stats", response_model=SSEStatsResponse)
async def get_sse_stats(
    current_user: User = Depends(get_current_user),
) -> SSEStatsResponse:
    """Get SSE service statistics.

    Args:
        current_user: Current authenticated user

    Returns:
        SSE service statistics
    """
    # Check admin role for detailed system statistics
    from chatter.core.auth import AuthService
    from chatter.utils.database import get_session
    
    async with get_session() as session:
        auth_service = AuthService(session)
        is_admin = await auth_service.is_admin(current_user.id)
        if not is_admin:
            from chatter.utils.problem import AuthorizationProblem
            raise AuthorizationProblem(
                detail="Admin privileges required for detailed system statistics"
            )
    
    
    stats = sse_service.get_stats()

    # For non-admin users, only show basic stats
    return SSEStatsResponse(
        total_connections=stats["total_connections"],
        your_connections=len(stats["connections_by_user"].get(current_user.id, [])),
    )


@router.post("/test-event", response_model=TestEventResponse)
async def trigger_test_event(
    current_user: User = Depends(get_current_user),
) -> TestEventResponse:
    """Trigger a test event for the current user.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message with event ID
    """
    event_id = await sse_service.trigger_event(
        EventType.SYSTEM_ALERT,
        {
            "message": "This is a test event",
            "test": True,
            "triggered_by": current_user.id,
        },
        user_id=current_user.id
    )

    return TestEventResponse(
        message="Test event triggered successfully",
        event_id=event_id
    )


@router.post("/broadcast-test", response_model=TestEventResponse)
async def trigger_broadcast_test(
    current_user: User = Depends(get_current_user),
) -> TestEventResponse:
    """Trigger a broadcast test event for all users.

    Args:
        current_user: Current authenticated user

    Returns:
        Success message with event ID
    """
    # Check admin role for broadcast events
    from chatter.core.auth import AuthService
    from chatter.utils.database import get_session
    
    async with get_session() as session:
        auth_service = AuthService(session)
        is_admin = await auth_service.is_admin(current_user.id)
        if not is_admin:
            from chatter.utils.problem import AuthorizationProblem
            raise AuthorizationProblem(
                detail="Admin privileges required for system broadcast events"
            )

    event_id = await sse_service.trigger_event(
        EventType.SYSTEM_ALERT,
        {
            "message": "This is a system-wide broadcast test",
            "broadcast": True,
            "triggered_by": current_user.id,
        },
        user_id=None  # Broadcast to all users
    )

    return TestEventResponse(
        message="Broadcast test event triggered successfully",
        event_id=event_id
    )
