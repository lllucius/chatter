"""Tests for A/B testing API endpoints."""

from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.api.auth import get_current_user
from chatter.main import app
from chatter.models.user import User


@pytest.mark.unit
class TestABTestingEndpoints:
    """Test A/B testing API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="test-user-id",
            email="test@example.com",
            username="testuser",
            is_active=True
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_create_ab_test_success(self):
        """Test successful A/B test creation."""
        # Arrange
        test_data = {
            "name": "Chat Model Comparison",
            "description": "Compare GPT-4 vs Claude performance",
            "test_type": "model",
            "allocation_strategy": "equal",
            "variants": [
                {
                    "name": "GPT-4", 
                    "description": "GPT-4 model variant",
                    "configuration": {"model": "gpt-4"},
                    "weight": 1.0
                },
                {
                    "name": "Claude", 
                    "description": "Claude model variant",
                    "configuration": {"model": "claude-3"},
                    "weight": 1.0
                }
            ],
            "metrics": ["response_time", "user_satisfaction"],
            "duration_days": 7,
            "min_sample_size": 100,
            "confidence_level": 0.95,
            "traffic_percentage": 100.0
        }

        mock_test = {
            "id": "test-123",
            "name": test_data["name"],
            "status": "draft",
            "created_by": self.mock_user.id
        }

        with patch('chatter.services.ab_testing.ABTestManager.create_test') as mock_create:
            mock_create.return_value = mock_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                "/api/v1/ab-tests/",
                json=test_data,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_201_CREATED
            response_data = response.json()
            assert response_data["name"] == test_data["name"]
            assert response_data["status"] == "draft"

    def test_create_ab_test_invalid_traffic_split(self):
        """Test A/B test creation with invalid traffic split."""
        # Arrange
        test_data = {
            "name": "Invalid Test",
            "variants": [
                {"name": "Variant A", "config": {}},
                {"name": "Variant B", "config": {}}
            ],
            "traffic_split": {"Variant A": 0.7, "Variant B": 0.4}  # Sums to 1.1
        }

        # Act
        headers = {"Authorization": "Bearer test-token"}
        response = self.client.post(
            "/api/v1/ab-tests/",
            json=test_data,
            headers=headers
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_ab_tests_success(self):
        """Test retrieving A/B tests."""
        # Arrange
        mock_tests = [
            {"id": "test-1", "name": "Test 1", "status": "active"},
            {"id": "test-2", "name": "Test 2", "status": "completed"}
        ]

        with patch('chatter.services.ab_testing.ABTestManager.get_user_tests') as mock_get:
            mock_get.return_value = mock_tests

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get("/api/v1/ab-tests/", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert len(response_data["tests"]) == 2

    def test_get_ab_test_by_id_success(self):
        """Test retrieving specific A/B test."""
        # Arrange
        test_id = "test-123"
        mock_test = {
            "id": test_id,
            "name": "Model Comparison Test",
            "status": "active",
            "variants": [
                {"name": "GPT-4", "config": {"model": "gpt-4"}},
                {"name": "Claude", "config": {"model": "claude-3"}}
            ]
        }

        with patch('chatter.services.ab_testing.ABTestManager.get_test') as mock_get:
            mock_get.return_value = mock_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/ab-tests/{test_id}", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["id"] == test_id

    def test_start_ab_test_success(self):
        """Test starting an A/B test."""
        # Arrange
        test_id = "test-123"
        mock_test = {
            "id": test_id,
            "status": "active",
            "start_date": datetime.utcnow().isoformat()
        }

        with patch('chatter.services.ab_testing.ABTestManager.start_test') as mock_start:
            mock_start.return_value = mock_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "active"

    def test_pause_ab_test_success(self):
        """Test pausing an A/B test."""
        # Arrange
        test_id = "test-123"
        mock_test = {
            "id": test_id,
            "status": "paused"
        }

        with patch('chatter.services.ab_testing.ABTestManager.pause_test') as mock_pause:
            mock_pause.return_value = mock_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(f"/api/v1/ab-tests/{test_id}/pause", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "paused"

    def test_end_ab_test_success(self):
        """Test ending an A/B test."""
        # Arrange
        test_id = "test-123"
        mock_test = {
            "id": test_id,
            "status": "completed",
            "end_date": datetime.utcnow().isoformat()
        }

        with patch('chatter.services.ab_testing.ABTestManager.end_test') as mock_end:
            mock_end.return_value = mock_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(f"/api/v1/ab-tests/{test_id}/end", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["status"] == "completed"

    def test_get_ab_test_results_success(self):
        """Test retrieving A/B test results."""
        # Arrange
        test_id = "test-123"
        mock_results = {
            "test_id": test_id,
            "variants": {
                "GPT-4": {
                    "participants": 500,
                    "conversion_rate": 0.85,
                    "metrics": {"response_time": 1.2, "satisfaction": 4.2}
                },
                "Claude": {
                    "participants": 500,
                    "conversion_rate": 0.82,
                    "metrics": {"response_time": 0.9, "satisfaction": 4.1}
                }
            },
            "statistical_significance": True,
            "winner": "GPT-4"
        }

        with patch('chatter.services.ab_testing.ABTestManager.get_test_results') as mock_results_func:
            mock_results_func.return_value = mock_results

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/ab-tests/{test_id}/results", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["winner"] == "GPT-4"
            assert response_data["statistical_significance"] is True

    def test_get_ab_test_metrics_success(self):
        """Test retrieving A/B test metrics."""
        # Arrange
        test_id = "test-123"
        mock_metrics = {
            "test_id": test_id,
            "total_participants": 1000,
            "active_participants": 150,
            "conversion_rate": 0.835,
            "confidence_level": 0.95,
            "daily_metrics": [
                {"date": "2024-01-01", "participants": 100, "conversions": 85},
                {"date": "2024-01-02", "participants": 120, "conversions": 98}
            ]
        }

        with patch('chatter.services.ab_testing.ABTestManager.get_test_metrics') as mock_metrics_func:
            mock_metrics_func.return_value = mock_metrics

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/ab-tests/{test_id}/metrics", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["total_participants"] == 1000

    def test_get_ab_test_performance_success(self):
        """Test retrieving A/B test performance data."""
        # Arrange
        test_id = "test-123"
        mock_performance = {
            "test_id": test_id,
            "runtime_days": 14,
            "data_quality_score": 0.92,
            "variant_balance": {"GPT-4": 0.51, "Claude": 0.49},
            "effect_size": 0.15,
            "power_analysis": {"current_power": 0.85, "required_power": 0.8}
        }

        with patch('chatter.services.ab_testing.ABTestManager.get_test_performance') as mock_perf:
            mock_perf.return_value = mock_performance

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.get(f"/api/v1/ab-tests/{test_id}/performance", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["runtime_days"] == 14

    def test_update_ab_test_success(self):
        """Test updating an A/B test."""
        # Arrange
        test_id = "test-123"
        update_data = {
            "name": "Updated Test Name",
            "description": "Updated description",
            "traffic_split": {"GPT-4": 0.6, "Claude": 0.4}
        }

        mock_updated_test = {
            "id": test_id,
            "name": update_data["name"],
            "description": update_data["description"]
        }

        with patch('chatter.services.ab_testing.ABTestManager.update_test') as mock_update:
            mock_update.return_value = mock_updated_test

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.put(
                f"/api/v1/ab-tests/{test_id}",
                json=update_data,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["name"] == update_data["name"]

    def test_delete_ab_test_success(self):
        """Test deleting an A/B test."""
        # Arrange
        test_id = "test-123"

        with patch('chatter.services.ab_testing.ABTestManager.delete_test') as mock_delete:
            mock_delete.return_value = True

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.delete(f"/api/v1/ab-tests/{test_id}", headers=headers)

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["message"] == "A/B test deleted successfully"

    def test_complete_ab_test_success(self):
        """Test completing an A/B test with final analysis."""
        # Arrange
        test_id = "test-123"
        completion_data = {
            "winner_variant": "GPT-4",
            "implement_winner": True,
            "notes": "GPT-4 showed significantly better performance"
        }

        mock_completion = {
            "test_id": test_id,
            "status": "completed",
            "final_results": {
                "winner": "GPT-4",
                "confidence": 0.95,
                "effect_size": 0.12
            }
        }

        with patch('chatter.services.ab_testing.ABTestManager.complete_test') as mock_complete:
            mock_complete.return_value = mock_completion

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post(
                f"/api/v1/ab-tests/{test_id}/complete",
                json=completion_data,
                headers=headers
            )

            # Assert
            assert response.status_code == status.HTTP_200_OK
            response_data = response.json()
            assert response_data["final_results"]["winner"] == "GPT-4"


@pytest.mark.integration
class TestABTestingIntegration:
    """Integration tests for A/B testing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.mock_user = User(
            id="integration-user-id",
            email="integration@example.com",
            username="integrationuser"
        )

        app.dependency_overrides[get_current_user] = lambda: self.mock_user

    def teardown_method(self):
        """Clean up after tests."""
        app.dependency_overrides.clear()

    def test_full_ab_test_lifecycle(self):
        """Test complete A/B test lifecycle."""
        headers = {"Authorization": "Bearer integration-token"}

        # Create test
        test_data = {
            "name": "Integration Test",
            "description": "Full lifecycle test",
            "variants": [
                {"name": "Control", "config": {"model": "gpt-3.5"}},
                {"name": "Treatment", "config": {"model": "gpt-4"}}
            ],
            "metrics": ["response_time", "accuracy"],
            "traffic_split": {"Control": 0.5, "Treatment": 0.5}
        }

        with patch('chatter.services.ab_testing.ABTestManager.create_test') as mock_create:
            mock_create.return_value = {"id": "integration-test-id", **test_data, "status": "draft"}

            # Create
            create_response = self.client.post("/api/v1/ab-tests/", json=test_data, headers=headers)
            assert create_response.status_code == status.HTTP_201_CREATED
            test_id = create_response.json()["id"]

            # Start test
            with patch('chatter.services.ab_testing.ABTestManager.start_test') as mock_start:
                mock_start.return_value = {"id": test_id, "status": "active"}

                start_response = self.client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)
                assert start_response.status_code == status.HTTP_200_OK

                # Get metrics
                with patch('chatter.services.ab_testing.ABTestManager.get_test_metrics') as mock_metrics:
                    mock_metrics.return_value = {"total_participants": 100}

                    metrics_response = self.client.get(f"/api/v1/ab-tests/{test_id}/metrics", headers=headers)
                    assert metrics_response.status_code == status.HTTP_200_OK

                    # Complete test
                    with patch('chatter.services.ab_testing.ABTestManager.complete_test') as mock_complete:
                        mock_complete.return_value = {
                            "test_id": test_id,
                            "status": "completed",
                            "final_results": {"winner": "Treatment"}
                        }

                        complete_response = self.client.post(
                            f"/api/v1/ab-tests/{test_id}/complete",
                            json={"winner_variant": "Treatment"},
                            headers=headers
                        )
                        assert complete_response.status_code == status.HTTP_200_OK
