"""Unit tests for agents API endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient


class TestAgentsUnit:
    """Unit tests for agents API endpoints."""

    @pytest.mark.unit
    async def test_create_agent_requires_auth(self, client: AsyncClient):
        """Test that creating agent requires authentication."""
        agent_data = {
            "name": "Test Agent",
            "description": "Test agent description",
            "agent_type": "chat"
        }
        
        response = await client.post("/api/v1/agents/", json=agent_data)
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_list_agents_requires_auth(self, client: AsyncClient):
        """Test that listing agents requires authentication."""
        response = await client.get("/api/v1/agents/")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_agent_templates_requires_auth(self, client: AsyncClient):
        """Test that getting agent templates requires authentication."""
        response = await client.get("/api/v1/agents/templates")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_agent_requires_auth(self, client: AsyncClient):
        """Test that getting specific agent requires authentication."""
        response = await client.get("/api/v1/agents/agent-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_update_agent_requires_auth(self, client: AsyncClient):
        """Test that updating agent requires authentication."""
        response = await client.put("/api/v1/agents/agent-id", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_delete_agent_requires_auth(self, client: AsyncClient):
        """Test that deleting agent requires authentication."""
        response = await client.delete("/api/v1/agents/agent-id")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_test_agent_requires_auth(self, client: AsyncClient):
        """Test that testing agent requires authentication."""
        response = await client.post("/api/v1/agents/agent-id/test", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_get_agent_health_requires_auth(self, client: AsyncClient):
        """Test that getting agent health requires authentication."""
        response = await client.get("/api/v1/agents/agent-id/health")
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_bulk_create_agents_requires_auth(self, client: AsyncClient):
        """Test that bulk creating agents requires authentication."""
        response = await client.post("/api/v1/agents/bulk", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    async def test_bulk_delete_agents_requires_auth(self, client: AsyncClient):
        """Test that bulk deleting agents requires authentication."""
        response = await client.delete("/api/v1/agents/bulk", json={})
        assert response.status_code == 401

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_create_agent_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent creation."""
        # Mock the agent service
        mock_service = AsyncMock()
        mock_agent = {
            "id": "agent-123",
            "name": "Test Agent",
            "description": "Test agent description",
            "agent_type": "chat",
            "status": "active",
            "created_by": "testuser",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
        mock_service.create_agent.return_value = mock_agent
        mock_agent_service.return_value = mock_service
        
        agent_data = {
            "name": "Test Agent",
            "description": "Test agent description",
            "agent_type": "chat",
            "configuration": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            }
        }
        
        response = await client.post("/api/v1/agents/", json=agent_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["id"] == "agent-123"
        assert data["name"] == "Test Agent"
        assert data["agent_type"] == "chat"

    @pytest.mark.unit
    async def test_create_agent_invalid_data(self, client: AsyncClient, auth_headers: dict):
        """Test agent creation with invalid data."""
        # Missing required fields
        agent_data = {
            "description": "Test agent description"
            # Missing name and agent_type
        }
        
        response = await client.post("/api/v1/agents/", json=agent_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_list_agents_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent listing."""
        mock_service = AsyncMock()
        mock_agents = [
            {
                "id": "agent-1",
                "name": "Agent 1",
                "agent_type": "chat",
                "status": "active",
                "created_at": "2024-01-01T12:00:00Z"
            },
            {
                "id": "agent-2",
                "name": "Agent 2",
                "agent_type": "assistant",
                "status": "inactive",
                "created_at": "2024-01-01T13:00:00Z"
            }
        ]
        
        mock_service.list_agents.return_value = {
            "agents": mock_agents,
            "total": 2,
            "page": 1,
            "per_page": 10
        }
        mock_agent_service.return_value = mock_service
        
        response = await client.get("/api/v1/agents/", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["agents"]) == 2
        assert data["total"] == 2

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_get_agent_templates_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent templates retrieval."""
        mock_service = AsyncMock()
        mock_templates = [
            {
                "id": "template-1",
                "name": "Chat Assistant Template",
                "description": "Template for chat assistants",
                "agent_type": "chat",
                "configuration": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.7
                }
            },
            {
                "id": "template-2", 
                "name": "Code Assistant Template",
                "description": "Template for code assistants",
                "agent_type": "coding",
                "configuration": {
                    "model": "gpt-4",
                    "temperature": 0.2
                }
            }
        ]
        
        mock_service.get_agent_templates.return_value = mock_templates
        mock_agent_service.return_value = mock_service
        
        response = await client.get("/api/v1/agents/templates", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Chat Assistant Template"

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_get_agent_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent retrieval."""
        mock_service = AsyncMock()
        mock_agent = {
            "id": "agent-123",
            "name": "Test Agent",
            "description": "Test agent description",
            "agent_type": "chat",
            "status": "active",
            "configuration": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "created_at": "2024-01-01T12:00:00Z"
        }
        
        mock_service.get_agent.return_value = mock_agent
        mock_agent_service.return_value = mock_service
        
        response = await client.get("/api/v1/agents/agent-123", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == "agent-123"
        assert data["name"] == "Test Agent"
        assert data["status"] == "active"

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_get_agent_not_found(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test agent retrieval for non-existent agent."""
        mock_service = AsyncMock()
        mock_service.get_agent.return_value = None
        mock_agent_service.return_value = mock_service
        
        response = await client.get("/api/v1/agents/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_update_agent_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent update."""
        mock_service = AsyncMock()
        mock_updated_agent = {
            "id": "agent-123",
            "name": "Updated Agent",
            "description": "Updated description",
            "agent_type": "chat",
            "status": "active",
            "updated_at": "2024-01-01T13:00:00Z"
        }
        
        mock_service.update_agent.return_value = mock_updated_agent
        mock_agent_service.return_value = mock_service
        
        update_data = {
            "name": "Updated Agent",
            "description": "Updated description"
        }
        
        response = await client.put("/api/v1/agents/agent-123", json=update_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Agent"
        assert data["description"] == "Updated description"

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_delete_agent_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent deletion."""
        mock_service = AsyncMock()
        mock_service.delete_agent.return_value = True
        mock_agent_service.return_value = mock_service
        
        response = await client.delete("/api/v1/agents/agent-123", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["agent_id"] == "agent-123"

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_test_agent_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent testing."""
        mock_service = AsyncMock()
        mock_test_result = {
            "agent_id": "agent-123",
            "test_input": "Hello, how are you?",
            "response": "I'm doing well, thank you! How can I assist you today?",
            "response_time": 1.25,
            "success": True,
            "metadata": {
                "tokens_used": 25,
                "model_used": "gpt-4"
            }
        }
        
        mock_service.test_agent.return_value = mock_test_result
        mock_agent_service.return_value = mock_service
        
        test_data = {
            "input": "Hello, how are you?",
            "include_metadata": True
        }
        
        response = await client.post("/api/v1/agents/agent-123/test", json=test_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["response_time"] == 1.25
        assert "metadata" in data

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_get_agent_health_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful agent health check."""
        mock_service = AsyncMock()
        mock_health = {
            "agent_id": "agent-123",
            "status": "healthy",
            "last_active": "2024-01-01T12:00:00Z",
            "response_time": 0.85,
            "error_rate": 0.02,
            "uptime": 3600.5,
            "checks": {
                "model_connection": "healthy",
                "memory_usage": "normal",
                "response_quality": "good"
            }
        }
        
        mock_service.get_agent_health.return_value = mock_health
        mock_agent_service.return_value = mock_service
        
        response = await client.get("/api/v1/agents/agent-123/health", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["error_rate"] == 0.02
        assert "checks" in data

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_bulk_create_agents_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful bulk agent creation."""
        mock_service = AsyncMock()
        mock_bulk_result = {
            "created_count": 3,
            "failed_count": 0,
            "created_agents": [
                {"id": "agent-1", "name": "Agent 1"},
                {"id": "agent-2", "name": "Agent 2"},
                {"id": "agent-3", "name": "Agent 3"}
            ],
            "errors": []
        }
        
        mock_service.bulk_create_agents.return_value = mock_bulk_result
        mock_agent_service.return_value = mock_service
        
        bulk_data = {
            "agents": [
                {
                    "name": "Agent 1",
                    "agent_type": "chat",
                    "description": "First agent"
                },
                {
                    "name": "Agent 2",
                    "agent_type": "assistant",
                    "description": "Second agent"
                },
                {
                    "name": "Agent 3",
                    "agent_type": "coding",
                    "description": "Third agent"
                }
            ]
        }
        
        response = await client.post("/api/v1/agents/bulk", json=bulk_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["created_count"] == 3
        assert data["failed_count"] == 0
        assert len(data["created_agents"]) == 3

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_bulk_delete_agents_success(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test successful bulk agent deletion."""
        mock_service = AsyncMock()
        mock_bulk_result = {
            "deleted_count": 2,
            "failed_count": 1,
            "deleted_agent_ids": ["agent-1", "agent-2"],
            "errors": [
                {"agent_id": "nonexistent-agent", "error": "Agent not found"}
            ]
        }
        
        mock_service.bulk_delete_agents.return_value = mock_bulk_result
        mock_agent_service.return_value = mock_service
        
        bulk_delete_data = {
            "agent_ids": ["agent-1", "agent-2", "nonexistent-agent"]
        }
        
        response = await client.delete("/api/v1/agents/bulk", json=bulk_delete_data, headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["deleted_count"] == 2
        assert data["failed_count"] == 1
        assert len(data["errors"]) == 1

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_agent_service_error_handling(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test agent service error handling."""
        mock_service = AsyncMock()
        mock_service.create_agent.side_effect = Exception("Agent service error")
        mock_agent_service.return_value = mock_service
        
        agent_data = {
            "name": "Test Agent",
            "agent_type": "chat",
            "description": "Test agent"
        }
        
        response = await client.post("/api/v1/agents/", json=agent_data, headers=auth_headers)
        assert response.status_code == 500

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_list_agents_with_filters(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test agent listing with filters."""
        mock_service = AsyncMock()
        mock_service.list_agents.return_value = {
            "agents": [],
            "total": 0,
            "page": 1,
            "per_page": 10
        }
        mock_agent_service.return_value = mock_service
        
        # Test with type filter
        response = await client.get("/api/v1/agents/?agent_type=chat", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify filter was passed to service
        mock_service.list_agents.assert_called()
        call_kwargs = mock_service.list_agents.call_args[1]
        assert "agent_type" in call_kwargs

    @pytest.mark.unit
    @patch('chatter.api.agents.AgentService')
    async def test_agent_test_with_invalid_input(self, mock_agent_service, client: AsyncClient, auth_headers: dict):
        """Test agent testing with invalid input."""
        mock_service = AsyncMock()
        mock_service.test_agent.side_effect = ValueError("Invalid test input")
        mock_agent_service.return_value = mock_service
        
        test_data = {
            "input": "",  # Empty input
            "include_metadata": False
        }
        
        response = await client.post("/api/v1/agents/agent-123/test", json=test_data, headers=auth_headers)
        assert response.status_code == 400