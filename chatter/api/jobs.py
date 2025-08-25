"""Job management endpoints."""

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
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
)

logger = get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
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
        if job_data.schedule_at:
            job_id = await job_queue.add_job(
                name=job_data.name,
                function_name=job_data.function_name,
                args=job_data.args,
                kwargs=job_data.kwargs,
                priority=job_data.priority,
                max_retries=job_data.max_retries,
                schedule_at=job_data.schedule_at,
            )
        else:
            job_id = await job_queue.add_job(
                name=job_data.name,
                function_name=job_data.function_name,
                args=job_data.args,
                kwargs=job_data.kwargs,
                priority=job_data.priority,
                max_retries=job_data.max_retries,
            )

        created_job = job_queue.jobs.get(job_id)
        if not created_job:
            raise InternalServerProblem(detail="Failed to retrieve created job")

        return JobResponse(
            id=created_job.id,
            name=created_job.name,
            function_name=created_job.function_name,
            priority=created_job.priority,
            status=created_job.status,
            created_at=created_job.created_at,
            started_at=created_job.started_at,
            completed_at=created_job.completed_at,
            scheduled_at=job_data.schedule_at,
            retry_count=created_job.retry_count,
            max_retries=created_job.max_retries,
            error_message=created_job.error_message,
            result=created_job.result,
            progress=created_job.progress,
            progress_message=created_job.progress_message,
        )

    except Exception as e:
        logger.error("Failed to create job", error=str(e))
        raise InternalServerProblem(detail="Failed to create job") from e


@router.get("/", response_model=JobListResponse)
async def list_jobs(
    request: JobListRequest = Depends(),
    current_user: User = Depends(get_current_user),
) -> JobListResponse:
    """List jobs with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user

    Returns:
        List of jobs
    """
    try:
        jobs = list(job_queue.jobs.values())

        # Apply filters
        if request.status is not None:
            jobs = [j for j in jobs if j.status == request.status]

        if request.priority is not None:
            jobs = [j for j in jobs if j.priority == request.priority]

        if request.function_name is not None:
            jobs = [j for j in jobs if j.function_name == request.function_name]

        job_responses = []
        for job in jobs:
            job_responses.append(JobResponse(
                id=job.id,
                name=job.name,
                function_name=job.function_name,
                priority=job.priority,
                status=job.status,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
                scheduled_at=None,  # Would need to track this
                retry_count=job.retry_count,
                max_retries=job.max_retries,
                error_message=job.error_message,
                result=job.result,
                progress=job.progress,
                progress_message=job.progress_message,
            ))

        return JobListResponse(
            jobs=job_responses,
            total=len(job_responses)
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
        job = job_queue.jobs.get(job_id)
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
            scheduled_at=None,  # Would need to track this
            retry_count=job.retry_count,
            max_retries=job.max_retries,
            error_message=job.error_message,
            result=job.result,
            progress=job.progress,
            progress_message=job.progress_message,
        )

    except NotFoundProblem:
        raise
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
        success = await job_queue.cancel_job(job_id)

        if not success:
            raise BadRequestProblem(detail="Failed to cancel job - check job status")

        return JobActionResponse(
            success=True,
            message=f"Job {job_id} cancelled successfully",
            job_id=job_id
        )

    except BadRequestProblem:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise InternalServerProblem(detail="Failed to cancel job") from e


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
        stats = await job_queue.get_stats()

        return JobStatsResponse(
            total_jobs=stats.get("total_jobs", 0),
            pending_jobs=stats.get("pending_jobs", 0),
            running_jobs=stats.get("running_jobs", 0),
            completed_jobs=stats.get("completed_jobs", 0),
            failed_jobs=stats.get("failed_jobs", 0),
            queue_size=stats.get("queue_size", 0),
            active_workers=stats.get("active_workers", 0),
        )

    except Exception as e:
        logger.error("Failed to get job stats", error=str(e))
        raise InternalServerProblem(detail="Failed to get job stats") from e
