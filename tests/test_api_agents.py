"""Tests for agent management API endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from chatter.main import app


@pytest.mark.unit
class TestAgentEndpoints:
    """Test agent management API endpoints."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_create_agent_success(self):
        """Test successful agent creation."""
        # Arrange
        agent_data = {
            "name": "Test Agent",
            "description": "A test agent for unit testing",
            "agent_type": "chat",
            "capabilities": ["text_generation", "question_answering"],
            "model_config": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "system_prompt": "You are a helpful AI assistant."
        }

        mock_agent = {
            "id": "agent-123",
            "name": "Test Agent",
            "description": "A test agent for unit testing",
            "agent_type": "chat",
            "capabilities": ["text_generation", "question_answering"],
            "model_config": {
                "model_name": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "system_prompt": "You are a helpful AI assistant.",
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.create_agent.return_value = mock_agent
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.post("/api/v1/agents/", json=agent_data, headers=headers)

                # Assert
                assert response.status_code == status.HTTP_201_CREATED
                response_data = response.json()
                assert response_data["id"] == "agent-123"
                assert response_data["name"] == "Test Agent"
                assert response_data["status"] == "active"

    def test_create_agent_invalid_data(self):
        """Test agent creation with invalid data."""
        # Arrange
        invalid_agent_data = {
            "name": "",  # Empty name should be invalid
            "agent_type": "invalid_type"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            # Act
            headers = {"Authorization": "Bearer test-token"}
            response = self.client.post("/api/v1/agents/", json=invalid_agent_data, headers=headers)

            # Assert
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_agent_success(self):
        """Test successful agent retrieval."""
        # Arrange
        agent_id = "agent-123"
        mock_agent = {
            "id": agent_id,
            "name": "Test Agent",
            "description": "A test agent",
            "agent_type": "chat",
            "capabilities": ["text_generation"],
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.get_agent.return_value = mock_agent
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get(f"/api/v1/agents/{agent_id}", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["id"] == agent_id
                assert response_data["name"] == "Test Agent"

    def test_get_agent_not_found(self):
        """Test agent retrieval when agent doesn't exist."""
        # Arrange
        agent_id = "nonexistent-agent"

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.get_agent.return_value = None
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get(f"/api/v1/agents/{agent_id}", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_list_agents_success(self):
        """Test successful agent listing."""
        # Arrange
        mock_agents = [
            {
                "id": "agent-1",
                "name": "Agent 1",
                "agent_type": "chat",
                "status": "active"
            },
            {
                "id": "agent-2",
                "name": "Agent 2",
                "agent_type": "workflow",
                "status": "inactive"
            }
        ]

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.list_agents.return_value = {
                    "agents": mock_agents,
                    "total": 2,
                    "limit": 10,
                    "offset": 0
                }
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get("/api/v1/agents/", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert len(response_data["agents"]) == 2
                assert response_data["total"] == 2

    def test_update_agent_success(self):
        """Test successful agent update."""
        # Arrange
        agent_id = "agent-123"
        update_data = {
            "name": "Updated Agent Name",
            "description": "Updated description",
            "model_config": {
                "temperature": 0.8
            }
        }

        mock_updated_agent = {
            "id": agent_id,
            "name": "Updated Agent Name",
            "description": "Updated description",
            "agent_type": "chat",
            "model_config": {"temperature": 0.8},
            "status": "active",
            "updated_at": "2024-01-02T00:00:00Z"
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.update_agent.return_value = mock_updated_agent
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.patch(f"/api/v1/agents/{agent_id}", json=update_data, headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["name"] == "Updated Agent Name"
                assert response_data["description"] == "Updated description"

    def test_delete_agent_success(self):
        """Test successful agent deletion."""
        # Arrange
        agent_id = "agent-123"

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.delete_agent.return_value = True
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.delete(f"/api/v1/agents/{agent_id}", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["success"] is True
                assert response_data["message"] == "Agent deleted successfully"

    def test_agent_interact_success(self):
        """Test successful agent interaction."""
        # Arrange
        agent_id = "agent-123"
        interaction_data = {
            "message": "Hello, how can you help me?",
            "context": {"user_preference": "concise"},
            "stream": False
        }

        mock_response = {
            "response": "I can help you with various tasks including answering questions, providing information, and assisting with analysis.",
            "metadata": {
                "response_time": 1.23,
                "tokens_used": 45,
                "model_used": "gpt-3.5-turbo"
            }
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.interact_with_agent.return_value = mock_response
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.post(
                    f"/api/v1/agents/{agent_id}/interact",
                    json=interaction_data,
                    headers=headers
                )

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert "response" in response_data
                assert "metadata" in response_data
                assert response_data["metadata"]["tokens_used"] == 45

    def test_get_agent_stats_success(self):
        """Test successful agent statistics retrieval."""
        # Arrange
        agent_id = "agent-123"
        mock_stats = {
            "agent_id": agent_id,
            "total_interactions": 150,
            "avg_response_time": 1.45,
            "success_rate": 0.95,
            "total_tokens_used": 12500,
            "last_interaction": "2024-01-01T12:00:00Z",
            "popular_capabilities": ["text_generation", "question_answering"]
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()
                mock_agent_manager.get_agent_stats.return_value = mock_stats
                mock_manager.return_value = mock_agent_manager

                # Act
                headers = {"Authorization": "Bearer test-token"}
                response = self.client.get(f"/api/v1/agents/{agent_id}/stats", headers=headers)

                # Assert
                assert response.status_code == status.HTTP_200_OK
                response_data = response.json()
                assert response_data["agent_id"] == agent_id
                assert response_data["total_interactions"] == 150
                assert response_data["success_rate"] == 0.95


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_agent_lifecycle_integration(self):
        """Test complete agent lifecycle - create, update, interact, delete."""
        headers = {"Authorization": "Bearer integration-token"}

        # Create agent
        agent_data = {
            "name": "Integration Test Agent",
            "description": "Agent for integration testing",
            "agent_type": "chat",
            "capabilities": ["text_generation"],
            "model_config": {"temperature": 0.7}
        }

        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}

            with patch('chatter.api.agents.get_agent_manager') as mock_manager:
                mock_agent_manager = AsyncMock()

                # Mock create
                created_agent = {"id": "integration-agent-id", **agent_data, "status": "active"}
                mock_agent_manager.create_agent.return_value = created_agent

                create_response = self.client.post("/api/v1/agents/", json=agent_data, headers=headers)
                assert create_response.status_code == status.HTTP_201_CREATED
                agent_id = create_response.json()["id"]

                # Mock update
                updated_agent = {**created_agent, "name": "Updated Integration Agent"}
                mock_agent_manager.update_agent.return_value = updated_agent

                update_response = self.client.patch(
                    f"/api/v1/agents/{agent_id}",
                    json={"name": "Updated Integration Agent"},
                    headers=headers
                )
                assert update_response.status_code == status.HTTP_200_OK

                # Mock interact
                interaction_response = {"response": "Hello from integration test", "metadata": {}}
                mock_agent_manager.interact_with_agent.return_value = interaction_response

                interact_response = self.client.post(
                    f"/api/v1/agents/{agent_id}/interact",
                    json={"message": "Hello"},
                    headers=headers
                )
                assert interact_response.status_code == status.HTTP_200_OK

                # Mock delete
                mock_agent_manager.delete_agent.return_value = True

                delete_response = self.client.delete(f"/api/v1/agents/{agent_id}", headers=headers)
                assert delete_response.status_code == status.HTTP_200_OK

                mock_manager.return_value = mock_agent_manager
