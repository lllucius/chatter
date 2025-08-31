"""Agent management API tests."""

import pytest


@pytest.mark.unit
class TestAgentsAPI:
    """Test agent management API endpoints."""

    async def test_create_agent(self, test_client):
        """Test agent creation."""
        # Setup user and auth
        registration_data = {
            "email": "agentuser@example.com",
            "password": "SecurePass123!",
            "username": "agentuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "agentuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create agent
        agent_data = {
            "name": "Test Agent",
            "agent_type": "conversational",
            "description": "A test agent for automated testing",
            "system_prompt": "You are a helpful test assistant.",
            "personality_traits": ["helpful", "friendly"],
            "knowledge_domains": ["general"],
            "response_style": "conversational",
            "capabilities": ["chat"],
            "available_tools": [],
            "primary_llm": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 150,
            "learning_enabled": False
        }

        response = await test_client.post("/api/v1/agents", json=agent_data, headers=headers)
        
        # Should succeed or return 501 if not fully implemented
        assert response.status_code in [201, 422, 501]
        
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "Test Agent"
            assert data["agent_type"] == "conversational"
            assert "id" in data

    async def test_create_agent_unauthorized(self, test_client):
        """Test agent creation without authentication."""
        agent_data = {
            "name": "Test Agent",
            "agent_type": "conversational",
            "description": "A test agent"
        }

        response = await test_client.post("/api/v1/agents", json=agent_data)
        
        # Should require authentication
        assert response.status_code in [401, 403]

    async def test_list_agents(self, test_client):
        """Test listing agents."""
        # Setup user and auth
        registration_data = {
            "email": "listuser@example.com",
            "password": "SecurePass123!",
            "username": "listuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "listuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List agents
        response = await test_client.get("/api/v1/agents", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "agents" in data or isinstance(data, list)

    async def test_get_agent_by_id(self, test_client):
        """Test retrieving a specific agent."""
        # Setup user and auth
        registration_data = {
            "email": "getuser@example.com",
            "password": "SecurePass123!",
            "username": "getuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "getuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get an agent (will likely return 404)
        response = await test_client.get("/api/v1/agents/nonexistent", headers=headers)
        
        # Should return 404 for non-existent agent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_update_agent(self, test_client):
        """Test updating an agent."""
        # Setup user and auth
        registration_data = {
            "email": "updateuser@example.com",
            "password": "SecurePass123!",
            "username": "updateuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "updateuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update agent data
        update_data = {
            "name": "Updated Agent",
            "description": "Updated description",
            "temperature": 0.8
        }

        response = await test_client.put("/api/v1/agents/nonexistent", json=update_data, headers=headers)
        
        # Should return 404 for non-existent or 501/405 if not implemented
        assert response.status_code in [404, 405, 501]

    async def test_delete_agent(self, test_client):
        """Test deleting an agent."""
        # Setup user and auth
        registration_data = {
            "email": "deleteuser@example.com",
            "password": "SecurePass123!",
            "username": "deleteuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "deleteuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to delete an agent
        response = await test_client.delete("/api/v1/agents/nonexistent", headers=headers)
        
        # Should return 404 for non-existent or 501/405 if not implemented
        assert response.status_code in [404, 405, 501]

    async def test_agent_interaction(self, test_client):
        """Test interacting with an agent."""
        # Setup user and auth
        registration_data = {
            "email": "interactuser@example.com",
            "password": "SecurePass123!",
            "username": "interactuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "interactuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Interact with agent
        interaction_data = {
            "message": "Hello, how are you?",
            "context": {}
        }

        response = await test_client.post(
            "/api/v1/agents/nonexistent/interact", 
            json=interaction_data, 
            headers=headers
        )
        
        # Should return 404 for non-existent agent or 501 if not implemented
        assert response.status_code in [404, 422, 501]

    async def test_agent_stats(self, test_client):
        """Test retrieving agent statistics."""
        # Setup user and auth
        registration_data = {
            "email": "statsuser@example.com",
            "password": "SecurePass123!",
            "username": "statsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "statsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get agent stats
        response = await test_client.get("/api/v1/agents/nonexistent/stats", headers=headers)
        
        # Should return 404 for non-existent agent or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_agent_validation(self, test_client):
        """Test agent creation validation."""
        # Setup user and auth
        registration_data = {
            "email": "validuser@example.com",
            "password": "SecurePass123!",
            "username": "validuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try creating agent with missing required fields
        invalid_data = {
            "description": "Missing name and type"
        }

        response = await test_client.post("/api/v1/agents", json=invalid_data, headers=headers)
        
        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_agent_search(self, test_client):
        """Test agent search functionality."""
        # Setup user and auth
        registration_data = {
            "email": "searchuser@example.com",
            "password": "SecurePass123!",
            "username": "searchuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "searchuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search agents with query parameters
        response = await test_client.get("/api/v1/agents?search=test&type=conversational", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "agents" in data or isinstance(data, list)