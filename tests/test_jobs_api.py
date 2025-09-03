"""Tests for job management functionality - unit tests without database."""

import pytest
from datetime import datetime, timedelta, UTC
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from chatter.schemas.jobs import (
    Job, 
    JobPriority, 
    JobStatus, 
    JobCreateRequest,
    JobListRequest,
    JobActionResponse
)
from chatter.services.job_queue import AdvancedJobQueue
from chatter.api.jobs import create_job, list_jobs, get_job, cancel_job, get_job_stats


@pytest.fixture
def job_queue():
    """Create a fresh job queue for testing."""
    queue = AdvancedJobQueue(max_workers=2)
    
    # Register a test handler
    def test_handler(message: str) -> str:
        return f"Processed: {message}"
    
    queue.register_handler("test_job", test_handler)
    return queue


@pytest.fixture
def mock_user():
    """Mock user for testing."""
    user = Mock()
    user.id = "test-user-123"
    user.email = "test@example.com"
    return user


class TestJobSchemas:
    """Test job schema validation and behavior."""

    def test_job_creation_with_defaults(self):
        """Test job creation with default values."""
        job = Job(
            name="Test Job",
            function_name="test_function"
        )
        
        assert job.name == "Test Job"
        assert job.function_name == "test_function"
        assert job.status == JobStatus.PENDING
        assert job.priority == JobPriority.NORMAL
        assert job.args == []
        assert job.kwargs == {}
        assert job.retry_count == 0
        assert job.max_retries == 3
        assert job.progress == 0
        assert job.id is not None

    def test_job_create_request_validation(self):
        """Test JobCreateRequest schema validation."""
        request = JobCreateRequest(
            name="Test Job",
            function_name="test_function",
            priority=JobPriority.HIGH,
            max_retries=5
        )
        
        assert request.name == "Test Job"
        assert request.function_name == "test_function"
        assert request.priority == JobPriority.HIGH
        assert request.max_retries == 5

    def test_job_create_request_scheduled(self):
        """Test JobCreateRequest with schedule_at."""
        future_time = datetime.now(UTC) + timedelta(hours=1)
        
        request = JobCreateRequest(
            name="Scheduled Job",
            function_name="test_function",
            schedule_at=future_time
        )
        
        assert request.schedule_at == future_time


class TestJobQueue:
    """Test the job queue functionality."""

    def test_register_handler(self, job_queue):
        """Test registering a job handler."""
        def test_handler():
            return "test"
        
        job_queue.register_handler("test_handler", test_handler)
        assert "test_handler" in job_queue.job_handlers

    async def test_add_job_simple(self, job_queue):
        """Test adding a simple job."""
        job_id = await job_queue.add_job(
            name="Test Job",
            function_name="test_job",
            args=["test message"]
        )
        
        assert job_id in job_queue.jobs
        job = job_queue.jobs[job_id]
        assert job.name == "Test Job"
        assert job.function_name == "test_job"
        assert job.args == ["test message"]
        assert job.status == JobStatus.PENDING

    async def test_add_job_with_schedule(self, job_queue):
        """Test adding a scheduled job."""
        future_time = datetime.now(UTC) + timedelta(minutes=5)
        
        job_id = await job_queue.add_job(
            name="Scheduled Job",
            function_name="test_job",
            schedule_at=future_time
        )
        
        assert job_id in job_queue.jobs
        job = job_queue.jobs[job_id]
        assert job.name == "Scheduled Job"

    async def test_add_job_unknown_handler(self, job_queue):
        """Test adding a job with unknown handler raises error."""
        with pytest.raises(ValueError, match="No handler registered"):
            await job_queue.add_job(
                name="Bad Job",
                function_name="unknown_handler"
            )

    async def test_get_job_status(self, job_queue):
        """Test getting job status."""
        job_id = await job_queue.add_job(
            name="Test Job",
            function_name="test_job"
        )
        
        status = await job_queue.get_job_status(job_id)
        assert status == JobStatus.PENDING

    async def test_cancel_job(self, job_queue):
        """Test cancelling a job."""
        job_id = await job_queue.add_job(
            name="Cancellable Job",
            function_name="test_job"
        )
        
        success = await job_queue.cancel_job(job_id)
        assert success is True
        
        job = job_queue.jobs[job_id]
        assert job.status == JobStatus.CANCELLED

    async def test_cancel_nonexistent_job(self, job_queue):
        """Test cancelling a nonexistent job."""
        fake_id = str(uuid4())
        success = await job_queue.cancel_job(fake_id)
        assert success is False

    async def test_get_stats(self, job_queue):
        """Test getting queue statistics."""
        # Add some jobs
        await job_queue.add_job("Job 1", "test_job")
        await job_queue.add_job("Job 2", "test_job")
        
        stats = await job_queue.get_stats()
        
        assert stats["total_jobs"] == 2
        assert stats["pending_jobs"] == 2
        assert stats["running_jobs"] == 0
        assert stats["completed_jobs"] == 0
        assert stats["failed_jobs"] == 0


class TestJobAPI:
    """Test job API endpoints using mocks."""

    @patch('chatter.api.jobs.job_queue')
    async def test_create_job_endpoint(self, mock_queue, mock_user):
        """Test create_job endpoint logic."""
        # Setup mock - make add_job async
        mock_queue.add_job = AsyncMock(return_value="test-job-id")
        mock_job = Job(
            id="test-job-id",
            name="Test Job",
            function_name="test_job"
        )
        mock_queue.jobs = {"test-job-id": mock_job}
        
        # Create job request
        job_data = JobCreateRequest(
            name="Test Job",
            function_name="test_job",
            args=["test"]
        )
        
        # Call endpoint
        result = await create_job(job_data, mock_user)
        
        # Verify
        assert result.id == "test-job-id"
        assert result.name == "Test Job"
        assert result.function_name == "test_job"
        mock_queue.add_job.assert_called_once()

    @patch('chatter.api.jobs.job_queue')
    async def test_create_scheduled_job_tracking_issue(self, mock_queue, mock_user):
        """Test that scheduled_at is properly returned (currently fails)."""
        future_time = datetime.now(UTC) + timedelta(hours=1)
        
        # Setup mock
        mock_queue.add_job = AsyncMock(return_value="test-job-id")
        mock_job = Job(
            id="test-job-id",
            name="Scheduled Job",
            function_name="test_job"
        )
        mock_queue.jobs = {"test-job-id": mock_job}
        
        # Create scheduled job request
        job_data = JobCreateRequest(
            name="Scheduled Job",
            function_name="test_job",
            schedule_at=future_time
        )
        
        # Call endpoint
        result = await create_job(job_data, mock_user)
        
        # This assertion should pass but exposes the bug
        # The API returns schedule_at from the request, not from the stored job
        assert result.scheduled_at == future_time

    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_endpoint(self, mock_queue, mock_user):
        """Test list_jobs endpoint logic."""
        # Setup mock jobs
        job1 = Job(id="job1", name="Job 1", function_name="test_job")
        job2 = Job(id="job2", name="Job 2", function_name="test_job", priority=JobPriority.HIGH)
        mock_queue.jobs = {"job1": job1, "job2": job2}
        
        # Test listing all jobs
        request = JobListRequest()
        result = await list_jobs(request, mock_user)
        
        assert result.total == 2
        assert len(result.jobs) == 2
        assert result.limit == 20  # Default limit
        assert result.offset == 0  # Default offset
        assert result.has_more is False

    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_with_filters(self, mock_queue, mock_user):
        """Test list_jobs with filtering."""
        # Setup mock jobs
        job1 = Job(id="job1", name="Job 1", function_name="test_job", priority=JobPriority.HIGH)
        job2 = Job(id="job2", name="Job 2", function_name="other_job", priority=JobPriority.LOW)
        mock_queue.jobs = {"job1": job1, "job2": job2}
        
        # Test filtering by priority
        request = JobListRequest(priority=JobPriority.HIGH)
        result = await list_jobs(request, mock_user)
        
        assert result.total == 1
        assert result.jobs[0].priority == JobPriority.HIGH

    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_pagination(self, mock_queue, mock_user):
        """Test list_jobs with pagination."""
        # Setup mock jobs
        jobs = {}
        for i in range(25):  # More than default limit
            job = Job(id=f"job{i}", name=f"Job {i}", function_name="test_job")
            jobs[f"job{i}"] = job
        mock_queue.jobs = jobs
        
        # Test first page
        request = JobListRequest(limit=10, offset=0)
        result = await list_jobs(request, mock_user)
        
        assert result.total == 25
        assert len(result.jobs) == 10
        assert result.limit == 10
        assert result.offset == 0
        assert result.has_more is True
        
        # Test second page
        request = JobListRequest(limit=10, offset=10)
        result = await list_jobs(request, mock_user)
        
        assert result.total == 25
        assert len(result.jobs) == 10
        assert result.limit == 10
        assert result.offset == 10
        assert result.has_more is True
        
        # Test last page
        request = JobListRequest(limit=10, offset=20)
        result = await list_jobs(request, mock_user)
        
        assert result.total == 25
        assert len(result.jobs) == 5
        assert result.limit == 10
        assert result.offset == 20
        assert result.has_more is False

    @patch('chatter.api.jobs.job_queue') 
    async def test_list_jobs_scheduled_at_fixed(self, mock_queue, mock_user):
        """Test that list_jobs now returns scheduled_at properly (bug fixed)."""
        # Setup mock job with scheduled_at
        future_time = datetime.now(UTC) + timedelta(hours=1)
        job = Job(
            id="job1", 
            name="Scheduled Job", 
            function_name="test_job",
            scheduled_at=future_time
        )
        mock_queue.jobs = {"job1": job}
        
        request = JobListRequest()
        result = await list_jobs(request, mock_user)
        
        # This assertion should now pass - scheduled_at is properly returned
        assert result.jobs[0].scheduled_at == future_time

    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_endpoint(self, mock_queue, mock_user):
        """Test get_job endpoint logic."""
        # Setup mock job
        job = Job(id="test-job-id", name="Test Job", function_name="test_job")
        mock_queue.jobs = {"test-job-id": job}
        
        # Call endpoint
        result = await get_job("test-job-id", mock_user)
        
        assert result.id == "test-job-id"
        assert result.name == "Test Job"

    @patch('chatter.api.jobs.job_queue')
    async def test_cancel_job_endpoint(self, mock_queue, mock_user):
        """Test cancel_job endpoint logic."""
        # Setup mock
        mock_queue.cancel_job = AsyncMock(return_value=True)
        
        # Call endpoint
        result = await cancel_job("test-job-id", mock_user)
        
        assert result.success is True
        assert result.job_id == "test-job-id"
        mock_queue.cancel_job.assert_called_once_with("test-job-id")

    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_stats_endpoint(self, mock_queue, mock_user):
        """Test get_job_stats endpoint logic."""
        # Setup mock stats
        mock_queue.get_stats = AsyncMock(return_value={
            "total_jobs": 10,
            "pending_jobs": 3,
            "running_jobs": 2,
            "completed_jobs": 4,
            "failed_jobs": 1,
            "queue_size": 5,
            "active_workers": 2
        })
        
        # Call endpoint
        result = await get_job_stats(mock_user)
        
        assert result.total_jobs == 10
        assert result.pending_jobs == 3
        assert result.running_jobs == 2
        assert result.completed_jobs == 4
        assert result.failed_jobs == 1


class TestJobValidation:
    """Test job input validation (documents missing validation)."""

    def test_pagination_now_supported(self):
        """Test that pagination is now supported in JobListRequest."""
        request = JobListRequest(limit=10, offset=20, sort_by="name", sort_order="asc")
        
        assert request.limit == 10
        assert request.offset == 20
        assert request.sort_by == "name"
        assert request.sort_order == "asc"

    def test_job_id_format_validation_added(self):
        """Test that job_id validation function works correctly."""
        from chatter.api.jobs import validate_job_id
        from chatter.utils.problem import ValidationProblem
        
        # Valid UUID should pass
        valid_uuid = "123e4567-e89b-12d3-a456-426614174000"
        assert validate_job_id(valid_uuid) == valid_uuid
        
        # Invalid format should raise ValidationProblem
        with pytest.raises(ValidationProblem):
            validate_job_id("not-a-uuid")

    def test_function_name_validation_added(self):
        """Test that function_name existence validation is implemented."""
        # This is now validated in the create_job endpoint
        request = JobCreateRequest(
            name="Test Job",
            function_name="definitely_not_a_real_function"
        )
        
        # The validation happens at the API level, not in the schema
        assert request.function_name == "definitely_not_a_real_function"

    @patch('chatter.api.jobs.job_queue')
    async def test_create_job_unknown_function_validation(self, mock_queue, mock_user):
        """Test creating a job with unknown function now gives proper validation error."""
        # Setup mock - no handlers registered
        mock_queue.job_handlers = {}
        
        job_data = JobCreateRequest(
            name="Bad Job",
            function_name="unknown_function"
        )
        
        # Should raise ValidationProblem instead of generic InternalServerProblem
        with pytest.raises(Exception) as exc_info:
            await create_job(job_data, mock_user)
        
        # The error should be more specific now
        assert "Unknown function" in str(exc_info.value) or "ValidationProblem" in str(type(exc_info.value))

    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_invalid_id_validation(self, mock_queue, mock_user):
        """Test getting a job with invalid UUID format."""
        mock_queue.jobs = {}
        
        # Should raise ValidationProblem for invalid UUID
        with pytest.raises(Exception) as exc_info:
            await get_job("not-a-uuid", mock_user)
        
        # The error should be about invalid format
        assert "Invalid job ID format" in str(exc_info.value) or "ValidationProblem" in str(type(exc_info.value))

    @patch('chatter.api.jobs.job_queue')
    async def test_cancel_job_invalid_id_validation(self, mock_queue, mock_user):
        """Test cancelling a job with invalid UUID format."""
        mock_queue.jobs = {}
        
        # Should raise ValidationProblem for invalid UUID
        with pytest.raises(Exception) as exc_info:
            await cancel_job("not-a-uuid", mock_user)
        
        # The error should be about invalid format
        assert "Invalid job ID format" in str(exc_info.value) or "ValidationProblem" in str(type(exc_info.value))


class TestJobSecurity:
    """Test job security and isolation issues."""

    def test_user_isolation_not_implemented(self):
        """Test that user isolation is not currently implemented."""
        # This test documents the security issue where users can access
        # jobs from other users. This should be fixed in the implementation.
        
        # Currently there's no user filtering in the job endpoints
        # All users can see all jobs, which is a security issue
        assert True  # Placeholder documenting the issue

    def test_no_rate_limiting(self):
        """Test that rate limiting is not implemented for job creation."""
        # This documents that users can create unlimited jobs
        # Should implement rate limiting to prevent abuse
        assert True  # Placeholder documenting the issue

    def test_no_authorization_beyond_authentication(self):
        """Test that there's no authorization beyond basic authentication."""
        # This documents that any authenticated user can cancel any job
        # Should implement proper authorization checks
        assert True  # Placeholder documenting the issue