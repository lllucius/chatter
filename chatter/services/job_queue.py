"""Advanced job queue system for background processing."""

import asyncio
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    function_name: str
    args: list[Any] = Field(default_factory=list)
    kwargs: dict[str, Any] = Field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: int = 60  # seconds
    timeout: int = 3600  # seconds
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobResult(BaseModel):
    """Job execution result."""
    job_id: str
    status: JobStatus
    result: Any = None
    error: str | None = None
    execution_time: float = 0.0
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AdvancedJobQueue:
    """Advanced job queue with priority, retry, and monitoring capabilities."""

    def __init__(self, max_workers: int = 4):
        """Initialize the job queue.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.workers: list[asyncio.Task] = []
        self.job_queue: asyncio.Queue = asyncio.Queue()
        self.priority_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self.jobs: dict[str, Job] = {}
        self.results: dict[str, JobResult] = {}
        self.job_handlers: dict[str, Callable] = {}
        self.running = False
        self._job_counter = 0

    def register_handler(self, name: str, handler: Callable) -> None:
        """Register a job handler function.

        Args:
            name: Name of the job handler
            handler: Async function to handle the job
        """
        self.job_handlers[name] = handler
        logger.info(f"Registered job handler: {name}")

    async def add_job(
        self,
        name: str,
        function_name: str,
        args: list[Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        priority: JobPriority = JobPriority.NORMAL,
        max_retries: int = 3,
        timeout: int = 3600,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Add a job to the queue.

        Args:
            name: Human-readable job name
            function_name: Name of the registered handler function
            args: Positional arguments for the job
            kwargs: Keyword arguments for the job
            priority: Job priority
            max_retries: Maximum retry attempts
            timeout: Job timeout in seconds
            tags: Job tags for filtering
            metadata: Additional job metadata

        Returns:
            Job ID
        """
        job = Job(
            name=name,
            function_name=function_name,
            args=args or [],
            kwargs=kwargs or {},
            priority=priority,
            max_retries=max_retries,
            timeout=timeout,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.jobs[job.id] = job

        # Add to priority queue with priority ordering
        priority_order = {
            JobPriority.CRITICAL: 0,
            JobPriority.HIGH: 1,
            JobPriority.NORMAL: 2,
            JobPriority.LOW: 3,
        }

        await self.priority_queue.put((priority_order[priority], self._job_counter, job))
        self._job_counter += 1

        logger.info(
            "Added job to queue",
            job_id=job.id,
            name=job.name,
            priority=job.priority,
            function_name=job.function_name,
        )

        return job.id

    async def get_job_status(self, job_id: str) -> JobStatus | None:
        """Get the status of a job.

        Args:
            job_id: Job ID

        Returns:
            Job status or None if not found
        """
        job = self.jobs.get(job_id)
        return job.status if job else None

    async def get_job_result(self, job_id: str) -> JobResult | None:
        """Get the result of a completed job.

        Args:
            job_id: Job ID

        Returns:
            Job result or None if not found
        """
        return self.results.get(job_id)

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job.

        Args:
            job_id: Job ID

        Returns:
            True if cancelled, False if not found or already completed
        """
        job = self.jobs.get(job_id)
        if not job:
            return False

        if job.status in [JobStatus.PENDING, JobStatus.RETRYING]:
            job.status = JobStatus.CANCELLED
            logger.info(f"Cancelled job {job_id}")
            return True
        elif job.status == JobStatus.RUNNING:
            # Mark for cancellation - worker will handle it
            job.status = JobStatus.CANCELLED
            logger.info(f"Marked running job {job_id} for cancellation")
            return True

        return False

    async def list_jobs(
        self,
        status: JobStatus | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
    ) -> list[Job]:
        """List jobs with optional filtering.

        Args:
            status: Filter by job status
            tags: Filter by job tags
            limit: Maximum number of jobs to return

        Returns:
            List of jobs
        """
        jobs = list(self.jobs.values())

        if status:
            jobs = [job for job in jobs if job.status == status]

        if tags:
            jobs = [
                job for job in jobs
                if any(tag in job.tags for tag in tags)
            ]

        # Sort by created_at descending
        jobs.sort(key=lambda x: x.created_at, reverse=True)

        return jobs[:limit]

    async def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        total_jobs = len(self.jobs)
        status_counts = {}

        for status in JobStatus:
            status_counts[status.value] = sum(
                1 for job in self.jobs.values() if job.status == status
            )

        return {
            "total_jobs": total_jobs,
            "queue_size": self.priority_queue.qsize(),
            "active_workers": len([w for w in self.workers if not w.done()]),
            "max_workers": self.max_workers,
            "status_counts": status_counts,
        }

    async def get_stats(self) -> dict[str, Any]:
        """Get job queue statistics.
        
        This method provides the same functionality as get_queue_stats
        but with an interface that matches the API expectations.
        
        Returns:
            Dictionary with queue statistics
        """
        return await self.get_queue_stats()

    async def start(self) -> None:
        """Start the job queue workers."""
        if self.running:
            return

        self.running = True
        logger.info(f"Starting job queue with {self.max_workers} workers")

        # Start worker tasks
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.max_workers)
        ]

        logger.info("Job queue started")

    async def stop(self) -> None:
        """Stop the job queue workers."""
        if not self.running:
            return

        logger.info("Stopping job queue")
        self.running = False

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Job queue stopped")

    async def _worker(self, worker_id: str) -> None:
        """Worker coroutine that processes jobs from the queue.

        Args:
            worker_id: Unique worker identifier
        """
        logger.info(f"Worker {worker_id} started")

        while self.running:
            try:
                # Get job from priority queue with timeout
                try:
                    _, _, job = await asyncio.wait_for(
                        self.priority_queue.get(), timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Check if job was cancelled
                if job.status == JobStatus.CANCELLED:
                    continue

                # Execute the job
                await self._execute_job(worker_id, job)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")

        logger.info(f"Worker {worker_id} stopped")

    async def _execute_job(self, worker_id: str, job: Job) -> None:
        """Execute a single job.

        Args:
            worker_id: Worker identifier
            job: Job to execute
        """
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

        logger.info(
            f"Worker {worker_id} executing job",
            job_id=job.id,
            name=job.name,
            function_name=job.function_name,
        )

        # Trigger job started event
        try:
            from chatter.services.sse_events import trigger_job_started
            await trigger_job_started(job.id, job.name)
        except Exception as e:
            logger.warning("Failed to trigger job started event", error=str(e))

        start_time = datetime.now(UTC)

        try:
            # Get job handler
            handler = self.job_handlers.get(job.function_name)
            if not handler:
                raise ValueError(f"No handler registered for function: {job.function_name}")

            # Execute job with timeout
            result = await asyncio.wait_for(
                handler(*job.args, **job.kwargs),
                timeout=job.timeout,
            )

            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(UTC)

            execution_time = (job.completed_at - start_time).total_seconds()

            job_result = JobResult(
                job_id=job.id,
                status=JobStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                completed_at=job.completed_at,
            )

            self.results[job.id] = job_result

            logger.info(
                "Job completed successfully",
                job_id=job.id,
                execution_time=execution_time,
                worker_id=worker_id,
            )

            # Trigger job completed event
            try:
                from chatter.services.sse_events import trigger_job_completed
                await trigger_job_completed(job.id, job.name, result or {})
            except Exception as e:
                logger.warning("Failed to trigger job completed event", error=str(e))

        except asyncio.TimeoutError:
            await self._handle_job_error(job, "Job timed out", worker_id)
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            logger.info(f"Job {job.id} was cancelled")
        except Exception as e:
            await self._handle_job_error(job, str(e), worker_id)

    async def _handle_job_error(self, job: Job, error_message: str, worker_id: str) -> None:
        """Handle job execution errors and retries.

        Args:
            job: Failed job
            error_message: Error message
            worker_id: Worker identifier
        """
        job.error_message = error_message
        job.retry_count += 1

        if job.retry_count <= job.max_retries:
            # Schedule retry
            job.status = JobStatus.RETRYING

            logger.warning(
                "Job failed, scheduling retry",
                job_id=job.id,
                retry_count=job.retry_count,
                max_retries=job.max_retries,
                error=error_message,
                worker_id=worker_id,
            )

            # Schedule retry with delay
            asyncio.create_task(self._schedule_retry(job))

        else:
            # Max retries exceeded
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(UTC)

            execution_time = (job.completed_at - job.started_at).total_seconds() if job.started_at else 0

            job_result = JobResult(
                job_id=job.id,
                status=JobStatus.FAILED,
                error=error_message,
                execution_time=execution_time,
                completed_at=job.completed_at,
            )

            self.results[job.id] = job_result

            logger.error(
                "Job failed permanently",
                job_id=job.id,
                retry_count=job.retry_count,
                error=error_message,
                worker_id=worker_id,
            )

            # Trigger job failed event
            try:
                from chatter.services.sse_events import trigger_job_failed
                await trigger_job_failed(job.id, job.name, error_message)
            except Exception as e:
                logger.warning("Failed to trigger job failed event", error=str(e))

    async def _schedule_retry(self, job: Job) -> None:
        """Schedule a job retry after delay.

        Args:
            job: Job to retry
        """
        await asyncio.sleep(job.retry_delay)

        if job.status == JobStatus.RETRYING and self.running:
            # Add back to queue with same priority
            priority_order = {
                JobPriority.CRITICAL: 0,
                JobPriority.HIGH: 1,
                JobPriority.NORMAL: 2,
                JobPriority.LOW: 3,
            }

            await self.priority_queue.put((priority_order[job.priority], self._job_counter, job))
            self._job_counter += 1


# Global job queue instance
job_queue = AdvancedJobQueue(max_workers=settings.background_worker_concurrency)


# Register some default job handlers
async def document_processing_job(document_id: str, file_content: bytes) -> dict[str, Any]:
    """Document processing job handler for background processing."""
    from chatter.utils.database import get_session_factory

    logger.info(f"Starting background processing for document {document_id}")
    
    try:
        # Get a database session for background processing
        async_session = get_session_factory()
        async with async_session() as session:
            from chatter.services.document_processing import DocumentProcessingService
            
            # Create processing service instance
            processing_service = DocumentProcessingService(session)
            
            # Process the document (chunking + embeddings)
            success = await processing_service.process_document(
                document_id, file_content
            )
            
            if success:
                logger.info(f"Document {document_id} processed successfully in background")
                return {
                    "document_id": document_id,
                    "status": "processed",
                    "success": True,
                }
            else:
                logger.error(f"Document {document_id} processing failed in background")
                return {
                    "document_id": document_id,
                    "status": "failed",
                    "success": False,
                    "error": "Processing failed",
                }
                
    except Exception as e:
        logger.error(f"Document {document_id} processing error in background", error=str(e))
        return {
            "document_id": document_id,
            "status": "failed",
            "success": False,
            "error": str(e),
        }


async def conversation_summarization_job(conversation_id: str) -> dict[str, Any]:
    """Default conversation summarization job handler."""
    logger.info(f"Summarizing conversation {conversation_id}")
    # Simulate processing time
    await asyncio.sleep(1)
    return {
        "conversation_id": conversation_id,
        "summary": "This is a summarized conversation",
        "summary_length": 100,
    }


async def vector_store_maintenance_job() -> dict[str, Any]:
    """Default vector store maintenance job handler."""
    logger.info("Performing vector store maintenance")
    # Simulate maintenance work
    await asyncio.sleep(5)
    return {
        "maintenance_type": "cleanup",
        "documents_processed": 1000,
        "space_freed": "100MB",
    }


async def data_export_job(user_id: str, export_type: str) -> dict[str, Any]:
    """Default data export job handler."""
    logger.info(f"Exporting data for user {user_id}, type: {export_type}")
    # Simulate export work
    await asyncio.sleep(10)
    return {
        "user_id": user_id,
        "export_type": export_type,
        "file_path": f"/exports/{user_id}_{export_type}.json",
        "size": "10MB",
    }


# Register default handlers
job_queue.register_handler("document_processing", document_processing_job)
job_queue.register_handler("conversation_summarization", conversation_summarization_job)
job_queue.register_handler("vector_store_maintenance", vector_store_maintenance_job)
job_queue.register_handler("data_export", data_export_job)
