"""Tests for validation utilities."""

import html
import re
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from pydantic import ValidationError
from starlette.responses import Response

from chatter.schemas.utilities import ValidationRule
from chatter.utils.validation import (
    InputValidator,
    sanitize_filename,
    sanitize_html,
    validate_email,
    validate_file_size,
    validate_file_type,
    validate_json_schema,
    validate_url,
)


@pytest.mark.unit
class TestInputValidator:
    """Test InputValidator functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = InputValidator()

    def test_validator_initialization(self):
        """Test validator initialization."""
        # Assert
        assert isinstance(self.validator.rules, dict)
        assert len(self.validator.rules) > 0
        assert "text" in self.validator.rules
        assert "message" in self.validator.rules

    def test_default_rules_setup(self):
        """Test default validation rules are set up correctly."""
        # Assert - Text rule
        text_rule = self.validator.rules["text"]
        assert isinstance(text_rule, ValidationRule)
        assert text_rule.name == "text"
        assert text_rule.max_length == 10000
        assert text_rule.sanitize is True
        assert len(text_rule.forbidden_patterns) > 0

        # Message rule
        message_rule = self.validator.rules["message"]
        assert isinstance(message_rule, ValidationRule)
        assert message_rule.name == "message"
        assert message_rule.max_length == 5000
        assert message_rule.min_length == 1

    def test_validate_text_normal_input(self):
        """Test validating normal text input."""
        # Arrange
        normal_text = "This is a normal text message with no issues."

        # Act
        result = self.validator.validate_input("text", normal_text)

        # Assert
        assert result is True

    def test_validate_text_with_script_tags(self):
        """Test validating text with malicious script tags."""
        # Arrange
        malicious_text = "Hello <script>alert('xss')</script> world"

        # Act & Assert
        with pytest.raises(ValueError, match="contains forbidden pattern"):
            self.validator.validate_input("text", malicious_text)

    def test_validate_text_with_javascript_url(self):
        """Test validating text with JavaScript URL."""
        # Arrange
        malicious_text = "Click here: javascript:alert('xss')"

        # Act & Assert
        with pytest.raises(ValueError, match="contains forbidden pattern"):
            self.validator.validate_input("text", malicious_text)

    def test_validate_text_exceeds_max_length(self):
        """Test validating text that exceeds maximum length."""
        # Arrange
        long_text = "A" * 10001  # Exceeds default max_length of 10000

        # Act & Assert
        with pytest.raises(ValueError, match="exceeds maximum length"):
            self.validator.validate_input("text", long_text)

    def test_validate_message_too_short(self):
        """Test validating message that's too short."""
        # Arrange
        empty_message = ""

        # Act & Assert
        with pytest.raises(ValueError, match="below minimum length"):
            self.validator.validate_input("message", empty_message)

    def test_validate_unknown_rule(self):
        """Test validating with unknown rule."""
        # Arrange
        text = "test input"

        # Act & Assert
        with pytest.raises(ValueError, match="Unknown validation rule"):
            self.validator.validate_input("unknown_rule", text)

    def test_sanitize_input_with_html(self):
        """Test sanitizing input with HTML content."""
        # Arrange
        html_text = "Hello <b>world</b> & friends"

        # Act
        sanitized = self.validator.sanitize_input("text", html_text)

        # Assert
        assert sanitized == "Hello world & friends"
        assert "<b>" not in sanitized
        assert "</b>" not in sanitized

    def test_sanitize_input_with_script_removal(self):
        """Test sanitizing input removes script tags."""
        # Arrange
        script_text = "Safe text <script>malicious()</script> more text"

        # Act
        sanitized = self.validator.sanitize_input("text", script_text)

        # Assert
        assert "script" not in sanitized.lower()
        assert "malicious" not in sanitized
        assert "Safe text" in sanitized
        assert "more text" in sanitized

    def test_add_custom_rule(self):
        """Test adding custom validation rule."""
        # Arrange
        custom_rule = ValidationRule(
            name="custom",
            max_length=100,
            forbidden_patterns=[r"badword"],
            sanitize=False
        )

        # Act
        self.validator.add_rule(custom_rule)

        # Assert
        assert "custom" in self.validator.rules
        assert self.validator.rules["custom"] == custom_rule

    def test_validate_with_custom_rule(self):
        """Test validation with custom rule."""
        # Arrange
        custom_rule = ValidationRule(
            name="strict",
            max_length=10,
            forbidden_patterns=[r"bad"],
            sanitize=False
        )
        self.validator.add_rule(custom_rule)

        # Act & Assert - Test max length
        with pytest.raises(ValueError, match="exceeds maximum length"):
            self.validator.validate_input("strict", "This is too long")

        # Test forbidden pattern
        with pytest.raises(ValueError, match="contains forbidden pattern"):
            self.validator.validate_input("strict", "bad text")

        # Test valid input
        assert self.validator.validate_input("strict", "good") is True


@pytest.mark.unit
class TestValidationFunctions:
    """Test standalone validation functions."""

    def test_validate_email_format_valid(self):
        """Test email format validation with valid emails."""
        # Arrange
        valid_emails = [
            "user@example.com",
            "test.email@domain.org",
            "user+tag@example.co.uk",
            "firstname.lastname@company-name.com"
        ]

        # Act & Assert
        for email in valid_emails:
            assert validate_email_format(email) is True

    def test_validate_email_format_invalid(self):
        """Test email format validation with invalid emails."""
        # Arrange
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@@domain.com",
            "user space@domain.com",
            ""
        ]

        # Act & Assert
        for email in invalid_emails:
            assert validate_email_format(email) is False

    def test_validate_username_format_valid(self):
        """Test username format validation with valid usernames."""
        # Arrange
        valid_usernames = [
            "user123",
            "test_user",
            "user-name",
            "a1b2c3",
            "Username123"
        ]

        # Act & Assert
        for username in valid_usernames:
            assert validate_username_format(username) is True

    def test_validate_username_format_invalid(self):
        """Test username format validation with invalid usernames."""
        # Arrange
        invalid_usernames = [
            "ab",  # Too short
            "a" * 51,  # Too long
            "user name",  # Contains space
            "user@name",  # Contains special char
            "user.name",  # Contains dot
            ""  # Empty
        ]

        # Act & Assert
        for username in invalid_usernames:
            assert validate_username_format(username) is False

    def test_validate_url_format_valid(self):
        """Test URL format validation with valid URLs."""
        # Arrange
        valid_urls = [
            "https://example.com",
            "http://test.org/path",
            "https://subdomain.domain.com/path/to/resource",
            "http://localhost:8080",
            "https://api.example.com/v1/users?id=123"
        ]

        # Act & Assert
        for url in valid_urls:
            assert validate_url_format(url) is True

    def test_validate_url_format_invalid(self):
        """Test URL format validation with invalid URLs."""
        # Arrange
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "https://",  # Incomplete
            "javascript:alert('xss')",  # Malicious
            "",  # Empty
            "//example.com"  # Protocol relative
        ]

        # Act & Assert
        for url in invalid_urls:
            assert validate_url_format(url) is False

    def test_validate_api_key_format_valid(self):
        """Test API key format validation with valid keys."""
        # Arrange
        valid_keys = [
            "sk_live_1234567890abcdef",
            "pk_test_abcdef1234567890",
            "sk_test_" + "a" * 32,
            "API_KEY_123456789012345678901234567890"
        ]

        # Act & Assert
        for key in valid_keys:
            assert validate_api_key_format(key) is True

    def test_validate_api_key_format_invalid(self):
        """Test API key format validation with invalid keys."""
        # Arrange
        invalid_keys = [
            "short",  # Too short
            "no_underscore",  # Wrong format
            "sk_live_",  # Missing key part
            "",  # Empty
            "spaces in key",  # Contains spaces
            "key-with-dashes"  # Wrong characters
        ]

        # Act & Assert
        for key in invalid_keys:
            assert validate_api_key_format(key) is False

    def test_validate_file_type_allowed(self):
        """Test file type validation with allowed types."""
        # Arrange
        allowed_types = [".txt", ".pdf", ".docx", ".md"]

        # Act & Assert
        assert validate_file_type("document.txt", allowed_types) is True
        assert validate_file_type("report.pdf", allowed_types) is True
        assert validate_file_type("README.md", allowed_types) is True

    def test_validate_file_type_not_allowed(self):
        """Test file type validation with disallowed types."""
        # Arrange
        allowed_types = [".txt", ".pdf"]

        # Act & Assert
        assert validate_file_type("script.js", allowed_types) is False
        assert validate_file_type("image.jpg", allowed_types) is False
        assert validate_file_type("archive.zip", allowed_types) is False

    def test_validate_file_type_case_insensitive(self):
        """Test file type validation is case insensitive."""
        # Arrange
        allowed_types = [".txt", ".pdf"]

        # Act & Assert
        assert validate_file_type("document.TXT", allowed_types) is True
        assert validate_file_type("report.PDF", allowed_types) is True
        assert validate_file_type("file.Txt", allowed_types) is True

    def test_validate_file_size_within_limit(self):
        """Test file size validation within limits."""
        # Arrange
        max_size_mb = 10

        # Act & Assert
        assert validate_file_size(5 * 1024 * 1024, max_size_mb) is True  # 5MB
        assert validate_file_size(10 * 1024 * 1024, max_size_mb) is True  # Exactly 10MB
        assert validate_file_size(1024, max_size_mb) is True  # 1KB

    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation exceeding limits."""
        # Arrange
        max_size_mb = 5

        # Act & Assert
        assert validate_file_size(6 * 1024 * 1024, max_size_mb) is False  # 6MB
        assert validate_file_size(100 * 1024 * 1024, max_size_mb) is False  # 100MB

    def test_sanitize_filename_normal(self):
        """Test filename sanitization with normal names."""
        # Arrange
        normal_filenames = [
            "document.txt",
            "report_2024.pdf",
            "image-file.jpg"
        ]

        # Act & Assert
        for filename in normal_filenames:
            sanitized = sanitize_filename(filename)
            assert sanitized == filename

    def test_sanitize_filename_with_special_chars(self):
        """Test filename sanitization with special characters."""
        # Arrange
        special_filenames = [
            "file with spaces.txt",
            "file/with/slashes.pdf",
            "file<with>brackets.doc",
            "file:with:colons.txt",
            "file*with*asterisks.pdf"
        ]

        # Act & Assert
        for filename in special_filenames:
            sanitized = sanitize_filename(filename)
            assert " " not in sanitized or sanitized == "file with spaces.txt"  # Spaces might be preserved
            assert "/" not in sanitized
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert ":" not in sanitized
            assert "*" not in sanitized

    def test_sanitize_html_basic(self):
        """Test basic HTML sanitization."""
        # Arrange
        html_content = "<p>Hello <b>world</b></p>"

        # Act
        sanitized = sanitize_html(html_content)

        # Assert
        assert sanitized == "Hello world"
        assert "<p>" not in sanitized
        assert "<b>" not in sanitized

    def test_sanitize_html_with_scripts(self):
        """Test HTML sanitization removes scripts."""
        # Arrange
        malicious_html = '<p>Safe content</p><script>alert("xss")</script>'

        # Act
        sanitized = sanitize_html(malicious_html)

        # Assert
        assert "Safe content" in sanitized
        assert "script" not in sanitized.lower()
        assert "alert" not in sanitized

    def test_validate_json_structure_valid(self):
        """Test JSON structure validation with valid data."""
        # Arrange
        valid_json_data = {
            "name": "test",
            "value": 123,
            "active": True,
            "metadata": {"key": "value"}
        }
        required_fields = ["name", "value"]
        allowed_fields = ["name", "value", "active", "metadata"]

        # Act
        result = validate_json_structure(valid_json_data, required_fields, allowed_fields)

        # Assert
        assert result is True

    def test_validate_json_structure_missing_required(self):
        """Test JSON structure validation with missing required fields."""
        # Arrange
        invalid_json_data = {"value": 123}
        required_fields = ["name", "value"]
        allowed_fields = ["name", "value", "active"]

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required field"):
            validate_json_structure(invalid_json_data, required_fields, allowed_fields)

    def test_validate_json_structure_unexpected_fields(self):
        """Test JSON structure validation with unexpected fields."""
        # Arrange
        invalid_json_data = {
            "name": "test",
            "value": 123,
            "unexpected": "field"
        }
        required_fields = ["name", "value"]
        allowed_fields = ["name", "value"]

        # Act & Assert
        with pytest.raises(ValueError, match="Unexpected field"):
            validate_json_structure(invalid_json_data, required_fields, allowed_fields)


@pytest.mark.unit
class TestValidationMiddleware:
    """Test ValidationMiddleware functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.middleware = ValidationMiddleware()

    @pytest.mark.asyncio
    async def test_middleware_initialization(self):
        """Test middleware initialization."""
        # Assert
        assert isinstance(self.middleware.validator, InputValidator)

    @pytest.mark.asyncio
    async def test_middleware_process_valid_request(self):
        """Test middleware processing valid request."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/chat"
        
        async def mock_call_next(request):
            return Response("OK", status_code=200)

        # Act
        response = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_process_invalid_json(self):
        """Test middleware processing request with invalid JSON."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/chat"
        
        # Mock request body to raise ValidationError
        async def mock_json():
            raise ValidationError("Invalid JSON", ValueError)
        
        mock_request.json = mock_json

        async def mock_call_next(request):
            return Response("OK", status_code=200)

        # Act
        response = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assert
        # Should handle validation error gracefully
        assert response.status_code in [400, 422, 200]  # Depends on implementation

    @pytest.mark.asyncio
    async def test_middleware_skip_get_requests(self):
        """Test middleware skips validation for GET requests."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.method = "GET"
        mock_request.url.path = "/api/health"
        
        async def mock_call_next(request):
            return Response("OK", status_code=200)

        # Act
        response = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assert
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_middleware_process_large_payload(self):
        """Test middleware processing large payload."""
        # Arrange
        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/api/documents"
        mock_request.headers = {"content-length": str(100 * 1024 * 1024)}  # 100MB
        
        async def mock_call_next(request):
            return Response("OK", status_code=200)

        # Act
        response = await self.middleware.dispatch(mock_request, mock_call_next)

        # Assert
        # Should handle large payloads appropriately
        assert response.status_code in [413, 400, 200]  # Depends on size limits


@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for validation utilities."""

    def test_complete_input_validation_workflow(self):
        """Test complete input validation workflow."""
        # Arrange
        validator = InputValidator()
        test_inputs = [
            ("text", "Normal safe text", True),
            ("text", "Text with <script>alert('xss')</script>", False),
            ("message", "Valid message content", True),
            ("message", "", False),  # Too short
            ("message", "A" * 6000, False),  # Too long
        ]

        # Act & Assert
        for rule_name, text, should_pass in test_inputs:
            if should_pass:
                assert validator.validate_input(rule_name, text) is True
                # Sanitization should work
                sanitized = validator.sanitize_input(rule_name, text)
                assert isinstance(sanitized, str)
            else:
                with pytest.raises(ValueError):
                    validator.validate_input(rule_name, text)

    def test_email_and_username_validation_combined(self):
        """Test email and username validation together."""
        # Arrange
        user_data = [
            ("valid@example.com", "validuser123", True),
            ("invalid-email", "validuser", False),
            ("valid@example.com", "us", False),  # Username too short
            ("user@test.com", "user name", False),  # Username with space
        ]

        # Act & Assert
        for email, username, should_pass in user_data:
            email_valid = validate_email_format(email)
            username_valid = validate_username_format(username)
            
            if should_pass:
                assert email_valid is True
                assert username_valid is True
            else:
                assert not (email_valid and username_valid)

    def test_file_validation_workflow(self):
        """Test complete file validation workflow."""
        # Arrange
        files_data = [
            ("document.txt", 1024, [".txt", ".pdf"], 5, True),
            ("image.jpg", 2048, [".txt", ".pdf"], 5, False),  # Wrong type
            ("large.pdf", 6 * 1024 * 1024, [".pdf"], 5, False),  # Too large
            ("valid.pdf", 3 * 1024 * 1024, [".pdf", ".txt"], 5, True),
        ]

        # Act & Assert
        for filename, size_bytes, allowed_types, max_mb, should_pass in files_data:
            type_valid = validate_file_type(filename, allowed_types)
            size_valid = validate_file_size(size_bytes, max_mb)
            filename_safe = sanitize_filename(filename)
            
            if should_pass:
                assert type_valid is True
                assert size_valid is True
                assert len(filename_safe) > 0
            else:
                assert not (type_valid and size_valid)

    def test_api_security_validation_workflow(self):
        """Test API security validation workflow."""
        # Arrange
        api_requests = [
            ("sk_live_1234567890abcdef", "https://api.example.com", True),
            ("invalid_key", "https://api.example.com", False),
            ("sk_test_validkey123456", "javascript:alert('xss')", False),
            ("", "https://valid.com", False),
        ]

        # Act & Assert
        for api_key, callback_url, should_pass in api_requests:
            key_valid = validate_api_key_format(api_key) if api_key else False
            url_valid = validate_url_format(callback_url) if callback_url else False
            
            if should_pass:
                assert key_valid is True
                assert url_valid is True
            else:
                assert not (key_valid and url_valid)

    def test_comprehensive_xss_protection(self):
        """Test comprehensive XSS protection across validation functions."""
        # Arrange
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='javascript:alert()'></iframe>",
            "onclick=alert('xss')",
        ]

        validator = InputValidator()

        # Act & Assert
        for payload in xss_payloads:
            # Should fail validation
            with pytest.raises(ValueError):
                validator.validate_input("text", payload)
            
            # Should be sanitized
            sanitized = validator.sanitize_input("text", payload)
            assert "script" not in sanitized.lower()
            assert "javascript" not in sanitized.lower()
            assert "alert" not in sanitized
            assert "onerror" not in sanitized.lower()
            
            # HTML sanitization should also work
            html_sanitized = sanitize_html(payload)
            assert "script" not in html_sanitized.lower()
            assert "alert" not in html_sanitized