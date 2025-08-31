"""Advanced job queue system for background processing using APScheduler."""

import asyncio
import concurrent.futures
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.executors.pool import (
    ThreadPoolExecutor as APSchedulerThreadPoolExecutor,
)
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from chatter.config import settings
from chatter.schemas.jobs import Job, JobPriority, JobResult, JobStatus
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class JobHandlerInfo:
    func: Callable[..., Any]
    is_async: bool
    # "asyncio" = run orchestration on event loop; if func is sync we offload with to_thread
    # "default" = run orchestration in a worker thread; async handlers are bounced back to main loop
    executor: str  # "asyncio" or "default"


class AdvancedJobQueue:
    """Advanced job queue with priority, retry, and monitoring capabilities using APScheduler."""

    def __init__(self, max_workers: int = 4):
        """Initialize the job queue with APScheduler.

        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.jobs: dict[str, Job] = {}
        self.results: dict[str, JobResult] = {}
        self.job_handlers: dict[str, JobHandlerInfo] = {}
        self.running = False
        self._main_loop: asyncio.AbstractEventLoop | None = None

        # Configure APScheduler
        job_stores = {
            "default": MemoryJobStore()
        }
        # Two executors:
        # - "asyncio" runs jobs inside the event loop (for true async jobs)
        # - "default" runs jobs in a worker thread
        executors = {
            "default": APSchedulerThreadPoolExecutor(max_workers=self.max_workers),
            "asyncio": AsyncIOExecutor(),
        }
        job_defaults = {
            "coalesce": False,
            "max_instances": max_workers,  # Control concurrency here
            "misfire_grace_time": 30,
        }

        self.scheduler = AsyncIOScheduler(
            jobstores=job_stores,
            executors=executors,
            job_defaults=job_defaults,
            timezone=UTC,
        )

    def register_handler(self, name: str, handler: Callable, executor: str | None = None) -> None:
        """Register a job handler function.

        Args:
            name: Name of the job handler
            handler: Function to handle the job (async or sync)
            executor: Optional override. "asyncio" or "default".
                      - If None (recommended):
                        - async def handler -> "asyncio"
                        - sync def handler  -> "asyncio" (we'll offload the call with asyncio.to_thread)
                      - Use "default" to run orchestration in a worker thread; note:
                        async handlers will still execute on the main loop via run_coroutine_threadsafe
                        to avoid cross-loop issues with loop-bound resources (DB drivers, etc.).
        """
        is_async = inspect.iscoroutinefunction(handler)
        # Default policy: use "asyncio" unless explicitly forced
        chosen = executor or "asyncio"

        if chosen not in ("asyncio", "default"):
            raise ValueError("executor must be 'asyncio', 'default', or None")

        self.job_handlers[name] = JobHandlerInfo(func=handler, is_async=is_async, executor=chosen)
        logger.info(f"Registered job handler: {name} (is_async={is_async}, executor={chosen})")

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
        schedule_at: datetime | None = None,
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
            schedule_at: Optional datetime to schedule job for later execution

        Returns:
            Job ID
        """
        if function_name not in self.job_handlers:
            raise ValueError(f"No handler registered for function: {function_name}")

        info = self.job_handlers[function_name]

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

        # Pick correct wrapper and executor up front
        job_func, executor_name = self._select_wrapper_and_executor(info)

        # Schedule job with APScheduler
        if schedule_at:
            # Schedule for future execution
            self.scheduler.add_job(
                func=job_func,
                trigger="date",
                run_date=schedule_at,
                args=[job.id],
                id=str(job.id),  # Ensure it's a string
                name=name,
                executor=executor_name,
                max_instances=1,
                coalesce=True,
                misfire_grace_time=30,
            )
        else:
            # Execute immediately with priority handling
            delay_seconds = {
                JobPriority.CRITICAL: 0,
                JobPriority.HIGH: 0.1,
                JobPriority.NORMAL: 0.5,
                JobPriority.LOW: 1.0,
            }

            run_date = datetime.now(UTC)
            if delay_seconds[priority] > 0:
                from datetime import timedelta
                run_date += timedelta(seconds=delay_seconds[priority])

            self.scheduler.add_job(
                func=job_func,
                trigger="date",
                run_date=run_date,
                args=[job.id],
                id=str(job.id),  # Ensure it's a string
                name=name,
                executor=executor_name,
                max_instances=1,
                coalesce=True,
                misfire_grace_time=30,
            )

        logger.info(
            "Added job to queue",
            job_id=job.id,
            name=job.name,
            priority=job.priority,
            function_name=job.function_name,
            scheduled_at=schedule_at,
            executor=executor_name,
        )

        return job.id

    async def schedule_job(self, job: Job, schedule_at: datetime) -> str:
        """Schedule a job for later execution.

        This method is for backwards compatibility with the API.

        Args:
            job: Job object (pre-created)
            schedule_at: When to execute the job

        Returns:
            Job ID
        """
        # Store the job
        self.jobs[job.id] = job

        info = self.job_handlers.get(job.function_name)
        if not info:
            raise ValueError(f"No handler registered for function: {job.function_name}")

        job_func, executor_name = self._select_wrapper_and_executor(info)

        # Schedule with APScheduler
        self.scheduler.add_job(
            func=job_func,
            trigger="date",
            run_date=schedule_at,
            args=[job.id],
            id=str(job.id),  # Ensure it's a string
            name=job.name,
            executor=executor_name,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=30,
        )

        logger.info(
            "Scheduled job",
            job_id=job.id,
            name=job.name,
            priority=job.priority,
            function_name=job.function_name,
            scheduled_at=schedule_at,
            executor=executor_name,
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
            try:
                # Cancel the APScheduler job
                self.scheduler.remove_job(job_id)
                job.status = JobStatus.CANCELLED
                logger.info(f"Cancelled job {job_id}")
                return True
            except Exception as e:
                logger.warning(f"Failed to cancel APScheduler job {job_id}: {e}")
                return False
        elif job.status == JobStatus.RUNNING:
            # For running jobs, mark for cancellation
            # APScheduler doesn't support stopping running jobs, but we can mark it
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
            jobs = [job for job in jobs if any(tag in job.tags for tag in tags)]

        # Sort by created_at descending
        jobs.sort(key=lambda x: x.created_at, reverse=True)

        return jobs[:limit]

    async def get_queue_stats(self) -> dict[str, Any]:
        """Get queue statistics.

        Returns:
            Dictionary with queue statistics
        """
        total_jobs = len(self.jobs)
        status_counts: dict[str, int] = {}

        for status in JobStatus:
            status_counts[status.value] = sum(1 for job in self.jobs.values() if job.status == status)

        # Get APScheduler stats
        scheduled_jobs = len(self.scheduler.get_jobs()) if self.running else 0

        return {
            "total_jobs": total_jobs,
            "queue_size": scheduled_jobs,
            "active_workers": scheduled_jobs,  # APScheduler manages workers internally
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
        total_jobs = len(self.jobs)
        status_counts: dict[str, int] = {}

        for status in JobStatus:
            status_counts[status.value] = sum(1 for job in self.jobs.values() if job.status == status)

        # Get APScheduler stats
        scheduled_jobs = len(self.scheduler.get_jobs()) if self.running else 0

        return {
            "total_jobs": total_jobs,
            "pending_jobs": status_counts.get("pending", 0),
            "running_jobs": status_counts.get("running", 0),
            "completed_jobs": status_counts.get("completed", 0),
            "failed_jobs": status_counts.get("failed", 0),
            "queue_size": scheduled_jobs,
            "active_workers": scheduled_jobs,  # APScheduler manages workers internally
            "max_workers": self.max_workers,
            "status_counts": status_counts,
        }

    async def start(self) -> None:
        """Start the job queue workers."""
        if self.running:
            return

        self.running = True
        logger.info(f"Starting job queue with APScheduler (max_workers: {self.max_workers})")

        # Capture the main event loop so thread workers can bounce async callbacks here
        try:
            self._main_loop = asyncio.get_running_loop()
        except RuntimeError:
            self._main_loop = None

        # Start APScheduler
        self.scheduler.start()

        logger.info("Job queue started")

    async def stop(self) -> None:
        """Stop the job queue workers."""
        if not self.running:
            return

        logger.info("Stopping job queue")
        self.running = False

        # Stop APScheduler
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)

        logger.info("Job queue stopped")

    # ----------------- Internal helpers -----------------

    def _select_wrapper_and_executor(self, info: JobHandlerInfo) -> tuple[Callable[..., Any], str]:
        """Choose the correct callable and executor name for APScheduler."""
        if info.executor == "default":
            # Orchestration in a worker thread
            return (self._execute_job_wrapper_sync, "default")
        else:
            # Orchestration on the event loop; offload sync handlers as needed
            return (self._execute_job_wrapper_async, "asyncio")

    # ----------------- Execution wrappers -----------------

    async def _execute_job_wrapper_async(self, job_id: str) -> None:
        """Wrapper function for APScheduler to execute jobs on the event loop."""
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for execution")
            return

        if job.status == JobStatus.CANCELLED:
            logger.info(f"Job {job_id} was cancelled before execution")
            return

        await self._execute_job_async(job)

    def _execute_job_wrapper_sync(self, job_id: str) -> None:
        """Wrapper function for APScheduler to execute jobs in a worker thread."""
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job {job_id} not found for execution")
            return

        if job.status == JobStatus.CANCELLED:
            logger.info(f"Job {job_id} was cancelled before execution")
            return

        # Run the full execution flow in this worker thread
        self._execute_job_sync(job)

    # ----------------- Execution flows -----------------

    async def _execute_job_async(self, job: Job) -> None:
        """Execute a single job with orchestration on the event loop."""
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

        logger.info(
            "Executing job",
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
            # Get job handler info
            info = self.job_handlers.get(job.function_name)
            if not info:
                raise ValueError(f"No handler registered for function: {job.function_name}")

            # Execute job with timeout
            if info.is_async:
                result = await asyncio.wait_for(
                    info.func(*job.args, **job.kwargs),
                    timeout=job.timeout,
                )
            else:
                # Run sync work without blocking the loop
                result = await asyncio.wait_for(
                    asyncio.to_thread(info.func, *job.args, **job.kwargs),
                    timeout=job.timeout,
                )

            # Job completed successfully
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(UTC)
            job.result = result  # Store result on job object too

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
            )

            # Trigger job completed event
            try:
                from chatter.services.sse_events import (
                    trigger_job_completed,
                )
                await trigger_job_completed(job.id, job.name, result or {})
            except Exception as e:
                logger.warning("Failed to trigger job completed event", error=str(e))

        except TimeoutError:
            await self._handle_job_error(job, "Job timed out")
        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            logger.info(f"Job {job.id} was cancelled")
        except Exception as e:
            await self._handle_job_error(job, str(e))

    def _execute_job_sync(self, job: Job) -> None:
        """Execute a single job with orchestration in a worker thread.

        Note: If the handler is async, we dispatch it back to the main loop
        with run_coroutine_threadsafe to avoid cross-loop resource issues.
        """
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now(UTC)

        logger.info(
            "Executing job (thread)",
            job_id=job.id,
            name=job.name,
            function_name=job.function_name,
        )

        # Trigger job started event on the main loop if available
        try:
            from chatter.services.sse_events import trigger_job_started
            if self._main_loop:
                asyncio.run_coroutine_threadsafe(
                    trigger_job_started(job.id, job.name), self._main_loop
                )
        except Exception as e:
            logger.warning("Failed to trigger job started event (thread)", error=str(e))

        start_time = datetime.now(UTC)

        def _complete_success(result: Any) -> None:
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(UTC)
            job.result = result
            execution_time = (job.completed_at - start_time).total_seconds()
            self.results[job.id] = JobResult(
                job_id=job.id,
                status=JobStatus.COMPLETED,
                result=result,
                execution_time=execution_time,
                completed_at=job.completed_at,
            )
            logger.info(
                "Job completed successfully (thread)",
                job_id=job.id,
                execution_time=execution_time,
            )
            # Trigger job completed on the main loop if available
            try:
                from chatter.services.sse_events import (
                    trigger_job_completed,
                )
                if self._main_loop:
                    asyncio.run_coroutine_threadsafe(
                        trigger_job_completed(job.id, job.name, result or {}),
                        self._main_loop,
                    )
            except Exception as e:
                logger.warning(
                    "Failed to trigger job completed event (thread)", error=str(e)
                )

        def _handle_error_sync(msg: str) -> None:
            # Run async error handler on the main loop if available
            try:
                if self._main_loop:
                    fut = asyncio.run_coroutine_threadsafe(
                        self._handle_job_error(job, msg), self._main_loop
                    )
                    fut.result()  # wait to keep state consistent
                else:
                    # Fallback: no loop available; mark failed locally
                    job.status = JobStatus.FAILED
                    job.completed_at = datetime.now(UTC)
                    execution_time = (
                        (job.completed_at - job.started_at).total_seconds()
                        if job.started_at
                        else 0
                    )
                    self.results[job.id] = JobResult(
                        job_id=job.id,
                        status=JobStatus.FAILED,
                        error=msg,
                        execution_time=execution_time,
                        completed_at=job.completed_at,
                    )
            except Exception as e:
                logger.warning("Error during sync error handling", error=str(e))

        try:
            info = self.job_handlers.get(job.function_name)
            if not info:
                _handle_error_sync(f"No handler registered for function: {job.function_name}")
                return

            if info.is_async:
                if not self._main_loop:
                    _handle_error_sync("No main event loop available for async handler")
                    return

                # Schedule coroutine on the main loop and wait here with a timeout
                fut = asyncio.run_coroutine_threadsafe(
                    info.func(*job.args, **job.kwargs), self._main_loop
                )
                try:
                    result = fut.result(timeout=job.timeout)
                except concurrent.futures.TimeoutError:
                    fut.cancel()
                    _handle_error_sync("Job timed out")
                    return

                _complete_success(result)
            else:
                # Best-effort: run sync handler directly (no preemptive timeout for arbitrary blocking calls)
                result = info.func(*job.args, **job.kwargs)
                _complete_success(result)

        except Exception as e:
            _handle_error_sync(str(e))

    async def _handle_job_error(self, job: Job, error_message: str) -> None:
        """Handle job execution errors and retries.

        Args:
            job: Failed job
            error_message: Error message
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
            )

            # Schedule retry with APScheduler
            await self._schedule_retry(job)

        else:
            # Max retries exceeded
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(UTC)

            execution_time = (
                (job.completed_at - job.started_at).total_seconds() if job.started_at else 0
            )

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
            )

            # Trigger job failed event
            try:
                from chatter.services.sse_events import (
                    trigger_job_failed,
                )

                await trigger_job_failed(job.id, job.name, error_message)
            except Exception as e:
                logger.warning("Failed to trigger job failed event", error=str(e))

    async def _schedule_retry(self, job: Job) -> None:
        """Schedule a job retry after delay using APScheduler.

        Args:
            job: Job to retry
        """
        from datetime import timedelta

        if not self.running:
            logger.warning(f"Not scheduling retry for job {job.id} - scheduler not running")
            return

        info = self.job_handlers.get(job.function_name)
        if not info:
            logger.error(f"No handler registered for function: {job.function_name}")
            return

        # Calculate retry delay (exponential backoff)
        retry_delay = min(job.retry_delay * (2 ** (job.retry_count - 1)), 3600)  # Cap at 1 hour
        run_date = datetime.now(UTC) + timedelta(seconds=retry_delay)

        # Remove existing job if it exists
        try:
            self.scheduler.remove_job(job.id)
        except Exception:
            pass  # Job might not exist in scheduler

        # Pick correct wrapper and executor up front
        job_func, executor_name = self._select_wrapper_and_executor(info)

        # Schedule retry
        self.scheduler.add_job(
            func=job_func,
            trigger="date",
            run_date=run_date,
            args=[job.id],
            id=str(job.id),  # Ensure it's a string
            name=f"{job.name} (retry {job.retry_count})",
            executor=executor_name,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=30,
        )

        logger.info(
            "Scheduled job retry",
            job_id=job.id,
            retry_count=job.retry_count,
            delay_seconds=retry_delay,
            run_date=run_date,
            executor=executor_name,
        )


# Global job queue instance
job_queue = AdvancedJobQueue(max_workers=settings.background_worker_concurrency)


# Register some default job handlers
async def document_processing_job(document_id: str, file_content: bytes) -> dict[str, Any]:
    """Document processing job handler for background processing."""
    from chatter.utils.database import get_session_maker

    logger.info(f"Starting background processing for document {document_id}")

    try:
        # Get a database session for background processing
        async_session = get_session_maker()
        async with async_session() as session:
            from chatter.services.document_processing import (
                DocumentProcessingService,
            )

            # Create processing service instance
            processing_service = DocumentProcessingService(session)

            # Process the document (chunking + embeddings)
            # If process_document does any blocking work, ensure it offloads with asyncio.to_thread
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
# Note: document_processing stays on the 'asyncio' executor by default to keep async DB work
# on the main loop. Offload any blocking bits inside the handler/service with asyncio.to_thread.
job_queue.register_handler("document_processing", document_processing_job)
job_queue.register_handler("conversation_summarization", conversation_summarization_job)
job_queue.register_handler("vector_store_maintenance", vector_store_maintenance_job)
job_queue.register_handler("data_export", data_export_job)
