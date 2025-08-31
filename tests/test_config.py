"""Test configuration and utilities for the comprehensive test suite."""

import os
from pathlib import Path

import pytest


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running tests"
    )
    config.addinivalue_line(
        "markers", "external: marks tests requiring external services"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to tests based on their location and name."""
    for item in items:
        # Add unit marker to all test files starting with test_
        if item.fspath.basename.startswith("test_"):
            item.add_marker(pytest.mark.unit)

        # Add integration marker to integration tests
        if "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)

        # Add slow marker to tests that might be slow
        if any(keyword in item.name.lower() for keyword in ["batch", "large", "performance", "concurrent"]):
            item.add_marker(pytest.mark.slow)

        # Add external marker to tests requiring external services
        if any(keyword in item.fspath.basename for keyword in ["llm", "embedding", "vector_store"]):
            item.add_marker(pytest.mark.external)


@pytest.fixture(scope="session")
def test_data_dir():
    """Provide path to test data directory."""
    return Path(__file__).parent / "test_data"


@pytest.fixture(scope="session")
def mock_settings():
    """Provide mock application settings for testing."""
    return {
        "database_url": "sqlite+aiosqlite:///:memory:",
        "secret_key": "test-secret-key-for-testing-only",
        "environment": "test",
        "debug": True,
        "testing": True
    }


@pytest.fixture
def mock_user_data():
    """Provide mock user data for testing."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "SecureTestPass123!",
        "display_name": "Test User",
        "is_active": True
    }


@pytest.fixture
def mock_conversation_data():
    """Provide mock conversation data for testing."""
    return {
        "title": "Test Conversation",
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful test assistant.",
        "temperature": 0.7,
        "max_tokens": 150
    }


@pytest.fixture
def mock_document_data():
    """Provide mock document data for testing."""
    return {
        "title": "Test Document",
        "filename": "test.txt",
        "content": b"This is test document content for testing purposes.",
        "content_type": "text/plain",
        "size": 52
    }


class TestDataHelper:
    """Helper class for managing test data."""

    @staticmethod
    def create_test_vectors(count=10, dimension=3):
        """Create test vectors for vector store testing."""
        import random
        vectors = []
        for i in range(count):
            vector = [random.random() for _ in range(dimension)]
            vectors.append({
                "id": f"test_vector_{i}",
                "vector": vector,
                "metadata": {
                    "text": f"Test document {i}",
                    "category": "test",
                    "index": i
                }
            })
        return vectors

    @staticmethod
    def create_test_embeddings(texts, dimension=384):
        """Create mock embeddings for texts."""
        import random
        embeddings = []
        for text in texts:
            # Create deterministic but random-looking embeddings
            random.seed(hash(text) % 2**32)
            embedding = [random.gauss(0, 1) for _ in range(dimension)]
            embeddings.append(embedding)
        return embeddings

    @staticmethod
    def assert_api_response_format(response_data, required_fields=None):
        """Assert that API response has expected format."""
        assert isinstance(response_data, dict), "Response should be a dictionary"

        if required_fields:
            for field in required_fields:
                assert field in response_data, f"Required field '{field}' missing from response"

    @staticmethod
    def assert_pagination_format(response_data):
        """Assert that paginated response has expected format."""
        required_fields = ["items", "total", "page", "per_page"]
        TestDataHelper.assert_api_response_format(response_data, required_fields)

        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["per_page"], int)


# Test data creation utilities
def create_test_user_data(email_suffix="example.com", username_prefix="testuser"):
    """Create unique test user data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    return {
        "email": f"{username_prefix}_{unique_id}@{email_suffix}",
        "username": f"{username_prefix}_{unique_id}",
        "password": "SecureTestPass123!",
        "display_name": f"Test User {unique_id}"
    }


def create_test_conversation_data(title_prefix="Test Conversation"):
    """Create test conversation data."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    return {
        "title": f"{title_prefix} {unique_id}",
        "model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful test assistant.",
        "temperature": 0.7,
        "max_tokens": 150
    }


# Skip conditions for different test types
skip_if_no_database = pytest.mark.skipif(
    not os.getenv("TEST_DATABASE_URL"),
    reason="Database not available for testing"
)

skip_if_no_redis = pytest.mark.skipif(
    not os.getenv("TEST_REDIS_URL"),
    reason="Redis not available for testing"
)

skip_if_no_llm_provider = pytest.mark.skipif(
    not any([
        os.getenv("OPENAI_API_KEY"),
        os.getenv("ANTHROPIC_API_KEY"),
        os.getenv("GOOGLE_API_KEY")
    ]),
    reason="No LLM provider API key available for testing"
)

skip_if_no_vector_store = pytest.mark.skipif(
    not any([
        os.getenv("PINECONE_API_KEY"),
        os.getenv("QDRANT_URL"),
        os.getenv("CHROMA_ENDPOINT")
    ]),
    reason="No vector store available for testing"
)


# Common test patterns
class CommonTestPatterns:
    """Common test patterns for API and service testing."""

    @staticmethod
    async def test_authentication_required(test_client, endpoint, method="GET"):
        """Test that endpoint requires authentication."""
        if method.upper() == "GET":
            response = await test_client.get(endpoint)
        elif method.upper() == "POST":
            response = await test_client.post(endpoint, json={})
        elif method.upper() == "PUT":
            response = await test_client.put(endpoint, json={})
        elif method.upper() == "DELETE":
            response = await test_client.delete(endpoint)

        assert response.status_code in [401, 403], f"Endpoint {endpoint} should require authentication"

    @staticmethod
    async def test_not_found_handling(test_client, endpoint_template, headers=None):
        """Test that non-existent resource returns 404."""
        endpoint = endpoint_template.format(id="nonexistent_id")
        response = await test_client.get(endpoint, headers=headers)

        assert response.status_code in [404, 501], f"Endpoint {endpoint} should return 404 for non-existent resource"

    @staticmethod
    async def test_validation_error_handling(test_client, endpoint, invalid_data, headers=None):
        """Test that invalid data returns validation error."""
        response = await test_client.post(endpoint, json=invalid_data, headers=headers)

        assert response.status_code in [400, 422], f"Endpoint {endpoint} should return validation error for invalid data"
