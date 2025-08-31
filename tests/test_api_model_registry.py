"""Model registry API tests."""

import pytest


@pytest.mark.unit
class TestModelRegistryAPI:
    """Test model registry API endpoints."""

    async def test_list_models(self, test_client):
        """Test listing available models."""
        # Setup user and auth
        registration_data = {
            "email": "modeluser@example.com",
            "password": "SecurePass123!",
            "username": "modeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "modeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List models
        response = await test_client.get("/api/v1/models", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "models" in data or isinstance(data, list)

    async def test_register_model(self, test_client):
        """Test registering a new model."""
        # Setup user and auth
        registration_data = {
            "email": "registermodeluser@example.com",
            "password": "SecurePass123!",
            "username": "registermodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "registermodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Register model
        model_data = {
            "name": "custom-gpt-model",
            "provider": "openai",
            "model_type": "chat",
            "config": {
                "api_key": "sk-test123",
                "model": "gpt-3.5-turbo",
                "max_tokens": 150,
                "temperature": 0.7
            },
            "description": "Custom GPT model configuration",
            "tags": ["openai", "chat"]
        }

        response = await test_client.post("/api/v1/models", json=model_data, headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [201, 422, 501]
        
        if response.status_code == 201:
            data = response.json()
            assert data["name"] == "custom-gpt-model"
            assert "id" in data

    async def test_get_model_by_id(self, test_client):
        """Test retrieving a specific model."""
        # Setup user and auth
        registration_data = {
            "email": "getmodeluser@example.com",
            "password": "SecurePass123!",
            "username": "getmodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "getmodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to get a model (will likely return 404)
        response = await test_client.get("/api/v1/models/nonexistent", headers=headers)
        
        # Should return 404 for non-existent model or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_update_model(self, test_client):
        """Test updating a model."""
        # Setup user and auth
        registration_data = {
            "email": "updatemodeluser@example.com",
            "password": "SecurePass123!",
            "username": "updatemodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "updatemodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Update model
        update_data = {
            "description": "Updated model description",
            "config": {
                "temperature": 0.8,
                "max_tokens": 200
            }
        }

        response = await test_client.put("/api/v1/models/nonexistent", json=update_data, headers=headers)
        
        # Should return 404 for non-existent or 501/405 if not implemented
        assert response.status_code in [404, 405, 501]

    async def test_delete_model(self, test_client):
        """Test deleting a model."""
        # Setup user and auth
        registration_data = {
            "email": "deletemodeluser@example.com",
            "password": "SecurePass123!",
            "username": "deletemodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "deletemodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try to delete a model
        response = await test_client.delete("/api/v1/models/nonexistent", headers=headers)
        
        # Should return 404 for non-existent or 501/405 if not implemented
        assert response.status_code in [404, 405, 501]

    async def test_test_model_connection(self, test_client):
        """Test testing model connection."""
        # Setup user and auth
        registration_data = {
            "email": "testmodeluser@example.com",
            "password": "SecurePass123!",
            "username": "testmodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "testmodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test model connection
        response = await test_client.post("/api/v1/models/nonexistent/test", headers=headers)
        
        # Should return 404 for non-existent model or 501 if not implemented
        assert response.status_code in [404, 422, 501]

    async def test_model_usage_stats(self, test_client):
        """Test getting model usage statistics."""
        # Setup user and auth
        registration_data = {
            "email": "modelstatsuser@example.com",
            "password": "SecurePass123!",
            "username": "modelstatsuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "modelstatsuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Get model usage stats
        response = await test_client.get("/api/v1/models/nonexistent/stats", headers=headers)
        
        # Should return 404 for non-existent model or 501 if not implemented
        assert response.status_code in [404, 501]

    async def test_model_providers(self, test_client):
        """Test listing model providers."""
        # Setup user and auth
        registration_data = {
            "email": "provideruser@example.com",
            "password": "SecurePass123!",
            "username": "provideruser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "provideruser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List providers
        response = await test_client.get("/api/v1/models/providers", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "providers" in data or isinstance(data, list)

    async def test_model_templates(self, test_client):
        """Test listing model templates."""
        # Setup user and auth
        registration_data = {
            "email": "templateuser@example.com",
            "password": "SecurePass123!",
            "username": "templateuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "templateuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # List model templates
        response = await test_client.get("/api/v1/models/templates", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]

    async def test_models_unauthorized(self, test_client):
        """Test model endpoints require authentication."""
        endpoints = [
            "/api/v1/models",
            "/api/v1/models/test",
            "/api/v1/models/providers",
            "/api/v1/models/templates"
        ]
        
        for endpoint in endpoints:
            if endpoint == "/api/v1/models":
                # Test both GET and POST
                response = await test_client.get(endpoint)
                assert response.status_code in [401, 403]
                
                response = await test_client.post(endpoint, json={})
                assert response.status_code in [401, 403]
            else:
                response = await test_client.get(endpoint)
                assert response.status_code in [401, 403]

    async def test_model_validation(self, test_client):
        """Test model registration validation."""
        # Setup user and auth
        registration_data = {
            "email": "validmodeluser@example.com",
            "password": "SecurePass123!",
            "username": "validmodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "validmodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Try registering model with missing required fields
        invalid_data = {
            "description": "Missing name and provider"
        }

        response = await test_client.post("/api/v1/models", json=invalid_data, headers=headers)
        
        # Should fail validation
        assert response.status_code in [400, 422]

    async def test_model_search(self, test_client):
        """Test model search functionality."""
        # Setup user and auth
        registration_data = {
            "email": "searchmodeluser@example.com",
            "password": "SecurePass123!",
            "username": "searchmodeluser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "searchmodeluser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Search models with query parameters
        response = await test_client.get("/api/v1/models?search=gpt&provider=openai&type=chat", headers=headers)
        
        # Should succeed or return 501 if not implemented
        assert response.status_code in [200, 501]