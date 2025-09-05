"""Unified rate limiting system consolidating all rate limiting schemes.

This is the primary rate limiting implementation for the Chatter platform.
It provides:

- Sliding window rate limiting algorithm
- Redis backend with memory fallback 
- Multiple rate limits per key (e.g., hourly + daily)
- FastAPI middleware with endpoint-specific limits
- Rich metadata and error responses

Use this module directly via:
- `get_unified_rate_limiter()` for programmatic access
- `UnifiedRateLimitMiddleware` for application-wide rate limiting
- `@rate_limit` decorator for endpoint-specific rate limiting
"""

import asyncio
import time
from collections import defaultdict, deque
from datetime import timedelta
from typing import Any, Callable

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from chatter.config import settings
from chatter.utils.logging import get_logger
from chatter.utils.problem import RateLimitProblem

logger = get_logger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        limit: int | None = None,
        window: int | None = None,
        retry_after: int | None = None,
        remaining: int | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        self.remaining = remaining


class SlidingWindowRateLimiter:
    """Sliding window rate limiter with memory and cache backend support."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        cache_service=None,
        use_cache: bool = True,
    ):
        """Initialize sliding window rate limiter.

        Args:
            limit: Maximum requests in window
            window_seconds: Window size in seconds
            cache_service: Optional cache service for distributed rate limiting
            use_cache: Whether to use cache backend if available
        """
        self.limit = limit
        self.window_seconds = window_seconds
        self.cache_service = cache_service
        self.use_cache = use_cache and cache_service is not None

        # Memory fallback storage
        self._memory_storage: dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def _get_requests_from_cache(self, key: str) -> list[float]:
        """Get request timestamps from cache."""
        if not self.use_cache:
            return []

        try:
            data = await self.cache_service.get(f"rate_limit:{key}")
            if data and isinstance(data, list):
                return [float(ts) for ts in data]
        except Exception as e:
            logger.warning(f"Cache get error for rate limit key {key}: {e}")

        return []

    async def _store_requests_to_cache(
        self, key: str, requests: list[float]
    ) -> None:
        """Store request timestamps to cache."""
        if not self.use_cache:
            return

        try:
            # Store with expiration slightly longer than window
            expire = timedelta(seconds=self.window_seconds + 60)
            await self.cache_service.set(
                f"rate_limit:{key}", requests, expire
            )
        except Exception as e:
            logger.warning(f"Cache set error for rate limit key {key}: {e}")

    async def _clean_old_requests(
        self, requests: list[float], current_time: float
    ) -> list[float]:
        """Remove requests outside the time window."""
        cutoff_time = current_time - self.window_seconds
        return [req_time for req_time in requests if req_time > cutoff_time]

    async def is_allowed(self, key: str) -> tuple[bool, dict[str, Any]]:
        """Check if request is allowed and return metadata.

        Args:
            key: Unique identifier for rate limiting

        Returns:
            Tuple of (allowed, metadata) where metadata contains:
            - remaining: Requests remaining
            - reset_time: Unix timestamp when limit resets
            - retry_after: Seconds to wait before retrying (if blocked)
        """
        current_time = time.time()

        async with self._lock:
            # Try to get from cache first, fallback to memory
            if self.use_cache:
                requests = await self._get_requests_from_cache(key)
                if not requests:
                    # Fallback to memory if cache miss
                    requests = list(self._memory_storage[key])
            else:
                requests = list(self._memory_storage[key])

            # Clean old requests
            requests = await self._clean_old_requests(requests, current_time)

            # Calculate metadata
            remaining = max(0, self.limit - len(requests))
            reset_time = int(current_time + self.window_seconds)
            retry_after = self.window_seconds if remaining == 0 else 0

            metadata = {
                "remaining": remaining,
                "reset_time": reset_time,
                "retry_after": retry_after,
                "limit": self.limit,
                "window": self.window_seconds,
            }

            # Check if request is allowed
            if len(requests) >= self.limit:
                return False, metadata

            # Add current request
            requests.append(current_time)

            # Store updated requests
            if self.use_cache:
                await self._store_requests_to_cache(key, requests)
            else:
                self._memory_storage[key] = deque(requests)

            # Update metadata
            metadata["remaining"] = max(0, self.limit - len(requests))

            return True, metadata

    async def get_status(self, key: str) -> dict[str, Any]:
        """Get current rate limit status without consuming a request."""
        current_time = time.time()

        async with self._lock:
            # Get requests from cache or memory
            if self.use_cache:
                requests = await self._get_requests_from_cache(key)
                if not requests:
                    requests = list(self._memory_storage[key])
            else:
                requests = list(self._memory_storage[key])

            # Clean old requests
            requests = await self._clean_old_requests(requests, current_time)

            return {
                "remaining": max(0, self.limit - len(requests)),
                "reset_time": int(current_time + self.window_seconds),
                "limit": self.limit,
                "window": self.window_seconds,
                "used": len(requests),
            }

    async def reset(self, key: str) -> None:
        """Reset rate limit for a specific key."""
        async with self._lock:
            if self.use_cache:
                try:
                    await self.cache_service.delete(f"rate_limit:{key}")
                except Exception as e:
                    logger.warning(f"Cache delete error for key {key}: {e}")

            if key in self._memory_storage:
                del self._memory_storage[key]


class UnifiedRateLimiter:
    """Unified rate limiter supporting multiple limits and algorithms."""

    def __init__(self, cache_service=None):
        """Initialize unified rate limiter.

        Args:
            cache_service: Optional cache service for distributed rate limiting
        """
        self.cache_service = cache_service
        self._limiters: dict[str, SlidingWindowRateLimiter] = {}
        self._lock = asyncio.Lock()

    def _get_limiter_key(
        self, identifier: str, limit: int, window: int
    ) -> str:
        """Generate unique key for rate limiter configuration."""
        return f"{identifier}:{limit}:{window}"

    async def _get_or_create_limiter(
        self, identifier: str, limit: int, window: int
    ) -> SlidingWindowRateLimiter:
        """Get or create rate limiter for specific configuration."""
        limiter_key = self._get_limiter_key(identifier, limit, window)

        if limiter_key not in self._limiters:
            self._limiters[limiter_key] = SlidingWindowRateLimiter(
                limit=limit,
                window_seconds=window,
                cache_service=self.cache_service,
                use_cache=self.cache_service is not None,
            )

        return self._limiters[limiter_key]

    async def check_rate_limit(
        self,
        key: str,
        limit: int | None = None,
        window: int | None = None,
        identifier: str | None = None,
    ) -> dict[str, Any]:
        """Check rate limit and return status.

        Args:
            key: Unique key for rate limiting (e.g., user_id, ip_address)
            limit: Maximum requests allowed (uses default if None)
            window: Time window in seconds (uses default if None)
            identifier: Rate limit type identifier (for multiple limits)

        Returns:
            Dictionary with rate limit status and metadata

        Raises:
            RateLimitExceeded: If rate limit is exceeded
        """
        # Use defaults from settings if not specified
        limit = limit or settings.rate_limit_requests
        window = window or settings.rate_limit_window
        identifier = identifier or "default"

        # Create full key including identifier
        full_key = f"{identifier}:{key}"

        async with self._lock:
            limiter = await self._get_or_create_limiter(
                identifier, limit, window
            )

        allowed, metadata = await limiter.is_allowed(full_key)

        if not allowed:
            raise RateLimitExceeded(
                message=f"Rate limit exceeded: {limit} requests per {window} seconds",
                limit=limit,
                window=window,
                retry_after=metadata.get("retry_after"),
                remaining=metadata.get("remaining"),
            )

        return {
            "allowed": True,
            "remaining": metadata["remaining"],
            "reset_time": metadata["reset_time"],
            "limit": limit,
            "window": window,
        }

    async def get_status(
        self,
        key: str,
        limit: int | None = None,
        window: int | None = None,
        identifier: str | None = None,
    ) -> dict[str, Any]:
        """Get rate limit status without consuming a request."""
        limit = limit or settings.rate_limit_requests
        window = window or settings.rate_limit_window
        identifier = identifier or "default"

        full_key = f"{identifier}:{key}"

        async with self._lock:
            limiter = await self._get_or_create_limiter(
                identifier, limit, window
            )

        return await limiter.get_status(full_key)

    async def reset(
        self,
        key: str,
        identifier: str | None = None,
    ) -> None:
        """Reset rate limit for a specific key."""
        identifier = identifier or "default"
        full_key = f"{identifier}:{key}"

        # Reset all limiters for this key
        for limiter_key, limiter in self._limiters.items():
            if limiter_key.startswith(f"{identifier}:"):
                await limiter.reset(full_key)

    async def cleanup_old_limiters(self, max_age: int = 3600) -> None:
        """Clean up old unused limiters to prevent memory leaks."""
        # This would be called periodically by a background task
        # For now, we rely on the cache TTL to clean up old data
        pass


class UnifiedRateLimitMiddleware(BaseHTTPMiddleware):
    """Unified rate limiting middleware supporting endpoint-specific limits."""

    def __init__(
        self,
        app,
        rate_limiter: UnifiedRateLimiter,
        default_limit: int | None = None,
        default_window: int | None = None,
        endpoint_limits: dict[str, tuple[int, int]] | None = None,
        key_func: Callable | None = None,
        skip_paths: list[str] | None = None,
    ):
        """Initialize unified rate limiting middleware.

        Args:
            app: FastAPI application
            rate_limiter: UnifiedRateLimiter instance
            default_limit: Default requests per window
            default_window: Default window size in seconds
            endpoint_limits: Per-endpoint limits {path: (limit, window)}
            key_func: Function to extract rate limit key from request
            skip_paths: Paths to skip rate limiting
        """
        super().__init__(app)
        self.rate_limiter = rate_limiter
        self.default_limit = default_limit or settings.rate_limit_requests
        self.default_window = default_window or settings.rate_limit_window
        self.endpoint_limits = endpoint_limits or {}
        self.key_func = key_func or self._default_key_func
        self.skip_paths = skip_paths or [
            "/healthz",
            "/readyz",
            "/live",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    def _default_key_func(self, request: Request) -> str:
        """Default function to extract rate limit key."""
        # Try to get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP-based limiting
        return self._get_client_ip(request)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return f"ip:{real_ip.strip()}"

        # Fallback to client IP
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _get_endpoint_limits(self, path: str) -> tuple[int, int]:
        """Get rate limits for specific endpoint."""
        # Check for exact path match first
        if path in self.endpoint_limits:
            return self.endpoint_limits[path]

        # Check for pattern matches (longest match first)
        matching_patterns = [
            (pattern, limits)
            for pattern, limits in self.endpoint_limits.items()
            if path.startswith(pattern)
        ]

        if matching_patterns:
            # Sort by pattern length (longest first) for most specific match
            matching_patterns.sort(key=lambda x: len(x[0]), reverse=True)
            return matching_patterns[0][1]

        return self.default_limit, self.default_window

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for certain paths
        if request.url.path in self.skip_paths:
            return await call_next(request)

        try:
            # Extract rate limit key
            key = self.key_func(request)
        except Exception as e:
            logger.warning(f"Failed to extract rate limit key: {e}")
            key = "unknown"

        # Get endpoint-specific limits
        path = request.url.path
        limit, window = self._get_endpoint_limits(path)

        # Create identifier for this endpoint
        identifier = f"endpoint:{path}"

        try:
            # Check rate limit
            status = await self.rate_limiter.check_rate_limit(
                key=key, limit=limit, window=window, identifier=identifier
            )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(
                status["remaining"]
            )
            response.headers["X-RateLimit-Reset"] = str(status["reset_time"])
            response.headers["X-RateLimit-Window"] = str(window)

            return response

        except RateLimitExceeded as e:
            logger.warning(
                "Rate limit exceeded",
                key=key,
                path=path,
                limit=e.limit,
                window=e.window,
                remaining=e.remaining,
            )

            # Return RFC 9457 compliant error response
            problem = RateLimitProblem(
                detail=e.message,
                retry_after=e.retry_after,
                limit=e.limit,
                window=e.window,
            )

            response = problem.to_response(request)

            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(e.limit or limit)
            response.headers["X-RateLimit-Remaining"] = str(
                e.remaining or 0
            )
            response.headers["X-RateLimit-Reset"] = str(
                int(time.time() + (e.window or window))
            )
            response.headers["X-RateLimit-Window"] = str(e.window or window)
            if e.retry_after:
                response.headers["Retry-After"] = str(e.retry_after)

            return response


# Global instances
_unified_rate_limiter: UnifiedRateLimiter | None = None


def get_unified_rate_limiter(cache_service=None) -> UnifiedRateLimiter:
    """Get global unified rate limiter instance."""
    global _unified_rate_limiter
    if _unified_rate_limiter is None:
        _unified_rate_limiter = UnifiedRateLimiter(cache_service=cache_service)
    return _unified_rate_limiter


def rate_limit(
    max_requests: int = 10,
    window_seconds: int = 60,
    identifier: str | None = None,
):
    """Decorator for rate limiting endpoints.

    Args:
        max_requests: Maximum requests allowed in the time window
        window_seconds: Time window in seconds
        identifier: Optional identifier for this rate limit (defaults to function name)

    Usage:
        @rate_limit(max_requests=5, window_seconds=60)
        async def my_endpoint():
            pass
    """
    from functools import wraps

    def decorator(func):
        nonlocal identifier
        if identifier is None:
            identifier = f"decorator:{func.__name__}"

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user info from arguments
            current_user = None
            request = None

            for arg in args:
                if hasattr(arg, "id"):  # Likely a user object
                    current_user = arg
                elif hasattr(arg, "client"):  # Likely a request object
                    request = arg

            # Try to get user from kwargs
            if not current_user:
                current_user = kwargs.get("current_user")

            if not request:
                request = kwargs.get("request")

            # Determine rate limit key
            if current_user and hasattr(current_user, "id"):
                key = f"user:{current_user.id}"
            elif request:
                # Extract IP from request
                client_ip = (
                    request.client.host if request.client else "unknown"
                )
                forwarded_for = request.headers.get("x-forwarded-for")
                if forwarded_for:
                    client_ip = forwarded_for.split(",")[0].strip()
                key = f"ip:{client_ip}"
            else:
                key = "unknown"

            # Check rate limit
            rate_limiter = get_unified_rate_limiter()
            try:
                await rate_limiter.check_rate_limit(
                    key=key,
                    limit=max_requests,
                    window=window_seconds,
                    identifier=identifier,
                )
            except RateLimitExceeded as e:
                raise RateLimitProblem(
                    detail=e.message,
                    retry_after=e.retry_after,
                    limit=e.limit,
                    window=e.window,
                ) from e

            return await func(*args, **kwargs)

        return wrapper

    return decorator