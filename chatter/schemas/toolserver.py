"""Tool server schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    model_validator,
)

from chatter.models.toolserver import (
    ServerStatus,
    ToolAccessLevel,
    ToolStatus,
    UserRole,
)


# OAuth configuration schema
class OAuthConfigSchema(BaseModel):
    """OAuth configuration for remote servers."""

    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    token_url: HttpUrl = Field(
        ..., description="OAuth token endpoint URL"
    )
    scope: str | None = Field(default=None, description="OAuth scope")


# Base schemas
class ToolServerBase(BaseModel):
    """Base schema for remote tool server."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Server name"
    )
    display_name: str = Field(
        ..., min_length=1, max_length=200, description="Display name"
    )
    description: str | None = Field(
        None, description="Server description"
    )
    base_url: HttpUrl | None = Field(
        None,
        description="Base URL for the remote server (null for built-in servers)",
    )
    transport_type: str = Field(
        "http",
        pattern="^(http|sse|stdio|websocket)$",
        description="Transport type: http, sse, stdio, or websocket",
    )
    oauth_config: OAuthConfigSchema | None = Field(
        None, description="OAuth configuration if required"
    )
    headers: dict[str, str] | None = Field(
        None, description="Additional HTTP headers"
    )
    timeout: int = Field(
        30,
        ge=5,
        le=300,
        description="Request timeout in seconds",
    )
    auto_start: bool = Field(
        True, description="Auto-connect to server on system startup"
    )
    auto_update: bool = Field(
        True, description="Auto-update server capabilities"
    )
    max_failures: int = Field(
        3,
        ge=1,
        le=10,
        description="Maximum consecutive failures before disabling",
    )


class ToolServerCreate(ToolServerBase):
    """Schema for creating a tool server."""

    @model_validator(mode="after")
    def validate_server_config(self) -> "ToolServerCreate":
        """Validate server configuration based on transport type."""
        if self.transport_type == "stdio":
            if not self.base_url:
                raise ValueError(
                    "stdio transport requires base_url for command specification"
                )

        if self.transport_type in ["http", "sse", "websocket"]:
            if not self.base_url:
                raise ValueError(
                    f"{self.transport_type} transport requires base_url"
                )

        if self.oauth_config:
            # Validate OAuth config completeness
            if not all(
                [
                    self.oauth_config.client_id,
                    self.oauth_config.client_secret,
                    self.oauth_config.token_url,
                ]
            ):
                raise ValueError(
                    "OAuth config requires client_id, client_secret, and token_url"
                )

        return self


class ToolServerUpdate(BaseModel):
    """Schema for updating a remote tool server."""

    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(None)
    base_url: HttpUrl | None = Field(None)
    transport_type: str | None = Field(
        None, pattern="^(http|sse|stdio|websocket)$"
    )
    oauth_config: OAuthConfigSchema | None = Field(None)
    headers: dict[str, str] | None = Field(None)
    timeout: int | None = Field(default=None, ge=5, le=300)
    auto_start: bool | None = Field(None)
    auto_update: bool | None = Field(None)
    max_failures: int | None = Field(default=None, ge=1, le=10)


class ToolServerStatusUpdate(BaseModel):
    """Schema for updating tool server status."""

    status: ServerStatus = Field(..., description="New server status")


class ServerToolBase(BaseModel):
    """Base schema for server tool."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Tool name"
    )
    display_name: str = Field(
        ..., min_length=1, max_length=200, description="Display name"
    )
    description: str | None = Field(
        None, description="Tool description"
    )
    args_schema: dict[str, Any] | None = Field(
        None, description="Tool arguments schema"
    )
    bypass_when_unavailable: bool = Field(
        False, description="Bypass when tool is unavailable"
    )


class ServerToolUpdate(BaseModel):
    """Schema for updating a server tool."""

    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(None)
    status: ToolStatus | None = Field(None)
    bypass_when_unavailable: bool | None = Field(None)


class ToolUsageCreate(BaseModel):
    """Schema for creating tool usage record."""

    tool_name: str = Field(..., description="Tool name")
    arguments: dict[str, Any] | None = Field(
        None, description="Tool arguments"
    )
    result: dict[str, Any] | None = Field(
        None, description="Tool result"
    )
    response_time_ms: float | None = Field(
        None, ge=0, description="Response time in milliseconds"
    )
    success: bool = Field(
        ..., description="Whether the call was successful"
    )
    error_message: str | None = Field(
        None, description="Error message if failed"
    )
    user_id: str | None = Field(default=None, description="User ID")
    conversation_id: str | None = Field(
        None, description="Conversation ID"
    )


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
    last_called: datetime | None = Field(
        None, description="Last call timestamp"
    )
    last_error: str | None = Field(
        None, description="Last error message"
    )
    avg_response_time_ms: float | None = Field(
        None, description="Average response time"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )


class ToolServerResponse(ToolServerBase):
    """Schema for tool server response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Server ID")
    status: ServerStatus = Field(..., description="Server status")
    is_builtin: bool = Field(
        ..., description="Whether server is built-in"
    )
    last_health_check: datetime | None = Field(
        None, description="Last health check"
    )
    last_startup_success: datetime | None = Field(
        None, description="Last successful startup"
    )
    last_startup_error: str | None = Field(
        None, description="Last startup error"
    )
    consecutive_failures: int = Field(
        ..., description="Consecutive failure count"
    )
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )
    created_by: str | None = Field(default=None, description="Creator user ID")
    tools: list[ServerToolResponse] = Field(
        default_factory=list, description="Server tools"
    )


class ToolUsageResponse(BaseModel):
    """Schema for tool usage response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Usage record ID")
    server_id: str = Field(..., description="Server ID")
    tool_id: str = Field(..., description="Tool ID")
    tool_name: str = Field(..., description="Tool name")
    user_id: str | None = Field(default=None, description="User ID")
    conversation_id: str | None = Field(
        None, description="Conversation ID"
    )
    arguments: dict[str, Any] | None = Field(
        None, description="Tool arguments"
    )
    result: dict[str, Any] | None = Field(
        None, description="Tool result"
    )
    response_time_ms: float | None = Field(
        None, description="Response time"
    )
    success: bool = Field(..., description="Success status")
    error_message: str | None = Field(default=None, description="Error message")
    called_at: datetime = Field(..., description="Call timestamp")


# Analytics schemas
class ToolServerMetrics(BaseModel):
    """Schema for tool server metrics."""

    server_id: str = Field(..., description="Server ID")
    server_name: str = Field(..., description="Server name")
    status: ServerStatus = Field(..., description="Server status")
    total_tools: int = Field(..., description="Total number of tools")
    enabled_tools: int = Field(
        ..., description="Number of enabled tools"
    )
    total_calls: int = Field(..., description="Total tool calls")
    total_errors: int = Field(..., description="Total errors")
    success_rate: float = Field(
        ..., ge=0, le=1, description="Success rate"
    )
    avg_response_time_ms: float | None = Field(
        None, description="Average response time"
    )
    last_activity: datetime | None = Field(
        None, description="Last activity timestamp"
    )
    uptime_percentage: float | None = Field(
        None, ge=0, le=1, description="Uptime percentage"
    )


class ToolMetrics(BaseModel):
    """Schema for individual tool metrics."""

    tool_id: str = Field(..., description="Tool ID")
    tool_name: str = Field(..., description="Tool name")
    server_name: str = Field(..., description="Server name")
    status: ToolStatus = Field(..., description="Tool status")
    total_calls: int = Field(..., description="Total calls")
    total_errors: int = Field(..., description="Total errors")
    success_rate: float = Field(
        ..., ge=0, le=1, description="Success rate"
    )
    avg_response_time_ms: float | None = Field(
        None, description="Average response time"
    )
    last_called: datetime | None = Field(
        None, description="Last call timestamp"
    )
    calls_last_24h: int = Field(
        ..., description="Calls in last 24 hours"
    )
    errors_last_24h: int = Field(
        ..., description="Errors in last 24 hours"
    )


class ToolServerAnalytics(BaseModel):
    """Schema for comprehensive tool server analytics."""

    # Overview metrics
    total_servers: int = Field(
        ..., description="Total number of servers"
    )
    active_servers: int = Field(
        ..., description="Number of active servers"
    )
    total_tools: int = Field(..., description="Total number of tools")
    enabled_tools: int = Field(
        ..., description="Number of enabled tools"
    )

    # Usage metrics
    total_calls_today: int = Field(..., description="Total calls today")
    total_calls_week: int = Field(
        ..., description="Total calls this week"
    )
    total_calls_month: int = Field(
        ..., description="Total calls this month"
    )
    total_errors_today: int = Field(
        ..., description="Total errors today"
    )
    overall_success_rate: float = Field(
        ..., ge=0, le=1, description="Overall success rate"
    )

    # Performance metrics
    avg_response_time_ms: float = Field(
        ..., description="Average response time"
    )
    p95_response_time_ms: float = Field(
        ..., description="95th percentile response time"
    )

    # Server metrics
    server_metrics: list[ToolServerMetrics] = Field(
        ..., description="Per-server metrics"
    )

    # Tool metrics
    top_tools: list[ToolMetrics] = Field(
        ..., description="Most used tools"
    )
    failing_tools: list[ToolMetrics] = Field(
        ..., description="Tools with errors"
    )

    # Time series data
    daily_usage: dict[str, int] = Field(
        ..., description="Daily usage over time"
    )
    daily_errors: dict[str, int] = Field(
        ..., description="Daily errors over time"
    )

    # Generated timestamp
    generated_at: datetime = Field(
        ..., description="Analytics generation time"
    )


class ToolServerHealthCheck(BaseModel):
    """Schema for tool server health check."""

    server_id: str = Field(..., description="Server ID")
    server_name: str = Field(..., description="Server name")
    status: ServerStatus = Field(..., description="Server status")
    is_running: bool = Field(
        ..., description="Whether server is running"
    )
    is_responsive: bool = Field(
        ..., description="Whether server is responsive"
    )
    tools_count: int = Field(
        ..., description="Number of available tools"
    )
    last_check: datetime = Field(
        ..., description="Last health check time"
    )
    error_message: str | None = Field(
        None, description="Error message if unhealthy"
    )


class BulkToolServerOperation(BaseModel):
    """Schema for bulk operations on tool servers."""

    server_ids: list[str] = Field(
        ..., min_length=1, description="List of server IDs"
    )
    operation: str = Field(..., description="Operation to perform")
    parameters: dict[str, Any] | None = Field(
        None, description="Operation parameters"
    )


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""

    total_requested: int = Field(
        ..., description="Total servers requested"
    )
    successful: int = Field(..., description="Successfully processed")
    failed: int = Field(..., description="Failed to process")
    results: list[dict[str, Any]] = Field(
        ..., description="Detailed results"
    )
    errors: list[str] = Field(
        default_factory=list, description="Error messages"
    )


class ToolServerListRequest(BaseModel):
    """Schema for tool server list request with parameters."""

    status: ServerStatus | None = Field(
        None, description="Filter by server status"
    )
    include_builtin: bool = Field(
        True, description="Include built-in servers"
    )


class ToolServerDeleteResponse(BaseModel):
    """Schema for tool server delete response."""

    message: str = Field(..., description="Success message")


class ToolServerOperationResponse(BaseModel):
    """Schema for tool server operation response."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Operation result message")


class ServerToolsRequest(BaseModel):
    """Schema for server tools request with pagination."""

    limit: int = Field(
        50, ge=1, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )


class ServerToolsResponse(BaseModel):
    """Schema for server tools response with pagination."""

    tools: list[ServerToolResponse] = Field(
        ..., description="List of server tools"
    )
    total_count: int = Field(..., description="Total number of tools")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class ToolOperationResponse(BaseModel):
    """Schema for tool operation response."""

    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Operation result message")


# Role-based access control schemas
class ToolPermissionBase(BaseModel):
    """Base schema for tool permissions."""

    user_id: str = Field(..., description="User ID")
    tool_id: str | None = Field(default=None, description="Specific tool ID")
    server_id: str | None = Field(
        None, description="Server ID (for all tools)"
    )
    access_level: ToolAccessLevel = Field(
        ..., description="Access level"
    )
    rate_limit_per_hour: int | None = Field(
        None, ge=0, description="Hourly rate limit"
    )
    rate_limit_per_day: int | None = Field(
        None, ge=0, description="Daily rate limit"
    )
    allowed_hours: list[int] | None = Field(
        None, description="Allowed hours (0-23)"
    )
    allowed_days: list[int] | None = Field(
        None, description="Allowed weekdays (0-6)"
    )
    expires_at: datetime | None = Field(
        None, description="Permission expiry"
    )


class ToolPermissionCreate(ToolPermissionBase):
    """Schema for creating tool permissions."""

    pass


class ToolPermissionUpdate(BaseModel):
    """Schema for updating tool permissions."""

    access_level: ToolAccessLevel | None = Field(None)
    rate_limit_per_hour: int | None = Field(default=None, ge=0)
    rate_limit_per_day: int | None = Field(default=None, ge=0)
    allowed_hours: list[int] | None = Field(None)
    allowed_days: list[int] | None = Field(None)
    expires_at: datetime | None = Field(None)


class ToolPermissionResponse(ToolPermissionBase):
    """Schema for tool permission response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Permission ID")
    granted_by: str = Field(..., description="Granter user ID")
    granted_at: datetime = Field(..., description="Grant timestamp")
    usage_count: int = Field(..., description="Usage count")
    last_used: datetime | None = Field(
        None, description="Last used timestamp"
    )


class RoleToolAccessBase(BaseModel):
    """Base schema for role-based tool access."""

    role: UserRole = Field(..., description="User role")
    tool_pattern: str | None = Field(
        None, description="Tool name pattern"
    )
    server_pattern: str | None = Field(
        None, description="Server name pattern"
    )
    access_level: ToolAccessLevel = Field(
        ..., description="Access level"
    )
    default_rate_limit_per_hour: int | None = Field(default=None, ge=0)
    default_rate_limit_per_day: int | None = Field(default=None, ge=0)
    allowed_hours: list[int] | None = Field(None)
    allowed_days: list[int] | None = Field(None)


class RoleToolAccessCreate(RoleToolAccessBase):
    """Schema for creating role-based tool access."""

    pass


class RoleToolAccessResponse(RoleToolAccessBase):
    """Schema for role-based tool access response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Access rule ID")
    created_by: str = Field(..., description="Creator user ID")
    created_at: datetime = Field(..., description="Creation timestamp")


class UserToolAccessCheck(BaseModel):
    """Schema for checking user tool access."""

    user_id: str = Field(..., description="User ID")
    tool_name: str = Field(..., description="Tool name")
    server_name: str | None = Field(default=None, description="Server name")


class ToolAccessResult(BaseModel):
    """Schema for tool access check result."""

    allowed: bool = Field(..., description="Whether access is allowed")
    access_level: ToolAccessLevel = Field(
        ..., description="Access level"
    )
    rate_limit_remaining_hour: int | None = Field(
        default=None, description="Remaining hourly calls"
    )
    rate_limit_remaining_day: int | None = Field(
        default=None, description="Remaining daily calls"
    )
    restriction_reason: str | None = Field(
        default=None, description="Reason if restricted"
    )
    expires_at: datetime | None = Field(
        default=None, description="Permission expiry"
    )
