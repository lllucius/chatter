"""Job management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, status
from ulid import ULID

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.jobs import JobPriority  # Add JobPriority import
from chatter.schemas.jobs import JobStatus  # Add JobStatus import
from chatter.schemas.jobs import (
    JobActionResponse,
    JobCreateRequest,
    JobListRequest,
    JobListResponse,
    JobResponse,
    JobStatsResponse,
)
from chatter.services.job_queue import job_queue
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
    ValidationProblem,
)

logger = get_logger(__name__)
router = APIRouter()


def validate_job_id(job_id: str) -> str:
    """Validate that job_id is a valid ULID format.

    Args:
        job_id: The job ID to validate

    Returns:
        The validated job ID

    Raises:
        ValidationProblem: If job_id is not a valid ULID
    """
    try:
        ULID.from_str(job_id)
        return job_id
    except ValueError as e:
        raise ValidationProblem(
            detail=f"Invalid job ID format: {job_id}. Must be a valid ULID."
        ) from e


@router.post(
    "/", response_model=JobResponse, status_code=status.HTTP_201_CREATED
)
async def create_job(
    job_data: JobCreateRequest,
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    """Create a new job.

    Args:
        job_data: Job creation data
        current_user: Current authenticated user

    Returns:
        Created job data
    """
    try:
        # Validate that the function handler exists
        if job_data.function_name not in job_queue.job_handlers:
            raise ValidationProblem(
                detail=f"Unknown function: {job_data.function_name}. "
                f"Available functions: {list(job_queue.job_handlers.keys())}"
            )

        if job_data.schedule_at:
            job_id = await job_queue.add_job(
                name=job_data.name,
                function_name=job_data.function_name,
                args=job_data.args,
                kwargs=job_data.kwargs,
                priority=job_data.priority,
                max_retries=job_data.max_retries,
                schedule_at=job_data.schedule_at,
                created_by_user_id=current_user.id,  # Add user ID for security
            )
        else:
            job_id = await job_queue.add_job(
                name=job_data.name,
                function_name=job_data.function_name,
                args=job_data.args,
                kwargs=job_data.kwargs,
                priority=job_data.priority,
                max_retries=job_data.max_retries,
                created_by_user_id=current_user.id,  # Add user ID for security
            )

        created_job = job_queue.jobs.get(job_id)
        if not created_job:
            raise InternalServerProblem(
                detail="Failed to retrieve created job"
            )

        return JobResponse(
            id=created_job.id,
            name=created_job.name,
            function_name=created_job.function_name,
            priority=created_job.priority,
            status=created_job.status,
            created_at=created_job.created_at,
            started_at=created_job.started_at,
            completed_at=created_job.completed_at,
            scheduled_at=created_job.scheduled_at,  # Use job's scheduled_at
            retry_count=created_job.retry_count,
            max_retries=created_job.max_retries,
            error_message=created_job.error_message,
            result=created_job.result,
            progress=created_job.progress,
            progress_message=created_job.progress_message,
        )

    except ValidationProblem:
        raise  # Re-raise validation errors as-is
    except ValueError as e:
        # Handle job queue validation errors
        raise ValidationProblem(detail=str(e)) from e
    except Exception as e:
        logger.error("Failed to create job", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create job"
        ) from e


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    request: JobListRequest = Depends(),
    current_user: User = Depends(get_current_user),
) -> JobListResponse:
    """List jobs with optional filtering and pagination.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs with pagination info
    """
    try:
        jobs = list(job_queue.jobs.values())

        # Apply user filter first (security) - users can only see their own jobs
        jobs = [
            j for j in jobs if j.created_by_user_id == current_user.id
        ]

        # Apply other filters
        if request.status is not None:
            jobs = [j for j in jobs if j.status == request.status]

        if request.priority is not None:
            jobs = [j for j in jobs if j.priority == request.priority]

        if request.function_name is not None:
            jobs = [
                j
                for j in jobs
                if j.function_name == request.function_name
            ]

        # Apply date filters
        if request.created_after is not None:
            jobs = [
                j for j in jobs if j.created_at >= request.created_after
            ]

        if request.created_before is not None:
            jobs = [
                j
                for j in jobs
                if j.created_at <= request.created_before
            ]

        # Apply tag filter (any of the provided tags)
        if request.tags:
            jobs = [
                j
                for j in jobs
                if any(tag in j.tags for tag in request.tags)
            ]

        # Apply search filter (search in name and metadata)
        if request.search:
            search_lower = request.search.lower()
            jobs = [
                j
                for j in jobs
                if (
                    search_lower in j.name.lower()
                    or any(
                        search_lower in str(v).lower()
                        for v in j.metadata.values()
                    )
                )
            ]

        # Total count before pagination
        total_jobs = len(jobs)

        # Apply sorting
        reverse_sort = request.sort_order == "desc"
        if request.sort_by == "created_at":
            jobs.sort(key=lambda x: x.created_at, reverse=reverse_sort)
        elif request.sort_by == "name":
            jobs.sort(key=lambda x: x.name, reverse=reverse_sort)
        elif request.sort_by == "priority":
            # Sort by priority order (critical > high > normal > low)
            priority_order = {
                JobPriority.CRITICAL: 4,
                JobPriority.HIGH: 3,
                JobPriority.NORMAL: 2,
                JobPriority.LOW: 1,
            }
            jobs.sort(
                key=lambda x: priority_order.get(x.priority, 0),
                reverse=reverse_sort,
            )
        elif request.sort_by == "status":
            jobs.sort(
                key=lambda x: x.status.value, reverse=reverse_sort
            )

        # Apply pagination
        start_idx = request.offset
        end_idx = start_idx + request.limit
        paginated_jobs = jobs[start_idx:end_idx]
        has_more = end_idx < total_jobs

        # Convert to response format
        job_responses = []
        for job in paginated_jobs:
            job_responses.append(
                JobResponse(
                    id=job.id,
                    name=job.name,
                    function_name=job.function_name,
                    priority=job.priority,
                    status=job.status,
                    created_at=job.created_at,
                    started_at=job.started_at,
                    completed_at=job.completed_at,
                    scheduled_at=job.scheduled_at,  # Use job's scheduled_at
                    retry_count=job.retry_count,
                    max_retries=job.max_retries,
                    error_message=job.error_message,
                    result=job.result,
                    progress=job.progress,
                    progress_message=job.progress_message,
                )
            )

        return JobListResponse(
            jobs=job_responses,
            total=total_jobs,
            limit=request.limit,
            offset=request.offset,
            has_more=has_more,
        )

    except Exception as e:
        logger.error("Failed to list jobs", error=str(e))
        raise InternalServerProblem(detail="Failed to list jobs") from e


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> JobResponse:
    """Get job by ID.

    Args:
        job_id: Job ID
        current_user: Current authenticated user

    Returns:
        Job data
    """
    try:
        # Validate job ID format
        validate_job_id(job_id)

        # Get job with user security check
        job = job_queue.get_user_job(job_id, current_user.id)
        if not job:
            raise NotFoundProblem(detail=f"Job {job_id} not found")

        return JobResponse(
            id=job.id,
            name=job.name,
            function_name=job.function_name,
            priority=job.priority,
            status=job.status,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            scheduled_at=job.scheduled_at,  # Use job's scheduled_at
            retry_count=job.retry_count,
            max_retries=job.max_retries,
            error_message=job.error_message,
            result=job.result,
            progress=job.progress,
            progress_message=job.progress_message,
        )

    except (NotFoundProblem, ValidationProblem):
        raise  # Re-raise these as-is
    except Exception as e:
        logger.error("Failed to get job", job_id=job_id, error=str(e))
        raise InternalServerProblem(detail="Failed to get job") from e


@router.post("/{job_id}/cancel", response_model=JobActionResponse)
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> JobActionResponse:
    """Cancel a job.

    Args:
        job_id: Job ID
        current_user: Current authenticated user

    Returns:
        Cancellation result
    """
    try:
        # Validate job ID format
        validate_job_id(job_id)

        # Use user-specific cancel method for security
        success = await job_queue.cancel_user_job(
            job_id, current_user.id
        )

        if not success:
            raise NotFoundProblem(detail=f"Job {job_id} not found")

        return JobActionResponse(
            success=True,
            message=f"Job {job_id} cancelled successfully",
            job_id=job_id,
        )

    except (BadRequestProblem, NotFoundProblem, ValidationProblem):
        raise  # Re-raise these as-is
    except Exception as e:
        logger.error(
            "Failed to cancel job", job_id=job_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to cancel job"
        ) from e


@router.get("/stats/overview", response_model=JobStatsResponse)
async def get_job_stats(
    current_user: User = Depends(get_current_user),
) -> JobStatsResponse:
    """Get job queue statistics.

    Args:
        current_user: Current authenticated user

    Returns:
        Job statistics
    """
    try:
        # Get stats filtered by user
        all_jobs = list(job_queue.jobs.values())
        user_jobs = [
            job
            for job in all_jobs
            if job.created_by_user_id == current_user.id
        ]

        stats = {
            "total_jobs": len(user_jobs),
            "pending_jobs": len(
                [j for j in user_jobs if j.status == JobStatus.PENDING]
            ),
            "running_jobs": len(
                [j for j in user_jobs if j.status == JobStatus.RUNNING]
            ),
            "completed_jobs": len(
                [
                    j
                    for j in user_jobs
                    if j.status == JobStatus.COMPLETED
                ]
            ),
            "failed_jobs": len(
                [j for j in user_jobs if j.status == JobStatus.FAILED]
            ),
            "queue_size": len(
                [
                    j
                    for j in user_jobs
                    if j.status
                    in [JobStatus.PENDING, JobStatus.RETRYING]
                ]
            ),
            "active_workers": len(
                [j for j in user_jobs if j.status == JobStatus.RUNNING]
            ),
        }

        return JobStatsResponse(
            total_jobs=stats["total_jobs"],
            pending_jobs=stats["pending_jobs"],
            running_jobs=stats["running_jobs"],
            completed_jobs=stats["completed_jobs"],
            failed_jobs=stats["failed_jobs"],
            queue_size=stats["queue_size"],
            active_workers=stats["active_workers"],
        )

    except Exception as e:
        logger.error("Failed to get job stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get job stats"
        ) from e


@router.post("/cleanup", response_model=dict)
async def cleanup_jobs(
    force: bool = False,
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Clean up old completed jobs to free up memory.

    Note: This is a system-wide cleanup operation that affects all users.
    Only completed, failed, or cancelled jobs older than 24 hours are removed.

    Args:
        force: If True, remove all completed/failed jobs regardless of age
        current_user: Current authenticated user

    Returns:
        Cleanup statistics
    """
    try:
        # For now, any authenticated user can trigger cleanup
        # In production, you might want to restrict this to admin users
        cleanup_stats = await job_queue.cleanup_jobs(force=force)

        return {
            "success": True,
            "message": f"Cleanup completed. Removed {cleanup_stats['removed']} jobs.",
            "statistics": cleanup_stats,
        }

    except Exception as e:
        logger.error("Failed to cleanup jobs", error=str(e))
        raise InternalServerProblem(
            detail="Failed to cleanup jobs"
        ) from e
