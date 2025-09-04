"""Server-Sent Events (SSE) API endpoints for real-time updates."""

import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from chatter.api.auth import get_current_user, get_current_admin_user
from chatter.config import settings
from chatter.models.user import User
from chatter.schemas.events import (
    SSEStatsResponse,
    TestEventResponse,
)
from chatter.services.sse_events import EventType, sse_service
from chatter.utils.logging import get_logger
from chatter.utils.rate_limiter import get_rate_limiter, RateLimitExceeded

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/stream",
    responses={
        200: {
            "content": {
                "text/event-stream": {"schema": {"type": "string"}}
            },
            "description": "Server-Sent Events stream for real-time updates",
        }
    },
)
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
    # Rate limit SSE connections per user
    rate_limiter = get_rate_limiter()
    try:
        await rate_limiter.check_rate_limit(
            f"sse_connections:{current_user.id}",
            limit_per_hour=50,  # Max 50 SSE connections per hour per user
        )
    except RateLimitExceeded as e:
        from chatter.utils.problem import RateLimitProblem
        raise RateLimitProblem(
            detail="Too many SSE connection attempts. Please wait before trying again."
        )

    async def generate_events():
        """Generate SSE formatted events."""
        try:
            # Create connection for this user
            connection_id = sse_service.create_connection(
                user_id=current_user.id
            )
        except ValueError as e:
            logger.warning(
                "Failed to create SSE connection",
                user_id=current_user.id,
                error=str(e),
            )
            from chatter.utils.problem import ServiceUnavailableProblem
            raise ServiceUnavailableProblem(
                detail="Too many active connections. Please try again later."
            )
        
        connection = sse_service.get_connection(connection_id)

        if not connection:
            logger.error(
                "Failed to retrieve SSE connection",
                user_id=current_user.id,
                connection_id=connection_id,
            )
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
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Client disconnected from SSE stream")
                    break

                # Skip keepalive events for the client unless explicitly requested
                if (
                    event.type == EventType.SYSTEM_STATUS
                    and event.data.get("keepalive", False)
                ):
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
                error=str(e),
            )
            from datetime import UTC, datetime
            error_event = {
                "type": "error",
                "data": {"error": "Stream connection error"},
                "timestamp": datetime.now(UTC).isoformat(),
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
            "Access-Control-Allow-Origin": ", ".join(settings.cors_origins),
            "Access-Control-Allow-Headers": ", ".join(settings.cors_allow_headers),
            "Access-Control-Allow-Credentials": str(settings.cors_allow_credentials).lower(),
        },
    )


@router.get(
    "/admin/stream",
    responses={
        200: {
            "content": {
                "text/event-stream": {"schema": {"type": "string"}}
            },
            "description": "Admin SSE stream for all system events",
        }
    },
)
async def admin_events_stream(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
) -> StreamingResponse:
    """Stream all system events for admin users.

    Args:
        request: FastAPI request object
        current_user: Current authenticated admin user

    Returns:
        StreamingResponse with SSE format for all events
    """

    async def generate_admin_events():
        """Generate SSE formatted events for admin stream."""
        # Create connection without user filter to receive all events
        connection_id = sse_service.create_connection(user_id=None)
        connection = sse_service.get_connection(connection_id)

        if not connection:
            logger.error(
                "Failed to create admin SSE connection",
                user_id=current_user.id,
            )
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
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("Admin client disconnected from SSE stream")
                    break

                # Skip keepalive events for admin stream too
                if (
                    event.type == EventType.SYSTEM_STATUS
                    and event.data.get("keepalive", False)
                ):
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
                error=str(e),
            )
            from datetime import UTC, datetime
            error_event = {
                "type": "error",
                "data": {"error": "Admin stream connection error"},
                "timestamp": datetime.now(UTC).isoformat(),
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
            "Access-Control-Allow-Origin": ", ".join(settings.cors_origins),
            "Access-Control-Allow-Headers": ", ".join(settings.cors_allow_headers),
            "Access-Control-Allow-Credentials": str(settings.cors_allow_credentials).lower(),
        },
    )


@router.get("/stats", response_model=SSEStatsResponse)
async def get_sse_stats(
    current_user: User = Depends(get_current_admin_user),
) -> SSEStatsResponse:
    """Get SSE service statistics.

    Args:
        current_user: Current authenticated admin user

    Returns:
        SSE service statistics
    """

    stats = sse_service.get_stats()

    # For non-admin users, only show basic stats
    return SSEStatsResponse(
        total_connections=stats["total_connections"],
        your_connections=len(
            stats["connections_by_user"].get(current_user.id, [])
        ),
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
        user_id=current_user.id,
    )

    return TestEventResponse(
        message="Test event triggered successfully", event_id=event_id
    )


@router.post("/broadcast-test", response_model=TestEventResponse)
async def trigger_broadcast_test(
    current_user: User = Depends(get_current_admin_user),
) -> TestEventResponse:
    """Trigger a broadcast test event for all users.

    Args:
        current_user: Current authenticated admin user

    Returns:
        Success message with event ID
    """

    event_id = await sse_service.trigger_event(
        EventType.SYSTEM_ALERT,
        {
            "message": "This is a system-wide broadcast test",
            "broadcast": True,
            "triggered_by": current_user.id,
        },
        user_id=None,  # Broadcast to all users
    )

    return TestEventResponse(
        message="Broadcast test event triggered successfully",
        event_id=event_id,
    )
