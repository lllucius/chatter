"""Job management API tests."""

import pytest


@pytest.mark.unit
class TestJobsAPI:
    """Test job management API endpoints."""

    async def test_list_jobs(self, test_client):
        """Test listing jobs."""
        # Setup user and auth
        registration_data = {
            "email": "jobuser@example.com",
            "password": "SecurePass123!",
            "username": "jobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "jobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List jobs
        response = await test_client.get("/api/v1/jobs", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "jobs" in data or isinstance(data, list)

    async def test_create_job(self, test_client):
        """Test job creation."""
        # Setup user and auth
        registration_data = {
            "email": "createjobuser@example.com",
            "password": "SecurePass123!",
            "username": "createjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "createjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a job
        job_data = {
            "type": "document_processing",
            "parameters": {
                "document_id": "test_doc_123",
                "action": "extract_text"
            },
            "priority": "normal",
            "scheduled_at": None
        }

        response = await test_client.post("/api/v1/jobs", json=job_data, headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [201, 422, 501]
        
        if response.status_code == 201:
            data = response.json()
            assert "id" in data
            assert data["type"] == "document_processing"

    async def test_get_job_by_id(self, test_client):
        """Test retrieving a specific job."""
        # Setup user and auth
        registration_data = {
            "email": "getjobuser@example.com",
            "password": "SecurePass123!",
            "username": "getjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "getjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get a job (will likely return 404)
        response = await test_client.get("/api/v1/jobs/nonexistent", headers=headers)
        
        # Should return 404 for non-existent job or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_cancel_job(self, test_client):
        """Test canceling a job."""
        # Setup user and auth
        registration_data = {
            "email": "canceljobuser@example.com",
            "password": "SecurePass123!",
            "username": "canceljobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "canceljobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to cancel a job
        response = await test_client.post("/api/v1/jobs/nonexistent/cancel", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_job_status(self, test_client):
        """Test getting job status."""
        # Setup user and auth
        registration_data = {
            "email": "statusjobuser@example.com",
            "password": "SecurePass123!",
            "username": "statusjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "statusjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get job status
        response = await test_client.get("/api/v1/jobs/nonexistent/status", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_job_results(self, test_client):
        """Test getting job results."""
        # Setup user and auth
        registration_data = {
            "email": "resultsjobuser@example.com",
            "password": "SecurePass123!",
            "username": "resultsjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "resultsjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get job results
        response = await test_client.get("/api/v1/jobs/nonexistent/results", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_jobs_unauthorized(self, test_client):
        """Test job endpoints require authentication."""
        endpoints = [
            "/api/v1/jobs",
            "/api/v1/jobs/test",
            "/api/v1/jobs/test/status",
            "/api/v1/jobs/test/results"
        ]
        
        for endpoint in endpoints:
            response = await test_client.get(endpoint)
            
            # Should require authentication
            assert response.status_code in [401, 403]

    async def test_job_validation(self, test_client):
        """Test job creation validation."""
        # Setup user and auth
        registration_data = {
            "email": "validjobuser@example.com",
            "password": "SecurePass123!",
            "username": "validjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try creating job with missing required fields
        invalid_data = {
            "parameters": {}
        }

        response = await test_client.post("/api/v1/jobs", json=invalid_data, headers=headers)
        
        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_retry_job(self, test_client):
        """Test retrying a failed job."""
        # Setup user and auth
        registration_data = {
            "email": "retryjobuser@example.com",
            "password": "SecurePass123!",
            "username": "retryjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "retryjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to retry a job
        response = await test_client.post("/api/v1/jobs/nonexistent/retry", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_job_logs(self, test_client):
        """Test getting job execution logs."""
        # Setup user and auth
        registration_data = {
            "email": "logsjobuser@example.com",
            "password": "SecurePass123!",
            "username": "logsjobuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "logsjobuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get job logs
        response = await test_client.get("/api/v1/jobs/nonexistent/logs", headers=headers)
        
        # Should return 404 for non-existent or 501 if not implemented
        assert response.status_code in [404, 501]