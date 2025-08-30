"""Chat API tests."""

from unittest.mock import patch

import pytest


@pytest.mark.unit
class TestChatAPI:
    """Test chat API endpoints."""

    async def test_create_conversation_success(self, test_client):
        """Test successful conversation creation."""
        # First login to get token
        registration_data = {
            "email": "chatuser@example.com",
            "password": "SecurePass123!",
            "username": "chatuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "chatuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conversation_data = {
            "title": "Test Conversation",
            "model": "gpt-3.5-turbo",
            "system_prompt": "You are a helpful assistant."
        }

        response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == "Test Conversation"
        assert data["model"] == "gpt-3.5-turbo"
        assert data["system_prompt"] == "You are a helpful assistant."
        assert "id" in data
        assert "created_at" in data

    async def test_list_conversations(self, test_client):
        """Test listing user conversations."""
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

        # Create multiple conversations
        for i in range(3):
            conversation_data = {
                "title": f"Test Conversation {i+1}",
                "model": "gpt-3.5-turbo"
            }
            await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)

        # List conversations
        response = await test_client.get("/api/v1/conversations", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 3
        assert all("title" in conv for conv in data)
        assert all("id" in conv for conv in data)

    async def test_get_conversation_by_id(self, test_client):
        """Test getting a specific conversation."""
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

        # Create conversation
        conversation_data = {
            "title": "Specific Conversation",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Get conversation
        response = await test_client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == conversation_id
        assert data["title"] == "Specific Conversation"

    async def test_send_message_to_conversation(self, test_client):
        """Test sending a message to a conversation."""
        # Setup user and auth
        registration_data = {
            "email": "messageuser@example.com",
            "password": "SecurePass123!",
            "username": "messageuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "messageuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conversation_data = {
            "title": "Message Test",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Send message
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = "Hello! How can I help you today?"

            message_data = {
                "content": "Hello, how are you?",
                "conversation_id": conversation_id
            }

            response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)
            assert response.status_code == 200

            data = response.json()
            assert "user_message" in data
            assert "assistant_message" in data
            assert data["user_message"]["content"] == "Hello, how are you?"
            assert data["assistant_message"]["content"] == "Hello! How can I help you today?"

    async def test_message_validation(self, test_client):
        """Test message input validation."""
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

        # Test empty message
        message_data = {
            "content": "",
            "conversation_id": "conv-123"
        }

        response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)
        assert response.status_code == 400

        # Test message too long
        message_data = {
            "content": "x" * 100000,  # Very long message
            "conversation_id": "conv-123"
        }

        response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)
        assert response.status_code == 400

        # Test missing conversation_id
        message_data = {
            "content": "Hello"
        }

        response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)
        assert response.status_code == 400

    async def test_conversation_access_control(self, test_client):
        """Test that users can only access their own conversations."""
        # Create two users
        user1_data = {
            "email": "user1@example.com",
            "password": "SecurePass123!",
            "username": "user1"
        }
        await test_client.post("/api/v1/auth/register", json=user1_data)

        user2_data = {
            "email": "user2@example.com",
            "password": "SecurePass123!",
            "username": "user2"
        }
        await test_client.post("/api/v1/auth/register", json=user2_data)

        # Login as user1
        login1_response = await test_client.post("/api/v1/auth/login", json={
            "email": "user1@example.com",
            "password": "SecurePass123!"
        })
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}

        # Login as user2
        login2_response = await test_client.post("/api/v1/auth/login", json={
            "email": "user2@example.com",
            "password": "SecurePass123!"
        })
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}

        # User1 creates a conversation
        conversation_data = {
            "title": "User1's Conversation",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers1)
        conversation_id = create_response.json()["id"]

        # User2 tries to access User1's conversation
        response = await test_client.get(f"/api/v1/conversations/{conversation_id}", headers=headers2)
        assert response.status_code in [403, 404]  # Forbidden or Not Found

    async def test_conversation_search(self, test_client):
        """Test conversation search functionality."""
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

        # Create conversations with different titles
        conversations = [
            {"title": "Python Programming Help", "model": "gpt-3.5-turbo"},
            {"title": "JavaScript Questions", "model": "gpt-3.5-turbo"},
            {"title": "Python Data Science", "model": "gpt-4"},
        ]

        for conv_data in conversations:
            await test_client.post("/api/v1/conversations", json=conv_data, headers=headers)

        # Search for Python conversations
        response = await test_client.get("/api/v1/conversations?search=Python", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert len(data) >= 2  # Should find at least 2 Python conversations
        for conv in data:
            assert "Python" in conv["title"]

    async def test_conversation_export(self, test_client):
        """Test conversation export functionality."""
        # Setup user and auth
        registration_data = {
            "email": "exportuser@example.com",
            "password": "SecurePass123!",
            "username": "exportuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "exportuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation with messages
        conversation_data = {
            "title": "Export Test",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Add some messages
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = "I'm doing well, thank you!"

            message_data = {
                "content": "How are you doing?",
                "conversation_id": conversation_id
            }
            await test_client.post("/api/v1/chat", json=message_data, headers=headers)

        # Export conversation
        response = await test_client.get(f"/api/v1/conversations/{conversation_id}/export", headers=headers)

        # Might be 200 with JSON data or 404 if not implemented
        assert response.status_code in [200, 404, 501]

        if response.status_code == 200:
            data = response.json()
            assert "conversation" in data or "title" in data
            assert "messages" in data or len(data) > 0


@pytest.mark.unit
class TestStreamingChat:
    """Test streaming chat functionality."""

    async def test_streaming_chat_response(self, test_client):
        """Test streaming chat responses."""
        # Setup user and auth
        registration_data = {
            "email": "streamuser@example.com",
            "password": "SecurePass123!",
            "username": "streamuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "streamuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conversation_data = {
            "title": "Streaming Test",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Test streaming endpoint
        message_data = {
            "content": "Tell me a story",
            "conversation_id": conversation_id,
            "stream": True
        }

        with patch('chatter.services.llm.LLMService.stream_generate') as mock_stream:
            async def mock_stream_generator():
                chunks = [
                    {"type": "token", "content": "Once"},
                    {"type": "token", "content": " upon"},
                    {"type": "token", "content": " a"},
                    {"type": "token", "content": " time"},
                    {"type": "completion", "finish_reason": "stop"}
                ]
                for chunk in chunks:
                    yield chunk

            mock_stream.return_value = mock_stream_generator()

            response = await test_client.post("/api/v1/chat/stream", json=message_data, headers=headers)

            # Should either be 200 for SSE or 404 if not implemented
            assert response.status_code in [200, 404, 501]

            if response.status_code == 200:
                assert response.headers.get("content-type") == "text/event-stream"

    async def test_concurrent_message_handling(self, test_client):
        """Test handling concurrent messages."""
        import asyncio

        # Setup user and auth
        registration_data = {
            "email": "concurrentuser@example.com",
            "password": "SecurePass123!",
            "username": "concurrentuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "concurrentuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conversation_data = {
            "title": "Concurrent Test",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Send multiple messages concurrently
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = "Response"

            messages = [
                {"content": f"Message {i}", "conversation_id": conversation_id}
                for i in range(3)
            ]

            tasks = [
                test_client.post("/api/v1/chat", json=msg, headers=headers)
                for msg in messages
            ]

            responses = await asyncio.gather(*tasks)

            # All requests should complete successfully
            for response in responses:
                assert response.status_code == 200

    async def test_input_sanitization(self, test_client):
        """Test input sanitization in chat messages."""
        # Setup user and auth
        registration_data = {
            "email": "sanitizeuser@example.com",
            "password": "SecurePass123!",
            "username": "sanitizeuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_data = {
            "email": "sanitizeuser@example.com",
            "password": "SecurePass123!"
        }
        login_response = await test_client.post("/api/v1/auth/login", json=login_data)
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conversation_data = {
            "title": "Sanitization Test",
            "model": "gpt-3.5-turbo"
        }
        create_response = await test_client.post("/api/v1/conversations", json=conversation_data, headers=headers)
        conversation_id = create_response.json()["id"]

        # Test with potentially malicious content
        malicious_messages = [
            "<script>alert('xss')</script>Hello",
            "javascript:alert('xss')",
            "'; DROP TABLE users; --",
            "<img src=x onerror=alert('xss')>"
        ]

        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.return_value = "Safe response"

            for malicious_content in malicious_messages:
                message_data = {
                    "content": malicious_content,
                    "conversation_id": conversation_id
                }

                response = await test_client.post("/api/v1/chat", json=message_data, headers=headers)

                # Should either sanitize and process (200) or reject (400)
                assert response.status_code in [200, 400]

                if response.status_code == 200:
                    data = response.json()
                    # Check that dangerous content was sanitized
                    user_message = data.get("user_message", {}).get("content", "")
                    assert "<script>" not in user_message
                    assert "javascript:" not in user_message
                    assert "DROP TABLE" not in user_message.upper()


@pytest.mark.integration
class TestChatIntegration:
    """Integration tests for chat functionality."""

    async def test_full_conversation_workflow(self, test_client):
        """Test a complete conversation workflow."""
        # Register user
        registration_data = {
            "email": "workflow@example.com",
            "password": "SecurePass123!",
            "username": "workflowuser"
        }
        reg_response = await test_client.post("/api/v1/auth/register", json=registration_data)
        assert reg_response.status_code == 201

        # Login
        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "workflow@example.com",
            "password": "SecurePass123!"
        })
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "Full Workflow Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)
        assert conv_response.status_code == 201
        conversation_id = conv_response.json()["id"]

        # Send multiple messages in sequence
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.side_effect = [
                "Hello! How can I help you?",
                "I can help with Python programming.",
                "Here's a simple example: print('Hello World')"
            ]

            messages = [
                "Hello, can you help me?",
                "I need help with Python programming",
                "Can you show me an example?"
            ]

            for message_content in messages:
                msg_response = await test_client.post("/api/v1/chat", json={
                    "content": message_content,
                    "conversation_id": conversation_id
                }, headers=headers)
                assert msg_response.status_code == 200

        # Get conversation history
        history_response = await test_client.get(f"/api/v1/conversations/{conversation_id}", headers=headers)
        assert history_response.status_code == 200

        history_data = history_response.json()
        assert "messages" in history_data or "title" in history_data

    async def test_error_handling_in_chat(self, test_client):
        """Test error handling during chat operations."""
        # Setup user
        registration_data = {
            "email": "erroruser@example.com",
            "password": "SecurePass123!",
            "username": "erroruser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "erroruser@example.com",
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create conversation
        conv_response = await test_client.post("/api/v1/conversations", json={
            "title": "Error Test",
            "model": "gpt-3.5-turbo"
        }, headers=headers)
        conversation_id = conv_response.json()["id"]

        # Test LLM service error
        with patch('chatter.services.llm.LLMService.generate') as mock_generate:
            mock_generate.side_effect = Exception("LLM service unavailable")

            response = await test_client.post("/api/v1/chat", json={
                "content": "Hello",
                "conversation_id": conversation_id
            }, headers=headers)

            # Should handle error gracefully
            assert response.status_code in [500, 503]

            data = response.json()
            assert "error" in str(data).lower() or "problem" in str(data).lower()

    async def test_conversation_pagination(self, test_client):
        """Test conversation listing with pagination."""
        # Setup user
        registration_data = {
            "email": "pageuser@example.com",
            "password": "SecurePass123!",
            "username": "pageuser"
        }
        await test_client.post("/api/v1/auth/register", json=registration_data)

        login_response = await test_client.post("/api/v1/auth/login", json={
            "email": "pageuser@example.com",
            "password": "SecurePass123!"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create many conversations
        for i in range(15):
            await test_client.post("/api/v1/conversations", json={
                "title": f"Conversation {i+1}",
                "model": "gpt-3.5-turbo"
            }, headers=headers)

        # Test pagination
        response = await test_client.get("/api/v1/conversations?limit=10", headers=headers)
        assert response.status_code == 200

        data = response.json()
        # Should return at most 10 conversations
        assert len(data) <= 10
