"""Health check and monitoring endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.schemas.health import (
    CorrelationTraceResponse,
    HealthCheckResponse,
    HealthStatus,
    MetricsResponse,
    ReadinessCheckResponse,
    ReadinessStatus,
)
from chatter.utils.database import get_session_generator, health_check
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem

logger = get_logger(__name__)
router = APIRouter()


@router.get("/healthz", response_model=HealthCheckResponse)
async def health_check_endpoint() -> HealthCheckResponse:
    """Basic health check endpoint.

    Returns:
        Health status
    """
    return HealthCheckResponse(
        status=HealthStatus.HEALTHY,
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/readyz", response_model=ReadinessCheckResponse)
async def readiness_check(
    session: AsyncSession = Depends(get_session_generator),
) -> JSONResponse:
    """Readiness check endpoint with database connectivity.

    This checks that the application is ready to serve traffic by validating
    that all external dependencies (database, etc.) are available.

    Args:
        session: Database session

    Returns:
        Readiness status with detailed checks.
        Returns 200 if ready, 503 if not ready.
    """
    checks = {}
    
    # Perform database health check with timeout
    try:
        import asyncio
        # Use the provided session and add timeout
        db_health = await asyncio.wait_for(
            health_check(session), 
            timeout=5.0  # 5 second timeout
        )
    except asyncio.TimeoutError:
        db_health = {
            "status": "unhealthy",
            "connected": False,
            "error": "Database health check timeout (>5s)"
        }
    except Exception as e:
        db_health = {
            "status": "unhealthy", 
            "connected": False,
            "error": f"Database health check failed: {str(e)}"
        }
    
    checks["database"] = db_health

    # Could add more checks here (Redis, external APIs, etc.)
    # checks["redis"] = await redis_health_check()
    # checks["external_api"] = await external_api_health_check()

    # Determine overall status
    all_healthy = all(
        check.get("status") == "healthy" for check in checks.values()
    )

    response_data = ReadinessCheckResponse(
        status=ReadinessStatus.READY if all_healthy else ReadinessStatus.NOT_READY,
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )

    # Return 503 if not ready (Kubernetes standard)
    status_code = status.HTTP_200_OK if all_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JSONResponse(
        content=response_data.model_dump(),
        status_code=status_code
    )


@router.get("/live", response_model=HealthCheckResponse)
async def liveness_check() -> HealthCheckResponse:
    """Liveness check endpoint for Kubernetes.

    This is a simple liveness probe that checks if the application process
    is running and responding. It should NOT check external dependencies.

    Returns:
        Health status indicating the application is alive
    """
    # Simple liveness check - just return that the process is running
    # This should never fail unless the process is dead
    return HealthCheckResponse(
        status=HealthStatus.ALIVE,
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics() -> MetricsResponse:
    """Get application metrics and monitoring data.

    Returns:
        Application metrics including performance and health data
    """
    from datetime import datetime, timezone
    
    # Use real timestamp
    current_timestamp = datetime.now(timezone.utc).isoformat()
    
    # Default empty metrics in case monitoring is unavailable
    health_metrics = {"status": "unknown", "checks_available": False}
    performance_stats = {"requests": 0, "errors": 0, "response_time_ms": 0}
    endpoint_stats = {}
    
    try:
        from chatter.core.monitoring import get_monitoring_service

        # Try to get metrics with individual fallbacks
        try:
            monitoring_service = await get_monitoring_service()
            health_data = monitoring_service.get_system_health()
            health_metrics.update(health_data)
            
            # Get endpoint stats
            endpoint_data = monitoring_service.stats_by_endpoint
            endpoint_stats.update({k: v.__dict__ for k, v in endpoint_data.items()})
            endpoint_stats.update(endpoint_data)
        except Exception as e:
            logger.warning(f"Failed to get endpoint stats: {e}")

        return MetricsResponse(
            timestamp=current_timestamp,
            service="chatter",
            version=settings.app_version,
            environment=settings.environment,
            health=health_metrics,
            performance=performance_stats,
            endpoints=endpoint_stats,
        )
        
    except ImportError:
        # Monitoring module not available
        logger.warning("Monitoring module not available, returning basic metrics")
        return MetricsResponse(
            timestamp=current_timestamp,
            service="chatter",
            version=settings.app_version,
            environment=settings.environment,
            health=health_metrics,
            performance=performance_stats,
            endpoints=endpoint_stats,
        )
    except Exception as e:
        # Other unexpected errors
        raise InternalServerProblem(
            detail=f"Metrics collection failed: {str(e)}"
        ) from e


@router.get(
    "/trace/{correlation_id}", response_model=CorrelationTraceResponse
)
async def get_correlation_trace(
    correlation_id: str,
) -> CorrelationTraceResponse:
    """Get trace of all requests for a correlation ID.

    Args:
        correlation_id: The correlation ID to trace

    Returns:
        List of requests associated with the correlation ID
    """
    try:
        from chatter.core.monitoring import get_monitoring_service

        monitoring_service = await get_monitoring_service()
        trace = monitoring_service.get_correlation_trace(correlation_id)

        return CorrelationTraceResponse(
            correlation_id=correlation_id,
            trace_length=len(trace),
            requests=trace,
        )
    except ImportError:
        # Monitoring module not available
        logger.warning("Monitoring module not available for correlation trace")
        return CorrelationTraceResponse(
            correlation_id=correlation_id,
            trace_length=0,
            requests=[],
        )
    except Exception as e:
        # Log the error but don't expose internal details
        logger.error(f"Failed to get correlation trace for {correlation_id}: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get trace for correlation ID: {correlation_id}"
        ) from e
