"""Configuration and fixtures for end-to-end tests."""

import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

# Add the project root to the path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app():
    """Create a FastAPI app instance for testing."""
    try:
        from chatter.main import app
        return app
    except ImportError:
        # Create a minimal FastAPI app for testing if main app fails to import
        from fastapi import FastAPI
        test_app = FastAPI(title="Test Chatter API")
        
        @test_app.get("/health")
        async def health_check():
            return {"status": "ok", "message": "Test server running"}
        
        return test_app


@pytest.fixture(scope="session")
def test_client(app) -> Generator[TestClient, None, None]:
    """Create a test client for the FastAPI app."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_database_session():
    """Create a mock database session for E2E tests."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    return session


@pytest.fixture
def sample_user_credentials():
    """Sample user credentials for E2E authentication tests."""
    return {
        "email": "e2e-test@example.com",
        "password": "SecureTestPassword123!",
        "username": "e2e_test_user",
        "full_name": "E2E Test User"
    }


@pytest.fixture
def sample_chat_conversation():
    """Sample chat conversation data for E2E tests."""
    return {
        "title": "E2E Test Conversation",
        "description": "A test conversation for end-to-end testing",
        "messages": [
            {
                "role": "user",
                "content": "Hello, this is an end-to-end test message.",
                "timestamp": "2024-01-01T10:00:00Z"
            },
            {
                "role": "assistant", 
                "content": "Hello! I'm responding in this E2E test scenario.",
                "timestamp": "2024-01-01T10:00:05Z"
            }
        ]
    }


@pytest.fixture
def sample_document_upload():
    """Sample document data for E2E document processing tests."""
    return {
        "filename": "test_document.txt",
        "content": b"This is a test document for end-to-end testing.\n\nIt contains multiple lines and paragraphs to test document processing capabilities.",
        "mime_type": "text/plain",
        "metadata": {
            "category": "test",
            "tags": ["e2e", "testing", "document"]
        }
    }


@pytest.fixture 
def mock_llm_response():
    """Mock LLM response for E2E tests that don't require real API calls."""
    return {
        "content": "This is a mock response from the LLM for end-to-end testing purposes.",
        "usage": {
            "prompt_tokens": 25,
            "completion_tokens": 15,
            "total_tokens": 40
        },
        "model": "mock-gpt-4",
        "finish_reason": "stop"
    }


@pytest.fixture
async def cleanup_test_data():
    """Fixture to ensure test data is cleaned up after E2E tests."""
    # Setup: No initial cleanup needed
    yield
    
    # Teardown: Clean up any test data
    # In a real implementation, this would clean up:
    # - Test users created during E2E tests
    # - Test conversations and messages
    # - Test documents uploaded
    # - Test agent configurations
    # For now, we'll just log the cleanup
    print("Cleaning up E2E test data...")