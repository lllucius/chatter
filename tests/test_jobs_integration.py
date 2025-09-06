"""Integration tests for jobs API endpoints."""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestJobsIntegration:
    """Integration tests for jobs API endpoints."""

    @pytest.mark.integration
    async def test_job_complete_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test complete job lifecycle from creation to completion."""
        # Create a job
        job_data = {
            "name": "Integration Test Job",
            "function_name": "test_function",
            "args": ["test_arg"],
            "kwargs": {"test_key": "test_value"},
            "priority": "normal",
        }

        create_response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        # Verify job was created
        get_response = await client.get(
            f"/api/v1/jobs/{job_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        job_data = get_response.json()
        assert job_data["name"] == "Integration Test Job"
        assert job_data["function_name"] == "test_function"
        assert job_data["status"] in ["pending", "running", "completed"]

        # Get job stats (should include our job)
        stats_response = await client.get(
            "/api/v1/jobs/stats/overview", headers=auth_headers
        )
        assert stats_response.status_code == 200

        stats = stats_response.json()
        assert stats["total_jobs"] >= 1
        assert isinstance(stats["pending_jobs"], int)
        assert isinstance(stats["running_jobs"], int)
        assert isinstance(stats["completed_jobs"], int)

    @pytest.mark.integration
    async def test_job_listing_and_filtering(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job listing and filtering functionality."""
        # Create multiple jobs with different statuses
        job_names = ["Job 1", "Job 2", "Job 3"]
        created_jobs = []

        for name in job_names:
            job_data = {
                "name": name,
                "function_name": "test_function",
                "args": [],
                "kwargs": {},
                "priority": "normal",
            }

            response = await client.post(
                "/api/v1/jobs/", json=job_data, headers=auth_headers
            )
            assert response.status_code == 201
            created_jobs.append(response.json()["id"])

        # List all jobs
        list_response = await client.get(
            "/api/v1/jobs/", headers=auth_headers
        )
        assert list_response.status_code == 200

        data = list_response.json()
        assert len(data["jobs"]) >= 3  # At least our 3 jobs
        assert data["total"] >= 3

        # Test pagination
        page_response = await client.get(
            "/api/v1/jobs/?page=1&per_page=2", headers=auth_headers
        )
        assert page_response.status_code == 200
        page_data = page_response.json()
        assert len(page_data["jobs"]) <= 2

        # Test status filtering (if any jobs have completed)
        status_response = await client.get(
            "/api/v1/jobs/?status=pending", headers=auth_headers
        )
        assert status_response.status_code == 200

        # All returned jobs should have pending status or be empty
        status_data = status_response.json()
        for job in status_data["jobs"]:
            assert job["status"] == "pending"

    @pytest.mark.integration
    async def test_job_cancellation_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job cancellation workflow."""
        # Create a job
        job_data = {
            "name": "Cancellation Test Job",
            "function_name": "slow_test_function",  # Hypothetical slow function
            "args": [],
            "kwargs": {},
            "priority": "low",
        }

        create_response = await client.post(
            "/api/v1/jobs/", json=job_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        # Try to cancel the job
        cancel_response = await client.post(
            f"/api/v1/jobs/{job_id}/cancel", headers=auth_headers
        )

        # Should succeed or fail gracefully depending on job state
        assert cancel_response.status_code in [200, 404, 400]

        if cancel_response.status_code == 200:
            cancel_data = cancel_response.json()
            assert cancel_data["success"] is True
            assert cancel_data["job_id"] == job_id
            assert cancel_data["action"] == "cancel"

    @pytest.mark.integration
    async def test_job_error_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job error handling scenarios."""
        # Test non-existent job operations
        nonexistent_id = "550e8400-e29b-41d4-a716-446655440000"

        # Get non-existent job
        get_response = await client.get(
            f"/api/v1/jobs/{nonexistent_id}", headers=auth_headers
        )
        assert get_response.status_code == 404

        # Cancel non-existent job
        cancel_response = await client.post(
            f"/api/v1/jobs/{nonexistent_id}/cancel",
            headers=auth_headers,
        )
        assert cancel_response.status_code == 404

        # Test invalid job ID formats
        invalid_ids = ["not-a-uuid", "12345", ""]

        for invalid_id in invalid_ids:
            if invalid_id:  # Skip empty string for URL path
                get_response = await client.get(
                    f"/api/v1/jobs/{invalid_id}", headers=auth_headers
                )
                assert get_response.status_code == 400

                cancel_response = await client.post(
                    f"/api/v1/jobs/{invalid_id}/cancel",
                    headers=auth_headers,
                )
                assert cancel_response.status_code == 400

    @pytest.mark.integration
    async def test_job_validation_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job creation validation scenarios."""
        # Test invalid function name
        invalid_function_data = {
            "name": "Invalid Function Job",
            "function_name": "nonexistent_function_12345",
            "args": [],
            "kwargs": {},
        }

        response = await client.post(
            "/api/v1/jobs/",
            json=invalid_function_data,
            headers=auth_headers,
        )
        assert (
            response.status_code == 400
        )  # Bad request for invalid function

        # Test missing required fields
        incomplete_data = {
            "name": "Incomplete Job"
            # Missing function_name
        }

        response = await client.post(
            "/api/v1/jobs/", json=incomplete_data, headers=auth_headers
        )
        assert response.status_code == 422  # Validation error

        # Test invalid priority
        invalid_priority_data = {
            "name": "Invalid Priority Job",
            "function_name": "test_function",
            "args": [],
            "kwargs": {},
            "priority": "invalid_priority",
        }

        response = await client.post(
            "/api/v1/jobs/",
            json=invalid_priority_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_job_stats_accuracy(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job statistics accuracy."""
        # Get initial stats
        initial_response = await client.get(
            "/api/v1/jobs/stats/overview", headers=auth_headers
        )
        assert initial_response.status_code == 200
        initial_stats = initial_response.json()

        # Create a few jobs
        job_count = 3
        created_jobs = []

        for i in range(job_count):
            job_data = {
                "name": f"Stats Test Job {i}",
                "function_name": "test_function",
                "args": [i],
                "kwargs": {"index": i},
            }

            response = await client.post(
                "/api/v1/jobs/", json=job_data, headers=auth_headers
            )
            assert response.status_code == 201
            created_jobs.append(response.json()["id"])

        # Get updated stats
        final_response = await client.get(
            "/api/v1/jobs/stats/overview", headers=auth_headers
        )
        assert final_response.status_code == 200
        final_stats = final_response.json()

        # Total jobs should have increased
        assert final_stats["total_jobs"] >= initial_stats["total_jobs"]

        # Stats should be consistent
        total_by_status = (
            final_stats["pending_jobs"]
            + final_stats["running_jobs"]
            + final_stats["completed_jobs"]
            + final_stats["failed_jobs"]
            + final_stats["cancelled_jobs"]
        )
        assert (
            total_by_status <= final_stats["total_jobs"]
        )  # May be equal or less due to cleanup

    @pytest.mark.integration
    async def test_job_cleanup_functionality(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job cleanup functionality."""
        # Get initial stats
        initial_response = await client.get(
            "/api/v1/jobs/stats/overview", headers=auth_headers
        )
        assert initial_response.status_code == 200
        initial_response.json()

        # Create some jobs that might complete
        for i in range(2):
            job_data = {
                "name": f"Cleanup Test Job {i}",
                "function_name": "test_function",
                "args": [],
                "kwargs": {},
            }

            response = await client.post(
                "/api/v1/jobs/", json=job_data, headers=auth_headers
            )
            assert response.status_code == 201

        # Wait a moment for potential job processing
        await asyncio.sleep(0.1)

        # Run cleanup
        cleanup_response = await client.post(
            "/api/v1/jobs/cleanup", headers=auth_headers
        )
        assert cleanup_response.status_code == 200

        cleanup_data = cleanup_response.json()
        assert "cleaned_count" in cleanup_data
        assert "remaining_count" in cleanup_data
        assert isinstance(cleanup_data["cleaned_count"], int)
        assert isinstance(cleanup_data["remaining_count"], int)

    @pytest.mark.integration
    async def test_concurrent_job_operations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test concurrent job operations."""
        # Create multiple jobs concurrently
        job_data_list = [
            {
                "name": f"Concurrent Job {i}",
                "function_name": "test_function",
                "args": [i],
                "kwargs": {"concurrent": True},
            }
            for i in range(5)
        ]

        # Create tasks for concurrent job creation
        create_tasks = [
            asyncio.create_task(
                client.post(
                    "/api/v1/jobs/", json=job_data, headers=auth_headers
                )
            )
            for job_data in job_data_list
        ]

        # Wait for all creations
        create_responses = await asyncio.gather(*create_tasks)

        # All should succeed
        created_job_ids = []
        for response in create_responses:
            assert response.status_code == 201
            created_job_ids.append(response.json()["id"])

        # Perform concurrent operations on jobs
        operation_tasks = []

        # Get each job concurrently
        for job_id in created_job_ids:
            operation_tasks.append(
                asyncio.create_task(
                    client.get(
                        f"/api/v1/jobs/{job_id}", headers=auth_headers
                    )
                )
            )

        # Also get stats and list jobs concurrently
        operation_tasks.extend(
            [
                asyncio.create_task(
                    client.get(
                        "/api/v1/jobs/stats/overview",
                        headers=auth_headers,
                    )
                ),
                asyncio.create_task(
                    client.get("/api/v1/jobs/", headers=auth_headers)
                ),
            ]
        )

        # Wait for all operations
        operation_responses = await asyncio.gather(*operation_tasks)

        # All should succeed
        for response in operation_responses:
            assert response.status_code == 200

    @pytest.mark.integration
    async def test_job_data_persistence(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test job data persistence and retrieval accuracy."""
        # Create job with complex data
        complex_job_data = {
            "name": "Complex Data Job",
            "function_name": "test_function",
            "args": [
                "string_arg",
                42,
                3.14,
                True,
                ["nested", "array"],
                {"nested": "object", "number": 123},
            ],
            "kwargs": {
                "string_param": "test_string",
                "number_param": 456,
                "float_param": 78.9,
                "boolean_param": False,
                "array_param": [1, 2, 3],
                "object_param": {
                    "nested_string": "nested_value",
                    "nested_number": 789,
                },
            },
            "priority": "high",
        }

        # Create job
        create_response = await client.post(
            "/api/v1/jobs/", json=complex_job_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        job_id = create_response.json()["id"]

        # Retrieve job and verify data integrity
        get_response = await client.get(
            f"/api/v1/jobs/{job_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        retrieved_job = get_response.json()
        assert retrieved_job["name"] == "Complex Data Job"
        assert retrieved_job["function_name"] == "test_function"
        assert retrieved_job["args"] == complex_job_data["args"]
        assert retrieved_job["kwargs"] == complex_job_data["kwargs"]
        assert retrieved_job["priority"] == "high"

        # Verify timestamp fields are present and valid
        assert "created_at" in retrieved_job
        assert "updated_at" in retrieved_job
        assert retrieved_job["created_at"] is not None
        assert retrieved_job["updated_at"] is not None
