"""Rate limiting middleware with proper headers."""

import time
from collections.abc import Awaitable, Callable
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware with X-RateLimit headers."""

    def __init__(self, app: Any, requests_per_minute: int = 60,
                 requests_per_hour: int = 1000) -> None:
        """Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Requests allowed per minute
            requests_per_hour: Requests allowed per hour
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage for request tracking
        # Format: {client_id: [list of timestamps]}
        self.request_history: dict[str, list[float]] = {}

    def _get_client_identifier(self, request: Request) -> str:
        """Get unique client identifier.

        Args:
            request: The incoming request

        Returns:
            Client identifier (IP or user ID)
        """
        # Try to get user ID from authorization header if present
        auth_header = request.headers.get("authorization")
        if auth_header:
            # Use a hash of the auth token as identifier
            import hashlib
            return hashlib.sha256(auth_header.encode()).hexdigest()[:16]

        # Fall back to client IP
        client_ip: str = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # forwarded_for is guaranteed to be str here due to the if check
            client_ip = forwarded_for.split(",")[0].strip()

        return client_ip

    def _clean_old_requests(self, client_id: str, window_seconds: int) -> None:
        """Remove old requests outside the time window.

        Args:
            client_id: Client identifier
            window_seconds: Time window in seconds
        """
        if client_id not in self.request_history:
            self.request_history[client_id] = []
            return

        current_time = time.time()
        self.request_history[client_id] = [
            req_time for req_time in self.request_history[client_id]
            if current_time - req_time < window_seconds
        ]

    def _check_rate_limit(self, client_id: str) -> tuple[bool, dict[str, str]]:
        """Check if client is within rate limits.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (allowed, headers_dict)
        """
        current_time = time.time()

        # Clean old requests for both windows
        self._clean_old_requests(client_id, 60)  # 1 minute
        self._clean_old_requests(client_id, 3600)  # 1 hour

        if client_id not in self.request_history:
            self.request_history[client_id] = []

        requests_last_minute = len([
            req_time for req_time in self.request_history[client_id]
            if current_time - req_time < 60
        ])

        requests_last_hour = len([
            req_time for req_time in self.request_history[client_id]
            if current_time - req_time < 3600
        ])

        # Calculate remaining requests
        remaining_minute = max(0, self.requests_per_minute - requests_last_minute)
        remaining_hour = max(0, self.requests_per_hour - requests_last_hour)

        # Calculate reset times
        reset_minute = int(current_time) + (60 - int(current_time) % 60)
        reset_hour = int(current_time) + (3600 - int(current_time) % 3600)

        # Prepare headers
        headers = {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Minute": str(remaining_minute),
            "X-RateLimit-Remaining-Hour": str(remaining_hour),
            "X-RateLimit-Reset-Minute": str(reset_minute),
            "X-RateLimit-Reset-Hour": str(reset_hour),
        }

        # Check if request should be allowed
        allowed = (requests_last_minute < self.requests_per_minute and
                  requests_last_hour < self.requests_per_hour)

        if allowed:
            # Add current request to history
            self.request_history[client_id].append(current_time)
        else:
            # Add retry-after header for rate limited requests
            if requests_last_minute >= self.requests_per_minute:
                headers["Retry-After"] = str(60 - int(current_time) % 60)
            else:
                headers["Retry-After"] = str(3600 - int(current_time) % 3600)

        return allowed, headers

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """Apply rate limiting with headers.

        Args:
            request: The incoming request
            call_next: The next middleware in the chain

        Returns:
            Response with rate limiting headers

        Raises:
            HTTPException: If rate limit exceeded
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/healthz", "/readyz", "/live", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        client_id = self._get_client_identifier(request)
        allowed, rate_headers = self._check_rate_limit(client_id)

        if not allowed:
            logger.warning(
                "Rate limit exceeded",
                client_id=client_id,
                path=request.url.path,
                method=request.method
            )

            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "type": "https://tools.ietf.org/html/rfc9457",
                    "title": "Too Many Requests",
                    "status": 429,
                    "detail": "Rate limit exceeded. Please try again later.",
                    "instance": str(request.url.path)
                },
                headers=rate_headers
            )

        # Process request
        response = await call_next(request)

        # Add rate limiting headers to response
        for header_name, header_value in rate_headers.items():
            response.headers[header_name] = header_value

        return response


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class RateLimiter:
    """Generic rate limiter interface."""
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed."""
        raise NotImplementedError
    
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests in window."""
        raise NotImplementedError


class MemoryRateLimiter(RateLimiter):
    """In-memory rate limiter implementation."""
    
    def __init__(self):
        self.requests: dict[str, list[float]] = {}
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed."""
        current_time = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < window
        ]
        
        if len(self.requests[key]) < limit:
            self.requests[key].append(current_time)
            return True
        
        return False
    
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests in window."""
        current_time = time.time()
        
        if key not in self.requests:
            return limit
        
        # Clean old requests
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if current_time - req_time < window
        ]
        
        return max(0, limit - len(self.requests[key]))


class RedisRateLimiter(RateLimiter):
    """Redis-based rate limiter implementation."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed using Redis."""
        current_time = int(time.time())
        pipe = self.redis.pipeline()
        
        # Use sliding window with Redis
        pipe.zremrangebyscore(key, 0, current_time - window)
        pipe.zcard(key)
        pipe.zadd(key, {str(current_time): current_time})
        pipe.expire(key, window)
        
        results = await pipe.execute()
        request_count = results[1]
        
        return request_count < limit
    
    async def get_remaining(self, key: str, limit: int, window: int) -> int:
        """Get remaining requests in window using Redis."""
        current_time = int(time.time())
        
        # Clean old entries and count current
        await self.redis.zremrangebyscore(key, 0, current_time - window)
        current_count = await self.redis.zcard(key)
        
        return max(0, limit - current_count)


def get_client_ip(request: Request) -> str:
    """Extract client IP from request."""
    client_ip = "unknown"
    
    if request.client:
        client_ip = request.client.host
    
    # Check for forwarded headers
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        client_ip = real_ip.strip()
    
    return client_ip


def create_rate_limit_key(request: Request, prefix: str = "rate_limit") -> str:
    """Create rate limit key from request."""
    client_ip = get_client_ip(request)
    
    # Try to get user ID from auth
    auth_header = request.headers.get("authorization")
    if auth_header:
        import hashlib
        user_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
        return f"{prefix}:user:{user_hash}"
    
    return f"{prefix}:ip:{client_ip}"
