"""Analytics and statistics schemas."""

from datetime import datetime
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from chatter.schemas.common import GetRequestBase


class ConversationStatsResponse(BaseModel):
    """Schema for conversation statistics response."""

    total_conversations: int = Field(
        ..., description="Total number of conversations"
    )
    conversations_by_status: dict[str, int] = Field(
        ..., description="Conversations grouped by status"
    )
    total_messages: int = Field(
        ..., description="Total number of messages"
    )
    messages_by_role: dict[str, int] = Field(
        ..., description="Messages grouped by role"
    )
    avg_messages_per_conversation: float = Field(
        ..., description="Average messages per conversation"
    )
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost incurred")
    avg_response_time_ms: float = Field(
        ..., description="Average response time in milliseconds"
    )
    conversations_by_date: dict[str, int] = Field(
        ..., description="Conversations by date"
    )
    most_active_hours: dict[str, int] = Field(
        ..., description="Most active hours"
    )
    popular_models: dict[str, int] = Field(
        ..., description="Popular LLM models"
    )
    popular_providers: dict[str, int] = Field(
        ..., description="Popular LLM providers"
    )

    # Message rating metrics
    total_ratings: int = Field(
        default=0, description="Total number of message ratings"
    )
    avg_message_rating: float = Field(
        default=0.0, description="Average message rating"
    )
    messages_with_ratings: int = Field(
        default=0, description="Number of messages with ratings"
    )
    rating_distribution: dict[str, int] = Field(
        default_factory=dict, description="Distribution of ratings (1-5 stars)"
    )


class UsageMetricsResponse(BaseModel):
    """Schema for usage metrics response."""

    # Token usage
    total_prompt_tokens: int = Field(
        ..., description="Total prompt tokens"
    )
    total_completion_tokens: int = Field(
        ..., description="Total completion tokens"
    )
    total_tokens: int = Field(..., description="Total tokens used")
    tokens_by_model: dict[str, int] = Field(
        ..., description="Token usage by model"
    )
    tokens_by_provider: dict[str, int] = Field(
        ..., description="Token usage by provider"
    )

    # Cost metrics
    total_cost: float = Field(..., description="Total cost")
    cost_by_model: dict[str, float] = Field(
        ..., description="Cost by model"
    )
    cost_by_provider: dict[str, float] = Field(
        ..., description="Cost by provider"
    )

    # Usage over time
    daily_usage: dict[str, int] = Field(
        ..., description="Daily token usage"
    )
    daily_cost: dict[str, float] = Field(..., description="Daily cost")

    # Performance metrics
    avg_response_time: float = Field(
        ..., description="Average response time"
    )
    response_times_by_model: dict[str, float] = Field(
        ..., description="Response times by model"
    )

    # Activity metrics
    active_days: int = Field(..., description="Number of active days")
    peak_usage_hour: int = Field(..., description="Peak usage hour")
    conversations_per_day: float = Field(
        ..., description="Average conversations per day"
    )


class PerformanceMetricsResponse(BaseModel):
    """Schema for performance metrics response."""

    # Response time metrics
    avg_response_time_ms: float = Field(
        ..., description="Average response time"
    )
    median_response_time_ms: float = Field(
        ..., description="Median response time"
    )
    p95_response_time_ms: float = Field(
        ..., description="95th percentile response time"
    )
    p99_response_time_ms: float = Field(
        ..., description="99th percentile response time"
    )

    # Throughput metrics
    requests_per_minute: float = Field(
        ..., description="Average requests per minute"
    )
    tokens_per_minute: float = Field(
        ..., description="Average tokens per minute"
    )

    # Error metrics
    total_errors: int = Field(..., description="Total number of errors")
    error_rate: float = Field(..., description="Error rate percentage")
    errors_by_type: dict[str, int] = Field(
        ..., description="Errors grouped by type"
    )

    # Model performance
    performance_by_model: dict[str, dict[str, float]] = Field(
        ..., description="Performance metrics by model"
    )
    performance_by_provider: dict[str, dict[str, float]] = Field(
        ..., description="Performance metrics by provider"
    )

    # System metrics
    database_response_time_ms: float = Field(
        ..., description="Average database response time"
    )
    vector_search_time_ms: float = Field(
        ..., description="Average vector search time"
    )
    embedding_generation_time_ms: float = Field(
        ..., description="Average embedding generation time"
    )


class DocumentAnalyticsResponse(BaseModel):
    """Schema for document analytics response."""

    # Document counts
    total_documents: int = Field(
        ..., description="Total number of documents"
    )
    documents_by_status: dict[str, int] = Field(
        ..., description="Documents by processing status"
    )
    documents_by_type: dict[str, int] = Field(
        ..., description="Documents by file type"
    )

    # Processing metrics
    avg_processing_time_seconds: float = Field(
        ..., description="Average processing time"
    )
    processing_success_rate: float = Field(
        ..., description="Processing success rate"
    )
    total_chunks: int = Field(..., description="Total number of chunks")
    avg_chunks_per_document: float = Field(
        ..., description="Average chunks per document"
    )

    # Storage metrics
    total_storage_bytes: int = Field(
        ..., description="Total storage used"
    )
    avg_document_size_bytes: float = Field(
        ..., description="Average document size"
    )
    storage_by_type: dict[str, int] = Field(
        ..., description="Storage usage by document type"
    )

    # Search metrics
    total_searches: int = Field(
        ..., description="Total number of searches"
    )
    avg_search_results: float = Field(
        ..., description="Average search results returned"
    )
    popular_search_terms: dict[str, int] = Field(
        ..., description="Popular search terms"
    )

    # Access metrics
    total_views: int = Field(..., description="Total document views")
    most_viewed_documents: list[dict[str, Any]] = Field(
        ..., description="Most viewed documents"
    )
    documents_by_access_level: dict[str, int] = Field(
        ..., description="Documents by access level"
    )


class PromptAnalyticsResponse(BaseModel):
    """Schema for prompt analytics response."""

    # Prompt counts
    total_prompts: int = Field(
        ..., description="Total number of prompts"
    )
    prompts_by_category: dict[str, int] = Field(
        ..., description="Prompts by category"
    )
    prompts_by_version: dict[str, int] = Field(
        ..., description="Prompts by version"
    )

    # Usage metrics
    total_prompt_usage: int = Field(
        ..., description="Total prompt usage count"
    )
    most_used_prompts: list[dict[str, Any]] = Field(
        ..., description="Most used prompts"
    )
    avg_usage_per_prompt: float = Field(
        ..., description="Average usage per prompt"
    )

    # Performance metrics
    avg_prompt_length: float = Field(
        ..., description="Average prompt length"
    )
    prompts_by_length_range: dict[str, int] = Field(
        ..., description="Prompts by length range"
    )

    # Testing metrics
    total_tests: int = Field(..., description="Total prompt tests")
    avg_test_score: float = Field(..., description="Average test score")
    prompts_with_tests: int = Field(
        ..., description="Number of prompts with tests"
    )


class ProfileAnalyticsResponse(BaseModel):
    """Schema for profile analytics response."""

    # Profile counts
    total_profiles: int = Field(
        ..., description="Total number of profiles"
    )
    profiles_by_type: dict[str, int] = Field(
        ..., description="Profiles by type"
    )
    profiles_by_provider: dict[str, int] = Field(
        ..., description="Profiles by LLM provider"
    )

    # Usage metrics
    total_profile_usage: int = Field(
        ..., description="Total profile usage count"
    )
    most_used_profiles: list[dict[str, Any]] = Field(
        ..., description="Most used profiles"
    )
    avg_usage_per_profile: float = Field(
        ..., description="Average usage per profile"
    )

    # Configuration metrics
    avg_temperature: float = Field(
        ..., description="Average temperature setting"
    )
    avg_max_tokens: float = Field(
        ..., description="Average max tokens setting"
    )
    popular_settings: dict[str, Any] = Field(
        ..., description="Popular configuration settings"
    )

    # Performance metrics
    performance_by_profile: dict[str, dict[str, float]] = Field(
        ..., description="Performance by profile"
    )
    cost_by_profile: dict[str, float] = Field(
        ..., description="Cost by profile"
    )


class SystemAnalyticsResponse(BaseModel):
    """Schema for system analytics response."""

    # User activity
    total_users: int = Field(..., description="Total number of users")
    active_users_today: int = Field(
        ..., description="Active users today"
    )
    active_users_week: int = Field(
        ..., description="Active users this week"
    )
    active_users_month: int = Field(
        ..., description="Active users this month"
    )

    # System health
    system_uptime_seconds: float = Field(
        ..., description="System uptime in seconds"
    )
    avg_cpu_usage: float = Field(
        ..., description="Average CPU usage percentage"
    )
    avg_memory_usage: float = Field(
        ..., description="Average memory usage percentage"
    )
    database_connections: int = Field(
        ..., description="Current database connections"
    )

    # API metrics
    total_api_requests: int = Field(
        ..., description="Total API requests"
    )
    requests_per_endpoint: dict[str, int] = Field(
        ..., description="Requests by endpoint"
    )
    avg_api_response_time: float = Field(
        ..., description="Average API response time"
    )
    api_error_rate: float = Field(..., description="API error rate")

    # Resource usage
    storage_usage_bytes: int = Field(
        ..., description="Total storage usage"
    )
    vector_database_size_bytes: int = Field(
        ..., description="Vector database size"
    )
    cache_hit_rate: float = Field(..., description="Cache hit rate")


class AnalyticsTimeRange(BaseModel):
    """Schema for analytics time range filter."""

    start_date: datetime | None = Field(
        default=None, description="Start date for analytics"
    )
    end_date: datetime | None = Field(
        default=None, description="End date for analytics"
    )
    period: str = Field(
        default="7d",
        description="Predefined period (1h, 24h, 7d, 30d, 90d)",
    )

    @field_validator("period")
    @classmethod
    def validate_period(cls, v: str) -> str:
        """Validate the period parameter."""
        valid_periods = {"1h", "24h", "7d", "30d", "90d"}
        if v not in valid_periods:
            raise ValueError(
                f"Invalid period '{v}'. Must be one of: {', '.join(valid_periods)}"
            )
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "AnalyticsTimeRange":
        """Validate that start_date is before end_date when both are provided."""
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("start_date must be before end_date")
            # Warn about very large date ranges (more than 1 year)
            delta = self.end_date - self.start_date
            if delta.days > 365:
                # Could raise a warning or validation error for performance
                pass
        return self


class ConversationStatsRequest(GetRequestBase):
    """Schema for conversation stats request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class UsageMetricsRequest(GetRequestBase):
    """Schema for usage metrics request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class PerformanceMetricsRequest(GetRequestBase):
    """Schema for performance metrics request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class DocumentAnalyticsRequest(GetRequestBase):
    """Schema for document analytics request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class SystemAnalyticsRequest(GetRequestBase):
    """Schema for system analytics request."""

    pass


class DashboardRequest(GetRequestBase):
    """Schema for dashboard request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class ToolServerAnalyticsRequest(GetRequestBase):
    """Schema for tool server analytics request."""

    time_range: AnalyticsTimeRange = Field(
        default_factory=lambda: AnalyticsTimeRange(),
        description="Time range filter",
    )


class AnalyticsExportRequest(BaseModel):
    """Schema for analytics export request."""

    metrics: list[str] = Field(
        ..., description="List of metrics to export"
    )
    time_range: AnalyticsTimeRange = Field(
        ..., description="Time range for export"
    )
    format: str = Field(
        "json", description="Export format (json, csv, xlsx)"
    )
    include_raw_data: bool = Field(
        False, description="Include raw data points"
    )

    @field_validator("metrics")
    @classmethod
    def validate_metrics(cls, v: list[str]) -> list[str]:
        """Validate metrics list."""
        if not v:
            raise ValueError("At least one metric must be specified")

        valid_metrics = {
            "conversations",
            "usage",
            "performance",
            "documents",
            "system",
            "toolservers",
            "custom",
        }

        for metric in v:
            if metric not in valid_metrics:
                raise ValueError(
                    f"Invalid metric '{metric}'. Valid metrics: {', '.join(valid_metrics)}"
                )
        return v

    @field_validator("format")
    @classmethod
    def validate_format(cls, v: str) -> str:
        """Validate export format."""
        valid_formats = {"json", "csv", "xlsx"}
        if v not in valid_formats:
            raise ValueError(
                f"Invalid format '{v}'. Must be one of: {', '.join(valid_formats)}"
            )
        return v


class AnalyticsExportResponse(BaseModel):
    """Schema for analytics export response."""

    export_id: str = Field(..., description="Export job ID")
    status: str = Field(..., description="Export status")
    download_url: str | None = Field(
        None, description="Download URL when ready"
    )
    created_at: datetime = Field(
        ..., description="Export creation time"
    )
    expires_at: datetime | None = Field(
        None, description="Download expiration time"
    )


class CustomMetricRequest(BaseModel):
    """Schema for custom metric creation request."""

    name: str = Field(
        ..., min_length=1, max_length=100, description="Metric name"
    )
    description: str | None = Field(
        None, description="Metric description"
    )
    query: str = Field(..., description="SQL query for the metric")
    refresh_interval_minutes: int = Field(
        60, ge=1, le=1440, description="Refresh interval in minutes"
    )
    is_public: bool = Field(
        False, description="Whether metric is public"
    )


class CustomMetricResponse(BaseModel):
    """Schema for custom metric response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Metric ID")
    name: str = Field(..., description="Metric name")
    description: str | None = Field(
        None, description="Metric description"
    )
    query: str = Field(..., description="SQL query")
    refresh_interval_minutes: int = Field(
        ..., description="Refresh interval"
    )
    is_public: bool = Field(..., description="Public status")
    last_updated: datetime | None = Field(
        None, description="Last update time"
    )
    owner_id: str = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation time")


class DashboardResponse(BaseModel):
    """Schema for analytics dashboard response."""

    conversation_stats: ConversationStatsResponse = Field(
        ..., description="Conversation statistics"
    )
    usage_metrics: UsageMetricsResponse = Field(
        ..., description="Usage metrics"
    )
    performance_metrics: PerformanceMetricsResponse = Field(
        ..., description="Performance metrics"
    )
    document_analytics: DocumentAnalyticsResponse = Field(
        ..., description="Document analytics"
    )
    system_health: SystemAnalyticsResponse = Field(
        ..., description="System health metrics"
    )
    custom_metrics: list[dict[str, Any]] = Field(
        ..., description="Custom metrics"
    )
    generated_at: datetime = Field(
        ..., description="Dashboard generation time"
    )
