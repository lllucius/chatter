"""Health check and monitoring endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.schemas.health import (
    CorrelationTraceResponse,
    HealthCheckResponse,
    MetricsResponse,
    ReadinessCheckResponse,
)
from chatter.utils.database import get_session, health_check
from chatter.utils.problem import InternalServerProblem

router = APIRouter()


@router.get("/healthz", response_model=HealthCheckResponse)
async def health_check_endpoint() -> HealthCheckResponse:
    """Basic health check endpoint.

    Returns:
        Health status
    """
    return HealthCheckResponse(
        status="healthy",
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
    )


@router.get("/readyz", response_model=ReadinessCheckResponse)
async def readiness_check(
    session: AsyncSession = Depends(get_session),
) -> ReadinessCheckResponse:
    """Readiness check endpoint with database connectivity.

    Args:
        session: Database session

    Returns:
        Readiness status with detailed checks
    """
    # Perform database health check
    db_health = await health_check()

    checks = {
        "database": db_health,
    }

    # Determine overall status
    all_healthy = all(
        check.get("status") == "healthy" for check in checks.values()
    )

    return ReadinessCheckResponse(
        status="ready" if all_healthy else "not_ready",
        service="chatter",
        version=settings.app_version,
        environment=settings.environment,
        checks=checks,
    )


@router.get("/live", response_model=HealthCheckResponse)
async def liveness_check() -> HealthCheckResponse:
    """Liveness check endpoint for Kubernetes (alias for /healthz).

    Returns:
        Health status (same as /healthz)
    """
    return HealthCheckResponse(
        status="healthy",
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
        from chatter.utils.monitoring import metrics_collector

        overall_stats = metrics_collector.get_overall_stats(
            window_minutes=60
        )
        health_metrics = metrics_collector.get_health_metrics()
        endpoint_stats = metrics_collector.get_endpoint_stats()

        return MetricsResponse(
            timestamp="2024-01-01T12:00:00Z",  # Would use actual timestamp
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
