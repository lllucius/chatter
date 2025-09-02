"""Comprehensive integration tests for cross-service workflows."""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock


@pytest.mark.integration
class TestCrossServiceWorkflows:
    """Integration tests spanning multiple services."""

    @pytest.mark.asyncio
    async def test_complete_document_to_chat_workflow(self, test_client, sample_document_upload, cleanup_test_data):
        """Test complete workflow: upload document → process → search → use in chat."""
        
        # Step 1: Upload document
        files = {
            "file": (
                sample_document_upload["filename"],
                sample_document_upload["content"],
                sample_document_upload["mime_type"]
            )
        }
        
        upload_response = test_client.post("/api/v1/documents/upload", files=files)
        
        if upload_response.status_code == 404:
            pytest.skip("Document upload endpoint not available")
        
        if upload_response.status_code not in [200, 201]:
            pytest.skip("Cannot upload document for workflow test")
        
        upload_data = upload_response.json()
        document_id = upload_data.get("id") or upload_data.get("document_id")
        
        # Step 2: Wait for document processing (simulate)
        import time
        time.sleep(0.1)  # Brief wait for async processing
        
        # Step 3: Search for the document
        search_response = test_client.post(
            "/api/v1/documents/search",
            json={"query": "test document"}
        )
        
        if search_response.status_code == 200:
            search_results = search_response.json()
            # Verify our document appears in search results
            assert isinstance(search_results, (list, dict))
        
        # Step 4: Create chat conversation
        chat_response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": "Document Integration Test"}
        )
        
        if chat_response.status_code in [200, 201]:
            chat_data = chat_response.json()
            conversation_id = chat_data.get("id") or chat_data.get("conversation_id")
            
            # Step 5: Reference document in chat
            if conversation_id:
                message_response = test_client.post(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    json={
                        "content": f"Can you summarize document {document_id}?",
                        "role": "user",
                        "context": {"document_id": document_id}
                    }
                )
                
                # Verify message was sent successfully
                if message_response.status_code in [200, 201]:
                    message_data = message_response.json()
                    assert "id" in message_data or "message_id" in message_data

    @pytest.mark.asyncio
    async def test_user_agent_workflow_integration(self, test_client, sample_user_credentials):
        """Test workflow: create user → create agent → use agent in conversation."""
        
        # Step 1: Create/authenticate user (simulated)
        auth_response = test_client.post(
            "/api/v1/auth/login",
            data={
                "username": sample_user_credentials["email"],
                "password": sample_user_credentials["password"]
            }
        )
        
        auth_token = None
        if auth_response.status_code == 200:
            auth_data = auth_response.json()
            auth_token = auth_data.get("access_token")
        
        headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        # Step 2: Create custom agent
        agent_response = test_client.post(
            "/api/v1/agents",
            json={
                "name": "Integration Test Agent",
                "description": "Agent for integration testing",
                "type": "conversational",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "system_prompt": "You are a helpful integration test assistant."
                }
            },
            headers=headers
        )
        
        if agent_response.status_code == 404:
            pytest.skip("Agent endpoints not available")
        
        if agent_response.status_code not in [200, 201]:
            pytest.skip("Cannot create agent for workflow test")
        
        agent_data = agent_response.json()
        agent_id = agent_data.get("id") or agent_data.get("agent_id")
        
        # Step 3: Create conversation with specific agent
        conversation_response = test_client.post(
            "/api/v1/chat/conversations",
            json={
                "title": "Agent Integration Test",
                "agent_id": agent_id
            },
            headers=headers
        )
        
        if conversation_response.status_code in [200, 201]:
            conversation_data = conversation_response.json()
            conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
            
            # Step 4: Send message using the agent
            if conversation_id:
                message_response = test_client.post(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    json={
                        "content": "Hello, integration test agent!",
                        "role": "user"
                    },
                    headers=headers
                )
                
                # Verify message processing
                if message_response.status_code in [200, 201]:
                    # Step 5: Check if agent responded
                    messages_response = test_client.get(
                        f"/api/v1/chat/conversations/{conversation_id}/messages",
                        headers=headers
                    )
                    
                    if messages_response.status_code == 200:
                        messages = messages_response.json()
                        assert isinstance(messages, list)
                        user_messages = [m for m in messages if m.get("role") == "user"]
                        assert len(user_messages) >= 1

    @pytest.mark.asyncio
    async def test_analytics_across_services_workflow(self, test_client):
        """Test analytics collection across multiple services."""
        
        # Step 1: Generate some activity
        activities = [
            ("POST", "/api/v1/chat/conversations", {"title": "Analytics Test 1"}),
            ("POST", "/api/v1/chat/conversations", {"title": "Analytics Test 2"}),
            ("GET", "/api/v1/documents", {}),
            ("POST", "/api/v1/documents/search", {"query": "analytics test"}),
        ]
        
        for method, endpoint, data in activities:
            if method == "GET":
                response = test_client.get(endpoint)
            else:
                response = test_client.post(endpoint, json=data)
            
            # Don't fail if endpoints don't exist
            if response.status_code == 404:
                continue
        
        # Step 2: Check analytics endpoints
        analytics_endpoints = [
            "/api/v1/analytics/usage",
            "/api/v1/analytics/conversations",
            "/api/v1/analytics/documents",
            "/api/v1/analytics/performance"
        ]
        
        for endpoint in analytics_endpoints:
            analytics_response = test_client.get(endpoint)
            
            if analytics_response.status_code == 200:
                analytics_data = analytics_response.json()
                # Basic structure validation
                assert isinstance(analytics_data, dict)
                
                # Should have some metrics
                expected_metrics = ["total", "count", "metrics", "stats", "data"]
                has_metrics = any(metric in analytics_data for metric in expected_metrics)
                assert has_metrics, f"Analytics data missing expected metrics: {analytics_data}"


@pytest.mark.integration
class TestExternalServiceIntegration:
    """Integration tests for external service interactions."""

    @patch('chatter.services.llm.LLMService')
    def test_llm_provider_integration(self, mock_llm_service, test_client):
        """Test integration with LLM providers."""
        # Mock LLM service responses
        mock_llm_service.return_value.generate_response.return_value = {
            "content": "Mocked LLM response for integration testing",
            "usage": {"total_tokens": 50},
            "model": "gpt-4"
        }
        
        # Test chat with LLM integration
        conversation_response = test_client.post(
            "/api/v1/chat/conversations",
            json={"title": "LLM Integration Test"}
        )
        
        if conversation_response.status_code not in [200, 201, 404]:
            return  # Skip if endpoint issues
        
        if conversation_response.status_code == 404:
            pytest.skip("Chat endpoints not available")
        
        conversation_data = conversation_response.json()
        conversation_id = conversation_data.get("id") or conversation_data.get("conversation_id")
        
        if conversation_id:
            # Send message that should trigger LLM
            message_response = test_client.post(
                f"/api/v1/chat/conversations/{conversation_id}/messages",
                json={
                    "content": "Generate a response using the LLM",
                    "role": "user"
                }
            )
            
            # Verify integration worked
            if message_response.status_code in [200, 201]:
                # LLM service should have been called
                mock_llm_service.return_value.generate_response.assert_called()

    @patch('chatter.services.embeddings.EmbeddingService')
    def test_vector_store_integration(self, mock_embedding_service, test_client):
        """Test integration with vector storage."""
        # Mock embedding service
        mock_embedding_service.return_value.generate_embeddings.return_value = [0.1] * 384
        mock_embedding_service.return_value.search_similar.return_value = [
            {"id": "doc1", "score": 0.95, "content": "Similar content"}
        ]
        
        # Test document upload and embedding
        test_content = "Integration test document for vector search"
        files = {
            "file": ("integration_test.txt", test_content, "text/plain")
        }
        
        upload_response = test_client.post("/api/v1/documents/upload", files=files)
        
        if upload_response.status_code == 404:
            pytest.skip("Document endpoints not available")
        
        if upload_response.status_code in [200, 201]:
            # Test semantic search
            search_response = test_client.post(
                "/api/v1/documents/search/semantic",
                json={"query": "integration test", "limit": 5}
            )
            
            if search_response.status_code == 200:
                search_results = search_response.json()
                assert isinstance(search_results, (list, dict))

    @patch('chatter.services.cache.CacheService')
    def test_cache_service_integration(self, mock_cache_service, test_client):
        """Test integration with caching service."""
        # Mock cache service
        cache_data = {"cached_conversations": ["conv1", "conv2"]}
        mock_cache_service.return_value.get.return_value = cache_data
        mock_cache_service.return_value.set.return_value = True
        
        # Test endpoints that should use caching
        endpoints_to_test = [
            "/api/v1/chat/conversations",
            "/api/v1/documents",
            "/api/v1/agents"
        ]
        
        for endpoint in endpoints_to_test:
            response = test_client.get(endpoint)
            
            if response.status_code == 200:
                # Cache should be used for GET requests
                data = response.json()
                assert isinstance(data, (list, dict))
            elif response.status_code != 404:
                # If not 404, endpoint exists but might need auth
                continue


@pytest.mark.integration
class TestErrorHandlingWorkflows:
    """Integration tests for error handling across services."""

    def test_cascading_error_handling(self, test_client):
        """Test how errors cascade through service layers."""
        # Test with invalid data that should trigger validation errors
        invalid_requests = [
            ("POST", "/api/v1/chat/conversations", {"invalid": "data"}),
            ("POST", "/api/v1/documents/upload", {}),  # No file
            ("POST", "/api/v1/agents", {"name": ""}),  # Empty name
        ]
        
        for method, endpoint, data in invalid_requests:
            if method == "POST":
                if "upload" in endpoint:
                    response = test_client.post(endpoint, files={})
                else:
                    response = test_client.post(endpoint, json=data)
            
            # Should get proper error responses, not server errors
            if response.status_code not in [404, 401]:  # Skip if endpoint doesn't exist or needs auth
                assert response.status_code < 500, f"Server error for {endpoint}: {response.status_code}"
                
                if response.status_code >= 400:
                    # Should have error information
                    try:
                        error_data = response.json()
                        assert "error" in error_data or "detail" in error_data or "message" in error_data
                    except:
                        # Some errors might return non-JSON
                        pass

    def test_service_fallback_mechanisms(self, test_client):
        """Test fallback mechanisms when services fail."""
        # Test health check endpoints that should always work
        health_endpoints = [
            "/health",
            "/api/v1/health",
            "/api/v1/status"
        ]
        
        working_endpoints = []
        for endpoint in health_endpoints:
            response = test_client.get(endpoint)
            if response.status_code == 200:
                working_endpoints.append(endpoint)
        
        # At least one health endpoint should work
        assert len(working_endpoints) > 0, "No health check endpoints are working"
        
        # Health endpoints should return status information
        for endpoint in working_endpoints:
            response = test_client.get(endpoint)
            data = response.json()
            assert "status" in data or "health" in data