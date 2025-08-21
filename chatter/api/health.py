"""Health check and monitoring endpoints."""

from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.config import settings
from chatter.utils.database import get_session, health_check

router = APIRouter()


@router.get("/healthz")
async def health_check_endpoint() -> Dict[str, Any]:
    """Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "chatter",
        "version": settings.app_version,
        "environment": settings.environment,
    }


@router.get("/readyz")
async def readiness_check(
    session: AsyncSession = Depends(get_session)
) -> Dict[str, Any]:
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
        check.get("status") == "healthy" 
        for check in checks.values()
    )
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "service": "chatter",
        "version": settings.app_version,
        "environment": settings.environment,
        "checks": checks,
    }


@router.get("/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check endpoint for Kubernetes.
    
    Returns:
        Simple liveness status
    """
    return {"status": "alive"}