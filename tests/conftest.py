"""Pytest configuration and shared fixtures."""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock

# Configure async test mode
pytest_asyncio.default_fixture_loop_scope = "function"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = True
    return mock


@pytest.fixture
def mock_db():
    """Mock database session for testing."""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "id": "01H8X9Y9Z9",
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def sample_chat_data():
    """Sample chat data for testing."""
    return {
        "id": "01H8X9Y9Z9",
        "title": "Test Chat",
        "messages": [
            {
                "id": "01H8X9Y9Z8",
                "content": "Hello, how are you?",
                "role": "user",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            {
                "id": "01H8X9Y9Z7",
                "content": "I'm doing well, thank you!",
                "role": "assistant",
                "timestamp": "2024-01-01T00:01:00Z"
            }
        ]
    }


@pytest.fixture
def sample_document_data():
    """Sample document data for testing."""
    return {
        "id": "01H8X9Y9Z6",
        "title": "Test Document",
        "content": "This is a test document content.",
        "file_type": "text/plain",
        "size": 1024,
        "uploaded_at": "2024-01-01T00:00:00Z"
    }


# Markers for test categorization
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.e2e = pytest.mark.e2e
pytest.mark.performance = pytest.mark.performance
pytest.mark.security = pytest.mark.security