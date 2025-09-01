"""Integration tests for workflow and API chains."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock

from chatter.main import app


@pytest.mark.integration
class TestWorkflowIntegration:
    """Integration tests for end-to-end workflow functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_document_processing_workflow(self):
        """Test complete document processing workflow."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Step 1: Upload document
            with patch('chatter.api.documents.get_document_service') as mock_doc_service:
                mock_service = AsyncMock()
                mock_service.upload_document.return_value = {
                    "id": "doc-123",
                    "filename": "test.pdf",
                    "status": "uploaded",
                    "size": 1024
                }
                mock_doc_service.return_value = mock_service
                
                upload_response = self.client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.pdf", b"fake pdf content", "application/pdf")},
                    headers=headers
                )
                assert upload_response.status_code == 201
                document_id = upload_response.json()["id"]
                
                # Step 2: Process document
                mock_service.process_document.return_value = {
                    "document_id": document_id,
                    "status": "processing",
                    "task_id": "task-456"
                }
                
                process_response = self.client.post(
                    f"/api/v1/documents/{document_id}/process",
                    headers=headers
                )
                assert process_response.status_code == 200
                
                # Step 3: Check processing status
                mock_service.get_processing_status.return_value = {
                    "document_id": document_id,
                    "status": "completed",
                    "extracted_text": "Sample document content",
                    "embeddings_created": True
                }
                
                status_response = self.client.get(
                    f"/api/v1/documents/{document_id}/status",
                    headers=headers
                )
                assert status_response.status_code == 200
                assert status_response.json()["status"] == "completed"

    def test_chat_conversation_workflow(self):
        """Test complete chat conversation workflow."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Step 1: Create conversation
            with patch('chatter.api.chat.get_chat_service') as mock_chat_service:
                mock_service = AsyncMock()
                mock_service.create_conversation.return_value = {
                    "id": "conv-123",
                    "title": "Test Conversation",
                    "user_id": "user-123",
                    "created_at": "2024-01-01T00:00:00Z"
                }
                mock_chat_service.return_value = mock_service
                
                create_response = self.client.post(
                    "/api/v1/chat/conversations",
                    json={"title": "Test Conversation"},
                    headers=headers
                )
                assert create_response.status_code == 201
                conversation_id = create_response.json()["id"]
                
                # Step 2: Send message
                mock_service.send_message.return_value = {
                    "id": "msg-123",
                    "conversation_id": conversation_id,
                    "content": "Hello, how can you help me?",
                    "role": "user",
                    "timestamp": "2024-01-01T00:01:00Z"
                }
                
                mock_service.process_message.return_value = {
                    "id": "msg-124",
                    "conversation_id": conversation_id,
                    "content": "I can help you with various tasks. What would you like to know?",
                    "role": "assistant",
                    "timestamp": "2024-01-01T00:01:05Z"
                }
                
                message_response = self.client.post(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    json={"content": "Hello, how can you help me?"},
                    headers=headers
                )
                assert message_response.status_code == 201
                
                # Step 3: Get conversation history
                mock_service.get_conversation_messages.return_value = {
                    "messages": [
                        {
                            "id": "msg-123",
                            "content": "Hello, how can you help me?",
                            "role": "user"
                        },
                        {
                            "id": "msg-124", 
                            "content": "I can help you with various tasks. What would you like to know?",
                            "role": "assistant"
                        }
                    ],
                    "total": 2
                }
                
                history_response = self.client.get(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    headers=headers
                )
                assert history_response.status_code == 200
                assert len(history_response.json()["messages"]) == 2

    def test_agent_interaction_workflow(self):
        """Test complete agent interaction workflow."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Step 1: Create agent
            with patch('chatter.api.agents.get_agent_manager') as mock_agent_manager:
                mock_manager = AsyncMock()
                mock_manager.create_agent.return_value = {
                    "id": "agent-123",
                    "name": "Test Agent",
                    "type": "chat",
                    "status": "active"
                }
                mock_agent_manager.return_value = mock_manager
                
                create_response = self.client.post(
                    "/api/v1/agents/",
                    json={
                        "name": "Test Agent",
                        "type": "chat",
                        "capabilities": ["text_generation"]
                    },
                    headers=headers
                )
                assert create_response.status_code == 201
                agent_id = create_response.json()["id"]
                
                # Step 2: Interact with agent
                mock_manager.interact_with_agent.return_value = {
                    "response": "Hello! I'm a test agent ready to help.",
                    "metadata": {
                        "response_time": 1.23,
                        "tokens_used": 25
                    }
                }
                
                interact_response = self.client.post(
                    f"/api/v1/agents/{agent_id}/interact",
                    json={"message": "Hello agent!"},
                    headers=headers
                )
                assert interact_response.status_code == 200
                assert "Hello! I'm a test agent" in interact_response.json()["response"]
                
                # Step 3: Get agent stats
                mock_manager.get_agent_stats.return_value = {
                    "agent_id": agent_id,
                    "total_interactions": 1,
                    "avg_response_time": 1.23,
                    "success_rate": 1.0
                }
                
                stats_response = self.client.get(
                    f"/api/v1/agents/{agent_id}/stats",
                    headers=headers
                )
                assert stats_response.status_code == 200
                assert stats_response.json()["total_interactions"] == 1

    def test_analytics_monitoring_workflow(self):
        """Test analytics and monitoring workflow."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-123", "username": "admin", "role": "admin"}
            
            # Step 1: Generate some activity (simulated)
            with patch('chatter.api.analytics.get_analytics_service') as mock_analytics:
                mock_service = AsyncMock()
                
                # Step 2: Check conversation analytics
                mock_service.get_conversation_stats.return_value = {
                    "total_conversations": 10,
                    "active_conversations": 3,
                    "avg_response_time": 1.5
                }
                
                conv_response = self.client.get(
                    "/api/v1/analytics/conversations",
                    headers=headers
                )
                assert conv_response.status_code == 200
                
                # Step 3: Check performance metrics
                mock_service.get_performance_metrics.return_value = {
                    "avg_response_time": 1.2,
                    "throughput_requests_per_second": 25.0,
                    "error_rate": 0.01
                }
                mock_analytics.return_value = mock_service
                
                perf_response = self.client.get(
                    "/api/v1/analytics/performance",
                    headers=headers
                )
                assert perf_response.status_code == 200
                
                # Step 4: Check system health
                mock_service.get_system_analytics.return_value = {
                    "system_health": "healthy",
                    "uptime_seconds": 3600,
                    "service_status": {"database": "healthy", "redis": "healthy"}
                }
                
                system_response = self.client.get(
                    "/api/v1/analytics/system",
                    headers=headers
                )
                assert system_response.status_code == 200
                assert system_response.json()["system_health"] == "healthy"

    def test_error_handling_workflow(self):
        """Test error handling across different API endpoints."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Test 1: Document service error
            with patch('chatter.api.documents.get_document_service') as mock_doc_service:
                mock_service = AsyncMock()
                mock_service.upload_document.side_effect = Exception("Storage service unavailable")
                mock_doc_service.return_value = mock_service
                
                upload_response = self.client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("test.pdf", b"content", "application/pdf")},
                    headers=headers
                )
                assert upload_response.status_code == 500
            
            # Test 2: Chat service error
            with patch('chatter.api.chat.get_chat_service') as mock_chat_service:
                mock_service = AsyncMock()
                mock_service.create_conversation.side_effect = Exception("Database connection failed")
                mock_chat_service.return_value = mock_service
                
                chat_response = self.client.post(
                    "/api/v1/chat/conversations",
                    json={"title": "Test"},
                    headers=headers
                )
                assert chat_response.status_code == 500
            
            # Test 3: Agent service error
            with patch('chatter.api.agents.get_agent_manager') as mock_agent_manager:
                mock_manager = AsyncMock()
                mock_manager.create_agent.side_effect = Exception("Configuration error")
                mock_agent_manager.return_value = mock_manager
                
                agent_response = self.client.post(
                    "/api/v1/agents/",
                    json={"name": "Test Agent", "type": "chat"},
                    headers=headers
                )
                assert agent_response.status_code == 500

    def test_concurrent_operations_workflow(self):
        """Test concurrent operations across multiple endpoints."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Setup mocks for concurrent operations
            with patch('chatter.api.documents.get_document_service') as mock_doc_service, \
                 patch('chatter.api.chat.get_chat_service') as mock_chat_service, \
                 patch('chatter.api.agents.get_agent_manager') as mock_agent_manager:
                
                # Mock responses
                mock_doc_service.return_value = AsyncMock()
                mock_doc_service.return_value.upload_document.return_value = {"id": "doc-1", "status": "uploaded"}
                
                mock_chat_service.return_value = AsyncMock()
                mock_chat_service.return_value.create_conversation.return_value = {"id": "conv-1", "title": "Test"}
                
                mock_agent_manager.return_value = AsyncMock()
                mock_agent_manager.return_value.create_agent.return_value = {"id": "agent-1", "name": "Test Agent"}
                
                # Execute concurrent requests
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                    # Submit concurrent requests
                    doc_future = executor.submit(
                        self.client.post,
                        "/api/v1/documents/upload",
                        files={"file": ("test1.pdf", b"content1", "application/pdf")},
                        headers=headers
                    )
                    
                    chat_future = executor.submit(
                        self.client.post,
                        "/api/v1/chat/conversations",
                        json={"title": "Concurrent Test"},
                        headers=headers
                    )
                    
                    agent_future = executor.submit(
                        self.client.post,
                        "/api/v1/agents/",
                        json={"name": "Concurrent Agent", "type": "chat"},
                        headers=headers
                    )
                    
                    # Wait for all requests to complete
                    doc_response = doc_future.result()
                    chat_response = chat_future.result()
                    agent_response = agent_future.result()
                
                # Assert all requests succeeded
                assert doc_response.status_code == 201
                assert chat_response.status_code == 201  
                assert agent_response.status_code == 201


@pytest.mark.integration
class TestAPIChainIntegration:
    """Integration tests for chained API operations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)

    def test_document_to_chat_workflow(self):
        """Test workflow from document upload to chat interaction."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Chain: Upload document → Process → Create chat → Ask about document
            with patch('chatter.api.documents.get_document_service') as mock_doc_service, \
                 patch('chatter.api.chat.get_chat_service') as mock_chat_service:
                
                # Step 1: Upload and process document
                mock_doc_service.return_value = AsyncMock()
                mock_doc_service.return_value.upload_document.return_value = {
                    "id": "doc-123", "filename": "research.pdf", "status": "uploaded"
                }
                mock_doc_service.return_value.process_document.return_value = {
                    "document_id": "doc-123", "status": "completed", "extracted_text": "Research findings..."
                }
                
                upload_response = self.client.post(
                    "/api/v1/documents/upload",
                    files={"file": ("research.pdf", b"research content", "application/pdf")},
                    headers=headers
                )
                document_id = upload_response.json()["id"]
                
                process_response = self.client.post(
                    f"/api/v1/documents/{document_id}/process",
                    headers=headers
                )
                assert process_response.status_code == 200
                
                # Step 2: Create conversation about the document
                mock_chat_service.return_value = AsyncMock()
                mock_chat_service.return_value.create_conversation.return_value = {
                    "id": "conv-123", "title": "Document Discussion", "context": {"document_id": document_id}
                }
                
                chat_response = self.client.post(
                    "/api/v1/chat/conversations",
                    json={"title": "Document Discussion", "context": {"document_id": document_id}},
                    headers=headers
                )
                conversation_id = chat_response.json()["id"]
                
                # Step 3: Ask question about the document
                mock_chat_service.return_value.send_message.return_value = {
                    "id": "msg-123", "content": "What are the key findings?", "role": "user"
                }
                mock_chat_service.return_value.process_message.return_value = {
                    "id": "msg-124", 
                    "content": "Based on the document, the key findings are...",
                    "role": "assistant",
                    "sources": [{"document_id": document_id, "page": 1}]
                }
                
                message_response = self.client.post(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    json={"content": "What are the key findings in the research document?"},
                    headers=headers
                )
                
                assert message_response.status_code == 201
                # Should reference the uploaded document
                response_data = message_response.json()
                assert "key findings" in response_data["content"].lower()

    def test_agent_creation_to_interaction_chain(self):
        """Test chain from agent creation to interaction and monitoring."""
        headers = {"Authorization": "Bearer integration-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "user-123", "username": "testuser"}
            
            # Chain: Create agent → Configure → Interact → Monitor performance
            with patch('chatter.api.agents.get_agent_manager') as mock_agent_manager, \
                 patch('chatter.api.analytics.get_analytics_service') as mock_analytics:
                
                mock_manager = AsyncMock()
                mock_agent_manager.return_value = mock_manager
                
                # Step 1: Create specialized agent
                mock_manager.create_agent.return_value = {
                    "id": "agent-123",
                    "name": "Research Assistant",
                    "type": "research",
                    "capabilities": ["document_analysis", "summarization"]
                }
                
                create_response = self.client.post(
                    "/api/v1/agents/",
                    json={
                        "name": "Research Assistant",
                        "type": "research", 
                        "capabilities": ["document_analysis", "summarization"],
                        "model_config": {"temperature": 0.3}
                    },
                    headers=headers
                )
                agent_id = create_response.json()["id"]
                
                # Step 2: Multiple interactions
                interactions = [
                    "Analyze this research paper",
                    "Summarize the methodology section",
                    "What are the limitations mentioned?"
                ]
                
                for i, query in enumerate(interactions):
                    mock_manager.interact_with_agent.return_value = {
                        "response": f"Analysis result for query {i+1}: {query}",
                        "metadata": {"tokens_used": 50 + i*10, "response_time": 1.0 + i*0.1}
                    }
                    
                    interact_response = self.client.post(
                        f"/api/v1/agents/{agent_id}/interact",
                        json={"message": query},
                        headers=headers
                    )
                    assert interact_response.status_code == 200
                
                # Step 3: Monitor agent performance
                mock_manager.get_agent_stats.return_value = {
                    "agent_id": agent_id,
                    "total_interactions": 3,
                    "avg_response_time": 1.1,
                    "success_rate": 1.0,
                    "total_tokens_used": 180
                }
                
                stats_response = self.client.get(
                    f"/api/v1/agents/{agent_id}/stats",
                    headers=headers
                )
                
                assert stats_response.status_code == 200
                stats = stats_response.json()
                assert stats["total_interactions"] == 3
                assert stats["success_rate"] == 1.0

    def test_multi_user_collaboration_workflow(self):
        """Test multi-user collaboration workflow."""
        # Simulate multiple users interacting with shared resources
        user1_headers = {"Authorization": "Bearer user1-token"}
        user2_headers = {"Authorization": "Bearer user2-token"}
        admin_headers = {"Authorization": "Bearer admin-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            # Setup user authentication
            def auth_side_effect(*args, **kwargs):
                auth_header = kwargs.get('headers', {}).get('Authorization', '')
                if 'user1' in auth_header:
                    return {"id": "user-1", "username": "user1", "role": "user"}
                elif 'user2' in auth_header:
                    return {"id": "user-2", "username": "user2", "role": "user"}
                else:
                    return {"id": "admin-1", "username": "admin", "role": "admin"}
            
            mock_auth.side_effect = auth_side_effect
            
            with patch('chatter.api.chat.get_chat_service') as mock_chat_service, \
                 patch('chatter.api.analytics.get_analytics_service') as mock_analytics:
                
                mock_service = AsyncMock()
                mock_chat_service.return_value = mock_service
                
                # User 1 creates a conversation
                mock_service.create_conversation.return_value = {
                    "id": "shared-conv-123", "title": "Team Discussion", "is_shared": True
                }
                
                conv_response = self.client.post(
                    "/api/v1/chat/conversations",
                    json={"title": "Team Discussion", "is_shared": True},
                    headers=user1_headers
                )
                conversation_id = conv_response.json()["id"]
                
                # User 2 joins the conversation
                mock_service.send_message.return_value = {
                    "id": "msg-1", "content": "Hi team!", "role": "user", "user_id": "user-2"
                }
                
                user2_msg_response = self.client.post(
                    f"/api/v1/chat/conversations/{conversation_id}/messages",
                    json={"content": "Hi team!"},
                    headers=user2_headers
                )
                assert user2_msg_response.status_code == 201
                
                # Admin monitors the collaboration
                mock_analytics.return_value = AsyncMock()
                mock_analytics.return_value.get_conversation_stats.return_value = {
                    "total_conversations": 1,
                    "shared_conversations": 1,
                    "total_participants": 2
                }
                
                admin_analytics_response = self.client.get(
                    "/api/v1/analytics/conversations",
                    headers=admin_headers
                )
                assert admin_analytics_response.status_code == 200

    def test_complete_system_health_monitoring_chain(self):
        """Test complete system health monitoring workflow."""
        admin_headers = {"Authorization": "Bearer admin-token"}
        
        with patch('chatter.api.auth.get_current_user') as mock_auth:
            mock_auth.return_value = {"id": "admin-1", "username": "admin", "role": "admin"}
            
            # Chain: System health → Performance metrics → Events monitoring → Alerts
            with patch('chatter.api.health.get_health_service') as mock_health_service, \
                 patch('chatter.api.analytics.get_analytics_service') as mock_analytics, \
                 patch('chatter.services.sse_events.sse_service') as mock_sse:
                
                # Step 1: Check overall system health
                health_response = self.client.get("/api/v1/health", headers=admin_headers)
                assert health_response.status_code == 200
                
                # Step 2: Get detailed performance metrics
                mock_analytics.return_value = AsyncMock()
                mock_analytics.return_value.get_performance_metrics.return_value = {
                    "avg_response_time": 1.5,
                    "error_rate": 0.02,
                    "throughput_requests_per_second": 45.0,
                    "memory_usage_mb": 512,
                    "cpu_usage_percent": 35.0
                }
                
                perf_response = self.client.get("/api/v1/analytics/performance", headers=admin_headers)
                assert perf_response.status_code == 200
                
                # Step 3: Check SSE events system
                mock_sse.get_stats.return_value = {
                    "active_connections": 15,
                    "events_per_second": 5.2,
                    "error_rate": 0.001
                }
                
                events_response = self.client.get("/api/v1/events/stats", headers=admin_headers)
                assert events_response.status_code == 200
                
                # Step 4: Verify system is healthy overall
                performance_data = perf_response.json()
                events_data = events_response.json()
                
                # System should be considered healthy
                assert performance_data["error_rate"] < 0.05
                assert events_data["error_rate"] < 0.01
                assert events_data["active_connections"] > 0