"""Job management schemas."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from ulid import ULID


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(str, Enum):
    """Job priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Job(BaseModel):
    """Job definition."""

    id: str = Field(default_factory=lambda: str(ULID()))
    name: str
    function_name: str
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )
    started_at: datetime | None = None
    completed_at: datetime | None = None
    scheduled_at: datetime | None = None  # When job is scheduled to run
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    result: Any = None  # Job execution result
    progress: int = 0  # Progress percentage (0-100)
    progress_message: str | None = None  # Progress description

    # User ownership for security
    created_by_user_id: str | None = (
        None  # ID of user who created the job
    )


class JobResult(BaseModel):
    """Job execution result."""

    job_id: str
    status: JobStatus
    result: Any = None
    error: str | None = None
    execution_time: float = 0.0
    completed_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC)
    )


class JobCreateRequest(BaseModel):
    """Request schema for creating a job."""

    name: str = Field(..., description="Job name")
    function_name: str = Field(..., description="Function to execute")
    args: list[Any] = Field(
        default_factory=list, description="Function arguments"
    )
    kwargs: dict[str, Any] = Field(
        default_factory=dict, description="Function keyword arguments"
    )
    priority: JobPriority = Field(
        JobPriority.NORMAL, description="Job priority"
    )
    max_retries: int = Field(
        3, ge=0, le=10, description="Maximum retry attempts"
    )
    schedule_at: datetime | None = Field(
        None, description="Schedule job for later execution"
    )


class JobResponse(BaseModel):
    """Response schema for job data."""

    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    function_name: str = Field(..., description="Function name")
    priority: JobPriority = Field(..., description="Job priority")
    status: JobStatus = Field(..., description="Job status")

    # Timing
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: datetime | None = Field(
        None, description="Start timestamp"
    )
    completed_at: datetime | None = Field(
        None, description="Completion timestamp"
    )
    scheduled_at: datetime | None = Field(
        None, description="Scheduled execution time"
    )

    # Execution details
    retry_count: int = Field(
        ..., description="Number of retry attempts"
    )
    max_retries: int = Field(..., description="Maximum retry attempts")
    error_message: str | None = Field(
        None, description="Error message if failed"
    )
    result: Any | None = Field(
        None, description="Job result if completed"
    )

    # Progress
    progress: int = Field(
        0, ge=0, le=100, description="Job progress percentage"
    )
    progress_message: str | None = Field(
        None, description="Progress message"
    )


class JobListRequest(BaseModel):
    """Request schema for listing jobs."""

    # Filtering options
    status: JobStatus | None = Field(
        None, description="Filter by status"
    )
    priority: JobPriority | None = Field(
        None, description="Filter by priority"
    )
    function_name: str | None = Field(
        None, description="Filter by function name"
    )

    # Date filtering
    created_after: datetime | None = Field(
        None, description="Filter jobs created after this date"
    )
    created_before: datetime | None = Field(
        None, description="Filter jobs created before this date"
    )

    # Tag filtering
    tags: list[str] | None = Field(
        None,
        description="Filter by job tags (any of the provided tags)",
    )

    # Search
    search: str | None = Field(
        None, description="Search in job names and metadata"
    )

    # Pagination
    limit: int = Field(
        20, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )

    # Sorting
    sort_by: str = Field("created_at", description="Field to sort by")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


class JobListResponse(BaseModel):
    """Response schema for job list."""

    jobs: list[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")

    # Pagination information
    limit: int = Field(..., description="Maximum results per page")
    offset: int = Field(..., description="Number of results skipped")
    has_more: bool = Field(
        ..., description="Whether more results exist"
    )


class JobActionResponse(BaseModel):
    """Response schema for job actions."""

    success: bool = Field(
        ..., description="Whether action was successful"
    )
    message: str = Field(..., description="Action result message")
    job_id: str = Field(..., description="Job ID")


class JobStatsResponse(BaseModel):
    """Response schema for job statistics."""

    total_jobs: int = Field(..., description="Total number of jobs")
    pending_jobs: int = Field(..., description="Number of pending jobs")
    running_jobs: int = Field(..., description="Number of running jobs")
    completed_jobs: int = Field(
        ..., description="Number of completed jobs"
    )
    failed_jobs: int = Field(..., description="Number of failed jobs")
    queue_size: int = Field(..., description="Current queue size")
    active_workers: int = Field(
        ..., description="Number of active workers"
    )
