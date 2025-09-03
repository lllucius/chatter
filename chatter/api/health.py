"""Health check and monitoring endpoints."""

from fastapi import APIRouter, Depends
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
from chatter.utils.problem import InternalServerProblem

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
) -> ReadinessCheckResponse:
    """Readiness check endpoint with database connectivity.

    This checks that the application is ready to serve traffic by validating
    that all external dependencies (database, etc.) are available.

    Args:
        session: Database session

    Returns:
        Readiness status with detailed checks
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

    return ReadinessCheckResponse(
        status=ReadinessStatus.READY if all_healthy else ReadinessStatus.NOT_READY,
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
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
    try:
        from datetime import datetime, timezone
        from chatter.utils.monitoring import metrics_collector

        overall_stats = metrics_collector.get_overall_stats(
            window_minutes=60
        )
        health_metrics = metrics_collector.get_health_metrics()
        endpoint_stats = metrics_collector.get_endpoint_stats()

        # Use real timestamp
        current_timestamp = datetime.now(timezone.utc).isoformat()

        return MetricsResponse(
            timestamp=current_timestamp,
            service="chatter",
            version=settings.app_version,
            environment=settings.environment,
            health=health_metrics,
            performance=overall_stats,
            endpoints=endpoint_stats,
        )
    except Exception as e:
        # No fallback metrics - raise proper problem instead
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
        from chatter.utils.monitoring import metrics_collector

        trace = metrics_collector.get_correlation_trace(correlation_id)

        return CorrelationTraceResponse(
            correlation_id=correlation_id,
            trace_length=len(trace),
            requests=trace,
        )
    except Exception as e:
        # No fallback response - raise proper problem instead
        raise InternalServerProblem(
            detail=f"Failed to get trace: {str(e)}"
        ) from e
