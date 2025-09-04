"""Integration tests for profiles API endpoints."""

import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestProfilesIntegration:
    """Integration tests for profiles API endpoints."""

    @pytest.mark.integration
    async def test_profile_complete_lifecycle(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test complete profile lifecycle from creation to deletion."""
        # Create profile
        profile_data = {
            "name": "Integration Test Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-3.5-turbo",
            "description": "Profile for integration testing",
            "temperature": 0.7,
            "max_tokens": 1500,
            "system_message": "You are a helpful assistant.",
            "profile_type": "chat"
        }
        
        create_response = await client.post("/api/v1/profiles/", json=profile_data, headers=auth_headers)
        assert create_response.status_code == 201
        
        profile_id = create_response.json()["id"]
        
        # Verify profile was created
        get_response = await client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        profile = get_response.json()
        assert profile["name"] == "Integration Test Profile"
        assert profile["llm_provider"] == "openai"
        assert profile["llm_model"] == "gpt-3.5-turbo"
        assert profile["temperature"] == 0.7
        
        # Update profile
        update_data = {
            "name": "Updated Integration Profile",
            "description": "Updated description",
            "temperature": 0.8
        }
        
        update_response = await client.put(f"/api/v1/profiles/{profile_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Verify updates
        get_response = await client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        updated_profile = get_response.json()
        assert updated_profile["name"] == "Updated Integration Profile"
        assert updated_profile["temperature"] == 0.8
        
        # Test profile functionality
        test_data = {
            "message": "Hello, this is a test message.",
            "include_metrics": True
        }
        
        test_response = await client.post(f"/api/v1/profiles/{profile_id}/test", json=test_data, headers=auth_headers)
        
        # Should succeed or fail gracefully depending on API availability
        if test_response.status_code == 200:
            test_result = test_response.json()
            assert "response" in test_result or "error" in test_result
        
        # Clone profile
        clone_data = {
            "name": "Cloned Integration Profile",
            "include_settings": True
        }
        
        clone_response = await client.post(f"/api/v1/profiles/{profile_id}/clone", json=clone_data, headers=auth_headers)
        assert clone_response.status_code == 201
        
        cloned_profile_id = clone_response.json()["id"]
        
        # Verify clone
        clone_get_response = await client.get(f"/api/v1/profiles/{cloned_profile_id}", headers=auth_headers)
        assert clone_get_response.status_code == 200
        
        cloned_profile = clone_get_response.json()
        assert cloned_profile["name"] == "Cloned Integration Profile"
        assert cloned_profile["llm_provider"] == profile["llm_provider"]
        assert cloned_profile["llm_model"] == profile["llm_model"]
        
        # Delete both profiles
        delete_response = await client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert delete_response.status_code == 200
        
        delete_clone_response = await client.delete(f"/api/v1/profiles/{cloned_profile_id}", headers=auth_headers)
        assert delete_clone_response.status_code == 200

    @pytest.mark.integration
    async def test_profile_list_and_filter(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test profile listing and filtering functionality."""
        # Create profiles with different providers
        profiles_to_create = [
            {
                "name": "OpenAI Profile",
                "llm_provider": "openai",
                "llm_model": "gpt-3.5-turbo",
                "temperature": 0.7
            },
            {
                "name": "Anthropic Profile",
                "llm_provider": "anthropic", 
                "llm_model": "claude-3-sonnet",
                "temperature": 0.5
            },
            {
                "name": "Another OpenAI Profile",
                "llm_provider": "openai",
                "llm_model": "gpt-4",
                "temperature": 0.9
            }
        ]
        
        created_profile_ids = []
        
        for profile_data in profiles_to_create:
            response = await client.post("/api/v1/profiles/", json=profile_data, headers=auth_headers)
            assert response.status_code == 201
            created_profile_ids.append(response.json()["id"])
        
        # List all profiles
        list_response = await client.get("/api/v1/profiles", headers=auth_headers)
        assert list_response.status_code == 200
        
        data = list_response.json()
        assert len(data["profiles"]) >= 3  # At least our 3 profiles
        assert data["total"] >= 3
        
        # Test provider filtering
        openai_response = await client.get("/api/v1/profiles?provider=openai", headers=auth_headers)
        assert openai_response.status_code == 200
        
        openai_data = openai_response.json()
        for profile in openai_data["profiles"]:
            assert profile["llm_provider"] == "openai"
        
        # Test pagination
        page_response = await client.get("/api/v1/profiles?page=1&per_page=2", headers=auth_headers)
        assert page_response.status_code == 200
        page_data = page_response.json()
        assert len(page_data["profiles"]) <= 2
        
        # Clean up
        for profile_id in created_profile_ids:
            await client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers)

    @pytest.mark.integration
    async def test_profile_stats_and_providers(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test profile statistics and provider information."""
        # Get initial stats
        stats_response = await client.get("/api/v1/profiles/stats/overview", headers=auth_headers)
        assert stats_response.status_code == 200
        
        initial_stats = stats_response.json()
        assert "total_profiles" in initial_stats
        assert isinstance(initial_stats["total_profiles"], int)
        
        # Create some profiles to affect stats
        test_profiles = [
            {
                "name": "Stats Test Profile 1",
                "llm_provider": "openai",
                "llm_model": "gpt-3.5-turbo"
            },
            {
                "name": "Stats Test Profile 2", 
                "llm_provider": "anthropic",
                "llm_model": "claude-3-haiku"
            }
        ]
        
        created_profile_ids = []
        for profile_data in test_profiles:
            response = await client.post("/api/v1/profiles/", json=profile_data, headers=auth_headers)
            assert response.status_code == 201
            created_profile_ids.append(response.json()["id"])
        
        # Get updated stats
        updated_stats_response = await client.get("/api/v1/profiles/stats/overview", headers=auth_headers)
        assert updated_stats_response.status_code == 200
        
        updated_stats = updated_stats_response.json()
        assert updated_stats["total_profiles"] >= initial_stats["total_profiles"]
        
        # Get available providers
        providers_response = await client.get("/api/v1/profiles/providers/available", headers=auth_headers)
        assert providers_response.status_code == 200
        
        providers_data = providers_response.json()
        assert isinstance(providers_data, dict)
        # Should have at least some common providers
        common_providers = ["openai", "anthropic", "google", "cohere"]
        available_providers = list(providers_data.keys())
        assert any(provider in available_providers for provider in common_providers)
        
        # Clean up
        for profile_id in created_profile_ids:
            await client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers)

    @pytest.mark.integration
    async def test_profile_error_scenarios(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test profile error handling scenarios."""
        # Test non-existent profile operations
        nonexistent_id = "nonexistent-profile-id"
        
        operations = [
            ("GET", f"/api/v1/profiles/{nonexistent_id}"),
            ("PUT", f"/api/v1/profiles/{nonexistent_id}"),
            ("DELETE", f"/api/v1/profiles/{nonexistent_id}"),
            ("POST", f"/api/v1/profiles/{nonexistent_id}/test"),
            ("POST", f"/api/v1/profiles/{nonexistent_id}/clone"),
        ]
        
        for method, url in operations:
            if method == "GET":
                response = await client.get(url, headers=auth_headers)
            elif method == "POST":
                response = await client.post(url, json={}, headers=auth_headers)
            elif method == "PUT":
                response = await client.put(url, json={}, headers=auth_headers)
            elif method == "DELETE":
                response = await client.delete(url, headers=auth_headers)
            
            # Should return appropriate error codes
            assert response.status_code in [400, 404, 422], f"Failed for {method} {url}"

    @pytest.mark.integration
    async def test_profile_data_validation(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test profile data validation in integration environment."""
        # Test invalid provider
        invalid_provider_data = {
            "name": "Invalid Provider Profile",
            "llm_provider": "nonexistent_provider_xyz",
            "llm_model": "some-model"
        }
        
        response = await client.post("/api/v1/profiles/", json=invalid_provider_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # Test missing required fields
        incomplete_data = {
            "name": "Incomplete Profile"
            # Missing llm_provider and llm_model
        }
        
        response = await client.post("/api/v1/profiles/", json=incomplete_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error
        
        # Test invalid temperature range
        invalid_temp_data = {
            "name": "Invalid Temperature Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-3.5-turbo",
            "temperature": 2.5  # Should be between 0 and 2
        }
        
        response = await client.post("/api/v1/profiles/", json=invalid_temp_data, headers=auth_headers)
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_profile_concurrent_operations(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test concurrent profile operations."""
        # Create multiple profiles concurrently
        profile_data_list = [
            {
                "name": f"Concurrent Profile {i}",
                "llm_provider": "openai",
                "llm_model": "gpt-3.5-turbo",
                "temperature": 0.5 + (i * 0.1)
            }
            for i in range(5)
        ]
        
        # Create tasks for concurrent profile creation
        create_tasks = [
            asyncio.create_task(client.post("/api/v1/profiles/", json=profile_data, headers=auth_headers))
            for profile_data in profile_data_list
        ]
        
        # Wait for all creations
        create_responses = await asyncio.gather(*create_tasks)
        
        # All should succeed
        created_profile_ids = []
        for response in create_responses:
            assert response.status_code == 201
            created_profile_ids.append(response.json()["id"])
        
        # Perform concurrent operations on all profiles
        operation_tasks = []
        
        # Get each profile
        for profile_id in created_profile_ids:
            operation_tasks.append(
                asyncio.create_task(client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers))
            )
        
        # Also get stats and list concurrently
        operation_tasks.extend([
            asyncio.create_task(client.get("/api/v1/profiles/stats/overview", headers=auth_headers)),
            asyncio.create_task(client.get("/api/v1/profiles", headers=auth_headers)),
            asyncio.create_task(client.get("/api/v1/profiles/providers/available", headers=auth_headers))
        ])
        
        # Wait for all operations
        operation_responses = await asyncio.gather(*operation_tasks)
        
        # All should succeed
        for response in operation_responses:
            assert response.status_code == 200
        
        # Clean up - delete all profiles
        cleanup_tasks = [
            asyncio.create_task(client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers))
            for profile_id in created_profile_ids
        ]
        
        cleanup_responses = await asyncio.gather(*cleanup_tasks)
        for response in cleanup_responses:
            assert response.status_code == 200

    @pytest.mark.integration
    async def test_profile_complex_data_handling(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test complex profile data handling."""
        # Create profile with complex configuration
        complex_profile_data = {
            "name": "Complex Configuration Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-4",
            "description": "A profile with complex configuration for testing data integrity",
            "temperature": 0.75,
            "max_tokens": 2048,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.2,
            "system_message": "You are an expert assistant with deep knowledge in multiple domains. Provide detailed, accurate, and helpful responses.",
            "profile_type": "chat",
            "custom_parameters": {
                "context_window": 4096,
                "response_format": "json",
                "safety_level": "moderate",
                "custom_instructions": [
                    "Always be helpful and accurate",
                    "Provide sources when possible",
                    "Be concise but complete"
                ]
            }
        }
        
        # Create profile
        create_response = await client.post("/api/v1/profiles/", json=complex_profile_data, headers=auth_headers)
        assert create_response.status_code == 201
        
        profile_id = create_response.json()["id"]
        
        # Verify complex data was stored correctly
        get_response = await client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert get_response.status_code == 200
        
        retrieved_profile = get_response.json()
        assert retrieved_profile["name"] == complex_profile_data["name"]
        assert retrieved_profile["temperature"] == complex_profile_data["temperature"]
        assert retrieved_profile["max_tokens"] == complex_profile_data["max_tokens"]
        assert retrieved_profile["system_message"] == complex_profile_data["system_message"]
        
        # Update with more complex data
        complex_update_data = {
            "description": "Updated complex description with Unicode: 🤖 AI Assistant 世界",
            "custom_parameters": {
                "updated_field": "new_value",
                "nested_config": {
                    "level_1": {
                        "level_2": ["array", "with", "values"],
                        "number": 42,
                        "boolean": True
                    }
                }
            }
        }
        
        update_response = await client.put(f"/api/v1/profiles/{profile_id}", json=complex_update_data, headers=auth_headers)
        assert update_response.status_code == 200
        
        # Verify complex update
        final_get_response = await client.get(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert final_get_response.status_code == 200
        
        final_profile = final_get_response.json()
        assert "🤖 AI Assistant 世界" in final_profile["description"]
        
        # Clean up
        delete_response = await client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert delete_response.status_code == 200

    @pytest.mark.integration
    async def test_profile_testing_functionality(self, client: AsyncClient, auth_headers: dict, db_session: AsyncSession):
        """Test profile testing functionality end-to-end."""
        # Create a test profile
        profile_data = {
            "name": "Testing Functionality Profile",
            "llm_provider": "openai",
            "llm_model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "system_message": "You are a test assistant."
        }
        
        create_response = await client.post("/api/v1/profiles/", json=profile_data, headers=auth_headers)
        assert create_response.status_code == 201
        
        profile_id = create_response.json()["id"]
        
        # Test different test scenarios
        test_scenarios = [
            {
                "message": "Hello, this is a simple test message.",
                "include_metrics": True
            },
            {
                "message": "What is 2 + 2?",
                "include_metrics": False
            },
            {
                "message": "Test message with Unicode: 测试消息 🚀",
                "include_metrics": True
            }
        ]
        
        for test_data in test_scenarios:
            test_response = await client.post(f"/api/v1/profiles/{profile_id}/test", json=test_data, headers=auth_headers)
            
            # Should handle gracefully whether API is available or not
            if test_response.status_code == 200:
                test_result = test_response.json()
                # Should have either success response or error information
                assert ("response" in test_result and test_result.get("success", True)) or \
                       ("error" in test_result and not test_result.get("success", False))
            else:
                # If testing fails, should return appropriate error codes
                assert test_response.status_code in [400, 500, 503]
        
        # Clean up
        delete_response = await client.delete(f"/api/v1/profiles/{profile_id}", headers=auth_headers)
        assert delete_response.status_code == 200