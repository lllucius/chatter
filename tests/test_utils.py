"""Test utilities and helper functions."""

from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, MagicMock
import uuid
from datetime import datetime, timezone


def generate_test_id() -> str:
    """Generate a test ID using UUID."""
    return str(uuid.uuid4())


def generate_test_ulid() -> str:
    """Generate a test ULID-like string."""
    return "01H8X9Y9Z9" + str(uuid.uuid4()).replace("-", "")[:10].upper()


def create_mock_user(
    user_id: Optional[str] = None,
    username: str = "testuser",
    email: str = "test@example.com",
    is_active: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Create a mock user object for testing."""
    return {
        "id": user_id or generate_test_ulid(),
        "username": username,
        "email": email,
        "is_active": is_active,
        "created_at": datetime.now(timezone.utc).isoformat(),
        **kwargs
    }


def create_mock_chat(
    chat_id: Optional[str] = None,
    title: str = "Test Chat",
    user_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a mock chat object for testing."""
    return {
        "id": chat_id or generate_test_ulid(),
        "title": title,
        "user_id": user_id or generate_test_ulid(),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "messages": [],
        **kwargs
    }


def create_mock_message(
    message_id: Optional[str] = None,
    content: str = "Test message",
    role: str = "user",
    chat_id: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Create a mock message object for testing."""
    return {
        "id": message_id or generate_test_ulid(),
        "content": content,
        "role": role,
        "chat_id": chat_id or generate_test_ulid(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs
    }


def create_mock_document(
    doc_id: Optional[str] = None,
    title: str = "Test Document",
    content: str = "Test document content",
    file_type: str = "text/plain",
    **kwargs
) -> Dict[str, Any]:
    """Create a mock document object for testing."""
    return {
        "id": doc_id or generate_test_ulid(),
        "title": title,
        "content": content,
        "file_type": file_type,
        "size": len(content.encode()),
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        **kwargs
    }


class MockAsyncContext:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class MockDatabase:
    """Mock database for testing."""
    
    def __init__(self):
        self.data = {}
        self.execute = AsyncMock()
        self.fetch = AsyncMock()
        self.fetchrow = AsyncMock()
        self.fetchval = AsyncMock()
    
    def transaction(self):
        return MockAsyncContext()
    
    async def close(self):
        pass


class MockRedis:
    """Mock Redis client for testing."""
    
    def __init__(self):
        self.data = {}
    
    async def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    async def set(self, key: str, value: str) -> bool:
        self.data[key] = value
        return True
    
    async def delete(self, key: str) -> int:
        if key in self.data:
            del self.data[key]
            return 1
        return 0
    
    async def exists(self, key: str) -> bool:
        return key in self.data


class MockLLMService:
    """Mock LLM service for testing."""
    
    def __init__(self):
        self.response = "Test LLM response"
    
    async def generate_response(self, prompt: str, **kwargs) -> str:
        return self.response
    
    async def generate_embedding(self, text: str) -> list:
        return [0.1, 0.2, 0.3, 0.4, 0.5]


def assert_response_structure(
    response: dict,
    required_fields: list,
    optional_fields: list = None
):
    """Assert that response has the required structure."""
    optional_fields = optional_fields or []
    
    # Check required fields exist
    for field in required_fields:
        assert field in response, f"Required field '{field}' missing from response"
    
    # Check no unexpected fields (except optional ones)
    all_expected = set(required_fields + optional_fields)
    actual_fields = set(response.keys())
    unexpected = actual_fields - all_expected
    
    assert not unexpected, f"Unexpected fields in response: {unexpected}"


def assert_error_response(response: dict, expected_status: int = 400):
    """Assert that response is a proper error response."""
    assert "error" in response or "detail" in response
    if "status_code" in response:
        assert response["status_code"] == expected_status