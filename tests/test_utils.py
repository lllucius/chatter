"""Test configuration and utilities shared across the test suite."""

import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Test configuration
TEST_CONFIG = {
    "database_url": os.getenv("TEST_DATABASE_URL", "sqlite:///test.db"),
    "api_base_url": os.getenv("TEST_API_URL", "http://localhost:8000"),
    "mock_external_apis": os.getenv(
        "MOCK_EXTERNAL_APIS", "true"
    ).lower()
    == "true",
    "test_timeout": int(os.getenv("TEST_TIMEOUT", "30")),
    "load_test_users": int(os.getenv("LOAD_TEST_USERS", "10")),
    "load_test_duration": int(os.getenv("LOAD_TEST_DURATION", "60")),
}


def get_test_config() -> dict[str, Any]:
    """Get test configuration settings."""
    return TEST_CONFIG.copy()


def is_integration_test_enabled() -> bool:
    """Check if integration tests should run."""
    return not os.getenv("SKIP_INTEGRATION_TESTS", "").lower() == "true"


def is_e2e_test_enabled() -> bool:
    """Check if E2E tests should run."""
    return not os.getenv("SKIP_E2E_TESTS", "").lower() == "true"


def is_load_test_enabled() -> bool:
    """Check if load tests should run."""
    return not os.getenv("SKIP_LOAD_TESTS", "").lower() == "true"


def create_mock_session() -> AsyncMock:
    """Create a mock database session for testing."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.refresh = AsyncMock()
    return session


def create_mock_client() -> AsyncMock:
    """Create a mock HTTP client for testing."""
    client = AsyncMock()
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.put = AsyncMock()
    client.delete = AsyncMock()
    client.patch = AsyncMock()
    return client


def skip_if_no_server(func):
    """Decorator to skip tests if server is not running."""

    def wrapper(*args, **kwargs):
        import requests

        try:
            response = requests.get(
                TEST_CONFIG["api_base_url"] + "/health", timeout=5
            )
            if response.status_code != 200:
                pytest.skip("Server not running or not responding")
        except requests.RequestException:
            pytest.skip("Server not accessible")
        return func(*args, **kwargs)

    return wrapper


def skip_if_no_database(func):
    """Decorator to skip tests if database is not available."""

    def wrapper(*args, **kwargs):
        if "sqlite" in TEST_CONFIG["database_url"]:
            return func(*args, **kwargs)  # SQLite should always work

        # For other databases, check connectivity
        try:
            import sqlalchemy

            engine = sqlalchemy.create_engine(
                TEST_CONFIG["database_url"]
            )
            with engine.connect():
                pass
        except Exception:
            pytest.skip("Database not available")
        return func(*args, **kwargs)

    return wrapper


class TestDataFactory:
    """Factory for creating test data."""

    @staticmethod
    def create_user_data(email: str | None = None) -> dict[str, Any]:
        """Create test user data."""
        import uuid

        user_id = str(uuid.uuid4())
        return {
            "id": user_id,
            "email": email or f"test_user_{user_id[:8]}@example.com",
            "username": f"testuser_{user_id[:8]}",
            "full_name": "Test User",
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
        }

    @staticmethod
    def create_conversation_data(
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Create test conversation data."""
        import uuid

        conv_id = str(uuid.uuid4())
        return {
            "id": conv_id,
            "title": f"Test Conversation {conv_id[:8]}",
            "description": "A test conversation for automated testing",
            "user_id": user_id or str(uuid.uuid4()),
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

    @staticmethod
    def create_message_data(
        conversation_id: str | None = None,
    ) -> dict[str, Any]:
        """Create test message data."""
        import uuid

        message_id = str(uuid.uuid4())
        return {
            "id": message_id,
            "conversation_id": conversation_id or str(uuid.uuid4()),
            "role": "user",
            "content": f"Test message content {message_id[:8]}",
            "created_at": "2024-01-01T00:00:00Z",
        }

    @staticmethod
    def create_document_data(
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        """Create test document data."""
        import uuid

        doc_id = str(uuid.uuid4())
        return {
            "id": doc_id,
            "title": f"Test Document {doc_id[:8]}",
            "filename": f"test_doc_{doc_id[:8]}.txt",
            "content": f"This is test document content for {doc_id}",
            "owner_id": owner_id or str(uuid.uuid4()),
            "file_size": 1024,
            "mime_type": "text/plain",
            "created_at": "2024-01-01T00:00:00Z",
        }

    @staticmethod
    def create_agent_data() -> dict[str, Any]:
        """Create test agent data."""
        import uuid

        agent_id = str(uuid.uuid4())
        return {
            "id": agent_id,
            "name": f"Test Agent {agent_id[:8]}",
            "description": "A test agent for automated testing",
            "type": "conversational",
            "config": {
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
            "created_at": "2024-01-01T00:00:00Z",
        }


class MockLLMService:
    """Mock LLM service for testing."""

    @staticmethod
    def generate_response(prompt: str, **kwargs) -> dict[str, Any]:
        """Generate a mock LLM response."""
        return {
            "content": f"Mock response to: {prompt[:50]}...",
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 10,
                "total_tokens": len(prompt.split()) + 10,
            },
            "model": "mock-gpt-4",
            "finish_reason": "stop",
        }


class MockEmbeddingService:
    """Mock embedding service for testing."""

    @staticmethod
    def generate_embeddings(texts: list) -> list:
        """Generate mock embeddings."""
        import random

        return [[random.random() for _ in range(384)] for _ in texts]

    @staticmethod
    def search_similar(query_embedding: list, limit: int = 10) -> list:
        """Mock similarity search."""
        return [
            {
                "id": f"doc_{i}",
                "score": 0.9 - (i * 0.1),
                "content": f"Similar document {i}",
            }
            for i in range(min(limit, 5))
        ]


# Test fixtures that can be imported
@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return get_test_config()


@pytest.fixture
def mock_llm_service():
    """Mock LLM service fixture."""
    return MockLLMService()


@pytest.fixture
def mock_embedding_service():
    """Mock embedding service fixture."""
    return MockEmbeddingService()


@pytest.fixture
def test_data_factory():
    """Test data factory fixture."""
    return TestDataFactory()


# Performance monitoring utilities
class PerformanceMonitor:
    """Monitor test performance."""

    def __init__(self):
        self.start_time = None
        self.memory_start = None

    def start(self):
        """Start monitoring."""
        import os
        import time

        import psutil

        self.start_time = time.time()
        process = psutil.Process(os.getpid())
        self.memory_start = process.memory_info().rss

    def stop(self) -> dict[str, float]:
        """Stop monitoring and return metrics."""
        import os
        import time

        import psutil

        if self.start_time is None:
            return {}

        end_time = time.time()
        process = psutil.Process(os.getpid())
        memory_end = process.memory_info().rss

        return {
            "duration_seconds": end_time - self.start_time,
            "memory_delta_mb": (memory_end - self.memory_start)
            / 1024
            / 1024,
        }
