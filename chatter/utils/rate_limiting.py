"""Rate limiting middleware for API endpoints."""

import time
from collections import defaultdict, deque
from typing import Any

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class TokenBucketRateLimiter:
    """Token bucket rate limiter implementation."""

    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.

        Args:
            capacity: Maximum number of tokens in bucket
            refill_rate: Number of tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from bucket.

        Args:
            tokens: Number of tokens to consume

        Returns:
            True if tokens were consumed, False if not enough tokens
        """
        now = time.time()
        # Add tokens based on time elapsed
        elapsed = now - self.last_refill
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.refill_rate
        )
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class SlidingWindowRateLimiter:
    """Sliding window rate limiter implementation."""

    def __init__(self, limit: int, window_seconds: int):
        """Initialize sliding window limiter.

        Args:
            limit: Maximum requests in window
            window_seconds: Window size in seconds
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = deque()

    def is_allowed(self) -> bool:
        """Check if request is allowed.

        Returns:
            True if request is allowed, False otherwise
        """
        now = time.time()
        # Remove old requests outside window
        while self.requests and self.requests[0] <= now - self.window_seconds:
            self.requests.popleft()

        # Check if we're under the limit
        if len(self.requests) < self.limit:
            self.requests.append(now)
            return True
        return False


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting requests."""

    def __init__(
        self,
        app: Any,
        default_limit: int = 100,
        default_window: int = 60,
        endpoint_limits: dict[str, tuple[int, int]] | None = None,
        key_func: callable | None = None,
    ):
        """Initialize rate limiting middleware.

        Args:
            app: FastAPI application
            default_limit: Default requests per window
            default_window: Default window size in seconds
            endpoint_limits: Per-endpoint limits {path: (limit, window)}
            key_func: Function to extract rate limit key from request
        """
        super().__init__(app)
        self.default_limit = default_limit
        self.default_window = default_window
        self.endpoint_limits = endpoint_limits or {}
        self.key_func = key_func or self._default_key_func

        # Storage for rate limiters per key
        self.limiters: dict[str, SlidingWindowRateLimiter] = defaultdict(
            lambda: SlidingWindowRateLimiter(default_limit, default_window)
        )

    def _default_key_func(self, request: Request) -> str:
        """Default function to extract rate limit key.

        Args:
            request: HTTP request

        Returns:
            Rate limit key (IP address)
        """
        # Use X-Forwarded-For if behind proxy, otherwise client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take first IP in case of multiple proxies
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return client_ip

    def _get_endpoint_limits(self, path: str) -> tuple[int, int]:
        """Get rate limits for specific endpoint.

        Args:
            path: Request path

        Returns:
            Tuple of (limit, window_seconds)
        """
        # Check for exact path match first
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]

        # Check for pattern matches
        for pattern, limits in self.endpoint_limits.items():
            if path.startswith(pattern):
                return limits

        return self.default_limit, self.default_window

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting.

        Args:
            request: HTTP request
            call_next: Next middleware in chain

        Returns:
            HTTP response
        """
        # Extract rate limit key
        try:
            key = self.key_func(request)
        except Exception as e:
            logger.warning(f"Failed to extract rate limit key: {e}")
            key = "unknown"

        # Get endpoint-specific limits
        path = request.url.path
        limit, window = self._get_endpoint_limits(path)

        # Create limiter for this key+endpoint if needed
        limiter_key = f"{key}:{path}"
        if limiter_key not in self.limiters:
            self.limiters[limiter_key] = SlidingWindowRateLimiter(limit, window)

        limiter = self.limiters[limiter_key]

        # Check rate limit
        if not limiter.is_allowed():
            logger.warning(
                "Rate limit exceeded",
                key=key,
                path=path,
                limit=limit,
                window=window,
            )

            # Calculate retry after
            retry_after = window

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests per {window} seconds.",
                headers={"Retry-After": str(retry_after)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = max(0, limit - len(limiter.requests))
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(time.time() + window)
        )

        return response


# Predefined rate limiting configurations
MODEL_REGISTRY_LIMITS = {
    # More restrictive for write operations
    "/api/v1/models/providers": (20, 60),  # Provider creation
    "/api/v1/models/models": (30, 60),     # Model creation
    "/api/v1/models/embedding-spaces": (15, 60),  # Embedding space creation

    # Moderate limits for updates
    "/api/v1/models/providers/": (50, 60),  # Provider updates (pattern match)
    "/api/v1/models/models/": (50, 60),     # Model updates (pattern match)

    # More permissive for read operations
    "/api/v1/models/": (200, 60),  # General read operations
}


def create_rate_limiting_middleware(
    limits: dict[str, tuple[int, int]] | None = None,
    default_limit: int = 100,
    default_window: int = 60,
) -> RateLimitingMiddleware:
    """Create rate limiting middleware with optional custom limits.

    Args:
        limits: Custom endpoint limits
        default_limit: Default requests per window
        default_window: Default window size in seconds

    Returns:
        Configured rate limiting middleware
    """
    endpoint_limits = limits or MODEL_REGISTRY_LIMITS

    def key_func(request: Request) -> str:
        """Enhanced key function that includes user info if available."""
        # Try to get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP-based limiting
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"

        return f"ip:{client_ip}"

    return RateLimitingMiddleware(
        app=None,  # Will be set by FastAPI
        default_limit=default_limit,
        default_window=default_window,
        endpoint_limits=endpoint_limits,
        key_func=key_func,
    )


class MemoryLeakProtection:
    """Utility to prevent memory leaks in rate limiting storage."""

    def __init__(
        self,
        limiters: dict,
        max_entries: int = 10000,
        cleanup_interval: int = 300,
    ):
        """Initialize memory leak protection.

        Args:
            limiters: Dictionary of rate limiters to protect
            max_entries: Maximum entries before cleanup
            cleanup_interval: Cleanup interval in seconds
        """
        self.limiters = limiters
        self.max_entries = max_entries
        self.cleanup_interval = cleanup_interval
        self.last_cleanup = time.time()

    def cleanup_if_needed(self):
        """Clean up old entries if needed."""
        now = time.time()

        # Check if cleanup is needed
        if (
            len(self.limiters) > self.max_entries
            or now - self.last_cleanup > self.cleanup_interval
        ):
            self._cleanup()
            self.last_cleanup = now

    def _cleanup(self):
        """Remove old unused limiters."""
        now = time.time()
        to_remove = []

        for key, limiter in self.limiters.items():
            # Remove if no recent requests
            if (
                not limiter.requests
                or limiter.requests[-1] < now - limiter.window_seconds * 2
            ):
                to_remove.append(key)

        for key in to_remove:
            del self.limiters[key]

        logger.debug(
            f"Rate limiter cleanup: removed {len(to_remove)} entries, "
            f"{len(self.limiters)} remaining"
        )
