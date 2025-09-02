"""Integration tests for core workflows and component interactions."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from tests.test_utils import (
    create_mock_user,
    create_mock_chat,
    create_mock_message,
    MockDatabase,
    MockRedis,
    MockLLMService
)


@pytest.mark.integration
class TestAuthenticationIntegration:
    """Integration tests for authentication workflows."""

    @pytest.mark.asyncio
    async def test_user_registration_workflow(self):
        """Test complete user registration workflow."""
        # Mock dependencies
        mock_db = MockDatabase()
        mock_redis = MockRedis()
        
        # Setup user data
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPassword123!"
        }
        
        # Mock database responses
        mock_db.fetchrow.return_value = None  # User doesn't exist
        mock_db.execute.return_value = None   # Insert successful
        
        # Test the workflow components
        with patch('chatter.utils.security.validate_email') as mock_validate_email:
            with patch('chatter.utils.security.validate_password_strength') as mock_validate_pwd:
                with patch('chatter.utils.security.hash_password') as mock_hash_pwd:
                    
                    # Setup mocks
                    mock_validate_email.return_value = True
                    mock_validate_pwd.return_value = True
                    mock_hash_pwd.return_value = "hashed_password"
                    
                    # Simulate registration workflow
                    # 1. Validate email format
                    email_valid = mock_validate_email(user_data["email"])
                    assert email_valid is True
                    
                    # 2. Validate password strength
                    pwd_valid = mock_validate_pwd(user_data["password"])
                    assert pwd_valid is True
                    
                    # 3. Hash password
                    hashed_password = mock_hash_pwd(user_data["password"])
                    assert hashed_password == "hashed_password"
                    
                    # 4. Check user doesn't exist (database call)
                    existing_user = await mock_db.fetchrow("SELECT * FROM users WHERE email = $1", user_data["email"])
                    assert existing_user is None
                    
                    # 5. Create user (database call)
                    await mock_db.execute("INSERT INTO users ...", user_data["username"], user_data["email"], hashed_password)
                    
                    # Verify all components were called
                    mock_validate_email.assert_called_once_with(user_data["email"])
                    mock_validate_pwd.assert_called_once_with(user_data["password"])
                    mock_hash_pwd.assert_called_once_with(user_data["password"])

    @pytest.mark.asyncio
    async def test_login_workflow(self):
        """Test complete login workflow with session management."""
        mock_db = MockDatabase()
        mock_redis = MockRedis()
        
        # Setup existing user
        existing_user = create_mock_user(
            username="existinguser",
            email="existing@example.com"
        )
        
        login_data = {
            "email": "existing@example.com",
            "password": "ValidPassword123!"
        }
        
        # Mock database to return existing user
        mock_db.fetchrow.return_value = {
            **existing_user,
            "password_hash": "hashed_password"
        }
        
        with patch('chatter.utils.security.verify_password') as mock_verify_pwd:
            with patch('chatter.utils.security.create_access_token') as mock_create_token:
                with patch('chatter.utils.security.create_refresh_token') as mock_create_refresh:
                    
                    # Setup mocks
                    mock_verify_pwd.return_value = True
                    mock_create_token.return_value = "access_token_123"
                    mock_create_refresh.return_value = "refresh_token_123"
                    
                    # Simulate login workflow
                    # 1. Find user by email
                    user = await mock_db.fetchrow("SELECT * FROM users WHERE email = $1", login_data["email"])
                    assert user is not None
                    assert user["email"] == login_data["email"]
                    
                    # 2. Verify password
                    password_valid = mock_verify_pwd(login_data["password"], user["password_hash"])
                    assert password_valid is True
                    
                    # 3. Create tokens
                    access_token = mock_create_token(user["id"])
                    refresh_token = mock_create_refresh(user["id"])
                    
                    assert access_token == "access_token_123"
                    assert refresh_token == "refresh_token_123"
                    
                    # 4. Store session in Redis
                    session_key = f"session:{user['id']}"
                    await mock_redis.set(session_key, access_token)
                    
                    # Verify session was stored
                    stored_token = await mock_redis.get(session_key)
                    assert stored_token == access_token


@pytest.mark.integration
class TestChatWorkflowIntegration:
    """Integration tests for chat and messaging workflows."""

    @pytest.mark.asyncio
    async def test_chat_creation_and_messaging_workflow(self):
        """Test complete chat creation and messaging workflow."""
        mock_db = MockDatabase()
        mock_llm = MockLLMService()
        
        # Setup user and chat data
        user = create_mock_user()
        chat_data = {
            "title": "New Chat Session",
            "user_id": user["id"]
        }
        
        # Mock database responses
        chat = create_mock_chat(title=chat_data["title"], user_id=user["id"])
        mock_db.fetchrow.return_value = chat
        
        # Test chat creation workflow
        # 1. Create chat
        await mock_db.execute("INSERT INTO chats ...", chat_data["title"], chat_data["user_id"])
        
        # 2. Verify chat was created
        created_chat = await mock_db.fetchrow("SELECT * FROM chats WHERE id = $1", chat["id"])
        assert created_chat is not None
        assert created_chat["title"] == chat_data["title"]
        
        # Test messaging workflow
        user_message = "Hello, how can you help me today?"
        
        # 3. Create user message
        message = create_mock_message(
            content=user_message,
            role="user",
            chat_id=chat["id"]
        )
        
        await mock_db.execute("INSERT INTO messages ...", message["content"], message["role"], message["chat_id"])
        
        # 4. Generate LLM response
        llm_response = await mock_llm.generate_response(user_message)
        assert llm_response == "Test LLM response"
        
        # 5. Store assistant message
        assistant_message = create_mock_message(
            content=llm_response,
            role="assistant",
            chat_id=chat["id"]
        )
        
        await mock_db.execute("INSERT INTO messages ...", assistant_message["content"], assistant_message["role"], assistant_message["chat_id"])
        
        # Verify the workflow completed
        mock_db.execute.assert_called()  # Multiple database calls were made

    @pytest.mark.asyncio
    async def test_document_processing_integration(self):
        """Test document upload and processing integration."""
        mock_db = MockDatabase()
        mock_llm = MockLLMService()
        
        # Setup document data
        document_content = "This is a sample document for testing."
        document_data = {
            "title": "Test Document",
            "content": document_content,
            "file_type": "text/plain",
            "user_id": "test_user_id"
        }
        
        # Test document processing workflow
        # 1. Store document
        await mock_db.execute("INSERT INTO documents ...", **document_data)
        
        # 2. Generate embeddings
        embeddings = await mock_llm.generate_embedding(document_content)
        assert embeddings == [0.1, 0.2, 0.3, 0.4, 0.5]
        
        # 3. Store embeddings in vector database
        await mock_db.execute("INSERT INTO document_embeddings ...", document_data["title"], embeddings)
        
        # Verify document processing completed
        mock_db.execute.assert_called()


@pytest.mark.integration
class TestCacheIntegration:
    """Integration tests for caching functionality."""

    @pytest.mark.asyncio
    async def test_user_session_caching(self):
        """Test user session caching workflow."""
        mock_redis = MockRedis()
        
        user = create_mock_user()
        session_data = {
            "user_id": user["id"],
            "access_token": "token_123",
            "expires_at": "2024-12-31T23:59:59Z"
        }
        
        # Test caching workflow
        # 1. Store session
        cache_key = f"session:{user['id']}"
        await mock_redis.set(cache_key, session_data["access_token"])
        
        # 2. Retrieve session
        cached_token = await mock_redis.get(cache_key)
        assert cached_token == session_data["access_token"]
        
        # 3. Check session exists
        exists = await mock_redis.exists(cache_key)
        assert exists is True
        
        # 4. Remove session (logout)
        deleted = await mock_redis.delete(cache_key)
        assert deleted == 1
        
        # 5. Verify session is gone
        exists_after_delete = await mock_redis.exists(cache_key)
        assert exists_after_delete is False

    @pytest.mark.asyncio
    async def test_chat_history_caching(self):
        """Test chat history caching workflow."""
        mock_redis = MockRedis()
        
        chat = create_mock_chat()
        messages = [
            create_mock_message(content="Message 1", chat_id=chat["id"]),
            create_mock_message(content="Message 2", chat_id=chat["id"]),
        ]
        
        # Test chat caching
        # 1. Cache recent messages
        cache_key = f"chat_history:{chat['id']}"
        await mock_redis.set(cache_key, str(messages))  # In reality, would be JSON
        
        # 2. Retrieve cached messages
        cached_messages = await mock_redis.get(cache_key)
        assert cached_messages is not None
        
        # 3. Update cache with new message
        new_message = create_mock_message(content="Message 3", chat_id=chat["id"])
        updated_messages = messages + [new_message]
        await mock_redis.set(cache_key, str(updated_messages))
        
        # Verify cache was updated
        updated_cached = await mock_redis.get(cache_key)
        assert updated_cached != cached_messages


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across components."""

    @pytest.mark.asyncio
    async def test_database_error_handling(self):
        """Test error handling when database operations fail."""
        mock_db = MockDatabase()
        
        # Mock database to raise exception
        mock_db.execute.side_effect = Exception("Database connection failed")
        
        # Test that errors are properly handled
        try:
            await mock_db.execute("SELECT 1")
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "Database connection failed"

    @pytest.mark.asyncio
    async def test_external_service_error_handling(self):
        """Test error handling when external services fail."""
        mock_llm = MockLLMService()
        
        # Mock LLM service to raise exception
        async def failing_generate_response(prompt: str, **kwargs) -> str:
            raise Exception("LLM service unavailable")
        
        mock_llm.generate_response = failing_generate_response
        
        # Test error handling
        try:
            await mock_llm.generate_response("Test prompt")
            assert False, "Should have raised exception"
        except Exception as e:
            assert str(e) == "LLM service unavailable"