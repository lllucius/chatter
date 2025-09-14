"""Integration tests for AB testing API endpoints."""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestABTestingIntegration:
    """Integration tests for AB testing API endpoints."""

    @pytest.mark.integration
    async def test_ab_test_complete_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test complete AB test lifecycle from creation to completion."""
        # Create test
        test_data = {
            "name": "Integration Test AB Test",
            "description": "Complete lifecycle test",
            "test_type": "prompt",
            "allocation_strategy": "equal",
            "variants": [
                {
                    "name": "control",
                    "description": "Control variant",
                    "configuration": {"param_a": "value1"},
                    "weight": 1.0,
                },
                {
                    "name": "variant_a",
                    "description": "Test variant A",
                    "configuration": {"param_a": "value2"},
                    "weight": 1.0,
                },
            ],
            "metrics": ["response_time", "user_satisfaction"],
            "duration_days": 7,
            "min_sample_size": 100,
            "confidence_level": 0.95,
            "traffic_percentage": 100.0,
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        test_id = create_response.json()["id"]

        # Verify test was created
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "draft"

        # Start test
        start_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200
        assert start_response.json()["success"] is True

        # Verify test is running
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "running"

        # Pause test
        pause_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/pause", headers=auth_headers
        )
        assert pause_response.status_code == 200

        # Complete test
        complete_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        assert complete_response.status_code == 200

        # Get final results
        results_response = await client.get(
            f"/api/v1/ab-tests/{test_id}/results", headers=auth_headers
        )
        assert results_response.status_code == 200

        # Delete test
        delete_response = await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

    @pytest.mark.integration
    async def test_ab_test_list_and_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test listing and filtering functionality."""
        # Create multiple tests
        test_names = ["Test 1", "Test 2", "Test 3"]
        created_tests = []

        for name in test_names:
            test_data = {
                "name": name,
                "description": f"Description for {name}",
                "variants": [
                    {"name": "control", "allocation": 50},
                    {"name": "variant", "allocation": 50},
                ],
            }

            response = await client.post(
                "/api/v1/ab-tests/",
                json=test_data,
                headers=auth_headers,
            )
            assert response.status_code == 201
            created_tests.append(response.json()["id"])

        # List all tests
        list_response = await client.get(
            "/api/v1/ab-tests/", headers=auth_headers
        )
        assert list_response.status_code == 200

        data = list_response.json()
        assert len(data["tests"]) >= 3  # At least our 3 tests
        assert data["total"] >= 3

        # Test pagination
        page_response = await client.get(
            "/api/v1/ab-tests/?page=1&per_page=2", headers=auth_headers
        )
        assert page_response.status_code == 200
        page_data = page_response.json()
        assert len(page_data["tests"]) <= 2

        # Clean up - delete created tests
        for test_id in created_tests:
            await client.delete(
                f"/api/v1/ab-tests/{test_id}", headers=auth_headers
            )

    @pytest.mark.integration
    async def test_ab_test_update_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test update functionality."""
        # Create test
        original_data = {
            "name": "Original Test Name",
            "description": "Original description",
            "variants": [
                {"name": "control", "allocation": 50},
                {"name": "variant_a", "allocation": 50},
            ],
        }

        create_response = await client.post(
            "/api/v1/ab-tests/",
            json=original_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Update test
        update_data = {
            "name": "Updated Test Name",
            "description": "Updated description",
            "variants": [
                {"name": "control", "allocation": 30},
                {"name": "variant_a", "allocation": 35},
                {"name": "variant_b", "allocation": 35},
            ],
        }

        update_response = await client.put(
            f"/api/v1/ab-tests/{test_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify updates
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        updated_test = get_response.json()
        assert updated_test["name"] == "Updated Test Name"
        assert updated_test["description"] == "Updated description"
        assert len(updated_test["variants"]) == 3

        # Clean up
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )

    @pytest.mark.integration
    async def test_ab_test_metrics_and_performance(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test metrics and performance tracking."""
        # Create and start test
        test_data = {
            "name": "Metrics Test",
            "description": "Test for metrics tracking",
            "variants": [
                {"name": "control", "allocation": 50},
                {"name": "variant_a", "allocation": 50},
            ],
            "target_metric": "click_through_rate",
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Start test
        await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )

        # Get metrics
        metrics_response = await client.get(
            f"/api/v1/ab-tests/{test_id}/metrics", headers=auth_headers
        )
        assert metrics_response.status_code == 200

        metrics_data = metrics_response.json()
        assert "test_id" in metrics_data
        assert "participants" in metrics_data

        # Get performance data
        performance_response = await client.get(
            f"/api/v1/ab-tests/{test_id}/performance",
            headers=auth_headers,
        )
        assert performance_response.status_code == 200

        performance_data = performance_response.json()
        assert isinstance(performance_data, dict)

        # Get recommendations
        recommendations_response = await client.get(
            f"/api/v1/ab-tests/{test_id}/recommendations",
            headers=auth_headers,
        )
        assert recommendations_response.status_code == 200

        recommendations_data = recommendations_response.json()
        assert isinstance(recommendations_data, dict)

        # Clean up
        await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )

    @pytest.mark.integration
    async def test_ab_test_error_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test error handling scenarios."""
        # Test non-existent test operations
        nonexistent_id = "nonexistent-test-id"

        operations = [
            ("GET", f"/api/v1/ab-tests/{nonexistent_id}"),
            ("PUT", f"/api/v1/ab-tests/{nonexistent_id}"),
            ("DELETE", f"/api/v1/ab-tests/{nonexistent_id}"),
            ("POST", f"/api/v1/ab-tests/{nonexistent_id}/start"),
            ("POST", f"/api/v1/ab-tests/{nonexistent_id}/pause"),
            ("POST", f"/api/v1/ab-tests/{nonexistent_id}/complete"),
            ("GET", f"/api/v1/ab-tests/{nonexistent_id}/results"),
            ("GET", f"/api/v1/ab-tests/{nonexistent_id}/metrics"),
        ]

        for method, url in operations:
            if method == "GET":
                response = await client.get(url, headers=auth_headers)
            elif method == "POST":
                response = await client.post(url, headers=auth_headers)
            elif method == "PUT":
                response = await client.put(
                    url, json={}, headers=auth_headers
                )
            elif method == "DELETE":
                response = await client.delete(
                    url, headers=auth_headers
                )

            assert (
                response.status_code == 404
            ), f"Failed for {method} {url}"

    @pytest.mark.integration
    async def test_ab_test_state_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test state transition validation."""
        # Create test
        test_data = {
            "name": "State Validation Test",
            "description": "Test state transitions",
            "variants": [
                {"name": "control", "allocation": 50},
                {"name": "variant_a", "allocation": 50},
            ],
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Try to pause draft test (should fail)
        pause_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/pause", headers=auth_headers
        )
        assert pause_response.status_code == 400

        # Try to complete draft test (should fail)
        complete_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        assert complete_response.status_code == 400

        # Start test (should succeed)
        start_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200

        # Try to start running test (should fail)
        start_again_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_again_response.status_code == 400

        # Try to delete running test (should fail)
        delete_running_response = await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert delete_running_response.status_code == 400

        # Pause the running test (should succeed)
        pause_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/pause", headers=auth_headers
        )
        assert pause_response.status_code == 200

        # Try to start paused test (should succeed - this is the fix being tested)
        restart_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert restart_response.status_code == 200

        # Complete test and then delete
        await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        delete_response = await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

    @pytest.mark.integration
    async def test_ab_test_concurrent_operations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test concurrent AB test operations."""
        # Create multiple tests concurrently
        test_data_list = [
            {
                "name": f"Concurrent Test {i}",
                "description": f"Concurrent test {i}",
                "variants": [
                    {"name": "control", "allocation": 50},
                    {"name": "variant", "allocation": 50},
                ],
            }
            for i in range(5)
        ]

        # Create tasks for concurrent test creation
        create_tasks = [
            asyncio.create_task(
                client.post(
                    "/api/v1/ab-tests/",
                    json=test_data,
                    headers=auth_headers,
                )
            )
            for test_data in test_data_list
        ]

        # Wait for all creations
        create_responses = await asyncio.gather(*create_tasks)

        # All should succeed
        created_test_ids = []
        for response in create_responses:
            assert response.status_code == 201
            created_test_ids.append(response.json()["id"])

        # Perform concurrent operations on all tests
        operation_tasks = []
        for test_id in created_test_ids:
            # Start each test
            operation_tasks.append(
                asyncio.create_task(
                    client.post(
                        f"/api/v1/ab-tests/{test_id}/start",
                        headers=auth_headers,
                    )
                )
            )

        # Wait for all operations
        operation_responses = await asyncio.gather(*operation_tasks)

        # All should succeed
        for response in operation_responses:
            assert response.status_code == 200

        # Clean up - complete and delete all tests
        cleanup_tasks = []
        for test_id in created_test_ids:
            cleanup_tasks.extend(
                [
                    asyncio.create_task(
                        client.post(
                            f"/api/v1/ab-tests/{test_id}/complete",
                            headers=auth_headers,
                        )
                    ),
                    asyncio.create_task(
                        client.delete(
                            f"/api/v1/ab-tests/{test_id}",
                            headers=auth_headers,
                        )
                    ),
                ]
            )

        await asyncio.gather(*cleanup_tasks)

    @pytest.mark.integration
    async def test_ab_test_data_persistence(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test AB test data persistence across operations."""
        # Create test with specific data
        original_test_data = {
            "name": "Persistence Test",
            "description": "Testing data persistence",
            "variants": [
                {"name": "control", "allocation": 40},
                {"name": "variant_a", "allocation": 30},
                {"name": "variant_b", "allocation": 30},
            ],
            "target_metric": "conversion_rate",
            "success_criteria": {
                "min_improvement": 15.0,
                "confidence_level": 95.0,
            },
            "metadata": {
                "experiment_type": "feature_flag",
                "team": "product",
                "priority": "high",
            },
        }

        # Create test
        create_response = await client.post(
            "/api/v1/ab-tests/",
            json=original_test_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Verify all data was persisted correctly
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        retrieved_test = get_response.json()
        assert retrieved_test["name"] == "Persistence Test"
        assert (
            retrieved_test["description"] == "Testing data persistence"
        )
        assert len(retrieved_test["variants"]) == 3
        assert retrieved_test["target_metric"] == "conversion_rate"

        # Start test and verify state persistence
        await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )

        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.json()["status"] == "running"

        # Update test and verify changes persist
        update_data = {
            "description": "Updated description for persistence test"
        }

        update_response = await client.put(
            f"/api/v1/ab-tests/{test_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify update persisted
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert (
            get_response.json()["description"]
            == "Updated description for persistence test"
        )

        # Clean up
        await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )

    @pytest.mark.integration
    async def test_ab_test_end_endpoint(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test the end AB test endpoint with winner selection."""
        # Create test
        test_data = {
            "name": "End Test AB Test",
            "description": "Testing end endpoint functionality",
            "test_type": "prompt",
            "allocation_strategy": "equal",
            "variants": [
                {
                    "name": "control",
                    "description": "Control variant",
                    "configuration": {"param_a": "value1"},
                    "weight": 1.0,
                },
                {
                    "name": "variant_a",
                    "description": "Test variant A",
                    "configuration": {"param_a": "value2"},
                    "weight": 1.0,
                },
            ],
            "metrics": ["response_time", "user_satisfaction"],
            "duration_days": 7,
            "min_sample_size": 100,
            "confidence_level": 0.95,
            "traffic_percentage": 100.0,
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Start the test first
        start_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200

        # Test ending with winner variant (query parameter)
        end_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/end?winner_variant=variant_a", 
            headers=auth_headers
        )
        assert end_response.status_code == 200
        
        end_data = end_response.json()
        assert end_data["success"] is True
        assert end_data["test_id"] == test_id
        assert end_data["new_status"] == "completed"
        assert "variant_a" in end_data["message"]

        # Verify test status is completed
        get_response = await client.get(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
        assert get_response.status_code == 200
        assert get_response.json()["status"] == "completed"

        # Clean up
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )

    @pytest.mark.integration
    async def test_ab_test_end_endpoint_without_winner(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test the end AB test endpoint without specifying a winner."""
        # Create test
        test_data = {
            "name": "End Test No Winner",
            "description": "Testing end endpoint without winner",
            "test_type": "prompt",
            "allocation_strategy": "equal",
            "variants": [
                {
                    "name": "control",
                    "description": "Control variant",
                    "configuration": {"param_a": "value1"},
                    "weight": 1.0,
                },
                {
                    "name": "variant_a",
                    "description": "Test variant A",
                    "configuration": {"param_a": "value2"},
                    "weight": 1.0,
                },
            ],
            "metrics": ["response_time"],
            "duration_days": 7,
            "min_sample_size": 50,
            "confidence_level": 0.95,
            "traffic_percentage": 100.0,
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Start the test first
        start_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200

        # Test ending without winner variant
        end_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/end", 
            headers=auth_headers
        )
        assert end_response.status_code == 200
        
        end_data = end_response.json()
        assert end_data["success"] is True
        assert end_data["test_id"] == test_id
        assert end_data["new_status"] == "completed"
        assert "ended successfully" in end_data["message"]

        # Clean up
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )

    @pytest.mark.integration
    async def test_ab_test_end_endpoint_invalid_winner(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test the end AB test endpoint with invalid winner variant."""
        # Create test
        test_data = {
            "name": "End Test Invalid Winner",
            "description": "Testing end endpoint with invalid winner",
            "test_type": "prompt",
            "allocation_strategy": "equal",
            "variants": [
                {
                    "name": "control",
                    "description": "Control variant",
                    "configuration": {"param_a": "value1"},
                    "weight": 1.0,
                },
                {
                    "name": "variant_a",
                    "description": "Test variant A",
                    "configuration": {"param_a": "value2"},
                    "weight": 1.0,
                },
            ],
            "metrics": ["response_time"],
            "duration_days": 7,
            "min_sample_size": 50,
            "confidence_level": 0.95,
            "traffic_percentage": 100.0,
        }

        create_response = await client.post(
            "/api/v1/ab-tests/", json=test_data, headers=auth_headers
        )
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # Start the test first
        start_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200

        # Test ending with invalid winner variant
        end_response = await client.post(
            f"/api/v1/ab-tests/{test_id}/end?winner_variant=nonexistent_variant", 
            headers=auth_headers
        )
        assert end_response.status_code == 400  # Should return Bad Request

        # Clean up
        await client.post(
            f"/api/v1/ab-tests/{test_id}/complete", headers=auth_headers
        )
        await client.delete(
            f"/api/v1/ab-tests/{test_id}", headers=auth_headers
        )
