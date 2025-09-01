"""Test configuration and fixtures for Chatter application."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

import pytest
from unittest.mock import AsyncMock, MagicMock

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