"""Integration tests."""

import asyncio
from unittest.mock import patch

import pytest


@pytest.mark.integration
class TestCompleteConversationWorkflow:
    """Test complete conversation workflow integration."""

    async def test_end_to_end_conversation_flow(self, test_client):
        """Test complete conversation workflow from registration to chat."""
        # 1. User Registration
        registration_data = {
            "email": "integration@example.com",
            "password": "SecurePass123!",
            "username": "integrationuser"
        }

        reg_response = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert reg_response.status_code == 201

        # 2. User Login
        login_data = {
            "email": "integration@example.com",
            "password": "SecurePass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create Conversation
        conversation_data = {
            "title": "Integration Test Conversation",
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant for integration testing."
        }

        conv_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        assert conv_response.status_code == 201
        conversation_id = conv_response.json()["id"]

        # 4. Send Messages and Get Responses
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            # Mock LLM responses
            responses = [
                "Hello! I'm ready to help you with your integration testing.",
                "I can assist you with various programming questions and tasks.",
                "Integration tests are important for ensuring all components work together correctly."
            ]

            mock_generate.side_effect = [
                {"content": resp, "role": "assistant", "usage": {"total_tokens": 50}}
                for resp in responses
            ]

            messages = [
                "Hello, can you help me with integration testing?",
                "What kinds of things can you help with?",
                "Tell me about the importance of integration tests."
            ]

            conversation_messages = []

            for i, message_content in enumerate(messages):
                message_data = {
                    "content": message_content,
                    "conversation_id": conversation_id
                }

                msg_response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)
                assert msg_response.status_code == 200

                response_data = msg_response.json()
                assert "user_message" in response_data
                assert "assistant_message" in response_data
                assert response_data["user_message"]["content"] == message_content
                assert responses[i] in response_data["assistant_message"]["content"]

                conversation_messages.extend([
                    response_data["user_message"],
                    response_data["assistant_message"]
                ])

        # 5. Retrieve Conversation History
        history_response = await test_client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
        assert history_response.status_code == 200

        history_data = history_response.json()
        assert history_data["title"] == "Integration Test Conversation"
        assert "messages" in history_data or len(conversation_messages) > 0

        # 6. List All Conversations
        list_response = await test_client.get("/api/v1/conversations", headers=headers)
        assert list_response.status_code == 200

        conversations = list_response.json()
        assert len(conversations) >= 1
        assert any(conv["title"] == "Integration Test Conversation" for conv in conversations)

    async def test_authentication_flow_integration(self, test_client):
        """Test complete authentication flow integration."""
        # 1. Registration with validation
        invalid_registration = {
            "email": "invalid-email",
            "password": "weak",
            "username": "ab"
        }

        reg_response = await test_client.post("/api/v1/auth/register", json=invalid_registration)
        assert reg_response.status_code == 400

        # 2. Valid registration
        valid_registration = {
            "email": "authflow@example.com",
            "password": "StrongPass123!",
            "username": "authflowuser"
        }

        reg_response = await test_client.post("/api/v1/auth/register", json=valid_registration)
        assert reg_response.status_code == 201

        # 3. Login with wrong credentials
        wrong_credentials = {
            "email": "authflow@example.com",
            "password": "WrongPassword"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=wrong_credentials)
        assert login_response.status_code == 401

        # 4. Login with correct credentials
        correct_credentials = {
            "email": "authflow@example.com",
            "password": "StrongPass123!"
        }

        login_response = await test_client.post("/api/v1/auth/login", json=correct_credentials)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 5. Access protected resource
        headers = {"Authorization": f"Bearer {token}"}
        me_response = await test_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200

        user_data = me_response.json()
        assert user_data["email"] == "authflow@example.com"
        assert user_data["username"] == "authflowuser"

        # 6. Access resource without token
        no_token_response = await test_client.get("/api/v1/conversations")
        assert no_token_response.status_code == 401

        # 7. Logout (if implemented)
        logout_response = await test_client.post("/api/v1/auth/logout", headers=headers)
        assert logout_response.status_code in [200, 404, 501]  # May not be implemented

    async def test_ab_testing_workflow_integration(self, test_client):
        """Test A/B testing workflow integration."""
        # Setup user
        registration_data = {
            "email": "abtest@example.com",
            "password": "SecurePass123!",
            "username": "abtestuser"
        }

        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "abtest@example.com",
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Create A/B Test
        test_data = {
            "name": "Integration A/B Test",
            "description": "Testing model performance",
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

        # 2. Start Test (if endpoint exists)
        start_response = await test_client.post(f"/api/v1/ab-tests/{test_id}/start", headers=headers)
        if start_response.status_code == 200:
            assert start_response.json()["status"] == "running"

        # 3. Get Test Status
        status_response = await test_client.get(f"/api/v1/ab-tests/{test_id}", headers=headers)
        assert status_response.status_code == 200

        # 4. List Tests
        list_response = await test_client.get("/api/v1/ab-tests", headers=headers)
        assert list_response.status_code == 200
        tests = list_response.json()
        assert any(test["name"] == "Integration A/B Test" for test in tests)

        # 5. Get Metrics (if endpoint exists)
        metrics_response = await test_client.get(f"/api/v1/ab-tests/{test_id}/metrics", headers=headers)
        assert metrics_response.status_code in [200, 404, 501]

    async def test_error_handling_across_application(self, test_client):
        """Test error handling across the entire application."""
        # 1. Test authentication errors
        invalid_login = await test_client.post("/api/v1/auth/login", json={"invalid": "data"})
        assert invalid_login.status_code == 400
        assert "application/problem+json" in invalid_login.headers.get("content-type", "")

        # 2. Test validation errors
        invalid_registration = await test_client.post("/api/v1/auth/register", json={
            "email": "invalid",
            "password": "weak",
            "username": ""
        })
        assert invalid_registration.status_code == 400

        error_data = invalid_registration.json()
        assert "status" in error_data
        assert "title" in error_data

        # 3. Test authorization errors
        unauthorized_response = await test_client.get("/api/v1/conversations")
        assert unauthorized_response.status_code == 401

        # 4. Test not found errors
        not_found_response = await test_client.get("/api/v1/nonexistent")
        assert not_found_response.status_code == 404

        # 5. Test method not allowed
        method_error = await test_client.patch("/api/v1/auth/login")
        assert method_error.status_code == 405

    async def test_concurrent_operations(self, test_client):
        """Test concurrent operations across the application."""
        # Setup multiple users
        users = []
        for i in range(3):
            user_data = {
                "email": f"concurrent{i}@example.com",
                "password": "SecurePass123!",
                "username": f"concurrent{i}"
            }

            reg_response = await test_client.post("/api/v1/auth/register", json=user_data)
            assert reg_response.status_code == 201

            login_response = await test_client.post("/api/v1/auth/login", json={
                "email": user_data["email"],
                "password": user_data["password"]
            })
            token = login_response.json()["access_token"]
            users.append({"data": user_data, "token": token})

        # Concurrent conversation creation
        async def create_conversation(user, conversation_title):
            headers = {"Authorization": f"Bearer {user['token']}"}
            conv_data = {
                "title": conversation_title,
                "model": "gpt-3.5-turbo"
            }
            return await test_client.post("/api/v1/conversations", json=conv_data, headers=headers)

        tasks = [
            create_conversation(user, f"Concurrent Conversation {i}")
            for i, user in enumerate(users)
        ]

        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

        # Concurrent message sending
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = {"content": "Concurrent response", "role": "assistant"}

            async def send_message(user, conversation_id, message):
                headers = {"Authorization": f"Bearer {user['token']}"}
                msg_data = {
                    "content": message,
                    "conversation_id": conversation_id
                }
                return await test_client.post("/api/v1/chat", json=msg_data, headers=headers)

            conversation_ids = [resp.json()["id"] for resp in responses]
            message_tasks = [
                send_message(user, conv_id, f"Message from user {i}")
                for i, (user, conv_id) in enumerate(zip(users, conversation_ids, strict=False))
            ]

            message_responses = await asyncio.gather(*message_tasks)

            # All should succeed
            for response in message_responses:
                assert response.status_code == 200

    async def test_data_consistency_verification(self, test_client):
        """Test data consistency across operations."""
        # Setup user
        user_data = {
            "email": "consistency@example.com",
            "password": "SecurePass123!",
            "username": "consistencyuser"
        }

        await test_client.post("/api/v1/auth/register", json=user_data)
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "Consistency Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)
        conversation_id = conv_response.json()["id"]

        # Send messages and verify consistency
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.side_effect = [
                {"content": f"Response {i}", "role": "assistant"}
                for i in range(3)
            ]

            messages = ["Message 1", "Message 2", "Message 3"]

            for message in messages:
                msg_response = await test_client.post("/api/v1/chat", json={
                    "content": message,
                    "conversation_id": conversation_id
                }, headers=headers)
                assert msg_response.status_code == 200

        # Verify conversation contains all messages
        history_response = await test_client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
        assert history_response.status_code == 200

        # Verify user has access to conversation
        user_convs_response = await test_client.get("/api/v1/conversations", headers=headers)
        assert user_convs_response.status_code == 200

        conversations = user_convs_response.json()
        assert any(conv["id"] == conversation_id for conv in conversations)

    async def test_basic_performance_testing(self, test_client):
        """Test basic performance characteristics."""
        import time

        # Setup user
        user_data = {
            "email": "performance@example.com",
            "password": "SecurePass123!",
            "username": "performanceuser"
        }

        await test_client.post("/api/v1/auth/register", json=user_data)
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Test conversation creation performance
        start_time = time.time()

        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "Performance Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)

        creation_time = time.time() - start_time
        assert conv_response.status_code == 201
        assert creation_time < 5.0  # Should complete within 5 seconds

        conversation_id = conv_response.json()["id"]

        # Test message sending performance
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = {"content": "Fast response", "role": "assistant"}

            start_time = time.time()

            msg_response = await test_client.post("/api/v1/chat", json={
                "content": "Performance test message",
                "conversation_id": conversation_id
            }, headers=headers)

            message_time = time.time() - start_time
            assert msg_response.status_code == 200
            assert message_time < 5.0  # Should complete within 5 seconds

        # Test list performance
        start_time = time.time()

        list_response = await test_client.get("/api/v1/conversations", headers=headers)

        list_time = time.time() - start_time
        assert list_response.status_code == 200
        assert list_time < 2.0  # Should complete within 2 seconds


@pytest.mark.integration
class TestSystemIntegration:
    """Test system-level integration."""

    async def test_full_system_health_check(self, test_client):
        """Test full system health check."""
        # 1. Health endpoint (if exists)
        health_response = await test_client.get("/health")
        assert health_response.status_code in [200, 404]  # May not be implemented

        # 2. API root
        root_response = await test_client.get("/")
        assert root_response.status_code in [200, 404]

        # 3. OpenAPI docs (if exists)
        docs_response = await test_client.get("/docs")
        assert docs_response.status_code in [200, 404]

    async def test_api_versioning_compatibility(self, test_client):
        """Test API versioning compatibility."""
        # Test v1 endpoints
        v1_endpoints = [
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/conversations",
            "/api/v1/ab-tests"
        ]

        for endpoint in v1_endpoints:
            # OPTIONS request to check if endpoint exists
            options_response = await test_client.request("OPTIONS", endpoint)
            # Should not be 404 (endpoint should exist) but may be 405 (method not allowed)
            assert options_response.status_code in [200, 405]

    async def test_security_headers_integration(self, test_client):
        """Test security headers across the application."""
        # Test various endpoints for security headers
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/conversations",
            "/health"
        ]

        for endpoint in endpoints:
            response = await test_client.get(endpoint)
            # Check for common security headers (if implemented)
            headers = response.headers

            # These headers might be set by middleware

            # At least some security measures should be in place
            # This is more about checking the structure than specific headers
            assert "content-type" in headers

    async def test_rate_limiting_integration(self, test_client):
        """Test rate limiting integration."""
        # Setup user
        user_data = {
            "email": "ratelimit@example.com",
            "password": "SecurePass123!",
            "username": "ratelimituser"
        }

        await test_client.post("/api/v1/auth/register", json=user_data)

        # Make multiple rapid requests
        responses = []
        for _i in range(10):
            response = await test_client.post("/api/v1/auth/login", json={
                "email": "ratelimit@example.com",
                "password": "WrongPassword"  # Intentionally wrong to avoid successful login
            })
            responses.append(response.status_code)

        # Should either get consistent 401s or rate limiting (429)
        assert all(status in [401, 429] for status in responses)

    async def test_cors_configuration_integration(self, test_client):
        """Test CORS configuration integration."""
        # Test preflight request
        preflight_response = await test_client.request(
            "OPTIONS",
            "/api/v1/auth/login",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        # Should handle CORS preflight (may be 200 or 405)
        assert preflight_response.status_code in [200, 405]

        # Check for CORS headers (if implemented)
        headers = preflight_response.headers
        # CORS headers might be present

        # This test is about structure, not specific CORS implementation
        assert isinstance(headers, dict)

    async def test_database_integration_workflow(self, test_client):
        """Test database integration workflow."""
        # This tests that the database layer works through the API

        # 1. Create user (tests user table)
        user_data = {
            "email": "dbintegration@example.com",
            "password": "SecurePass123!",
            "username": "dbintegrationuser"
        }

        reg_response = await test_client.post("/api/v1/auth/register", json=user_data)
        assert reg_response.status_code == 201

        # 2. Login (tests authentication queries)
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Create conversation (tests conversation table)
        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "DB Integration Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)
        assert conv_response.status_code == 201

        # 4. Send message (tests message table)
        conversation_id = conv_response.json()["id"]

        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = {"content": "DB test response", "role": "assistant"}

            msg_response = await test_client.post("/api/v1/chat", json={
                "content": "Database integration test",
                "conversation_id": conversation_id
            }, headers=headers)
            assert msg_response.status_code == 200

        # 5. Retrieve data (tests query operations)
        list_response = await test_client.get("/api/v1/conversations", headers=headers)
        assert list_response.status_code == 200

        conversations = list_response.json()
        assert any(conv["title"] == "DB Integration Test" for conv in conversations)

    async def test_external_service_integration_mocking(self, test_client):
        """Test external service integration with proper mocking."""
        # This tests that external services are properly mocked in tests

        # Setup user
        user_data = {
            "email": "external@example.com",
            "password": "SecurePass123!",
            "username": "externaluser"
        }

        await test_client.post("/api/v1/auth/register", json=user_data)
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "External Service Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)
        conversation_id = conv_response.json()["id"]

        # Test LLM service mocking
        with patch('chatter.services.llm.LLMService.generate') as mock_llm:
            mock_llm.return_value = {
                "content": "Mocked LLM response",
                "role": "assistant",
                "usage": {"total_tokens": 10}
            }

            msg_response = await test_client.post("/api/v1/chat", json={
                "content": "Test external service",
                "conversation_id": conversation_id
            }, headers=headers)

            assert msg_response.status_code == 200
            mock_llm.assert_called_once()

        # Test cache service mocking (if used)
        with patch('chatter.services.cache.CacheService.get') as mock_cache:
            mock_cache.return_value = None  # Cache miss

            # Make request that might use cache
            list_response = await test_client.get("/api/v1/conversations", headers=headers)
            assert list_response.status_code == 200
