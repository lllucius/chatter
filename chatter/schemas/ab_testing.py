"""A/B testing schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.schemas.common import ListRequestBase


# Enums defined locally to avoid circular imports
from enum import Enum


class TestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TestType(str, Enum):
    PROMPT = "prompt"
    MODEL = "model"
    PARAMETER = "parameter"
    WORKFLOW = "workflow"
    TEMPLATE = "template"


class VariantAllocation(str, Enum):
    EQUAL = "equal"
    WEIGHTED = "weighted"
    GRADUAL_ROLLOUT = "gradual_rollout"
    USER_ATTRIBUTE = "user_attribute"


class MetricType(str, Enum):
    RESPONSE_TIME = "response_time"
    USER_SATISFACTION = "user_satisfaction"
    ACCURACY = "accuracy"
    ENGAGEMENT = "engagement"
    CONVERSION = "conversion"
    ERROR_RATE = "error_rate"
    TOKEN_USAGE = "token_usage"
    CUSTOM = "custom"


class TestVariant(BaseModel):
    """Test variant definition."""

    name: str = Field(..., description="Variant name")
    description: str = Field(..., description="Variant description")
    configuration: dict[str, Any] = Field(
        ..., description="Variant configuration"
    )
    weight: float = Field(
        1.0, ge=0.0, description="Variant weight for allocation"
    )


class ABTestCreateRequest(BaseModel):
    """Request schema for creating an A/B test."""

    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    test_type: TestType = Field(..., description="Type of test")
    allocation_strategy: VariantAllocation = Field(
        ..., description="Allocation strategy"
    )

    variants: list[TestVariant] = Field(
        ..., min_length=2, description="Test variants"
    )
    metrics: list[MetricType] = Field(
        ..., min_length=1, description="Metrics to track"
    )

    # Test configuration
    duration_days: int = Field(
        7, ge=1, le=365, description="Test duration in days"
    )
    min_sample_size: int = Field(
        100, ge=10, description="Minimum sample size"
    )
    confidence_level: float = Field(
        0.95,
        ge=0.5,
        le=0.99,
        description="Statistical confidence level",
    )

    # Targeting
    target_audience: dict[str, Any] | None = Field(
        None, description="Target audience criteria"
    )
    traffic_percentage: float = Field(
        100.0,
        ge=0.1,
        le=100.0,
        description="Percentage of traffic to include",
    )

    # Metadata
    tags: list[str] = Field(
        default_factory=list, description="Test tags"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class ABTestUpdateRequest(BaseModel):
    """Request schema for updating an A/B test."""

    name: str | None = Field(default=None, description="Test name")
    description: str | None = Field(
        None, description="Test description"
    )
    status: TestStatus | None = Field(
        default=None, description="Test status"
    )

    # Configuration updates (only allowed for draft tests)
    duration_days: int | None = Field(
        None, ge=1, le=365, description="Test duration in days"
    )
    min_sample_size: int | None = Field(
        None, ge=10, description="Minimum sample size"
    )
    confidence_level: float | None = Field(
        None,
        ge=0.5,
        le=0.99,
        description="Statistical confidence level",
    )
    traffic_percentage: float | None = Field(
        None, ge=0.1, le=100.0, description="Traffic percentage"
    )

    # Metadata
    tags: list[str] | None = Field(
        default=None, description="Test tags"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ABTestResponse(BaseModel):
    """Response schema for A/B test data."""

    id: str = Field(..., description="Test ID")
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    test_type: TestType = Field(..., description="Type of test")
    status: TestStatus = Field(..., description="Test status")
    allocation_strategy: VariantAllocation = Field(
        ..., description="Allocation strategy"
    )

    variants: list[TestVariant] = Field(
        ..., description="Test variants"
    )
    metrics: list[MetricType] = Field(
        ..., description="Metrics being tracked"
    )

    # Test configuration
    duration_days: int = Field(..., description="Test duration in days")
    min_sample_size: int = Field(..., description="Minimum sample size")
    confidence_level: float = Field(
        ..., description="Statistical confidence level"
    )

    # Targeting
    target_audience: dict[str, Any] | None = Field(
        None, description="Target audience criteria"
    )
    traffic_percentage: float = Field(
        ..., description="Percentage of traffic included"
    )

    # Status information
    start_date: datetime | None = Field(
        None, description="Test start date"
    )
    end_date: datetime | None = Field(
        default=None, description="Test end date"
    )
    participant_count: int = Field(
        0, description="Number of participants"
    )

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )
    created_by: str = Field(..., description="Creator")
    tags: list[str] = Field(..., description="Test tags")
    metadata: dict[str, Any] = Field(
        ..., description="Additional metadata"
    )


class ABTestListRequest(ListRequestBase):
    """Request schema for listing A/B tests."""

    status: TestStatus | None = Field(
        None, description="Filter by status"
    )
    test_type: TestType | None = Field(
        None, description="Filter by test type"
    )
    tags: list[str] | None = Field(
        default=None, description="Filter by tags"
    )


class ABTestListResponse(BaseModel):
    """Response schema for A/B test list."""

    tests: list[ABTestResponse] = Field(
        ..., description="List of tests"
    )
    total: int = Field(..., description="Total number of tests")


class ABTestActionResponse(BaseModel):
    """Response schema for test actions (start, pause, complete)."""

    success: bool = Field(
        ..., description="Whether action was successful"
    )
    message: str = Field(..., description="Action result message")
    test_id: str = Field(..., description="Test ID")
    new_status: TestStatus = Field(..., description="New test status")


class ABTestDeleteResponse(BaseModel):
    """Response schema for test deletion."""

    success: bool = Field(
        ..., description="Whether deletion was successful"
    )
    message: str = Field(..., description="Deletion result message")


class TestMetric(BaseModel):
    """Test metric data."""

    metric_type: MetricType = Field(..., description="Type of metric")
    variant_name: str = Field(..., description="Variant name")
    value: float = Field(..., description="Metric value")
    sample_size: int = Field(..., description="Sample size")
    confidence_interval: list[float] | None = Field(
        None, description="95% confidence interval"
    )


class ABTestResultsResponse(BaseModel):
    """Response schema for A/B test results."""

    test_id: str = Field(..., description="Test ID")
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")

    # Results data
    metrics: list[TestMetric] = Field(
        ..., description="Metric results by variant"
    )
    statistical_significance: dict[str, bool] = Field(
        ..., description="Statistical significance by metric"
    )
    confidence_intervals: dict[str, dict[str, list[float]]] = Field(
        ..., description="Confidence intervals"
    )

    # Recommendations
    winning_variant: str | None = Field(
        None, description="Recommended winning variant"
    )
    recommendation: str = Field(
        ..., description="Action recommendation"
    )

    # Metadata
    generated_at: datetime = Field(
        ..., description="Results generation timestamp"
    )
    sample_size: int = Field(..., description="Total sample size")
    duration_days: int = Field(..., description="Test duration so far")


class ABTestMetricsResponse(BaseModel):
    """Response schema for A/B test metrics."""

    test_id: str = Field(..., description="Test ID")
    metrics: list[TestMetric] = Field(
        ..., description="Current metrics"
    )
    participant_count: int = Field(
        ..., description="Current participant count"
    )
    last_updated: datetime = Field(
        ..., description="Last metrics update"
    )


class VariantPerformance(BaseModel):
    """Performance data for a specific variant."""
    
    name: str = Field(..., description="Variant name")
    participants: int = Field(..., description="Number of participants")
    conversions: int = Field(..., description="Number of conversions")
    conversion_rate: float = Field(..., description="Conversion rate")
    revenue: float = Field(0.0, description="Total revenue")
    cost: float = Field(0.0, description="Total cost")
    roi: float = Field(0.0, description="Return on investment")


class StatisticalAnalysis(BaseModel):
    """Statistical analysis results."""
    
    confidence_level: float = Field(..., description="Confidence level used")
    statistical_significance: bool = Field(..., description="Is result statistically significant")
    p_value: float = Field(..., description="P-value")
    effect_size: float = Field(..., description="Effect size")
    power: float = Field(..., description="Statistical power")
    confidence_intervals: dict[str, list[float]] = Field(
        ..., description="Confidence intervals by variant"
    )


class ABTestAnalyticsResponse(BaseModel):
    """Comprehensive A/B test analytics response."""
    
    test_id: str = Field(..., description="Test ID")
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")
    
    # Performance data
    total_participants: int = Field(..., description="Total participants")
    variants: list[VariantPerformance] = Field(..., description="Variant performance data")
    
    # Statistical analysis
    statistical_analysis: StatisticalAnalysis = Field(
        ..., description="Statistical analysis results"
    )
    
    # Results and recommendations
    winner: str | None = Field(None, description="Winning variant")
    improvement: float | None = Field(None, description="Improvement percentage")
    recommendation: str = Field(..., description="Recommendation")
    
    # Test progress
    duration_days: int = Field(..., description="Days test has been running")
    remaining_days: int | None = Field(None, description="Days remaining")
    progress_percentage: float = Field(..., description="Test progress percentage")
    
    # Metadata
    generated_at: datetime = Field(..., description="Analytics generation timestamp")
    last_updated: datetime = Field(..., description="Last data update")
