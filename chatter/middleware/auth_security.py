"""Enhanced authentication middleware with rate limiting and security features."""

from datetime import UTC, datetime, timedelta

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from chatter.utils.logging import get_logger
from chatter.utils.unified_rate_limiter import get_unified_rate_limiter

logger = get_logger(__name__)


class AuthRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware specifically for authentication endpoints."""

    def __init__(self, app):
        super().__init__(app)
        self.rate_limiter = get_unified_rate_limiter()

        # Rate limiting configurations
        self.rate_limits = {
            "login": {"per_minute": 5, "per_hour": 20, "per_day": 100},
            "register": {
                "per_minute": 2,
                "per_hour": 10,
                "per_day": 20,
            },
            "password_reset": {
                "per_minute": 1,
                "per_hour": 5,
                "per_day": 10,
            },
            "refresh": {
                "per_minute": 10,
                "per_hour": 100,
                "per_day": 500,
            },
        }

    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting to authentication endpoints."""
        if self._is_auth_endpoint(request):
            try:
                await self._apply_auth_rate_limiting(request)
            except Exception as e:
                if hasattr(e, 'status_code') and e.status_code == 429:
                    return self._create_rate_limit_response(e)
                # Log error but don't block request if rate limiting fails
                logger.error(f"Rate limiting error: {e}")

        return await call_next(request)

    def _is_auth_endpoint(self, request: Request) -> bool:
        """Check if request is to an authentication endpoint."""
        path = str(request.url.path)
        auth_paths = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/auth/password-reset",
            "/api/v1/auth/change-password",
        ]
        return any(
            path.startswith(auth_path) for auth_path in auth_paths
        )

    async def _apply_auth_rate_limiting(self, request: Request):
        """Apply appropriate rate limiting based on endpoint."""
        client_ip = self._get_client_ip(request)
        path = str(request.url.path)

        # Determine endpoint type
        endpoint_type = None
        if "/login" in path:
            endpoint_type = "login"
        elif "/register" in path:
            endpoint_type = "register"
        elif "/password-reset" in path:
            endpoint_type = "password_reset"
        elif "/refresh" in path:
            endpoint_type = "refresh"

        if endpoint_type and endpoint_type in self.rate_limits:
            limits = self.rate_limits[endpoint_type]

            # Apply IP-based rate limiting
            await self._check_ip_rate_limits(
                client_ip, endpoint_type, limits
            )

            # Apply additional user-based limiting for login attempts
            if endpoint_type == "login":
                await self._check_login_user_rate_limits(request)

    async def _check_ip_rate_limits(
        self, client_ip: str, endpoint_type: str, limits: dict
    ):
        """Check IP-based rate limits."""
        # Per-minute limit
        if "per_minute" in limits:
            await self.rate_limiter.check_rate_limit(
                key=f"auth_{endpoint_type}_ip:{client_ip}",
                limit=limits["per_minute"],
                window=60,
                identifier=f"{endpoint_type}_per_minute",
            )

        # Per-hour limit
        if "per_hour" in limits:
            await self.rate_limiter.check_rate_limit(
                key=f"auth_{endpoint_type}_ip:{client_ip}",
                limit=limits["per_hour"],
                window=3600,
                identifier=f"{endpoint_type}_per_hour",
            )

        # Per-day limit
        if "per_day" in limits:
            await self.rate_limiter.check_rate_limit(
                key=f"auth_{endpoint_type}_ip:{client_ip}",
                limit=limits["per_day"],
                window=86400,
                identifier=f"{endpoint_type}_per_day",
            )

    async def _check_login_user_rate_limits(self, request: Request):
        """Check user-specific rate limits for login attempts."""
        try:
            # Extract user identifier from request body
            user_identifier = await self._extract_user_identifier(
                request
            )
            if user_identifier:
                # More restrictive user-specific limits
                await self.rate_limiter.check_rate_limit(
                    key=f"auth_login_user:{user_identifier}",
                    limit=10,  # 10 attempts per hour per user
                    window=3600,
                    identifier="login_user_per_hour",
                )
        except Exception as e:
            # Don't fail if we can't extract user identifier
            logger.debug(f"Could not extract user identifier: {e}")

    async def _extract_user_identifier(
        self, request: Request
    ) -> str | None:
        """Extract user identifier from login request."""
        try:
            # Read request body safely
            body = await request.body()
            if body:
                import json

                data = json.loads(body)
                return data.get("username") or data.get("email")
        except Exception:
            pass
        return None

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        # Check for forwarded headers (load balancer/proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"

    def _create_rate_limit_response(self, exception) -> JSONResponse:
        """Create standardized rate limit response."""
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "type": "about:blank",
                "title": "Rate Limit Exceeded",
                "status": 429,
                "detail": "Too many requests. Please try again later.",
                "instance": f"/auth/rate-limit/{datetime.now(UTC).isoformat()}",
                "retry_after": getattr(exception, 'retry_after', 60),
            },
            headers={
                "Retry-After": str(
                    getattr(exception, 'retry_after', 60)
                ),
                "X-RateLimit-Limit": str(
                    getattr(exception, 'limit', 'unknown')
                ),
                "X-RateLimit-Remaining": str(
                    getattr(exception, 'remaining', 0)
                ),
                "X-RateLimit-Reset": str(
                    int(
                        (
                            datetime.now(UTC) + timedelta(seconds=60)
                        ).timestamp()
                    )
                ),
            },
        )


def setup_auth_middleware(app):
    """Setup all authentication middleware."""
    app.add_middleware(AuthRateLimitMiddleware)
