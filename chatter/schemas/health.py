"""Health check schemas for API responses."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    ALIVE = "alive"
    UNHEALTHY = "unhealthy"


class ReadinessStatus(str, Enum):
    """Readiness status enumeration."""

    READY = "ready"
    NOT_READY = "not_ready"


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: HealthStatus = Field(..., description="Health status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")


class DatabaseHealthCheck(BaseModel):
    """Schema for database health check."""

    status: HealthStatus = Field(..., description="Database status")
    connected: bool = Field(
        ..., description="Database connection status"
    )
    response_time_ms: float | None = Field(
        None, description="Database response time in milliseconds"
    )
    database_type: str | None = Field(default=None, description="Database type")
    error: str | None = Field(
        None, description="Error message if unhealthy"
    )


class ReadinessCheckResponse(BaseModel):
    """Schema for readiness check response."""

    status: ReadinessStatus = Field(..., description="Readiness status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    checks: dict[str, Any] = Field(
        ..., description="Health check results"
    )


class LivenessCheckResponse(BaseModel):
    """Schema for liveness check response."""

    status: HealthStatus = Field(..., description="Liveness status")


class MetricsResponse(BaseModel):
    """Schema for application metrics response."""

    timestamp: str = Field(
        ..., description="Metrics collection timestamp (ISO 8601)"
    )
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    environment: str = Field(..., description="Environment")
    health: dict[str, Any] = Field(..., description="Health metrics")
    performance: dict[str, Any] = Field(
        ..., description="Performance statistics"
    )
    endpoints: dict[str, Any] = Field(
        ..., description="Endpoint statistics"
    )


class CorrelationTraceResponse(BaseModel):
    """Schema for correlation trace response."""

    correlation_id: str = Field(..., description="Correlation ID")
    trace_length: int = Field(
        ..., description="Number of requests in trace"
    )
    requests: list[dict[str, Any]] = Field(
        ..., description="List of requests in trace"
    )
