"""Request correlation ID utilities for tracing requests across services."""

import uuid
from contextvars import ContextVar
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variable to store correlation ID for the current request
correlation_id_var: ContextVar[str | None] = ContextVar(
    'correlation_id', default=None
)


def generate_correlation_id() -> str:
    """Generate a new correlation ID.

    Returns:
        A new UUID4 string to use as correlation ID
    """
    return str(uuid.uuid4())


def get_correlation_id() -> str | None:
    """Get the current correlation ID from context.

    Returns:
        Current correlation ID or None if not set
    """
    return correlation_id_var.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID in context.

    Args:
        correlation_id: The correlation ID to set
    """
    correlation_id_var.set(correlation_id)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation IDs to requests and responses."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Add correlation ID to request and response.

        Args:
            request: The incoming request
            call_next: The next middleware in the chain

        Returns:
            Response with correlation ID header
        """
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get(
            'x-correlation-id',
            generate_correlation_id()
        )

        # Set in context for logging and other services
        set_correlation_id(correlation_id)

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers['x-correlation-id'] = correlation_id

        return response
