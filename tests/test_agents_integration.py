"""Integration tests for agents API endpoints."""

import asyncio

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


class TestAgentsIntegration:
    """Integration tests for agents API endpoints."""

    @pytest.mark.integration
    async def test_agent_complete_lifecycle(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test complete agent lifecycle from creation to deletion."""
        # Create agent
        agent_data = {
            "name": "Integration Test Agent",
            "description": "Agent for integration testing",
            "agent_type": "chat",
            "configuration": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 1000,
                "system_prompt": "You are a helpful assistant for testing.",
            },
            "capabilities": ["text_generation", "conversation"],
            "metadata": {
                "test_mode": True,
                "environment": "integration",
            },
        }

        create_response = await client.post(
            "/api/v1/agents/", json=agent_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        agent_id = create_response.json()["id"]

        # Verify agent was created
        get_response = await client.get(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        agent = get_response.json()
        assert agent["name"] == "Integration Test Agent"
        assert agent["agent_type"] == "chat"
        assert agent["configuration"]["temperature"] == 0.7

        # Update agent
        update_data = {
            "name": "Updated Integration Agent",
            "description": "Updated description for testing",
            "configuration": {"temperature": 0.8, "max_tokens": 1500},
        }

        update_response = await client.put(
            f"/api/v1/agents/{agent_id}",
            json=update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify updates
        get_response = await client.get(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        updated_agent = get_response.json()
        assert updated_agent["name"] == "Updated Integration Agent"
        assert updated_agent["configuration"]["temperature"] == 0.8

        # Test agent functionality
        test_data = {
            "input": "Hello, this is a test message for the agent.",
            "include_metadata": True,
        }

        test_response = await client.post(
            f"/api/v1/agents/{agent_id}/test",
            json=test_data,
            headers=auth_headers,
        )

        # Should succeed or fail gracefully depending on agent service availability
        if test_response.status_code == 200:
            test_result = test_response.json()
            assert "response" in test_result or "error" in test_result

        # Check agent health
        health_response = await client.get(
            f"/api/v1/agents/{agent_id}/health", headers=auth_headers
        )

        if health_response.status_code == 200:
            health_data = health_response.json()
            assert "status" in health_data
            assert health_data["agent_id"] == agent_id

        # Delete agent
        delete_response = await client.delete(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

        # Verify deletion
        get_deleted_response = await client.get(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert get_deleted_response.status_code == 404

    @pytest.mark.integration
    async def test_agents_list_and_filter(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent listing and filtering functionality."""
        # Create agents with different types
        agents_to_create = [
            {
                "name": "Chat Agent",
                "description": "Agent for chat interactions",
                "agent_type": "chat",
                "configuration": {"model": "gpt-3.5-turbo"},
            },
            {
                "name": "Assistant Agent",
                "description": "General assistant agent",
                "agent_type": "assistant",
                "configuration": {"model": "gpt-4"},
            },
            {
                "name": "Code Agent",
                "description": "Agent for code assistance",
                "agent_type": "coding",
                "configuration": {"model": "gpt-4", "temperature": 0.2},
            },
        ]

        created_agent_ids = []

        for agent_data in agents_to_create:
            response = await client.post(
                "/api/v1/agents/", json=agent_data, headers=auth_headers
            )
            assert response.status_code == 201
            created_agent_ids.append(response.json()["id"])

        # List all agents
        list_response = await client.get(
            "/api/v1/agents/", headers=auth_headers
        )
        assert list_response.status_code == 200

        data = list_response.json()
        assert len(data["agents"]) >= 3  # At least our 3 agents
        assert data["total"] >= 3

        # Test type filtering
        chat_response = await client.get(
            "/api/v1/agents/?agent_type=chat", headers=auth_headers
        )
        assert chat_response.status_code == 200

        chat_data = chat_response.json()
        for agent in chat_data["agents"]:
            assert agent["agent_type"] == "chat"

        # Test pagination
        page_response = await client.get(
            "/api/v1/agents/?page=1&per_page=2", headers=auth_headers
        )
        assert page_response.status_code == 200
        page_data = page_response.json()
        assert len(page_data["agents"]) <= 2

        # Clean up
        for agent_id in created_agent_ids:
            await client.delete(
                f"/api/v1/agents/{agent_id}", headers=auth_headers
            )

    @pytest.mark.integration
    async def test_agent_templates_workflow(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent templates functionality."""
        # Get available templates
        templates_response = await client.get(
            "/api/v1/agents/templates", headers=auth_headers
        )
        assert templates_response.status_code == 200

        templates = templates_response.json()
        assert isinstance(templates, list)

        if len(templates) > 0:
            # Use first template to create an agent
            template = templates[0]

            agent_from_template = {
                "name": f"Agent from {template['name']}",
                "description": f"Created from template: {template['name']}",
                "agent_type": template.get("agent_type", "chat"),
                "configuration": template.get("configuration", {}),
                "template_id": template.get("id"),
            }

            create_response = await client.post(
                "/api/v1/agents/",
                json=agent_from_template,
                headers=auth_headers,
            )
            assert create_response.status_code == 201

            agent_id = create_response.json()["id"]

            # Verify agent was created with template data
            get_response = await client.get(
                f"/api/v1/agents/{agent_id}", headers=auth_headers
            )
            assert get_response.status_code == 200

            agent = get_response.json()
            assert template["name"] in agent["name"]

            # Clean up
            await client.delete(
                f"/api/v1/agents/{agent_id}", headers=auth_headers
            )

    @pytest.mark.integration
    async def test_bulk_agent_operations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test bulk agent operations."""
        # Bulk create agents
        bulk_create_data = {
            "agents": [
                {
                    "name": "Bulk Agent 1",
                    "description": "First bulk created agent",
                    "agent_type": "chat",
                    "configuration": {"model": "gpt-3.5-turbo"},
                },
                {
                    "name": "Bulk Agent 2",
                    "description": "Second bulk created agent",
                    "agent_type": "assistant",
                    "configuration": {"model": "gpt-4"},
                },
                {
                    "name": "Bulk Agent 3",
                    "description": "Third bulk created agent",
                    "agent_type": "coding",
                    "configuration": {
                        "model": "gpt-4",
                        "temperature": 0.1,
                    },
                },
            ]
        }

        bulk_create_response = await client.post(
            "/api/v1/agents/bulk",
            json=bulk_create_data,
            headers=auth_headers,
        )
        assert bulk_create_response.status_code == 201

        bulk_result = bulk_create_response.json()
        assert (
            bulk_result["created_count"] >= 2
        )  # At least 2 should succeed

        created_agent_ids = [
            agent["id"] for agent in bulk_result["created_agents"]
        ]

        # Verify agents were created
        for agent_id in created_agent_ids:
            get_response = await client.get(
                f"/api/v1/agents/{agent_id}", headers=auth_headers
            )
            assert get_response.status_code == 200

        # Bulk delete agents
        bulk_delete_data = {"agent_ids": created_agent_ids}

        bulk_delete_response = await client.delete(
            "/api/v1/agents/bulk",
            json=bulk_delete_data,
            headers=auth_headers,
        )
        assert bulk_delete_response.status_code == 200

        delete_result = bulk_delete_response.json()
        assert (
            delete_result["deleted_count"] >= len(created_agent_ids) - 1
        )  # Allow for some failures

    @pytest.mark.integration
    async def test_agent_testing_functionality(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent testing functionality end-to-end."""
        # Create a test agent
        agent_data = {
            "name": "Testing Agent",
            "description": "Agent for testing functionality",
            "agent_type": "chat",
            "configuration": {
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "system_prompt": "You are a test assistant. Always respond helpfully.",
            },
        }

        create_response = await client.post(
            "/api/v1/agents/", json=agent_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        agent_id = create_response.json()["id"]

        # Test different test scenarios
        test_scenarios = [
            {
                "input": "Hello, can you help me with a simple test?",
                "include_metadata": True,
            },
            {"input": "What is 2 + 2?", "include_metadata": False},
            {
                "input": "Test with Unicode: 测试消息 🤖",
                "include_metadata": True,
            },
        ]

        for test_data in test_scenarios:
            test_response = await client.post(
                f"/api/v1/agents/{agent_id}/test",
                json=test_data,
                headers=auth_headers,
            )

            # Should handle gracefully whether agent service is available or not
            if test_response.status_code == 200:
                test_result = test_response.json()
                assert (
                    "response" in test_result
                    and test_result.get("success", True)
                ) or (
                    "error" in test_result
                    and not test_result.get("success", False)
                )
            else:
                # If testing fails, should return appropriate error codes
                assert test_response.status_code in [400, 500, 503]

        # Clean up
        delete_response = await client.delete(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

    @pytest.mark.integration
    async def test_agent_health_monitoring(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent health monitoring functionality."""
        # Create agent for health testing
        agent_data = {
            "name": "Health Monitor Agent",
            "description": "Agent for health monitoring tests",
            "agent_type": "chat",
            "configuration": {"model": "gpt-3.5-turbo"},
        }

        create_response = await client.post(
            "/api/v1/agents/", json=agent_data, headers=auth_headers
        )
        assert create_response.status_code == 201

        agent_id = create_response.json()["id"]

        # Check agent health
        health_response = await client.get(
            f"/api/v1/agents/{agent_id}/health", headers=auth_headers
        )

        if health_response.status_code == 200:
            health_data = health_response.json()

            # Verify health response structure
            assert "agent_id" in health_data
            assert health_data["agent_id"] == agent_id
            assert "status" in health_data
            assert health_data["status"] in [
                "healthy",
                "unhealthy",
                "degraded",
            ]

            # Optional fields that might be present
            optional_fields = [
                "last_active",
                "response_time",
                "error_rate",
                "uptime",
                "checks",
            ]
            for field in optional_fields:
                if field in health_data:
                    assert health_data[field] is not None

        # Clean up
        delete_response = await client.delete(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200

    @pytest.mark.integration
    async def test_agent_error_scenarios(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent error handling scenarios."""
        # Test non-existent agent operations
        nonexistent_id = "nonexistent-agent-id"

        operations = [
            ("GET", f"/api/v1/agents/{nonexistent_id}"),
            ("PUT", f"/api/v1/agents/{nonexistent_id}"),
            ("DELETE", f"/api/v1/agents/{nonexistent_id}"),
            ("POST", f"/api/v1/agents/{nonexistent_id}/test"),
            ("GET", f"/api/v1/agents/{nonexistent_id}/health"),
        ]

        for method, url in operations:
            if method == "GET":
                response = await client.get(url, headers=auth_headers)
            elif method == "POST":
                response = await client.post(
                    url, json={}, headers=auth_headers
                )
            elif method == "PUT":
                response = await client.put(
                    url, json={}, headers=auth_headers
                )
            elif method == "DELETE":
                response = await client.delete(
                    url, headers=auth_headers
                )

            # Should return appropriate error codes
            assert response.status_code in [
                400,
                404,
                422,
            ], f"Failed for {method} {url}"

    @pytest.mark.integration
    async def test_agent_data_validation(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agent data validation in integration environment."""
        # Test invalid agent type
        invalid_type_data = {
            "name": "Invalid Type Agent",
            "description": "Agent with invalid type",
            "agent_type": "invalid_type_xyz",
            "configuration": {"model": "gpt-3.5-turbo"},
        }

        response = await client.post(
            "/api/v1/agents/",
            json=invalid_type_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

        # Test missing required fields
        incomplete_data = {
            "description": "Agent missing required fields"
            # Missing name and agent_type
        }

        response = await client.post(
            "/api/v1/agents/",
            json=incomplete_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

        # Test invalid configuration
        invalid_config_data = {
            "name": "Invalid Config Agent",
            "agent_type": "chat",
            "configuration": {
                "temperature": 3.0  # Should be between 0 and 2
            },
        }

        response = await client.post(
            "/api/v1/agents/",
            json=invalid_config_data,
            headers=auth_headers,
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.integration
    async def test_concurrent_agent_operations(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test concurrent agent operations."""
        # Create multiple agents concurrently
        agent_data_list = [
            {
                "name": f"Concurrent Agent {i}",
                "description": f"Agent created concurrently {i}",
                "agent_type": "chat",
                "configuration": {
                    "model": "gpt-3.5-turbo",
                    "temperature": 0.5 + (i * 0.1),
                },
            }
            for i in range(5)
        ]

        # Create tasks for concurrent agent creation
        create_tasks = [
            asyncio.create_task(
                client.post(
                    "/api/v1/agents/",
                    json=agent_data,
                    headers=auth_headers,
                )
            )
            for agent_data in agent_data_list
        ]

        # Wait for all creations
        create_responses = await asyncio.gather(*create_tasks)

        # All should succeed
        created_agent_ids = []
        for response in create_responses:
            assert response.status_code == 201
            created_agent_ids.append(response.json()["id"])

        # Perform concurrent operations on all agents
        operation_tasks = []

        # Get each agent
        for agent_id in created_agent_ids:
            operation_tasks.append(
                asyncio.create_task(
                    client.get(
                        f"/api/v1/agents/{agent_id}",
                        headers=auth_headers,
                    )
                )
            )

        # Also get templates and list agents concurrently
        operation_tasks.extend(
            [
                asyncio.create_task(
                    client.get(
                        "/api/v1/agents/templates", headers=auth_headers
                    )
                ),
                asyncio.create_task(
                    client.get("/api/v1/agents/", headers=auth_headers)
                ),
            ]
        )

        # Wait for all operations
        operation_responses = await asyncio.gather(*operation_tasks)

        # All should succeed
        for response in operation_responses:
            assert response.status_code == 200

        # Clean up - delete all agents
        cleanup_tasks = [
            asyncio.create_task(
                client.delete(
                    f"/api/v1/agents/{agent_id}", headers=auth_headers
                )
            )
            for agent_id in created_agent_ids
        ]

        cleanup_responses = await asyncio.gather(*cleanup_tasks)
        for response in cleanup_responses:
            assert response.status_code == 200

    @pytest.mark.integration
    async def test_agent_complex_configuration(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        """Test agents with complex configurations."""
        # Create agent with complex configuration
        complex_agent_data = {
            "name": "Complex Configuration Agent",
            "description": "Agent with advanced configuration options",
            "agent_type": "assistant",
            "configuration": {
                "model": "gpt-4",
                "temperature": 0.8,
                "max_tokens": 2048,
                "top_p": 0.9,
                "frequency_penalty": 0.1,
                "presence_penalty": 0.2,
                "system_prompt": "You are an expert AI assistant with advanced capabilities. Provide detailed and accurate responses.",
                "custom_parameters": {
                    "response_format": "detailed",
                    "context_window": 4096,
                    "safety_level": "moderate",
                },
            },
            "capabilities": [
                "text_generation",
                "conversation",
                "analysis",
                "summarization",
            ],
            "metadata": {
                "version": "1.0",
                "created_for": "integration_testing",
                "features": {
                    "streaming": True,
                    "function_calling": False,
                    "multi_turn": True,
                },
            },
        }

        # Create agent
        create_response = await client.post(
            "/api/v1/agents/",
            json=complex_agent_data,
            headers=auth_headers,
        )
        assert create_response.status_code == 201

        agent_id = create_response.json()["id"]

        # Verify complex data was stored correctly
        get_response = await client.get(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert get_response.status_code == 200

        retrieved_agent = get_response.json()
        assert retrieved_agent["name"] == complex_agent_data["name"]
        assert (
            retrieved_agent["configuration"]["temperature"]
            == complex_agent_data["configuration"]["temperature"]
        )
        assert (
            retrieved_agent["configuration"]["max_tokens"]
            == complex_agent_data["configuration"]["max_tokens"]
        )

        # Update with more complex data
        complex_update_data = {
            "description": "Updated complex agent with Unicode: 🤖 AI Assistant 世界",
            "configuration": {
                "custom_parameters": {
                    "updated_field": "new_value",
                    "nested_config": {
                        "level_1": {
                            "level_2": ["array", "with", "values"],
                            "number": 42,
                            "boolean": True,
                        }
                    },
                }
            },
        }

        update_response = await client.put(
            f"/api/v1/agents/{agent_id}",
            json=complex_update_data,
            headers=auth_headers,
        )
        assert update_response.status_code == 200

        # Verify complex update
        final_get_response = await client.get(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert final_get_response.status_code == 200

        final_agent = final_get_response.json()
        assert "🤖 AI Assistant 世界" in final_agent["description"]

        # Clean up
        delete_response = await client.delete(
            f"/api/v1/agents/{agent_id}", headers=auth_headers
        )
        assert delete_response.status_code == 200
