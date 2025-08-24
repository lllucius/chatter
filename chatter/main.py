"""Main FastAPI application for Chatter."""

import asyncio
import json
import time
import traceback
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from chatter.config import settings
from chatter.utils.database import close_database, init_database
from chatter.utils.logging import get_logger, setup_logging
from chatter.utils.problem import (
    InternalServerProblem,
    ProblemException,
)

# Set up uvloop for better async performance
try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass  # uvloop not available

# Set up logging
logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log requests and responses when debug logging is enabled."""
        start_time = time.time()

        # Always capture request body for potential error logging
        request_body = b""
        if request.method in ["POST", "PUT", "PATCH"]:
            request_body = await request.body()
            # Re-create request with body for downstream processing
            request._body = request_body

        # Log request if debug enabled
        if settings.debug_http_requests:
            logger.debug(
                "HTTP Request",
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                body=request_body.decode("utf-8", errors="ignore")
                if request_body
                else None,
            )

        response = await call_next(request)
        print("TYPE", type(response))

        # Calculate request duration
        duration = time.time() - start_time

        # Check if this is an error response (4xx or 5xx)
        is_error = response.status_code >= 400

        # For error responses, always log detailed information regardless of debug setting
        if is_error:
            # Try to capture response body for error cases
            response_body = None
            try:
                # For streaming responses, we can't easily capture the body
                # But for most error responses, we can try to read it
                if hasattr(response, "body") and response.body:
                    response_body = response.body.decode(
                        "utf-8", errors="ignore"
                    )
            except Exception:
                # If we can't capture response body, that's okay
                pass

            # Capture current stack trace to help identify where the error originated
            try:
                # Get the current stack trace (this will show the call path through the middleware)
                traceback.format_stack()
            except Exception:
                pass

            logger.error(
                "HTTP Error Response",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
                request_headers=dict(request.headers),
                request_body=request_body.decode(
                    "utf-8", errors="ignore"
                )
                if request_body
                else None,
                response_headers=json.dumps(
                    dict(response.headers), indent=4
                ),
                response_body=response_body,
                # stack_trace=json.dumps(stack_trace)
            )
        elif settings.debug_http_requests:
            # Normal debug logging for non-error responses
            logger.debug(
                "HTTP Response",
                status_code=response.status_code,
                headers=dict(response.headers),
                duration=duration,
            )
        else:
            # Always log basic request info for non-errors
            logger.info(
                "HTTP Request",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
            )

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info(
        "Starting Chatter application", version=settings.app_version
    )

    # Initialize database
    await init_database()
    logger.info("Database initialized")

    # Initialize built-in tool servers
    try:
        from chatter.services.toolserver import ToolServerService
        from chatter.utils.database import get_session_factory

        async_session = get_session_factory()
        async with async_session() as session:
            service = ToolServerService(session)
            await service.initialize_builtin_servers()

        logger.info("Built-in tool servers initialized")
    except Exception as e:
        logger.error(
            "Failed to initialize built-in tool servers", error=str(e)
        )

    # Start background scheduler
    try:
        from chatter.services.scheduler import start_scheduler

        await start_scheduler()
        logger.info("Tool server scheduler started")
    except Exception as e:
        logger.error("Failed to start scheduler", error=str(e))

    # Application startup complete
    logger.info("Chatter application started successfully")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Chatter application")

    # Stop scheduler
    try:
        from chatter.services.scheduler import stop_scheduler

        await stop_scheduler()
        logger.info("Tool server scheduler stopped")
    except Exception as e:
        logger.error("Failed to stop scheduler", error=str(e))

    await close_database()
    logger.info("Chatter application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""

    # Set up logging first
    setup_logging()

    # Create FastAPI app
    app = FastAPI(
        title=settings.api_title,
        description=settings.api_description,
        version=settings.api_version,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json"
        if settings.is_development
        else None,
    )

    # Add security middleware
    if settings.security_headers_enabled:

        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            """Add security headers to all responses."""
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"
            response.headers[
                "Referrer-Policy"
            ] = "strict-origin-when-cross-origin"
            return response

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Add trusted host middleware
    if settings.trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts
        )

    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)

    # Add exception handlers
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(ProblemException)
    async def problem_exception_handler(
        request: Request, exc: ProblemException
    ) -> JSONResponse:
        """Handle ProblemException instances."""
        logger.error(
            "Problem exception",
            url=str(request.url),
            method=request.method,
            status_code=exc.status_code,
            title=exc.title,
            detail=exc.detail,
        )
        return exc.to_response(request)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with RFC 9457 format."""
        logger.error(
            "Validation exception",
            url=str(request.url),
            method=request.method,
            errors=[str(error) for error in exc.errors()],
        )
        from chatter.utils.problem import ValidationProblem

        validation_problem = ValidationProblem(
            detail="The request contains invalid data",
            validation_errors=exc.errors(),
        )
        return validation_problem.to_response(request)

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Global exception handler."""
        logger.exception(
            "Unhandled exception",
            url=str(request.url),
            method=request.method,
            exception=str(exc),
        )

        if settings.is_development:
            problem = InternalServerProblem(
                detail=f"An internal server error occurred: {str(exc)}",
                error_type=type(exc).__name__,
                error_traceback=str(exc) if settings.debug else None,
            )
        else:
            problem = InternalServerProblem()

        return problem.to_response(request)

    # --- DELAYED IMPORTS: Routers registered here only ---
    from chatter.api import (
        ab_testing,
        agents,
        analytics,
        auth,
        chat,
        data_management,
        documents,
        health,
        jobs,
        plugins,
        profiles,
        prompts,
        toolserver,
        webhooks,
    )

    app.include_router(health.router, tags=["Health"])

    app.include_router(
        auth.router,
        prefix=f"{settings.api_prefix}/auth",
        tags=["Authentication"],
    )

    app.include_router(
        chat.router, prefix=f"{settings.api_prefix}/chat", tags=["Chat"]
    )

    app.include_router(
        documents.router,
        prefix=f"{settings.api_prefix}/documents",
        tags=["Documents"],
    )

    app.include_router(
        profiles.router,
        prefix=f"{settings.api_prefix}/profiles",
        tags=["Profiles"],
    )

    app.include_router(
        prompts.router,
        prefix=f"{settings.api_prefix}/prompts",
        tags=["Prompts"],
    )

    app.include_router(
        analytics.router,
        prefix=f"{settings.api_prefix}/analytics",
        tags=["Analytics"],
    )

    app.include_router(
        toolserver.router,
        prefix=f"{settings.api_prefix}/toolservers",
        tags=["Tool Servers"],
    )

    # New API endpoints from PR #23
    app.include_router(
        agents.router,
        prefix=f"{settings.api_prefix}/agents",
        tags=["Agents"],
    )

    app.include_router(
        ab_testing.router,
        prefix=f"{settings.api_prefix}/ab-tests",
        tags=["A/B Testing"],
    )

    app.include_router(
        webhooks.router,
        prefix=f"{settings.api_prefix}/webhooks",
        tags=["Webhooks"],
    )

    app.include_router(
        plugins.router,
        prefix=f"{settings.api_prefix}/plugins",
        tags=["Plugins"],
    )

    app.include_router(
        jobs.router,
        prefix=f"{settings.api_prefix}/jobs",
        tags=["Jobs"],
    )

    app.include_router(
        data_management.router,
        prefix=f"{settings.api_prefix}/data",
        tags=["Data Management"],
    )

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Welcome to Chatter API",
            "version": settings.app_version,
            "docs": "/docs" if settings.is_development else None,
        }

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "chatter.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        workers=settings.workers if not settings.reload else 1,
        log_level=settings.log_level.lower(),
        access_log=settings.debug_http_requests,
    )
