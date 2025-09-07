"""Main FastAPI application for Chatter."""

import asyncio
import json

# Set up uvloop for better async performance (not in testing)
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from chatter.config import settings
from chatter.utils.database import close_database, init_database
from chatter.utils.logging import get_logger, setup_logging
from chatter.utils.problem import (
    InternalServerProblem,
    ProblemException,
)

if os.environ.get("ENVIRONMENT") != "testing":
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except ImportError:
        pass  # uvloop not available

# Set up logging
logger = get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging and metrics collection."""

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
                body=(
                    request_body.decode("utf-8", errors="ignore")
                    if request_body
                    else None
                ),
            )

        response = await call_next(request)

        # Calculate request duration
        duration = time.time() - start_time
        duration_ms = duration * 1000

        # Check if this is an error response (4xx or 5xx)
        is_error = response.status_code >= 400

        # Get correlation ID for metrics
        correlation_id = response.headers.get(
            'x-correlation-id', 'unknown'
        )

        # Check if request was rate limited
        rate_limited = response.status_code == 429

        # Record metrics
        try:
            from chatter.core.monitoring import record_request_metrics

            record_request_metrics(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                response_time_ms=duration_ms,
                correlation_id=correlation_id,
                rate_limited=rate_limited,
            )
        except Exception as e:
            logger.warning(
                "Failed to record request metrics", error=str(e)
            )

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

            logger.error(
                "HTTP Error Response",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
                duration_ms=duration_ms,
                correlation_id=correlation_id,
                request_headers=dict(request.headers),
                request_body=(
                    request_body.decode("utf-8", errors="ignore")
                    if request_body
                    else None
                ),
                response_headers=json.dumps(
                    dict(response.headers), indent=4
                ),
                response_body=response_body,
                rate_limited=rate_limited,
            )
        elif settings.debug_http_requests:
            # Normal debug logging for non-error responses
            logger.debug(
                "HTTP Response",
                status_code=response.status_code,
                headers=dict(response.headers),
                duration=duration,
                duration_ms=duration_ms,
                correlation_id=correlation_id,
            )
        else:
            # Always log basic request info for non-errors
            logger.info(
                "HTTP Request",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration,
                duration_ms=duration_ms,
                correlation_id=correlation_id,
            )

        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info(
        "Starting Chatter application", version=settings.app_version
    )

    # Validate configuration first
    try:
        from chatter.utils.config_validator import (
            validate_startup_configuration,
        )

        validate_startup_configuration()
        logger.info("Configuration validation passed")
    except Exception as e:
        logger.error("Configuration validation failed", error=str(e))
        if settings.is_production:
            raise
        else:
            logger.warning(
                "Continuing startup despite configuration issues (development mode)"
            )

    # Initialize database
    await init_database()
    logger.info("Database initialized")

    # Initialize built-in tool servers
    try:
        from chatter.services.toolserver import ToolServerService
        from chatter.utils.database import get_session_maker

        async_session = get_session_maker()
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

    # Start background job queue
    try:
        from chatter.services.job_queue import job_queue

        await job_queue.start()
        logger.info("Background job queue started")
    except Exception as e:
        logger.error("Failed to start job queue", error=str(e))

    # Start SSE event service
    try:
        from chatter.services.sse_events import sse_service

        await sse_service.start()
        logger.info("SSE event service started")
    except Exception as e:
        logger.error("Failed to start SSE event service", error=str(e))

    # Initialize unified event system
    try:
        from chatter.core.monitoring import MonitoringService
        from chatter.core.unified_events import initialize_event_system
        from chatter.utils.audit_logging import AuditLogger
        from chatter.utils.database import get_session_maker

        # Get database session for audit logger
        async_session = get_session_maker()
        audit_logger = AuditLogger()
        monitoring_service = MonitoringService()

        await initialize_event_system(audit_logger, monitoring_service)
        logger.info("Unified event system initialized")
    except Exception as e:
        logger.error(
            "Failed to initialize unified event system", error=str(e)
        )
        # Don't fail startup if unified events fail, use fallback

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

    # Stop background job queue
    try:
        from chatter.services.job_queue import job_queue

        await job_queue.stop()
        logger.info("Background job queue stopped")
    except Exception as e:
        logger.error("Failed to stop job queue", error=str(e))

    # Stop SSE event service
    try:
        from chatter.services.sse_events import sse_service

        await sse_service.stop()
        logger.info("SSE event service stopped")
    except Exception as e:
        logger.error("Failed to stop SSE event service", error=str(e))

    # Shutdown unified event system
    try:
        from chatter.core.unified_events import shutdown_event_system

        await shutdown_event_system()
        logger.info("Unified event system shutdown")
    except Exception as e:
        logger.error(
            "Failed to shutdown unified event system", error=str(e)
        )

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
        openapi_version="3.0.3",
        openapi_url=(
            "/openapi.json" if settings.is_development else None
        ),
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
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
            response.headers["Referrer-Policy"] = (
                "strict-origin-when-cross-origin"
            )
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
    if settings.trusted_hosts_for_env:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts_for_env,
        )

    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add correlation ID middleware (before logging)
    from chatter.utils.correlation import CorrelationIdMiddleware

    app.add_middleware(CorrelationIdMiddleware)

    # Add rate limiting middleware (unified system)
    from chatter.utils.unified_rate_limiter import (
        UnifiedRateLimitMiddleware,
        get_unified_rate_limiter,
    )

    # Initialize cache service for distributed rate limiting
    cache_service = None
    if settings.rate_limit_use_cache:
        try:
            from chatter.core.cache_factory import get_general_cache

            cache_service = get_general_cache()
            # Note: Cache service will connect during first use
        except Exception as e:
            logger.warning(
                f"Failed to initialize cache for rate limiting: {e}"
            )

    # Create unified rate limiter
    rate_limiter = get_unified_rate_limiter(cache_service=cache_service)

    # Define endpoint-specific limits
    endpoint_limits = {
        # Authentication endpoints (more restrictive)
        "/api/v1/auth/login": (
            settings.effective_rate_limit_auth_requests,
            settings.effective_rate_limit_auth_window,
        ),
        "/api/v1/auth/register": (
            settings.effective_rate_limit_auth_requests,
            settings.effective_rate_limit_auth_window,
        ),
        "/api/v1/auth/refresh": (
            settings.effective_rate_limit_auth_requests,
            settings.effective_rate_limit_auth_window,
        ),
        # Analytics endpoints
        "/api/v1/analytics/": (
            settings.rate_limit_analytics_requests,
            settings.rate_limit_analytics_window,
        ),
        # Model registry write operations
        "/api/v1/models/providers": (
            settings.rate_limit_model_write_requests,
            settings.rate_limit_model_write_window,
        ),
        "/api/v1/models/models": (
            settings.rate_limit_model_write_requests,
            settings.rate_limit_model_write_window,
        ),
        "/api/v1/models/embedding-spaces": (
            settings.rate_limit_model_write_requests,
            settings.rate_limit_model_write_window,
        ),
        # Model registry read operations (more permissive)
        "/api/v1/models/": (
            settings.rate_limit_model_read_requests,
            settings.rate_limit_model_read_window,
        ),
    }

    app.add_middleware(
        UnifiedRateLimitMiddleware,
        rate_limiter=rate_limiter,
        endpoint_limits=endpoint_limits,
    )

    # Add custom middleware
    app.add_middleware(LoggingMiddleware)

    # Add exception handlers
    from fastapi.exceptions import RequestValidationError

    from chatter.core.exceptions import AuthenticationError

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(
        request: Request, exc: AuthenticationError
    ) -> JSONResponse:
        """Handle AuthenticationError with RFC 9457 format."""
        logger.error(
            "Authentication error",
            url=str(request.url),
            method=request.method,
            error=str(exc),
        )
        from chatter.utils.problem import AuthenticationProblem

        auth_problem = AuthenticationProblem(detail=str(exc))
        return auth_problem.to_response(request)

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
        events,
        health,
        jobs,
        model_registry,
        plugins,
        profiles,
        prompts,
        toolserver,
        workflows,
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
        workflows.router,
        prefix=f"{settings.api_prefix}",
        tags=["Workflows"],
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
        events.router,
        prefix=f"{settings.api_prefix}/events",
        tags=["Events"],
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

    app.include_router(
        model_registry.router,
        prefix=f"{settings.api_prefix}/models",
        tags=["Model Registry"],
    )

    # Mount static files for the web interface
    import os

    static_dir = os.path.join(
        os.path.dirname(__file__), "../frontend/build"
    )
    if os.path.exists(static_dir):
        try:
            static_files_dir = os.path.join(static_dir, "static")
            if os.path.exists(static_files_dir):
                app.mount(
                    "/static",
                    StaticFiles(directory=static_files_dir),
                    name="static",
                )

                # Serve React app for all non-API routes
                @app.get("/{full_path:path}")
                async def serve_react_app(full_path: str):
                    # Don't intercept API routes, docs, or health checks
                    if (
                        full_path.startswith("api/")
                        or full_path.startswith("health")
                        or full_path.startswith("docs")
                        or full_path.startswith("redoc")
                        or full_path.startswith("openapi.json")
                    ):
                        return {"error": "Not found"}

                    from fastapi.responses import FileResponse

                    index_file = os.path.join(static_dir, "index.html")
                    if os.path.exists(index_file):
                        return FileResponse(index_file)
                    else:
                        return {"error": "Frontend not available"}

                logger.info(
                    "Frontend static files mounted successfully"
                )
            else:
                logger.warning(
                    "Frontend static directory not found, skipping mount"
                )
        except Exception as e:
            logger.warning(f"Failed to mount static files: {e}")
    else:
        logger.debug(
            "Frontend build directory not found, skipping frontend setup"
        )

    # Setup enhanced documentation
    try:
        from chatter.utils.documentation import setup_enhanced_docs

        setup_enhanced_docs(app)
        logger.info("Enhanced API documentation configured")
    except Exception as e:
        logger.warning(
            "Failed to setup enhanced documentation", error=str(e)
        )

    @app.get("/")
    async def root():
        """Root endpoint."""
        # If frontend is available, serve it; otherwise return API info
        static_dir = os.path.join(
            os.path.dirname(__file__), "../frontend/build"
        )
        if os.path.exists(static_dir):
            from fastapi.responses import FileResponse

            index_file = os.path.join(static_dir, "index.html")
            return FileResponse(index_file)
        else:
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
