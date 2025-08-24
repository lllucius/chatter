"""Health check and monitoring endpoints."""


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.schemas.health import (
    HealthCheckResponse,
    LivenessCheckResponse,
    ReadinessCheckResponse,
)
from chatter.utils.database import get_session, health_check

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
    session: AsyncSession = Depends(get_session)
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
