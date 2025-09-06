"""Unit tests for jobs API endpoints."""

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient

from chatter.schemas.jobs import JobPriority, JobStatus


class TestJobsUnit:
    """Unit tests for jobs API endpoints."""

    @pytest.mark.unit
    async def test_create_job_requires_auth(self, client: AsyncClient):
        """Test that creating job requires authentication."""
        job_data = {
            "name": "Test Job",
            "function_name": "test_function",
            "args": [],
            "kwargs": {},
        }

        response = await client.post("/api/v1/jobs/", json=job_data)
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_list_jobs_requires_auth(self, client: AsyncClient):
        """Test that listing jobs requires authentication."""
        response = await client.get("/api/v1/jobs/")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_job_requires_auth(self, client: AsyncClient):
        """Test that getting specific job requires authentication."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.get(f"/api/v1/jobs/{job_id}")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_cancel_job_requires_auth(self, client: AsyncClient):
        """Test that canceling job requires authentication."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        response = await client.post(f"/api/v1/jobs/{job_id}/cancel")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_job_stats_requires_auth(
        self, client: AsyncClient
    ):
        """Test that getting job stats requires authentication."""
        response = await client.get("/api/v1/jobs/stats/overview")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_cleanup_jobs_requires_auth(
        self, client: AsyncClient
    ):
        """Test that cleanup jobs requires authentication."""
        response = await client.post("/api/v1/jobs/cleanup")
        assert response.status_code == 401

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_create_job_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job creation."""
        # Mock job queue
        mock_job = MagicMock()
        mock_job.id = "job-123"
        mock_job.name = "Test Job"
        mock_job.function_name = "test_function"
        mock_job.status = JobStatus.PENDING
        mock_job.priority = JobPriority.NORMAL
        mock_job.created_at = "2024-01-01T12:00:00Z"
        mock_job.created_by = "testuser"

        mock_job_queue.has_handler.return_value = True
        mock_job_queue.submit.return_value = mock_job

        job_data = {
            "name": "Test Job",
            "function_name": "test_function",
            "args": ["arg1", "arg2"],
            "kwargs": {"key1": "value1"},
            "priority": "normal",
        }

        response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["id"] == "job-123"
        assert data["name"] == "Test Job"
        assert data["status"] == "pending"

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_create_job_invalid_function(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test job creation with invalid function name."""
        mock_job_queue.has_handler.return_value = False

        job_data = {
            "name": "Test Job",
            "function_name": "nonexistent_function",
            "args": [],
            "kwargs": {},
        }

        response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert response.status_code == 400

    @pytest.mark.unit
    async def test_create_job_invalid_data(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test job creation with invalid data."""
        # Missing required fields
        job_data = {
            "name": "Test Job"
            # Missing function_name
        }

        response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job listing."""
        mock_jobs = [
            {
                "id": "job-1",
                "name": "Job 1",
                "status": "completed",
                "created_at": "2024-01-01T12:00:00Z",
            },
            {
                "id": "job-2",
                "name": "Job 2",
                "status": "pending",
                "created_at": "2024-01-01T13:00:00Z",
            },
        ]

        mock_job_queue.list_jobs.return_value = {
            "jobs": mock_jobs,
            "total": 2,
            "page": 1,
            "per_page": 10,
        }

        response = await client.get(
            "/api/v1/jobs/", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["total"] == 2

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_with_filters(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test job listing with filters."""
        mock_job_queue.list_jobs.return_value = {
            "jobs": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
        }

        # Test with status filter
        response = await client.get(
            "/api/v1/jobs/?status=completed", headers=auth_headers
        )
        assert response.status_code == 200

        # Verify filters were passed to job queue
        mock_job_queue.list_jobs.assert_called()
        call_args = mock_job_queue.list_jobs.call_args[1]
        assert "status" in call_args

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job retrieval."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_job = {
            "id": job_id,
            "name": "Test Job",
            "status": "completed",
            "result": "Job completed successfully",
            "created_at": "2024-01-01T12:00:00Z",
            "completed_at": "2024-01-01T12:05:00Z",
        }

        mock_job_queue.get_job.return_value = mock_job

        response = await client.get(
            f"/api/v1/jobs/{job_id}", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == job_id
        assert data["status"] == "completed"
        assert data["result"] == "Job completed successfully"

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_not_found(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test job retrieval for non-existent job."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_job_queue.get_job.return_value = None

        response = await client.get(
            f"/api/v1/jobs/{job_id}", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.unit
    async def test_get_job_invalid_id_format(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test job retrieval with invalid job ID format."""
        invalid_job_id = "not-a-uuid"

        response = await client.get(
            f"/api/v1/jobs/{invalid_job_id}", headers=auth_headers
        )
        assert response.status_code == 400

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_cancel_job_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job cancellation."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"

        mock_job_queue.cancel_job.return_value = True

        response = await client.post(
            f"/api/v1/jobs/{job_id}/cancel", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["job_id"] == job_id
        assert data["action"] == "cancel"

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_cancel_job_not_found(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test cancellation of non-existent job."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        mock_job_queue.cancel_job.return_value = False

        response = await client.post(
            f"/api/v1/jobs/{job_id}/cancel", headers=auth_headers
        )
        assert response.status_code == 404

    @pytest.mark.unit
    async def test_cancel_job_invalid_id_format(
        self, client: AsyncClient, auth_headers: dict
    ):
        """Test job cancellation with invalid job ID format."""
        invalid_job_id = "not-a-uuid"

        response = await client.post(
            f"/api/v1/jobs/{invalid_job_id}/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 400

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_get_job_stats_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job stats retrieval."""
        mock_stats = {
            "total_jobs": 100,
            "pending_jobs": 5,
            "running_jobs": 3,
            "completed_jobs": 85,
            "failed_jobs": 7,
            "cancelled_jobs": 0,
            "queue_size": 8,
            "worker_count": 4,
            "average_processing_time": 45.5,
        }

        mock_job_queue.get_stats.return_value = mock_stats

        response = await client.get(
            "/api/v1/jobs/stats/overview", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total_jobs"] == 100
        assert data["pending_jobs"] == 5
        assert data["running_jobs"] == 3
        assert data["queue_size"] == 8

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_cleanup_jobs_success(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test successful job cleanup."""
        mock_job_queue.cleanup_completed_jobs.return_value = {
            "cleaned_count": 25,
            "remaining_count": 75,
        }

        response = await client.post(
            "/api/v1/jobs/cleanup", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["cleaned_count"] == 25
        assert data["remaining_count"] == 75

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_job_queue_error_handling(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test job queue error handling."""
        mock_job_queue.submit.side_effect = Exception("Job queue error")

        job_data = {
            "name": "Test Job",
            "function_name": "test_function",
            "args": [],
            "kwargs": {},
        }

        response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert response.status_code == 500

    @pytest.mark.unit
    @patch('chatter.api.jobs.job_queue')
    async def test_list_jobs_pagination(
        self, mock_job_queue, client: AsyncClient, auth_headers: dict
    ):
        """Test job listing pagination."""
        mock_job_queue.list_jobs.return_value = {
            "jobs": [],
            "total": 50,
            "page": 2,
            "per_page": 20,
        }

        response = await client.get(
            "/api/v1/jobs/?page=2&per_page=20", headers=auth_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 50
        assert data["page"] == 2
        assert data["per_page"] == 20
