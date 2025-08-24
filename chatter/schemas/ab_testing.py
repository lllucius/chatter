"""A/B testing schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from chatter.services.ab_testing import TestStatus, TestType, VariantAllocation, MetricType
from chatter.schemas.common import DeleteRequestBase, GetRequestBase, ListRequestBase


class TestVariant(BaseModel):
    """Test variant definition."""
    
    name: str = Field(..., description="Variant name")
    description: str = Field(..., description="Variant description")
    configuration: Dict[str, Any] = Field(..., description="Variant configuration")
    weight: float = Field(1.0, ge=0.0, description="Variant weight for allocation")


class ABTestCreateRequest(BaseModel):
    """Request schema for creating an A/B test."""
    
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    test_type: TestType = Field(..., description="Type of test")
    allocation_strategy: VariantAllocation = Field(..., description="Allocation strategy")
    
    variants: List[TestVariant] = Field(..., min_items=2, description="Test variants")
    metrics: List[MetricType] = Field(..., min_items=1, description="Metrics to track")
    
    # Test configuration
    duration_days: int = Field(7, ge=1, le=365, description="Test duration in days")
    min_sample_size: int = Field(100, ge=10, description="Minimum sample size")
    confidence_level: float = Field(0.95, ge=0.5, le=0.99, description="Statistical confidence level")
    
    # Targeting
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience criteria")
    traffic_percentage: float = Field(100.0, ge=0.1, le=100.0, description="Percentage of traffic to include")
    
    # Metadata
    tags: List[str] = Field(default_factory=list, description="Test tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ABTestUpdateRequest(BaseModel):
    """Request schema for updating an A/B test."""
    
    name: Optional[str] = Field(None, description="Test name")
    description: Optional[str] = Field(None, description="Test description")
    status: Optional[TestStatus] = Field(None, description="Test status")
    
    # Configuration updates (only allowed for draft tests)
    duration_days: Optional[int] = Field(None, ge=1, le=365, description="Test duration in days")
    min_sample_size: Optional[int] = Field(None, ge=10, description="Minimum sample size")
    confidence_level: Optional[float] = Field(None, ge=0.5, le=0.99, description="Statistical confidence level")
    traffic_percentage: Optional[float] = Field(None, ge=0.1, le=100.0, description="Traffic percentage")
    
    # Metadata
    tags: Optional[List[str]] = Field(None, description="Test tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ABTestResponse(BaseModel):
    """Response schema for A/B test data."""
    
    id: str = Field(..., description="Test ID")
    name: str = Field(..., description="Test name")
    description: str = Field(..., description="Test description")
    test_type: TestType = Field(..., description="Type of test")
    status: TestStatus = Field(..., description="Test status")
    allocation_strategy: VariantAllocation = Field(..., description="Allocation strategy")
    
    variants: List[TestVariant] = Field(..., description="Test variants")
    metrics: List[MetricType] = Field(..., description="Metrics being tracked")
    
    # Test configuration
    duration_days: int = Field(..., description="Test duration in days")
    min_sample_size: int = Field(..., description="Minimum sample size")
    confidence_level: float = Field(..., description="Statistical confidence level")
    
    # Targeting
    target_audience: Optional[Dict[str, Any]] = Field(None, description="Target audience criteria")
    traffic_percentage: float = Field(..., description="Percentage of traffic included")
    
    # Status information
    start_date: Optional[datetime] = Field(None, description="Test start date")
    end_date: Optional[datetime] = Field(None, description="Test end date")
    participant_count: int = Field(0, description="Number of participants")
    
    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator")
    tags: List[str] = Field(..., description="Test tags")
    metadata: Dict[str, Any] = Field(..., description="Additional metadata")


class ABTestListRequest(ListRequestBase):
    """Request schema for listing A/B tests."""
    
    status: Optional[TestStatus] = Field(None, description="Filter by status")
    test_type: Optional[TestType] = Field(None, description="Filter by test type")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


class ABTestListResponse(BaseModel):
    """Response schema for A/B test list."""
    
    tests: List[ABTestResponse] = Field(..., description="List of tests")
    total: int = Field(..., description="Total number of tests")


class ABTestActionResponse(BaseModel):
    """Response schema for test actions (start, pause, complete)."""
    
    success: bool = Field(..., description="Whether action was successful")
    message: str = Field(..., description="Action result message")
    test_id: str = Field(..., description="Test ID")
    new_status: TestStatus = Field(..., description="New test status")


class ABTestDeleteResponse(BaseModel):
    """Response schema for test deletion."""
    
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")


class TestMetric(BaseModel):
    """Test metric data."""
    
    metric_type: MetricType = Field(..., description="Type of metric")
    variant_name: str = Field(..., description="Variant name")
    value: float = Field(..., description="Metric value")
    sample_size: int = Field(..., description="Sample size")
    confidence_interval: Optional[List[float]] = Field(None, description="95% confidence interval")


class ABTestResultsResponse(BaseModel):
    """Response schema for A/B test results."""
    
    test_id: str = Field(..., description="Test ID")
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(..., description="Test status")
    
    # Results data
    metrics: List[TestMetric] = Field(..., description="Metric results by variant")
    statistical_significance: Dict[str, bool] = Field(..., description="Statistical significance by metric")
    confidence_intervals: Dict[str, Dict[str, List[float]]] = Field(..., description="Confidence intervals")
    
    # Recommendations
    winning_variant: Optional[str] = Field(None, description="Recommended winning variant")
    recommendation: str = Field(..., description="Action recommendation")
    
    # Metadata
    generated_at: datetime = Field(..., description="Results generation timestamp")
    sample_size: int = Field(..., description="Total sample size")
    duration_days: int = Field(..., description="Test duration so far")


class ABTestMetricsResponse(BaseModel):
    """Response schema for A/B test metrics."""
    
    test_id: str = Field(..., description="Test ID")
    metrics: List[TestMetric] = Field(..., description="Current metrics")
    participant_count: int = Field(..., description="Current participant count")
    last_updated: datetime = Field(..., description="Last metrics update")