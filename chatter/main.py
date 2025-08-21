"""Main FastAPI application for Chatter."""

import asyncio
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvloop
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from chatter.config import settings
from chatter.utils.logging import setup_logging, get_logger
from chatter.utils.database import init_database, close_database
from chatter.api import auth, chat, documents, analytics, health, profiles, toolserver

# Set up uvloop for better async performance
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass  # uvloop not available

# Set up logging
logger = get_logger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Collect metrics for each request."""
        start_time = time.time()
        
        response = await call_next(request)
        
        # Extract endpoint from route
        endpoint = request.url.path
        if hasattr(request, 'route') and request.route:
            endpoint = request.route.path
        
        # Record metrics
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(time.time() - start_time)
        
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Log requests and responses when debug logging is enabled."""
        start_time = time.time()
        
        # Log request if debug enabled
        if settings.debug_http_requests:
            body = b""
            if request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                # Re-create request with body for downstream processing
                request._body = body
            
            logger.debug(
                "HTTP Request",
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                body=body.decode('utf-8', errors='ignore') if body else None
            )
        
        response = await call_next(request)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log response if debug enabled
        if settings.debug_http_requests:
            logger.debug(
                "HTTP Response",
                status_code=response.status_code,
                headers=dict(response.headers),
                duration=duration
            )
        else:
            # Always log basic request info
            logger.info(
                "HTTP Request",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                duration=duration
            )
        
        return response


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting Chatter application", version=settings.app_version)
    
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
        logger.error("Failed to initialize built-in tool servers", error=str(e))
    
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
        openapi_url="/openapi.json" if settings.is_development else None,
    )
    
    # Add security middleware
    if settings.security_headers_enabled:
        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
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
            TrustedHostMiddleware,
            allowed_hosts=settings.trusted_hosts
        )
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Add custom middleware
    app.add_middleware(LoggingMiddleware)
    
    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware)
    
    # Add exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Global exception handler."""
        logger.exception(
            "Unhandled exception",
            url=str(request.url),
            method=request.method,
            exception=str(exc)
        )
        
        if settings.is_development:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal server error",
                    "detail": str(exc),
                    "type": type(exc).__name__
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"}
            )
    
    # Add Prometheus metrics endpoint
    if settings.enable_metrics:
        @app.get(settings.metrics_path, include_in_schema=False)
        async def metrics():
            """Prometheus metrics endpoint."""
            return Response(
                generate_latest(),
                media_type=CONTENT_TYPE_LATEST
            )
    
    # Include API routers
    app.include_router(
        health.router,
        tags=["Health"]
    )
    
    app.include_router(
        auth.router,
        prefix=f"{settings.api_prefix}/auth",
        tags=["Authentication"]
    )
    
    app.include_router(
        chat.router,
        prefix=f"{settings.api_prefix}/chat",
        tags=["Chat"]
    )
    
    app.include_router(
        documents.router,
        prefix=f"{settings.api_prefix}/documents",
        tags=["Documents"]
    )
    
    app.include_router(
        profiles.router,
        prefix=f"{settings.api_prefix}/profiles",
        tags=["Profiles"]
    )
    
    app.include_router(
        analytics.router,
        prefix=f"{settings.api_prefix}/analytics",
        tags=["Analytics"]
    )
    
    app.include_router(
        toolserver.router,
        prefix=f"{settings.api_prefix}/toolservers",
        tags=["Tool Servers"]
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