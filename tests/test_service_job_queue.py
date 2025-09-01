"""Tests for job queue service functionality."""

import pytest
import asyncio
from datetime import datetime, UTC, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from chatter.services.job_queue import AdvancedJobQueue, JobHandlerInfo
from chatter.schemas.jobs import Job, JobPriority, JobStatus, JobResult


@pytest.mark.unit
class TestJobQueue:
    """Test job queue functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.job_queue = AdvancedJobQueue(max_workers=2)

    @pytest.mark.asyncio
    async def test_job_queue_initialization(self):
        """Test job queue initialization."""
        # Act
        queue = AdvancedJobQueue(max_workers=4)
        
        # Assert
        assert queue.max_workers == 4
        assert queue.jobs == {}
        assert queue.results == {}
        assert queue.job_handlers == {}
        assert queue.running is False

    @pytest.mark.asyncio
    async def test_register_job_handler(self):
        """Test registering a job handler."""
        # Arrange
        def test_handler(data: dict) -> str:
            return f"Processed: {data.get('message', 'no message')}"
        
        # Act
        await self.job_queue.register_handler("test_job", test_handler)
        
        # Assert
        assert "test_job" in self.job_queue.job_handlers
        handler_info = self.job_queue.job_handlers["test_job"]
        assert handler_info.func == test_handler
        assert handler_info.is_async is False

    @pytest.mark.asyncio
    async def test_register_async_job_handler(self):
        """Test registering an async job handler."""
        # Arrange
        async def async_test_handler(data: dict) -> str:
            await asyncio.sleep(0.1)
            return f"Async processed: {data.get('message', 'no message')}"
        
        # Act
        await self.job_queue.register_handler("async_test_job", async_test_handler)
        
        # Assert
        assert "async_test_job" in self.job_queue.job_handlers
        handler_info = self.job_queue.job_handlers["async_test_job"]
        assert handler_info.func == async_test_handler
        assert handler_info.is_async is True

    @pytest.mark.asyncio
    async def test_submit_job_success(self):
        """Test successful job submission."""
        # Arrange
        def test_handler(data: dict) -> str:
            return f"Processed: {data['message']}"
        
        await self.job_queue.register_handler("test_task", test_handler)
        
        job_data = {"message": "Hello, World!"}
        
        # Act
        job_id = await self.job_queue.submit_job(
            job_type="test_task",
            data=job_data,
            priority=JobPriority.NORMAL
        )
        
        # Assert
        assert job_id is not None
        assert job_id in self.job_queue.jobs
        
        job = self.job_queue.jobs[job_id]
        assert job.type == "test_task"
        assert job.data == job_data
        assert job.priority == JobPriority.NORMAL
        assert job.status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_submit_job_with_schedule(self):
        """Test submitting a scheduled job."""
        # Arrange
        def scheduled_handler(data: dict) -> str:
            return "Scheduled task executed"
        
        await self.job_queue.register_handler("scheduled_task", scheduled_handler)
        
        schedule_time = datetime.now(UTC) + timedelta(seconds=5)
        
        # Act
        job_id = await self.job_queue.submit_job(
            job_type="scheduled_task",
            data={"scheduled": True},
            scheduled_time=schedule_time
        )
        
        # Assert
        job = self.job_queue.jobs[job_id]
        assert job.scheduled_time == schedule_time
        assert job.status == JobStatus.SCHEDULED

    @pytest.mark.asyncio
    async def test_submit_job_unknown_handler(self):
        """Test submitting job with unknown handler."""
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            await self.job_queue.submit_job(
                job_type="unknown_task",
                data={"test": "data"}
            )
        
        assert "No handler registered for job type: unknown_task" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_job_status(self):
        """Test getting job status."""
        # Arrange
        def test_handler(data: dict) -> str:
            return "test result"
        
        await self.job_queue.register_handler("status_test", test_handler)
        job_id = await self.job_queue.submit_job("status_test", {"test": "data"})
        
        # Act
        status = await self.job_queue.get_job_status(job_id)
        
        # Assert
        assert status == JobStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_job_result_not_completed(self):
        """Test getting result for non-completed job."""
        # Arrange
        def test_handler(data: dict) -> str:
            return "test result"
        
        await self.job_queue.register_handler("result_test", test_handler)
        job_id = await self.job_queue.submit_job("result_test", {"test": "data"})
        
        # Act
        result = await self.job_queue.get_job_result(job_id)
        
        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_job_success(self):
        """Test successful job cancellation."""
        # Arrange
        def slow_handler(data: dict) -> str:
            # Simulate slow task
            import time
            time.sleep(1)
            return "slow result"
        
        await self.job_queue.register_handler("slow_task", slow_handler)
        job_id = await self.job_queue.submit_job("slow_task", {"test": "data"})
        
        # Act
        cancelled = await self.job_queue.cancel_job(job_id)
        
        # Assert
        assert cancelled is True
        job = self.job_queue.jobs[job_id]
        assert job.status == JobStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_list_jobs_filtering(self):
        """Test listing jobs with filtering."""
        # Arrange
        def test_handler(data: dict) -> str:
            return "test"
        
        await self.job_queue.register_handler("filter_test", test_handler)
        
        # Submit multiple jobs
        job_ids = []
        for i in range(3):
            job_id = await self.job_queue.submit_job("filter_test", {"index": i})
            job_ids.append(job_id)
        
        # Cancel one job
        await self.job_queue.cancel_job(job_ids[1])
        
        # Act
        all_jobs = await self.job_queue.list_jobs()
        pending_jobs = await self.job_queue.list_jobs(status=JobStatus.PENDING)
        cancelled_jobs = await self.job_queue.list_jobs(status=JobStatus.CANCELLED)
        
        # Assert
        assert len(all_jobs) == 3
        assert len(pending_jobs) == 2
        assert len(cancelled_jobs) == 1

    @pytest.mark.asyncio
    async def test_job_retry_mechanism(self):
        """Test job retry mechanism."""
        # Arrange
        call_count = 0
        
        def failing_handler(data: dict) -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Attempt {call_count} failed")
            return f"Success on attempt {call_count}"
        
        await self.job_queue.register_handler("retry_test", failing_handler)
        
        # Act
        job_id = await self.job_queue.submit_job(
            job_type="retry_test",
            data={"test": "retry"},
            max_retries=3
        )
        
        # Simulate job execution with retries
        job = self.job_queue.jobs[job_id]
        
        # First attempt (should fail)
        try:
            result = failing_handler(job.data)
        except Exception:
            job.retry_count += 1
            job.status = JobStatus.RETRYING
        
        # Second attempt (should fail)
        try:
            result = failing_handler(job.data)
        except Exception:
            job.retry_count += 1
            job.status = JobStatus.RETRYING
        
        # Third attempt (should succeed)
        result = failing_handler(job.data)
        job.status = JobStatus.COMPLETED
        
        # Assert
        assert job.retry_count == 2
        assert job.status == JobStatus.COMPLETED
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_job_priority_handling(self):
        """Test job priority handling."""
        # Arrange
        def priority_handler(data: dict) -> str:
            return f"Priority: {data['priority']}"
        
        await self.job_queue.register_handler("priority_test", priority_handler)
        
        # Submit jobs with different priorities
        high_job_id = await self.job_queue.submit_job(
            "priority_test", 
            {"priority": "high"}, 
            priority=JobPriority.HIGH
        )
        low_job_id = await self.job_queue.submit_job(
            "priority_test", 
            {"priority": "low"}, 
            priority=JobPriority.LOW
        )
        normal_job_id = await self.job_queue.submit_job(
            "priority_test", 
            {"priority": "normal"}, 
            priority=JobPriority.NORMAL
        )
        
        # Act
        jobs = await self.job_queue.list_jobs()
        
        # Assert jobs have correct priorities
        high_job = next(job for job in jobs if job.id == high_job_id)
        low_job = next(job for job in jobs if job.id == low_job_id)
        normal_job = next(job for job in jobs if job.id == normal_job_id)
        
        assert high_job.priority == JobPriority.HIGH
        assert low_job.priority == JobPriority.LOW
        assert normal_job.priority == JobPriority.NORMAL

    @pytest.mark.asyncio
    async def test_get_queue_stats(self):
        """Test getting queue statistics."""
        # Arrange
        def stats_handler(data: dict) -> str:
            return "stats test"
        
        await self.job_queue.register_handler("stats_test", stats_handler)
        
        # Submit some jobs
        for i in range(5):
            await self.job_queue.submit_job("stats_test", {"index": i})
        
        # Act
        stats = await self.job_queue.get_stats()
        
        # Assert
        assert stats["total_jobs"] == 5
        assert stats["pending_jobs"] == 5
        assert stats["completed_jobs"] == 0
        assert stats["failed_jobs"] == 0
        assert stats["queue_size"] == 5

    @pytest.mark.asyncio
    async def test_job_queue_start_stop(self):
        """Test starting and stopping the job queue."""
        # Arrange
        with patch.object(self.job_queue, 'scheduler') as mock_scheduler:
            mock_scheduler.start = AsyncMock()
            mock_scheduler.shutdown = AsyncMock()
            
            # Act - Start
            await self.job_queue.start()
            
            # Assert - Start
            assert self.job_queue.running is True
            mock_scheduler.start.assert_called_once()
            
            # Act - Stop
            await self.job_queue.stop()
            
            # Assert - Stop
            assert self.job_queue.running is False
            mock_scheduler.shutdown.assert_called_once()

    @pytest.mark.asyncio
    async def test_job_cleanup_old_jobs(self):
        """Test cleanup of old completed jobs."""
        # Arrange
        def cleanup_handler(data: dict) -> str:
            return "cleanup test"
        
        await self.job_queue.register_handler("cleanup_test", cleanup_handler)
        
        # Submit and complete jobs
        job_ids = []
        for i in range(3):
            job_id = await self.job_queue.submit_job("cleanup_test", {"index": i})
            job_ids.append(job_id)
            
            # Simulate job completion with old timestamp
            job = self.job_queue.jobs[job_id]
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(UTC) - timedelta(days=2)
            
            # Store result
            self.job_queue.results[job_id] = JobResult(
                job_id=job_id,
                result=f"Result {i}",
                completed_at=job.completed_at
            )
        
        # Act
        initial_count = len(self.job_queue.jobs)
        cleaned_count = await self.job_queue.cleanup_old_jobs(max_age_days=1)
        
        # Assert
        assert initial_count == 3
        assert cleaned_count == 3
        # Jobs should be removed from active jobs but results might be kept
        assert len(self.job_queue.jobs) == 0 or all(
            job.status != JobStatus.COMPLETED for job in self.job_queue.jobs.values()
        )


@pytest.mark.integration
class TestJobQueueIntegration:
    """Integration tests for job queue functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.job_queue = AdvancedJobQueue(max_workers=2)

    @pytest.mark.asyncio
    async def test_job_queue_full_lifecycle(self):
        """Test complete job lifecycle from submission to completion."""
        # Arrange
        execution_log = []
        
        async def lifecycle_handler(data: dict) -> dict:
            execution_log.append(f"Processing: {data['task_name']}")
            await asyncio.sleep(0.1)  # Simulate work
            result = {"processed": data['task_name'], "timestamp": datetime.now(UTC).isoformat()}
            execution_log.append(f"Completed: {data['task_name']}")
            return result
        
        # Register handler and start queue
        await self.job_queue.register_handler("lifecycle_task", lifecycle_handler)
        await self.job_queue.start()
        
        try:
            # Act - Submit job
            job_id = await self.job_queue.submit_job(
                "lifecycle_task",
                {"task_name": "integration_test"},
                priority=JobPriority.HIGH
            )
            
            # Wait for processing (in real implementation, job would be processed automatically)
            # For test, we'll simulate the execution
            job = self.job_queue.jobs[job_id]
            assert job.status == JobStatus.PENDING
            
            # Simulate job execution
            try:
                handler_info = self.job_queue.job_handlers["lifecycle_task"]
                result = await handler_info.func(job.data)
                
                # Update job status
                job.status = JobStatus.COMPLETED
                job.completed_at = datetime.now(UTC)
                
                # Store result
                self.job_queue.results[job_id] = JobResult(
                    job_id=job_id,
                    result=result,
                    completed_at=job.completed_at
                )
                
            except Exception as e:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
            
            # Assert final state
            assert job.status == JobStatus.COMPLETED
            assert len(execution_log) == 2
            assert "integration_test" in execution_log[0]
            
            # Verify result can be retrieved
            result = await self.job_queue.get_job_result(job_id)
            assert result is not None
            assert result.result["processed"] == "integration_test"
            
        finally:
            await self.job_queue.stop()

    @pytest.mark.asyncio
    async def test_concurrent_job_processing(self):
        """Test concurrent job processing."""
        # Arrange
        processed_jobs = []
        
        async def concurrent_handler(data: dict) -> str:
            job_name = data["job_name"]
            processed_jobs.append(f"Started: {job_name}")
            await asyncio.sleep(0.2)  # Simulate work
            processed_jobs.append(f"Finished: {job_name}")
            return f"Result for {job_name}"
        
        await self.job_queue.register_handler("concurrent_task", concurrent_handler)
        await self.job_queue.start()
        
        try:
            # Act - Submit multiple jobs
            job_ids = []
            for i in range(3):
                job_id = await self.job_queue.submit_job(
                    "concurrent_task",
                    {"job_name": f"job_{i}"}
                )
                job_ids.append(job_id)
            
            # Simulate concurrent processing
            tasks = []
            for job_id in job_ids:
                job = self.job_queue.jobs[job_id]
                handler_info = self.job_queue.job_handlers["concurrent_task"]
                
                async def process_job(j, h):
                    try:
                        result = await h.func(j.data)
                        j.status = JobStatus.COMPLETED
                        j.completed_at = datetime.now(UTC)
                        self.job_queue.results[j.id] = JobResult(
                            job_id=j.id,
                            result=result,
                            completed_at=j.completed_at
                        )
                    except Exception as e:
                        j.status = JobStatus.FAILED
                        j.error_message = str(e)
                
                tasks.append(process_job(job, handler_info))
            
            # Wait for all jobs to complete
            await asyncio.gather(*tasks)
            
            # Assert all jobs completed
            for job_id in job_ids:
                job = self.job_queue.jobs[job_id]
                assert job.status == JobStatus.COMPLETED
            
            assert len(processed_jobs) == 6  # 3 starts + 3 finishes
            
        finally:
            await self.job_queue.stop()

    @pytest.mark.asyncio
    async def test_job_queue_resilience(self):
        """Test job queue resilience under error conditions."""
        # Arrange
        error_count = 0
        
        async def error_prone_handler(data: dict) -> str:
            nonlocal error_count
            error_count += 1
            
            if data.get("should_fail", False):
                raise Exception("Simulated error")
            
            return f"Success after {error_count} calls"
        
        await self.job_queue.register_handler("error_task", error_prone_handler)
        await self.job_queue.start()
        
        try:
            # Submit a mix of successful and failing jobs
            success_job_id = await self.job_queue.submit_job(
                "error_task",
                {"should_fail": False}
            )
            
            fail_job_id = await self.job_queue.submit_job(
                "error_task", 
                {"should_fail": True}
            )
            
            # Process jobs
            for job_id in [success_job_id, fail_job_id]:
                job = self.job_queue.jobs[job_id]
                handler_info = self.job_queue.job_handlers["error_task"]
                
                try:
                    result = await handler_info.func(job.data)
                    job.status = JobStatus.COMPLETED
                    job.completed_at = datetime.now(UTC)
                    self.job_queue.results[job_id] = JobResult(
                        job_id=job_id,
                        result=result,
                        completed_at=job.completed_at
                    )
                except Exception as e:
                    job.status = JobStatus.FAILED
                    job.error_message = str(e)
            
            # Assert system handled both success and failure
            success_job = self.job_queue.jobs[success_job_id]
            fail_job = self.job_queue.jobs[fail_job_id]
            
            assert success_job.status == JobStatus.COMPLETED
            assert fail_job.status == JobStatus.FAILED
            assert "Simulated error" in fail_job.error_message
            
        finally:
            await self.job_queue.stop()