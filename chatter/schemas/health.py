"""Health check schemas for API responses."""

from typing import Any

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")


class DatabaseHealthCheck(BaseModel):
    """Schema for database health check."""

    status: str = Field(..., description="Database status")
    latency_ms: float | None = Field(
        None, description="Database latency in milliseconds"
    )
    error: str | None = Field(
        None, description="Error message if unhealthy"
    )


class ReadinessCheckResponse(BaseModel):
    """Schema for readiness check response."""

    status: str = Field(..., description="Readiness status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    checks: dict[str, Any] = Field(
        ..., description="Health check results"
    )


class LivenessCheckResponse(BaseModel):
    """Schema for liveness check response."""

    status: str = Field(..., description="Liveness status")
