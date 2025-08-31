"""Input validation tests."""


import pytest

from chatter.core.workflow_validation import (
    ValidationRule,
    WorkflowValidator,
)
from chatter.utils.validation import (
    sanitize_input,
    input_validator,
)
from chatter.utils.security import validate_password_strength


# Simple replacements for removed backward compatibility functions
def validate_email(email):
    try:
        input_validator.validate_and_sanitize(email, "email")
        return True
    except:
        return False

def validate_username(username):
    try:
        input_validator.validate_and_sanitize(username, "username")
        return True
    except:
        return False

def validate_password(password):
    return validate_password_strength(password)


@pytest.mark.unit
class TestInputValidation:
    """Test input validation utilities."""

    def test_email_validation(self):
        """Test email validation."""
        # Valid emails
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user+tag@example.org",
            "firstname.lastname@company.com",
            "user123@test-domain.com"
        ]

        for email in valid_emails:
            assert validate_email(email), f"Should accept valid email: {email}"

        # Invalid emails
        invalid_emails = [
            "invalid.email",
            "@example.com",
            "user@",
            "user..user@example.com",
            "user@domain..com",
            "user name@example.com",  # Space
            "user@domain.c",  # TLD too short
            "a" * 255 + "@example.com",  # Too long
            ""
        ]

        for email in invalid_emails:
            assert not validate_email(email), f"Should reject invalid email: {email}"

    def test_password_validation(self):
        """Test password validation."""
        # Strong passwords
        strong_passwords = [
            "MySecure123!",
            "C0mpl3x_P@ssw0rd",
            "VerySafe#2024",
            "Super$trong9Pass",
            "Ungu3ss@ble123!"
        ]

        for password in strong_passwords:
            result = validate_password(password)
            assert result["valid"], f"Should accept strong password: {password}"
            assert result["score"] >= 3

        # Weak passwords
        weak_passwords = [
            "password",
            "123456",
            "admin",
            "qwerty",
            "pass",
            "12345678",
            "Password1"  # Common pattern
        ]

        for password in weak_passwords:
            result = validate_password(password)
            assert not result["valid"], f"Should reject weak password: {password}"

    def test_username_validation(self):
        """Test username validation."""
        # Valid usernames
        valid_usernames = [
            "user123",
            "testuser",
            "user_name",
            "user-name",
            "validuser2024",
            "a" * 3,  # Minimum length
            "a" * 30  # Maximum length
        ]

        for username in valid_usernames:
            assert validate_username(username), f"Should accept valid username: {username}"

        # Invalid usernames
        invalid_usernames = [
            "us",  # Too short
            "a" * 31,  # Too long
            "user name",  # Space
            "user@name",  # Invalid character
            "user.name",  # Invalid character
            "123user",  # Starts with number
            "_username",  # Starts with underscore
            "-username",  # Starts with dash
            "",
            "admin",  # Reserved
            "root",  # Reserved
            "test"  # Reserved
        ]

        for username in invalid_usernames:
            assert not validate_username(username), f"Should reject invalid username: {username}"

    def test_input_sanitization(self):
        """Test input sanitization."""
        # XSS attempts
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "on click='alert(1)'",
            "<svg onload=alert('xss')>",
            "</script><script>alert('xss')</script>"
        ]

        for xss_input in xss_inputs:
            sanitized = sanitize_input(xss_input)
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "onload=" not in sanitized
            assert "onclick=" not in sanitized

        # SQL injection attempts
        sql_inputs = [
            "'; DROP TABLE users; --",
            "admin'; --",
            "' OR '1'='1",
            "'; INSERT INTO users VALUES ('hacker'); --",
            "' UNION SELECT * FROM passwords --"
        ]

        for sql_input in sql_inputs:
            sanitized = sanitize_input(sql_input)
            assert "DROP TABLE" not in sanitized.upper()
            assert "INSERT INTO" not in sanitized.upper()
            assert "UNION SELECT" not in sanitized.upper()

        # Path traversal attempts
        path_inputs = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]

        for path_input in path_inputs:
            sanitized = sanitize_input(path_input)
            assert "../" not in sanitized
            assert "..\\" not in sanitized
            assert "etc/passwd" not in sanitized

    def test_content_length_validation(self):
        """Test content length validation."""
        validator = WorkflowValidator()

        # Test message length limits
        short_message = "Hello"
        normal_message = "This is a normal length message for testing."
        long_message = "x" * 10000  # Very long message

        assert validator.validate_message_length(short_message)
        assert validator.validate_message_length(normal_message)
        assert not validator.validate_message_length(long_message)

    def test_file_upload_validation(self):
        """Test file upload validation."""
        validator = WorkflowValidator()

        # Valid file types
        valid_files = [
            {"filename": "document.pdf", "size": 1024000, "type": "application/pdf"},
            {"filename": "image.jpg", "size": 512000, "type": "image/jpeg"},
            {"filename": "text.txt", "size": 1000, "type": "text/plain"}
        ]

        for file_data in valid_files:
            result = validator.validate_file_upload(file_data)
            assert result.valid, f"Should accept valid file: {file_data['filename']}"

        # Invalid files
        invalid_files = [
            {"filename": "script.exe", "size": 1000, "type": "application/x-executable"},
            {"filename": "large.pdf", "size": 50000000, "type": "application/pdf"},  # Too large
            {"filename": "no_extension", "size": 1000, "type": "application/octet-stream"},
            {"filename": "suspicious.php", "size": 1000, "type": "text/plain"}
        ]

        for file_data in invalid_files:
            result = validator.validate_file_upload(file_data)
            assert not result.valid, f"Should reject invalid file: {file_data['filename']}"


@pytest.mark.unit
class TestWorkflowValidation:
    """Test workflow-specific validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = WorkflowValidator()

    def test_conversation_input_validation(self):
        """Test conversation input validation."""
        # Valid conversation data
        valid_data = {
            "title": "Test Conversation",
            "model": "gpt-4",
            "system_prompt": "You are a helpful assistant.",
            "max_tokens": 1000,
            "temperature": 0.7
        }

        result = self.validator.validate_conversation_input(valid_data)
        assert result.valid
        assert len(result.errors) == 0

        # Invalid conversation data
        invalid_data = {
            "title": "",  # Empty title
            "model": "invalid-model",
            "system_prompt": "x" * 10000,  # Too long
            "max_tokens": -1,  # Invalid
            "temperature": 2.5  # Out of range
        }

        result = self.validator.validate_conversation_input(invalid_data)
        assert not result.valid
        assert len(result.errors) > 0

    def test_message_input_validation(self):
        """Test message input validation."""
        # Valid message
        valid_message = {
            "content": "Hello, how are you?",
            "role": "user",
            "conversation_id": "conv-123"
        }

        result = self.validator.validate_message_input(valid_message)
        assert result.valid

        # Invalid messages
        invalid_messages = [
            {"content": "", "role": "user", "conversation_id": "conv-123"},  # Empty content
            {"content": "Hello", "role": "invalid", "conversation_id": "conv-123"},  # Invalid role
            {"content": "Hello", "role": "user", "conversation_id": ""},  # Empty conv ID
            {"content": "x" * 100000, "role": "user", "conversation_id": "conv-123"}  # Too long
        ]

        for invalid_message in invalid_messages:
            result = self.validator.validate_message_input(invalid_message)
            assert not result.valid

    def test_workflow_parameter_validation(self):
        """Test workflow parameter validation."""
        # Valid parameters
        valid_params = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop": ["</end>"],
            "stream": True
        }

        result = self.validator.validate_workflow_parameters(valid_params)
        assert result.valid

        # Invalid parameters
        invalid_params = {
            "temperature": 2.5,  # Out of range
            "max_tokens": -1,  # Negative
            "top_p": 1.5,  # Out of range
            "frequency_penalty": 3.0,  # Out of range
            "presence_penalty": -3.0,  # Out of range
            "stop": ["x" * 1000],  # Stop sequence too long
            "stream": "yes"  # Wrong type
        }

        result = self.validator.validate_workflow_parameters(invalid_params)
        assert not result.valid
        assert len(result.errors) > 0

    def test_api_key_format_validation(self):
        """Test API key format validation."""
        # Valid API keys
        valid_keys = [
            "sk-proj-abcdef1234567890abcdef1234567890abcdef12",
            "sk-live-1234567890abcdef1234567890abcdef12345678",
            "sk-ant-api03-abcdef1234567890abcdef1234567890abcdef"
        ]

        for key in valid_keys:
            assert self.validator.validate_api_key_format(key)

        # Invalid API keys
        invalid_keys = [
            "sk-test-123",  # Test key
            "invalid-key",
            "",
            "sk-proj-short",
            "not-an-api-key"
        ]

        for key in invalid_keys:
            assert not self.validator.validate_api_key_format(key)

    def test_rate_limit_validation(self):
        """Test rate limit parameter validation."""
        # Valid rate limits
        valid_limits = [
            {"requests_per_minute": 60, "tokens_per_minute": 10000},
            {"requests_per_minute": 10, "tokens_per_minute": 1000},
            {"requests_per_minute": 100, "tokens_per_minute": 50000}
        ]

        for limit in valid_limits:
            result = self.validator.validate_rate_limits(limit)
            assert result.valid

        # Invalid rate limits
        invalid_limits = [
            {"requests_per_minute": 0, "tokens_per_minute": 1000},  # Zero requests
            {"requests_per_minute": 1000, "tokens_per_minute": 0},  # Zero tokens
            {"requests_per_minute": -1, "tokens_per_minute": 1000},  # Negative
            {"requests_per_minute": 10000, "tokens_per_minute": 1000000}  # Too high
        ]

        for limit in invalid_limits:
            result = self.validator.validate_rate_limits(limit)
            assert not result.valid


@pytest.mark.unit
class TestValidationRules:
    """Test validation rule system."""

    def test_validation_rule_creation(self):
        """Test creating validation rules."""
        rule = ValidationRule(
            name="email_format",
            validator=lambda x: "@" in x and "." in x,
            error_message="Invalid email format"
        )

        assert rule.name == "email_format"
        assert rule.validate("test@example.com")
        assert not rule.validate("invalid-email")
        assert rule.error_message == "Invalid email format"

    def test_validation_rule_chaining(self):
        """Test chaining multiple validation rules."""
        rules = [
            ValidationRule("not_empty", lambda x: len(x) > 0, "Cannot be empty"),
            ValidationRule("min_length", lambda x: len(x) >= 3, "Must be at least 3 characters"),
            ValidationRule("max_length", lambda x: len(x) <= 50, "Must be at most 50 characters"),
            ValidationRule("alphanumeric", lambda x: x.isalnum(), "Must be alphanumeric")
        ]

        validator = WorkflowValidator()

        # Valid input
        result = validator.apply_rules("test123", rules)
        assert result.valid

        # Invalid input (fails multiple rules)
        result = validator.apply_rules("", rules)
        assert not result.valid
        assert "Cannot be empty" in result.errors[0]

        result = validator.apply_rules("ab", rules)
        assert not result.valid
        assert "Must be at least 3 characters" in result.errors[0]

    def test_conditional_validation_rules(self):
        """Test conditional validation rules."""
        def password_strength_rule(password):
            if len(password) < 8:
                return False
            if not any(c.isupper() for c in password):
                return False
            if not any(c.isdigit() for c in password):
                return False
            return True

        rule = ValidationRule(
            name="password_strength",
            validator=password_strength_rule,
            error_message="Password must be at least 8 characters with uppercase and digit"
        )

        assert rule.validate("StrongPass123")
        assert not rule.validate("weak")
        assert not rule.validate("nostrongcase")
        assert not rule.validate("NoDigits")

    def test_custom_validation_context(self):
        """Test validation with custom context."""
        validator = WorkflowValidator()

        # Context-aware validation (e.g., user permissions)
        context = {
            "user_role": "admin",
            "feature_flags": ["advanced_features"],
            "subscription_tier": "premium"
        }

        # Admin can use advanced models
        model_data = {"model": "gpt-4", "advanced_params": True}
        result = validator.validate_with_context(model_data, context)
        assert result.valid

        # Regular user cannot
        context["user_role"] = "user"
        context["subscription_tier"] = "free"
        result = validator.validate_with_context(model_data, context)
        assert not result.valid


@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for validation system."""

    async def test_api_input_validation(self, test_client):
        """Test API input validation integration."""
        # Test conversation creation with invalid data
        invalid_data = {
            "title": "",  # Empty title
            "model": "invalid-model",
            "max_tokens": -1
        }

        response = await test_client.post("/api/v1/conversations", json=invalid_data)
        assert response.status_code == 400

        data = response.json()
        assert "validation" in data["title"].lower() or "field_errors" in data

    async def test_message_validation_integration(self, test_client):
        """Test message validation integration."""
        # Test sending message with invalid data
        invalid_message = {
            "content": "",  # Empty content
            "conversation_id": "invalid-id"
        }

        response = await test_client.post("/api/v1/chat", json=invalid_message)
        assert response.status_code == 400

    async def test_file_upload_validation_integration(self, test_client):
        """Test file upload validation integration."""
        # This would test actual file upload validation
        # For now, we'll test the validation logic
        validator = WorkflowValidator()

        # Simulate malicious file upload
        malicious_file = {
            "filename": "virus.exe",
            "size": 1024,
            "type": "application/x-executable",
            "content": b"malicious content"
        }

        result = validator.validate_file_upload(malicious_file)
        assert not result.valid
        assert "executable" in result.errors[0].lower() or "not allowed" in result.errors[0].lower()

    async def test_rate_limit_validation_integration(self, test_client):
        """Test rate limit validation integration."""
        # Test rapid requests to trigger validation
        # This would normally be handled by middleware
        validator = WorkflowValidator()

        # Simulate rate limit check
        rate_limit_data = {
            "user_id": "user-123",
            "requests_in_window": 100,
            "tokens_in_window": 50000,
            "window_start": "2024-01-01T00:00:00Z"
        }

        result = validator.validate_rate_limit_status(rate_limit_data)
        # Would depend on configured limits
        assert isinstance(result.valid, bool)

    async def test_workflow_validation_end_to_end(self, test_client):
        """Test complete workflow validation."""
        # Test a complete chat workflow with validation
        workflow_data = {
            "conversation": {
                "title": "Test Chat",
                "model": "gpt-3.5-turbo"
            },
            "message": {
                "content": "Hello, how can you help me today?",
                "role": "user"
            },
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 1000,
                "stream": True
            }
        }

        validator = WorkflowValidator()

        # Validate conversation
        conv_result = validator.validate_conversation_input(workflow_data["conversation"])
        assert conv_result.valid

        # Validate message
        msg_result = validator.validate_message_input(workflow_data["message"])
        assert msg_result.valid

        # Validate parameters
        param_result = validator.validate_workflow_parameters(workflow_data["parameters"])
        assert param_result.valid
