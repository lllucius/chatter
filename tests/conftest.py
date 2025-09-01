"""Test configuration and fixtures for Chatter application."""

import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest


# Mock required modules that may not be available in test environment
class MockModule:
    def __getattr__(self, name):
        return MagicMock()

# Mock modules that might not be available
for module_name in [
    'fastapi',
    'sqlalchemy.ext.asyncio',
    'chatter.models',
    'chatter.core',
    'chatter.services',
    'chatter.api',
    'chatter.utils',
    'chatter.schemas'
]:
    if module_name not in sys.modules:
        sys.modules[module_name] = MockModule()

# Async event loop configuration for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_session():
    """Create a mock database session for testing."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def mock_client():
    """Create a mock HTTP client for testing."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    return client


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": True,
    }


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing."""
    return {
        "id": "test-chat-id",
        "title": "Test Chat",
        "messages": [
            {
                "id": "msg-1",
                "role": "user",
                "content": "Hello, world!",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        ]
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "id": "test-agent-id",
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "type": "conversational",
        "config": {"temperature": 0.7}
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "id": "test-conv-id",
        "title": "Test Conversation",
        "description": "A test conversation",
        "status": "active",
        "user_id": "test-user-id"
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "id": "test-doc-id",
        "title": "Test Document",
        "content": "This is a test document with some content.",
        "metadata": {
            "source": "test",
            "category": "testing",
            "tags": ["test", "document"]
        }
    }
