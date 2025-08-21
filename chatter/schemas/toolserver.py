"""Tool server schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from chatter.models.toolserver import ServerStatus, ToolStatus


# Base schemas
class ToolServerBase(BaseModel):
    """Base schema for tool server."""

    name: str = Field(..., min_length=1, max_length=100, description="Server name")
    display_name: str = Field(..., min_length=1, max_length=200, description="Display name")
    description: str | None = Field(None, description="Server description")
    command: str = Field(..., min_length=1, max_length=500, description="Command to start server")
    args: list[str] = Field(default_factory=list, description="Command arguments")
    env: dict[str, str] | None = Field(None, description="Environment variables")
    auto_start: bool = Field(True, description="Auto-start server on system startup")
    auto_update: bool = Field(True, description="Auto-update server capabilities")
    max_failures: int = Field(3, ge=1, le=10, description="Maximum consecutive failures before disabling")


class ToolServerCreate(ToolServerBase):
    """Schema for creating a tool server."""
    pass


class ToolServerUpdate(BaseModel):
    """Schema for updating a tool server."""

    display_name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None)
    command: str | None = Field(None, min_length=1, max_length=500)
    args: list[str] | None = Field(None)
    env: dict[str, str] | None = Field(None)
    auto_start: bool | None = Field(None)
    auto_update: bool | None = Field(None)
    max_failures: int | None = Field(None, ge=1, le=10)


class ToolServerStatusUpdate(BaseModel):
    """Schema for updating tool server status."""

    status: ServerStatus = Field(..., description="New server status")


class ServerToolBase(BaseModel):
    """Base schema for server tool."""

    name: str = Field(..., min_length=1, max_length=100, description="Tool name")
    display_name: str = Field(..., min_length=1, max_length=200, description="Display name")
    description: str | None = Field(None, description="Tool description")
    args_schema: dict[str, Any] | None = Field(None, description="Tool arguments schema")
    bypass_when_unavailable: bool = Field(False, description="Bypass when tool is unavailable")


class ServerToolUpdate(BaseModel):
    """Schema for updating a server tool."""

    display_name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None)
    status: ToolStatus | None = Field(None)
    bypass_when_unavailable: bool | None = Field(None)


class ToolUsageCreate(BaseModel):
    """Schema for creating tool usage record."""

    tool_name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] | None = Field(None, description="Tool arguments")
    result: dict[str, Any] | None = Field(None, description="Tool result")
    response_time_ms: float | None = Field(None, ge=0, description="Response time in milliseconds")
    success: bool = Field(..., description="Whether the call was successful")
    error_message: str | None = Field(None, description="Error message if failed")
    user_id: str | None = Field(None, description="User ID")
    conversation_id: str | None = Field(None, description="Conversation ID")


# Response schemas
class ServerToolResponse(ServerToolBase):
    """Schema for server tool response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Tool ID")
    server_id: str = Field(..., description="Server ID")
    status: ToolStatus = Field(..., description="Tool status")
    is_available: bool = Field(..., description="Tool availability")
    total_calls: int = Field(..., description="Total number of calls")
    total_errors: int = Field(..., description="Total number of errors")
    last_called: datetime | None = Field(None, description="Last call timestamp")
    last_error: str | None = Field(None, description="Last error message")
    avg_response_time_ms: float | None = Field(None, description="Average response time")
    discovered_at: datetime = Field(..., description="Discovery timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class ToolServerResponse(ToolServerBase):
    """Schema for tool server response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Server ID")
    status: ServerStatus = Field(..., description="Server status")
    is_builtin: bool = Field(..., description="Whether server is built-in")
    last_health_check: datetime | None = Field(None, description="Last health check")
    last_startup_success: datetime | None = Field(None, description="Last successful startup")
    last_startup_error: str | None = Field(None, description="Last startup error")
    consecutive_failures: int = Field(..., description="Consecutive failure count")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str | None = Field(None, description="Creator user ID")
    tools: list[ServerToolResponse] = Field(default_factory=list, description="Server tools")


class ToolUsageResponse(BaseModel):
    """Schema for tool usage response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Usage record ID")
    server_id: str = Field(..., description="Server ID")
    tool_id: str = Field(..., description="Tool ID")
    tool_name: str = Field(..., description="Tool name")
    user_id: str | None = Field(None, description="User ID")
    conversation_id: str | None = Field(None, description="Conversation ID")
    arguments: dict[str, Any] | None = Field(None, description="Tool arguments")
    result: dict[str, Any] | None = Field(None, description="Tool result")
    response_time_ms: float | None = Field(None, description="Response time")
    success: bool = Field(..., description="Success status")
    error_message: str | None = Field(None, description="Error message")
    called_at: datetime = Field(..., description="Call timestamp")


# Analytics schemas
class ToolServerMetrics(BaseModel):
    """Schema for tool server metrics."""

    server_id: str = Field(..., description="Server ID")
    server_name: str = Field(..., description="Server name")
    status: ServerStatus = Field(..., description="Server status")
    total_tools: int = Field(..., description="Total number of tools")
    enabled_tools: int = Field(..., description="Number of enabled tools")
    total_calls: int = Field(..., description="Total tool calls")
    total_errors: int = Field(..., description="Total errors")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate")
    avg_response_time_ms: float | None = Field(None, description="Average response time")
    last_activity: datetime | None = Field(None, description="Last activity timestamp")
    uptime_percentage: float | None = Field(None, ge=0, le=1, description="Uptime percentage")


class ToolMetrics(BaseModel):
    """Schema for individual tool metrics."""

    tool_id: str = Field(..., description="Tool ID")
    tool_name: str = Field(..., description="Tool name")
    server_name: str = Field(..., description="Server name")
    status: ToolStatus = Field(..., description="Tool status")
    total_calls: int = Field(..., description="Total calls")
    total_errors: int = Field(..., description="Total errors")
    success_rate: float = Field(..., ge=0, le=1, description="Success rate")
    avg_response_time_ms: float | None = Field(None, description="Average response time")
    last_called: datetime | None = Field(None, description="Last call timestamp")
    calls_last_24h: int = Field(..., description="Calls in last 24 hours")
    errors_last_24h: int = Field(..., description="Errors in last 24 hours")


class ToolServerAnalytics(BaseModel):
    """Schema for comprehensive tool server analytics."""

    # Overview metrics
    total_servers: int = Field(..., description="Total number of servers")
    active_servers: int = Field(..., description="Number of active servers")
    total_tools: int = Field(..., description="Total number of tools")
    enabled_tools: int = Field(..., description="Number of enabled tools")

    # Usage metrics
    total_calls_today: int = Field(..., description="Total calls today")
    total_calls_week: int = Field(..., description="Total calls this week")
    total_calls_month: int = Field(..., description="Total calls this month")
    total_errors_today: int = Field(..., description="Total errors today")
    overall_success_rate: float = Field(..., ge=0, le=1, description="Overall success rate")

    # Performance metrics
    avg_response_time_ms: float = Field(..., description="Average response time")
    p95_response_time_ms: float = Field(..., description="95th percentile response time")

    # Server metrics
    server_metrics: list[ToolServerMetrics] = Field(..., description="Per-server metrics")

    # Tool metrics
    top_tools: list[ToolMetrics] = Field(..., description="Most used tools")
    failing_tools: list[ToolMetrics] = Field(..., description="Tools with errors")

    # Time series data
    daily_usage: dict[str, int] = Field(..., description="Daily usage over time")
    daily_errors: dict[str, int] = Field(..., description="Daily errors over time")

    # Generated timestamp
    generated_at: datetime = Field(..., description="Analytics generation time")


class ToolServerHealthCheck(BaseModel):
    """Schema for tool server health check."""

    server_id: str = Field(..., description="Server ID")
    server_name: str = Field(..., description="Server name")
    status: ServerStatus = Field(..., description="Server status")
    is_running: bool = Field(..., description="Whether server is running")
    is_responsive: bool = Field(..., description="Whether server is responsive")
    tools_count: int = Field(..., description="Number of available tools")
    last_check: datetime = Field(..., description="Last health check time")
    error_message: str | None = Field(None, description="Error message if unhealthy")


class BulkToolServerOperation(BaseModel):
    """Schema for bulk operations on tool servers."""

    server_ids: list[str] = Field(..., min_items=1, description="List of server IDs")
    operation: str = Field(..., description="Operation to perform")
    parameters: dict[str, Any] | None = Field(None, description="Operation parameters")


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""

    total_requested: int = Field(..., description="Total servers requested")
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed to process")
    results: list[dict[str, Any]] = Field(..., description="Detailed results")
    errors: list[str] = Field(default_factory=list, description="Error messages")
