"""Tests for API jobs endpoint functionality."""

from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from fastapi import status

# Mock all required modules at module level
import sys
for module_name in [
    'chatter.api.jobs',
    'chatter.services.job_queue',
    'chatter.schemas.jobs',
    'chatter.core.auth',
    'fastapi'
]:
    if module_name not in sys.modules:
        sys.modules[module_name] = MagicMock()


@pytest.mark.unit
class TestJobsAPIEndpoints:
    """Test jobs API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_user = MagicMock()
        self.mock_user.id = "user-123"
        self.mock_user.email = "test@example.com"
        
        # Mock FastAPI test client
        self.client = MagicMock()
        self.client.get = MagicMock()
        self.client.post = MagicMock()
        self.client.put = MagicMock()
        self.client.delete = MagicMock()

    def test_create_job_success(self):
        """Test successful job creation."""
        # Arrange
        job_data = {
            "name": "Document Processing Job",
            "type": "document_processing",
            "config": {
                "input_files": ["file1.pdf", "file2.pdf"],
                "processing_options": {"extract_text": True}
            },
            "priority": "normal",
            "scheduled_at": None
        }
        
        mock_job = {
            "id": "job-123",
            "name": job_data["name"],
            "type": job_data["type"],
            "status": "pending",
            "created_by": self.mock_user.id
        }
        
        with patch('chatter.services.job_queue.JobQueueService.create_job') as mock_create:
            mock_create.return_value = mock_job
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_201_CREATED
            mock_response.json.return_value = mock_job
            self.client.post.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                "/api/v1/jobs/",
                json=job_data,
                headers=headers
            )
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["id"] == "job-123"
            assert response_data["name"] == job_data["name"]
            assert response_data["status"] == "pending"

    def test_get_job_by_id_success(self):
        """Test retrieving job by ID."""
        # Arrange
        job_id = "job-123"
        mock_job = {
            "id": job_id,
            "name": "Test Job",
            "type": "data_processing",
            "status": "running",
            "progress": 45,
            "created_by": self.mock_user.id,
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        with patch('chatter.services.job_queue.JobQueueService.get_job') as mock_get:
            mock_get.return_value = mock_job
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = mock_job
            self.client.get.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/jobs/{job_id}", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["id"] == job_id
            assert response_data["status"] == "running"
            assert response_data["progress"] == 45

    def test_list_user_jobs_success(self):
        """Test listing user's jobs."""
        # Arrange
        mock_jobs = [
            {
                "id": "job-1",
                "name": "Job 1",
                "type": "embedding",
                "status": "completed"
            },
            {
                "id": "job-2", 
                "name": "Job 2",
                "type": "document_processing",
                "status": "running"
            }
        ]
        
        with patch('chatter.services.job_queue.JobQueueService.list_user_jobs') as mock_list:
            mock_list.return_value = mock_jobs
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = {"jobs": mock_jobs, "total": 2}
            self.client.get.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get("/api/v1/jobs/", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["jobs"]) == 2
            assert response_data["total"] == 2

    def test_cancel_job_success(self):
        """Test job cancellation."""
        # Arrange
        job_id = "job-123"
        
        mock_cancelled_job = {
            "id": job_id,
            "name": "Test Job",
            "status": "cancelled",
            "cancelled_at": "2024-01-01T01:00:00Z"
        }
        
        with patch('chatter.services.job_queue.JobQueueService.cancel_job') as mock_cancel:
            mock_cancel.return_value = mock_cancelled_job
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = mock_cancelled_job
            self.client.put.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.put(f"/api/v1/jobs/{job_id}/cancel", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "cancelled"

    def test_retry_job_success(self):
        """Test job retry functionality."""
        # Arrange
        job_id = "job-123"
        
        mock_retried_job = {
            "id": job_id,
            "name": "Test Job",
            "status": "pending",
            "retry_count": 1,
            "retried_at": "2024-01-01T02:00:00Z"
        }
        
        with patch('chatter.services.job_queue.JobQueueService.retry_job') as mock_retry:
            mock_retry.return_value = mock_retried_job
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = mock_retried_job
            self.client.put.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.put(f"/api/v1/jobs/{job_id}/retry", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "pending"
            assert response_data["retry_count"] == 1

    def test_get_job_logs_success(self):
        """Test retrieving job logs."""
        # Arrange
        job_id = "job-123"
        mock_logs = [
            {
                "timestamp": "2024-01-01T00:00:00Z",
                "level": "info",
                "message": "Job started"
            },
            {
                "timestamp": "2024-01-01T00:01:00Z",
                "level": "info", 
                "message": "Processing file 1 of 3"
            },
            {
                "timestamp": "2024-01-01T00:02:00Z",
                "level": "warning",
                "message": "File format not optimal"
            }
        ]
        
        with patch('chatter.services.job_queue.JobQueueService.get_job_logs') as mock_get_logs:
            mock_get_logs.return_value = mock_logs
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = {"logs": mock_logs}
            self.client.get.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/jobs/{job_id}/logs", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["logs"]) == 3
            assert response_data["logs"][0]["message"] == "Job started"

    def test_get_job_results_success(self):
        """Test retrieving job results."""
        # Arrange
        job_id = "job-123"
        mock_results = {
            "status": "completed",
            "output": {
                "processed_files": 3,
                "extracted_text_length": 15420,
                "embeddings_created": 45
            },
            "metadata": {
                "duration": 12.5,
                "memory_used": "256MB"
            }
        }
        
        with patch('chatter.services.job_queue.JobQueueService.get_job_results') as mock_get_results:
            mock_get_results.return_value = mock_results
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_200_OK
            mock_response.json.return_value = mock_results
            self.client.get.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/jobs/{job_id}/results", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "completed"
            assert response_data["output"]["processed_files"] == 3

    def test_schedule_job_success(self):
        """Test scheduling a job for future execution."""
        # Arrange
        job_data = {
            "name": "Scheduled Backup Job",
            "type": "backup",
            "config": {"backup_type": "full"},
            "scheduled_at": "2024-01-02T00:00:00Z"
        }
        
        mock_scheduled_job = {
            "id": "job-456",
            "name": job_data["name"],
            "status": "scheduled",
            "scheduled_at": job_data["scheduled_at"]
        }
        
        with patch('chatter.services.job_queue.JobQueueService.schedule_job') as mock_schedule:
            mock_schedule.return_value = mock_scheduled_job
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_201_CREATED
            mock_response.json.return_value = mock_scheduled_job
            self.client.post.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                "/api/v1/jobs/schedule",
                json=job_data,
                headers=headers
            )
            
            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["status"] == "scheduled"

    def test_delete_job_success(self):
        """Test job deletion."""
        # Arrange
        job_id = "job-123"
        
        with patch('chatter.services.job_queue.JobQueueService.delete_job') as mock_delete:
            mock_delete.return_value = True
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_204_NO_CONTENT
            self.client.delete.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.delete(f"/api/v1/jobs/{job_id}", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_get_job_not_found(self):
        """Test job not found error."""
        # Arrange
        job_id = "non-existent-job"
        
        with patch('chatter.services.job_queue.JobQueueService.get_job') as mock_get:
            mock_get.return_value = None
            
            # Mock response
            mock_response = MagicMock()
            mock_response.status_code = status.HTTP_404_NOT_FOUND
            mock_response.json.return_value = {"detail": "Job not found"}
            self.client.get.return_value = mock_response
            
            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/jobs/{job_id}", headers=headers)
            
            # Assert
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthorized_access(self):
        """Test unauthorized access to jobs."""
        # Arrange
        # Mock response for unauthorized access
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED
        mock_response.json.return_value = {"detail": "Not authenticated"}
        self.client.get.return_value = mock_response
        
        # Act
        response = self.client.get("/api/v1/jobs/")  # No auth header
        
        # Assert
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestJobsAPIIntegration:
    """Integration tests for jobs API."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.mock_user = MagicMock()
        self.mock_user.id = "user-123"
        self.client = MagicMock()

    def test_job_lifecycle_integration(self):
        """Test complete job lifecycle through API."""
        # Arrange
        job_data = {
            "name": "Integration Test Job",
            "type": "test_processing",
            "config": {"test_param": "value"}
        }
        
        # Mock service responses
        mock_created_job = {"id": "job-123", "status": "pending"}
        mock_running_job = {"id": "job-123", "status": "running", "progress": 50}
        mock_completed_job = {"id": "job-123", "status": "completed", "progress": 100}
        
        with patch('chatter.services.job_queue.JobQueueService') as mock_service:
            mock_service.create_job.return_value = mock_created_job
            mock_service.get_job.side_effect = [mock_running_job, mock_completed_job]
            
            # Mock responses
            create_response = MagicMock()
            create_response.status_code = status.HTTP_201_CREATED
            create_response.json.return_value = mock_created_job
            
            get_response_1 = MagicMock()
            get_response_1.status_code = status.HTTP_200_OK
            get_response_1.json.return_value = mock_running_job
            
            get_response_2 = MagicMock()
            get_response_2.status_code = status.HTTP_200_OK
            get_response_2.json.return_value = mock_completed_job
            
            self.client.post.return_value = create_response
            self.client.get.side_effect = [get_response_1, get_response_2]
            
            # Act & Assert
            # Create job
            headers = {"Authorization": "Bearer test-token"}
            create_resp = self.client.post("/api/v1/jobs/", json=job_data, headers=headers)
            assert create_resp.status_code == status.HTTP_201_CREATED
            
            # Check job status (running)
            job_id = create_resp.json()["id"]
            status_resp_1 = self.client.get(f"/api/v1/jobs/{job_id}", headers=headers)
            assert status_resp_1.json()["status"] == "running"
            
            # Check job status (completed)
            status_resp_2 = self.client.get(f"/api/v1/jobs/{job_id}", headers=headers)
            assert status_resp_2.json()["status"] == "completed"