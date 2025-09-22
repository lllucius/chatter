"""Enhanced security headers middleware for production hardening."""

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    def __init__(self, app, strict_transport_security: bool = True):
        """Initialize security headers middleware.

        Args:
            app: FastAPI application instance
            strict_transport_security: Whether to add HSTS headers
        """
        super().__init__(app)
        self.strict_transport_security = strict_transport_security

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none'"
        )

        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"

        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer Policy
        response.headers[
            "Referrer-Policy"
        ] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=(), "
            "payment=(), usb=(), magnetometer=(), gyroscope=(), "
            "accelerometer=(), ambient-light-sensor=()"
        )

        # X-Permitted-Cross-Domain-Policies
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # Cross-Origin-Embedder-Policy
        response.headers[
            "Cross-Origin-Embedder-Policy"
        ] = "require-corp"

        # Cross-Origin-Opener-Policy
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"

        # Cross-Origin-Resource-Policy
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"

        # Strict-Transport-Security (HTTPS only)
        if (
            self.strict_transport_security
            and request.url.scheme == "https"
        ):
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains; preload"

        # Remove server information
        if "Server" in response.headers:
            del response.headers["Server"]
        if "X-Powered-By" in response.headers:
            del response.headers["X-Powered-By"]

        return response


class ContentTypeValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate content types for security."""

    ALLOWED_CONTENT_TYPES = {
        "application/json",
        "application/x-www-form-urlencoded",
        "multipart/form-data",
        "text/plain",
        "application/pdf",
        "text/markdown",
        "text/html",
        "application/xml",
        "text/xml",
    }

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Validate content type for security."""
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = (
                request.headers.get("content-type", "")
                .split(";")[0]
                .strip()
            )

            if (
                content_type
                and content_type not in self.ALLOWED_CONTENT_TYPES
            ):
                logger.warning(
                    "Blocked request with invalid content type",
                    content_type=content_type,
                    path=request.url.path,
                )
                from fastapi import HTTPException

                raise HTTPException(
                    status_code=415,
                    detail=f"Content type '{content_type}' not allowed",
                )

        return await call_next(request)
