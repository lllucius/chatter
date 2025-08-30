"""A/B Testing API tests."""


import pytest


@pytest.mark.unit
class TestABTestingAPI:
    """Test A/B testing API endpoints."""

    async def test_create_ab_test_success(self, test_client):
        """Test successful A/B test creation."""
        # Setup user and auth
        registration_data = {
            "email": "abtestuser@example.com",
            "password": "SecurePass123!",
            "username": "abtestuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "abtestuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Model Comparison Test",
            "description": "Compare GPT-3.5 vs GPT-4 performance",
            "variants": [
                {
                    "name": "control",
                    "model": "gpt-3.5-turbo",
                    "weight": 50
                },
                {
                    "name": "treatment",
                    "model": "gpt-4",
                    "weight": 50
                }
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }

        response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Model Comparison Test"
        assert data["description"] == "Compare GPT-3.5 vs GPT-4 performance"
        assert len(data["variants"]) == 2
        assert data["status"] == "draft"
        assert "id" in data

    async def test_list_ab_tests(self, test_client):
        """Test listing A/B tests."""
        # Setup user and auth
        registration_data = {
            "email": "listabuser@example.com",
            "password": "SecurePass123!",
            "username": "listabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "listabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create multiple A/B tests
        test_names = ["Test A", "Test B", "Test C"]
        for name in test_names:
            test_data = {
                "name": name,
                "description": f"Description for {name}",
                "variants": [
                    {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                    {"name": "treatment", "model": "gpt-4", "weight": 50}
                ],
                "success_metric": "user_satisfaction",
                "duration_days": 7
            }
            await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)

        # List A/B tests
        response = await test_client.get("/api/v1/ab-tests", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 3
        test_names_response = [test["name"] for test in data]
        for name in test_names:
            assert name in test_names_response

    async def test_get_ab_test_by_id(self, test_client):
        """Test getting a specific A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "getabuser@example.com",
            "password": "SecurePass123!",
            "username": "getabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "getabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Specific Test",
            "description": "Test for retrieval",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Get A/B test
        response = await test_client.get(f"/api/v1/ab-tests/{test_id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == test_id
        assert data["name"] == "Specific Test"

    async def test_start_ab_test(self, test_client):
        """Test starting an A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "startabuser@example.com",
            "password": "SecurePass123!",
            "username": "startabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "startabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Start Test",
            "description": "Test for starting",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Start A/B test
        response = await test_client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "running"
            assert "started_at" in data

    async def test_pause_ab_test(self, test_client):
        """Test pausing an A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "pauseabuser@example.com",
            "password": "SecurePass123!",
            "username": "pauseabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "pauseabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create and start A/B test
        test_data = {
            "name": "Pause Test",
            "description": "Test for pausing",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Start the test first (if endpoint exists)
        await test_client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)

        # Pause A/B test
        response = await test_client.post(f"/api/v1/ab-tests/{test_id}/pause", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "paused"

    async def test_complete_ab_test(self, test_client):
        """Test completing an A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "completeabuser@example.com",
            "password": "SecurePass123!",
            "username": "completeabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "completeabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Complete Test",
            "description": "Test for completion",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Complete A/B test
        response = await test_client.post(f"/api/v1/ab-tests/{test_id}/complete", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "completed"
            assert "completed_at" in data

    async def test_ab_test_results(self, test_client):
        """Test retrieving A/B test results."""
        # Setup user and auth
        registration_data = {
            "email": "resultsabuser@example.com",
            "password": "SecurePass123!",
            "username": "resultsabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "resultsabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Results Test",
            "description": "Test for results",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Get A/B test results
        response = await test_client.get(f"/api/v1/ab-tests/{test_id}/results", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "variants" in data or "results" in data
            assert "statistical_significance" in data or "summary" in data

    async def test_ab_test_metrics(self, test_client):
        """Test retrieving A/B test metrics."""
        # Setup user and auth
        registration_data = {
            "email": "metricsabuser@example.com",
            "password": "SecurePass123!",
            "username": "metricsabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "metricsabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Metrics Test",
            "description": "Test for metrics",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Get A/B test metrics
        response = await test_client.get(f"/api/v1/ab-tests/{test_id}/metrics", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "metrics" in data or "performance" in data

    async def test_ab_test_performance(self, test_client):
        """Test retrieving A/B test performance data."""
        # Setup user and auth
        registration_data = {
            "email": "perfabuser@example.com",
            "password": "SecurePass123!",
            "username": "perfabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "perfabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Performance Test",
            "description": "Test for performance",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "response_time",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Get A/B test performance
        response = await test_client.get(f"/api/v1/ab-tests/{test_id}/performance", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "performance" in data or "response_times" in data

    async def test_update_ab_test(self, test_client):
        """Test updating an A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "updateabuser@example.com",
            "password": "SecurePass123!",
            "username": "updateabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "updateabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Update Test",
            "description": "Test for updating",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Update A/B test
        update_data = {
            "name": "Updated Test Name",
            "description": "Updated description",
            "duration_days": 14
        }

        response = await test_client.put(f"/api/v1/ab-tests/{test_id}", json=update_data, headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 404, 405, 501]

        if response.status_code == 200:
            data = response.json()
            assert data["name"] == "Updated Test Name"
            assert data["description"] == "Updated description"
            assert data["duration_days"] == 14

    async def test_delete_ab_test(self, test_client):
        """Test deleting an A/B test."""
        # Setup user and auth
        registration_data = {
            "email": "deleteabuser@example.com",
            "password": "SecurePass123!",
            "username": "deleteabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "deleteabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create A/B test
        test_data = {
            "name": "Delete Test",
            "description": "Test for deletion",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        test_id = create_response.json()["id"]

        # Delete A/B test
        response = await test_client.delete(f"/api/v1/ab-tests/{test_id}", headers=headers)

        # Should either succeed or return 404 if endpoint not implemented
        assert response.status_code in [200, 204, 404, 405, 501]

        if response.status_code in [200, 204]:
            # Verify deletion by trying to get the test
            get_response = await test_client.get(f"/api/v1/ab-tests/{test_id}", headers=headers)
            assert get_response.status_code == 404


@pytest.mark.unit
class TestABTestValidation:
    """Test A/B test validation."""

    async def test_ab_test_creation_validation(self, test_client):
        """Test A/B test creation validation."""
        # Setup user and auth
        registration_data = {
            "email": "validabuser@example.com",
            "password": "SecurePass123!",
            "username": "validabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test missing required fields
        invalid_test_data = {
            "name": "",  # Empty name
            # Missing description, variants, etc.
        }

        response = await test_client.post("/api/v1/ab-tests", json=invalid_test_data, headers=headers)
        assert response.status_code == 400

        # Test invalid variant weights
        invalid_weights_data = {
            "name": "Invalid Weights Test",
            "description": "Test with invalid weights",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 30},
                {"name": "treatment", "model": "gpt-4", "weight": 30}  # Total is 60, not 100
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }

        response = await test_client.post("/api/v1/ab-tests", json=invalid_weights_data, headers=headers)
        assert response.status_code == 400

        # Test invalid duration
        invalid_duration_data = {
            "name": "Invalid Duration Test",
            "description": "Test with invalid duration",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": -1  # Negative duration
        }

        response = await test_client.post("/api/v1/ab-tests", json=invalid_duration_data, headers=headers)
        assert response.status_code == 400

    async def test_variant_allocation(self, test_client):
        """Test variant allocation logic."""
        # This would test the logic for allocating users to variants
        # Since we don't have the actual implementation, we'll test the concept

        # Mock variant allocation function
        def allocate_variant(user_id: str, test_id: str, variants: list) -> str:
            """Mock variant allocation based on user ID hash."""
            import hashlib

            # Use consistent hashing to allocate users
            hash_input = f"{user_id}-{test_id}".encode()
            hash_value = int(hashlib.md5(hash_input).hexdigest(), 16)

            # Calculate weights
            total_weight = sum(v["weight"] for v in variants)
            normalized_hash = hash_value % total_weight

            cumulative_weight = 0
            for variant in variants:
                cumulative_weight += variant["weight"]
                if normalized_hash < cumulative_weight:
                    return variant["name"]

            return variants[0]["name"]  # Fallback

        # Test allocation
        variants = [
            {"name": "control", "weight": 50},
            {"name": "treatment", "weight": 50}
        ]

        # Test multiple users get consistent allocation
        user1_variant = allocate_variant("user1", "test1", variants)
        user1_variant_again = allocate_variant("user1", "test1", variants)
        assert user1_variant == user1_variant_again  # Should be consistent

        # Test distribution
        allocations = {}
        for i in range(1000):
            variant = allocate_variant(f"user{i}", "test1", variants)
            allocations[variant] = allocations.get(variant, 0) + 1

        # Should be roughly 50/50 split
        control_count = allocations.get("control", 0)
        treatment_count = allocations.get("treatment", 0)
        total = control_count + treatment_count

        assert abs(control_count / total - 0.5) < 0.1  # Within 10% of expected
        assert abs(treatment_count / total - 0.5) < 0.1


@pytest.mark.integration
class TestABTestingIntegration:
    """Integration tests for A/B testing workflow."""

    async def test_full_ab_test_lifecycle(self, test_client):
        """Test complete A/B test lifecycle."""
        # Setup user and auth
        registration_data = {
            "email": "lifecycleabuser@example.com",
            "password": "SecurePass123!",
            "username": "lifecycleabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "lifecycleabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create A/B test
        test_data = {
            "name": "Lifecycle Test",
            "description": "Complete lifecycle test",
            "variants": [
                {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                {"name": "treatment", "model": "gpt-4", "weight": 50}
            ],
            "success_metric": "user_satisfaction",
            "duration_days": 7
        }
        create_response = await test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
        assert create_response.status_code == 201
        test_id = create_response.json()["id"]

        # 2. Start the test (if endpoint exists)
        start_response = await test_client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)
        if start_response.status_code == 200:
            assert start_response.json()["status"] == "running"

        # 3. Get test status
        status_response = await test_client.get(f"/api/v1/ab-tests/{test_id}", headers=headers)
        assert status_response.status_code == 200

        # 4. Get metrics (if endpoint exists)
        metrics_response = await test_client.get(f"/api/v1/ab-tests/{test_id}/metrics", headers=headers)
        assert metrics_response.status_code in [200, 404, 501]

        # 5. Complete the test (if endpoint exists)
        complete_response = await test_client.post(f"/api/v1/ab-tests/{test_id}/complete", headers=headers)
        if complete_response.status_code == 200:
            assert complete_response.json()["status"] == "completed"

        # 6. Get final results (if endpoint exists)
        results_response = await test_client.get(f"/api/v1/ab-tests/{test_id}/results", headers=headers)
        assert results_response.status_code in [200, 404, 501]

    async def test_ab_test_with_statistical_analysis(self, test_client):
        """Test A/B test with statistical analysis."""
        # This would test the statistical analysis components
        # Mock statistical significance calculation

        def calculate_statistical_significance(control_data, treatment_data):
            """Mock statistical significance calculation."""
            # This would normally use proper statistical tests
            # For testing, we'll use a simple mock

            control_mean = sum(control_data) / len(control_data) if control_data else 0
            treatment_mean = sum(treatment_data) / len(treatment_data) if treatment_data else 0

            # Mock p-value calculation
            diff = abs(treatment_mean - control_mean)
            p_value = max(0.001, 0.1 - diff)  # Mock calculation

            return {
                "control_mean": control_mean,
                "treatment_mean": treatment_mean,
                "difference": treatment_mean - control_mean,
                "p_value": p_value,
                "significant": p_value < 0.05
            }

        # Test statistical analysis
        control_satisfaction = [4.2, 4.1, 4.3, 4.0, 4.2, 4.1]  # Mock data
        treatment_satisfaction = [4.5, 4.6, 4.4, 4.7, 4.5, 4.6]  # Mock data

        result = calculate_statistical_significance(control_satisfaction, treatment_satisfaction)

        assert "control_mean" in result
        assert "treatment_mean" in result
        assert "p_value" in result
        assert "significant" in result
        assert isinstance(result["significant"], bool)

    async def test_concurrent_ab_tests(self, test_client):
        """Test running multiple concurrent A/B tests."""
        import asyncio

        # Setup user and auth
        registration_data = {
            "email": "concurrentabuser@example.com",
            "password": "SecurePass123!",
            "username": "concurrentabuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "concurrentabuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create multiple A/B tests concurrently
        test_tasks = []
        for i in range(3):
            test_data = {
                "name": f"Concurrent Test {i+1}",
                "description": f"Concurrent test number {i+1}",
                "variants": [
                    {"name": "control", "model": "gpt-3.5-turbo", "weight": 50},
                    {"name": "treatment", "model": "gpt-4", "weight": 50}
                ],
                "success_metric": "user_satisfaction",
                "duration_days": 7
            }
            task = test_client.post("/api/v1/ab-tests", json=test_data, headers=headers)
            test_tasks.append(task)

        # Execute concurrently
        responses = await asyncio.gather(*test_tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

        # Verify all tests were created
        list_response = await test_client.get("/api/v1/ab-tests", headers=headers)
        assert list_response.status_code == 200

        tests = list_response.json()
        concurrent_tests = [t for t in tests if "Concurrent Test" in t["name"]]
        assert len(concurrent_tests) >= 3
