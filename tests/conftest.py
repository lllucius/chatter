"""Test configuration and fixtures for Chatter application."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


# Async event loop configuration for tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def job_queue():
    """Create a job queue instance for testing and ensure it's cleaned up."""
    from chatter.services.job_queue import AdvancedJobQueue

    queue = AdvancedJobQueue(max_workers=2)
    yield queue

    # Ensure cleanup to prevent hanging
    if queue.running:
        await queue.stop()


# Cleanup fixture to prevent hanging due to background services
@pytest.fixture(scope="session", autouse=True)
async def cleanup_global_services():
    """Ensure global services are stopped after tests to prevent hanging."""
    yield

    # Stop global job queue if it was started during tests
    try:
        from chatter.services.job_queue import job_queue

        if job_queue.running:
            await job_queue.stop()
    except Exception:
        # Ignore errors during cleanup
        pass


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
                "timestamp": "2024-01-01T00:00:00Z",
            }
        ],
    }


@pytest.fixture
def sample_agent_data():
    """Sample agent data for testing."""
    return {
        "id": "test-agent-id",
        "name": "Test Agent",
        "description": "A test agent for unit testing",
        "type": "conversational",
        "config": {"temperature": 0.7},
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "id": "test-conv-id",
        "title": "Test Conversation",
        "description": "A test conversation",
        "status": "active",
        "user_id": "test-user-id",
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
            "tags": ["test", "document"],
        },
    }


# Database model fixtures for testing
@pytest.fixture
def test_user():
    """Create a test user instance."""
    from chatter.models.user import User

    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password_here",
        full_name="Test User",
    )
    return user


@pytest.fixture
def test_conversation(test_user):
    """Create a test conversation instance."""
    from chatter.models.conversation import Conversation

    conversation = Conversation(
        user_id=test_user.id,
        title="Test Conversation",
        description="A test conversation",
    )
    return conversation


@pytest.fixture
def test_document(test_user):
    """Create a test document instance."""
    from chatter.models.document import Document, DocumentType

    document = Document(
        owner_id=test_user.id,
        filename="test.txt",
        original_filename="test.txt",
        file_size=100,
        file_hash="test123",
        mime_type="text/plain",
        document_type=DocumentType.TEXT,
        title="Test Document",
        content="Test content",
    )
    return document


@pytest.fixture
def test_session():
    """Create a mock test session."""
    session = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.refresh = MagicMock()
    return session
