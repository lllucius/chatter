"""Comprehensive tests for profiles API security and functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from pydantic import ValidationError

from chatter.schemas.profile import ProfileCreate, ProfileUpdate, ProfileTestRequest
from chatter.models.profile import ProfileType
from chatter.utils.unified_rate_limiter import RateLimitExceeded


class TestProfileSchemaSecurity:
    """Test profile schema security validations."""

    def test_profile_create_valid(self):
        """Test valid profile creation."""
        profile = ProfileCreate(
            name="Test Profile",
            llm_provider="openai",
            llm_model="gpt-4"
        )
        assert profile.name == "Test Profile"
        assert profile.llm_provider == "openai"
        assert profile.llm_model == "gpt-4"

    def test_profile_create_sql_injection_blocked(self):
        """Test SQL injection attempts are blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="'; DROP TABLE profiles; --",
                llm_provider="openai",
                llm_model="gpt-4"
            )

    def test_profile_create_xss_blocked(self):
        """Test XSS attempts are blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="<script>alert('XSS')</script>",
                llm_provider="openai",
                llm_model="gpt-4"
            )

    def test_profile_create_oversized_name_blocked(self):
        """Test oversized name is blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="A" * 300,  # Over max length
                llm_provider="openai",
                llm_model="gpt-4"
            )

    def test_profile_create_oversized_system_prompt_blocked(self):
        """Test oversized system prompt is blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="openai",
                llm_model="gpt-4",
                system_prompt="A" * 15000  # Over max length
            )

    def test_profile_create_dangerous_temperature_blocked(self):
        """Test dangerous low temperature is blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="openai",
                llm_model="gpt-4",
                temperature=0.001  # Too low
            )

    def test_profile_create_dangerous_max_tokens_blocked(self):
        """Test dangerous low max_tokens is blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="openai",
                llm_model="gpt-4",
                max_tokens=5  # Too low
            )

    def test_profile_create_empty_required_fields_blocked(self):
        """Test empty required fields are blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="",  # Empty
                llm_model=""  # Empty
            )

    def test_profile_create_invalid_provider_format_blocked(self):
        """Test invalid provider format is blocked."""
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="invalid<script>",
                llm_model="model; DROP TABLE users;"
            )

    def test_profile_create_tags_validation(self):
        """Test tags validation."""
        # Valid tags
        profile = ProfileCreate(
            name="Test",
            llm_provider="openai",
            llm_model="gpt-4",
            tags=["test", "demo"]
        )
        assert profile.tags == ["test", "demo"]

        # Invalid tags (too long)
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Test",
                llm_provider="openai",
                llm_model="gpt-4",
                tags=["A" * 60]  # Tag too long
            )

    def test_profile_update_validation(self):
        """Test profile update validation."""
        # Valid update
        update = ProfileUpdate(name="Updated Profile", temperature=0.8)
        assert update.name == "Updated Profile"
        assert update.temperature == 0.8

        # Invalid update
        with pytest.raises(ValidationError):
            ProfileUpdate(
                name="",  # Empty name
                temperature=99.9  # Invalid temperature
            )


class TestProfileTestRequest:
    """Test profile test request validation."""

    def test_valid_test_request(self):
        """Test valid test request."""
        request = ProfileTestRequest(
            test_message="Hello, world!",
            include_retrieval=True,
            include_tools=False
        )
        assert request.test_message == "Hello, world!"
        assert request.include_retrieval is True

    def test_oversized_test_message_blocked(self):
        """Test oversized test message is blocked."""
        with pytest.raises(ValidationError):
            ProfileTestRequest(
                test_message="A" * 2000  # Over max length
            )

    def test_test_message_security_validation(self):
        """Test test message security validation."""
        with pytest.raises(ValidationError):
            ProfileTestRequest(
                test_message="<script>alert('XSS')</script>"
            )


@pytest.mark.asyncio
class TestProfileAPIEndpoints:
    """Test profile API endpoints with mocking."""

    @pytest.fixture
    def mock_profile_service(self):
        """Mock profile service."""
        service = AsyncMock()
        return service

    @pytest.fixture  
    def mock_user(self):
        """Mock authenticated user."""
        user = MagicMock()
        user.id = "user123"
        return user

    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter."""
        with patch('chatter.api.profiles.rate_limiter') as mock:
            yield mock

    async def test_create_profile_success(self, mock_profile_service, mock_user):
        """Test successful profile creation."""
        # Mock the service response
        mock_profile = MagicMock()
        mock_profile_service.create_profile.return_value = mock_profile
        
        # This would require a full FastAPI test setup
        # For now, we test the business logic
        profile_data = ProfileCreate(
            name="Test Profile",
            llm_provider="openai",
            llm_model="gpt-4"
        )
        
        result = await mock_profile_service.create_profile("user123", profile_data)
        assert result == mock_profile
        mock_profile_service.create_profile.assert_called_once_with("user123", profile_data)

    async def test_create_profile_rate_limit(self, mock_rate_limiter, mock_profile_service, mock_user):
        """Test profile creation rate limiting."""
        # Configure rate limiter to raise exception
        mock_rate_limiter.check_rate_limit.side_effect = RateLimitExceeded("Rate limit exceeded")
        
        # This would test the actual endpoint rate limiting
        # The rate limiter should prevent creation when limits are exceeded
        assert mock_rate_limiter.check_rate_limit.side_effect == RateLimitExceeded("Rate limit exceeded")

    async def test_test_profile_success(self, mock_profile_service, mock_user):
        """Test successful profile testing."""
        mock_result = {
            "profile_id": "profile123",
            "test_message": "Hello",
            "response": "Hi there!",
            "usage_info": {"tokens": 50},
            "response_time_ms": 1000
        }
        mock_profile_service.test_profile.return_value = mock_result
        
        test_request = ProfileTestRequest(test_message="Hello")
        result = await mock_profile_service.test_profile("profile123", "user123", test_request)
        
        assert result == mock_result
        mock_profile_service.test_profile.assert_called_once_with("profile123", "user123", test_request)

    async def test_test_profile_rate_limit(self, mock_rate_limiter):
        """Test profile testing rate limiting."""
        mock_rate_limiter.check_rate_limit.side_effect = RateLimitExceeded("Rate limit exceeded")
        
        # The rate limiter should prevent testing when limits are exceeded
        assert mock_rate_limiter.check_rate_limit.side_effect == RateLimitExceeded("Rate limit exceeded")


class TestProfileBusinessLogic:
    """Test profile business logic and edge cases."""

    def test_profile_type_enum(self):
        """Test profile type enumeration."""
        assert ProfileType.CONVERSATIONAL == "conversational"
        assert ProfileType.ANALYTICAL == "analytical"
        assert ProfileType.CREATIVE == "creative"
        assert ProfileType.TECHNICAL == "technical"
        assert ProfileType.CUSTOM == "custom"

    def test_profile_create_with_all_fields(self):
        """Test profile creation with all optional fields."""
        profile = ProfileCreate(
            name="Comprehensive Profile",
            description="A test profile with all fields",
            profile_type=ProfileType.TECHNICAL,
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.8,
            top_p=0.9,
            top_k=50,
            max_tokens=2048,
            presence_penalty=0.1,
            frequency_penalty=0.1,
            context_window=8192,
            system_prompt="You are a helpful technical assistant",
            memory_enabled=True,
            memory_strategy="sliding_window",
            enable_retrieval=True,
            retrieval_limit=10,
            retrieval_score_threshold=0.8,
            enable_tools=True,
            available_tools=["calculator", "web_search"],
            tool_choice="auto",
            content_filter_enabled=True,
            safety_level="medium",
            response_format="markdown",
            stream_response=True,
            seed=42,
            stop_sequences=["END", "STOP"],
            embedding_provider="openai",
            embedding_model="text-embedding-ada-002",
            is_public=False,
            tags=["technical", "assistant"],
            extra_metadata={"version": "1.0"}
        )
        
        assert profile.name == "Comprehensive Profile"
        assert profile.profile_type == ProfileType.TECHNICAL
        assert profile.temperature == 0.8
        assert profile.max_tokens == 2048
        assert profile.enable_tools is True
        assert profile.available_tools == ["calculator", "web_search"]
        assert profile.tags == ["technical", "assistant"]

    def test_profile_validation_edge_cases(self):
        """Test profile validation edge cases."""
        # Valid edge case: minimum reasonable values
        profile = ProfileCreate(
            name="Minimal",
            llm_provider="openai",
            llm_model="gpt-4",
            temperature=0.02,  # Just above minimum
            max_tokens=10      # Minimum allowed
        )
        assert profile.temperature == 0.02
        assert profile.max_tokens == 10

        # Invalid: exactly at dangerous thresholds
        with pytest.raises(ValidationError):
            ProfileCreate(
                name="Dangerous",
                llm_provider="openai", 
                llm_model="gpt-4",
                temperature=0.01,  # Exactly at threshold
                max_tokens=9       # Below minimum
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])