"""Job management schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from chatter.services.job_queue import JobStatus, JobPriority
from chatter.schemas.common import DeleteRequestBase, GetRequestBase, ListRequestBase


class JobCreateRequest(BaseModel):
    """Request schema for creating a job."""
    
    name: str = Field(..., description="Job name")
    function_name: str = Field(..., description="Function to execute")
    args: List[Any] = Field(default_factory=list, description="Function arguments")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Function keyword arguments")
    priority: JobPriority = Field(JobPriority.NORMAL, description="Job priority")
    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts")
    schedule_at: Optional[datetime] = Field(None, description="Schedule job for later execution")


class JobResponse(BaseModel):
    """Response schema for job data."""
    
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    function_name: str = Field(..., description="Function name")
    priority: JobPriority = Field(..., description="Job priority")
    status: JobStatus = Field(..., description="Job status")
    
    # Timing
    created_at: datetime = Field(..., description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    scheduled_at: Optional[datetime] = Field(None, description="Scheduled execution time")
    
    # Execution details
    retry_count: int = Field(..., description="Number of retry attempts")
    max_retries: int = Field(..., description="Maximum retry attempts")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    result: Optional[Any] = Field(None, description="Job result if completed")
    
    # Progress
    progress: int = Field(0, ge=0, le=100, description="Job progress percentage")
    progress_message: Optional[str] = Field(None, description="Progress message")


class JobListRequest(ListRequestBase):
    """Request schema for listing jobs."""
    
    status: Optional[JobStatus] = Field(None, description="Filter by status")
    priority: Optional[JobPriority] = Field(None, description="Filter by priority")
    function_name: Optional[str] = Field(None, description="Filter by function name")


class JobListResponse(BaseModel):
    """Response schema for job list."""
    
    jobs: List[JobResponse] = Field(..., description="List of jobs")
    total: int = Field(..., description="Total number of jobs")


class JobActionResponse(BaseModel):
    """Response schema for job actions."""
    
    success: bool = Field(..., description="Whether action was successful")
    message: str = Field(..., description="Action result message")
    job_id: str = Field(..., description="Job ID")


class JobStatsResponse(BaseModel):
    """Response schema for job statistics."""
    
    total_jobs: int = Field(..., description="Total number of jobs")
    pending_jobs: int = Field(..., description="Number of pending jobs")
    running_jobs: int = Field(..., description="Number of running jobs")
    completed_jobs: int = Field(..., description="Number of completed jobs")
    failed_jobs: int = Field(..., description="Number of failed jobs")
    queue_size: int = Field(..., description="Current queue size")
    active_workers: int = Field(..., description="Number of active workers")