"""Tests for security utilities."""

import re
from unittest.mock import patch

import pytest

from chatter.utils.security import (
    SENSITIVE_PATTERNS,
    SECRET_KEYS,
    generate_api_key_hash,
    hash_api_key,
    hash_password,
    is_sensitive_key,
    mask_sensitive_value,
    sanitize_log_data,
    sanitize_string,
    sanitize_url,
    verify_api_key,
    verify_password,
)


@pytest.mark.unit
class TestPasswordHandling:
    """Test password hashing and verification."""

    def test_hash_password(self):
        """Test password hashing."""
        # Arrange
        password = "test_password_123"

        # Act
        hashed = hash_password(password)

        # Assert
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be different from original
        assert hashed.startswith("$2b$")  # bcrypt format

    def test_hash_password_different_results(self):
        """Test that hashing same password produces different results."""
        # Arrange
        password = "same_password"

        # Act
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Assert
        assert hash1 != hash2  # Different salts should produce different hashes

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        # Arrange
        password = "correct_password"
        hashed = hash_password(password)

        # Act
        result = verify_password(password, hashed)

        # Assert
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        # Arrange
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(correct_password)

        # Act
        result = verify_password(wrong_password, hashed)

        # Assert
        assert result is False

    def test_verify_password_invalid_hash(self):
        """Test password verification with invalid hash."""
        # Arrange
        password = "test_password"
        invalid_hash = "not_a_bcrypt_hash"

        # Act
        result = verify_password(password, invalid_hash)

        # Assert
        assert result is False

    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs."""
        # Act & Assert
        assert verify_password("", "") is False
        assert verify_password("password", "") is False
        assert verify_password("", "hash") is False


@pytest.mark.unit
class TestApiKeyHandling:
    """Test API key hashing and verification."""

    def test_hash_api_key_default_salt(self):
        """Test API key hashing with default salt."""
        # Arrange
        api_key = "test_api_key_123"

        # Act
        hashed = hash_api_key(api_key)

        # Assert
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex length
        assert hashed != api_key

    def test_hash_api_key_custom_salt(self):
        """Test API key hashing with custom salt."""
        # Arrange
        api_key = "test_api_key_123"
        salt = "custom_salt_16ch"

        # Act
        hashed = hash_api_key(api_key, salt)

        # Assert
        assert isinstance(hashed, str)
        assert len(hashed) == 64
        assert hashed != api_key

    def test_hash_api_key_different_salts(self):
        """Test that different salts produce different hashes."""
        # Arrange
        api_key = "same_api_key"
        salt1 = "salt1_16_chars_x"
        salt2 = "salt2_16_chars_y"

        # Act
        hash1 = hash_api_key(api_key, salt1)
        hash2 = hash_api_key(api_key, salt2)

        # Assert
        assert hash1 != hash2

    def test_verify_api_key_correct(self):
        """Test API key verification with correct key."""
        # Arrange
        api_key = "test_api_key_123"
        hashed = hash_api_key(api_key)

        # Act
        result = verify_api_key(api_key, hashed)

        # Assert
        assert result is True

    def test_verify_api_key_incorrect(self):
        """Test API key verification with incorrect key."""
        # Arrange
        correct_key = "correct_api_key"
        wrong_key = "wrong_api_key"
        hashed = hash_api_key(correct_key)

        # Act
        result = verify_api_key(wrong_key, hashed)

        # Assert
        assert result is False

    def test_verify_api_key_custom_salt(self):
        """Test API key verification with custom salt."""
        # Arrange
        api_key = "test_api_key"
        salt = "custom_salt_test"
        hashed = hash_api_key(api_key, salt)

        # Act
        result = verify_api_key(api_key, hashed, salt)

        # Assert
        assert result is True

    def test_generate_api_key_hash(self):
        """Test API key generation."""
        # Act
        plain_key, hashed_key = generate_api_key_hash()

        # Assert
        assert isinstance(plain_key, str)
        assert isinstance(hashed_key, str)
        assert len(plain_key) == 32  # Default length
        assert len(hashed_key) == 64  # SHA-256 hex
        assert verify_api_key(plain_key, hashed_key)

    def test_generate_api_key_hash_custom_length(self):
        """Test API key generation with custom length."""
        # Arrange
        length = 64

        # Act
        plain_key, hashed_key = generate_api_key_hash(length)

        # Assert
        assert len(plain_key) == length
        assert verify_api_key(plain_key, hashed_key)

    def test_generate_api_key_uniqueness(self):
        """Test that generated API keys are unique."""
        # Act
        key1, _ = generate_api_key_hash()
        key2, _ = generate_api_key_hash()

        # Assert
        assert key1 != key2


@pytest.mark.unit
class TestSensitiveDataSanitization:
    """Test sensitive data sanitization functions."""

    def test_sanitize_string_api_key(self):
        """Test sanitizing API keys from strings."""
        # Arrange
        text = 'The API_KEY is "abc123def456ghi789" for authentication'

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert "abc123def456ghi789" not in sanitized
        assert "API_KEY=[MASKED]" in sanitized

    def test_sanitize_string_password(self):
        """Test sanitizing passwords from strings."""
        # Arrange
        text = 'password: "mySecretPassword123"'

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert "mySecretPassword123" not in sanitized
        assert "password=[MASKED]" in sanitized

    def test_sanitize_string_jwt_token(self):
        """Test sanitizing JWT tokens from strings."""
        # Arrange
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        text = f"Authorization token: {jwt_token}"

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert jwt_token not in sanitized
        assert "[MASKED]" in sanitized

    def test_sanitize_string_email(self):
        """Test sanitizing email addresses from strings."""
        # Arrange
        text = "Contact us at user@example.com for support"

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert "user@example.com" not in sanitized
        assert "user@[MASKED]" in sanitized

    def test_sanitize_string_credit_card(self):
        """Test sanitizing credit card numbers from strings."""
        # Arrange
        text = "Credit card: 1234-5678-9012-3456"

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert "1234-5678-9012-3456" not in sanitized
        assert "[MASKED]" in sanitized

    def test_sanitize_string_multiple_patterns(self):
        """Test sanitizing multiple sensitive patterns from one string."""
        # Arrange
        text = 'api_key="secret123" password="mypass" user@domain.com'

        # Act
        sanitized = sanitize_string(text)

        # Assert
        assert "secret123" not in sanitized
        assert "mypass" not in sanitized
        assert "user@domain.com" not in sanitized
        assert "api_key=[MASKED]" in sanitized
        assert "password=[MASKED]" in sanitized
        assert "user@[MASKED]" in sanitized

    def test_sanitize_string_non_string_input(self):
        """Test sanitizing non-string input."""
        # Arrange
        non_string = 12345

        # Act
        result = sanitize_string(non_string)

        # Assert
        assert result == non_string

    def test_mask_sensitive_value(self):
        """Test masking sensitive values."""
        # Arrange
        value = "secretapikey123456"

        # Act
        masked = mask_sensitive_value(value)

        # Assert
        assert masked == "secr**********3456"
        assert "secretapikey123456" not in masked

    def test_mask_sensitive_value_short(self):
        """Test masking short sensitive values."""
        # Arrange
        value = "short"

        # Act
        masked = mask_sensitive_value(value)

        # Assert
        assert masked == "[MASKED]"

    def test_mask_sensitive_value_custom_show_chars(self):
        """Test masking with custom number of visible characters."""
        # Arrange
        value = "verylongapikey123"
        show_chars = 2

        # Act
        masked = mask_sensitive_value(value, show_chars)

        # Assert
        assert masked == "ve*************23"

    def test_sanitize_url(self):
        """Test sanitizing URLs with credentials."""
        # Arrange
        url = "postgres://user:password@localhost:5432/database"

        # Act
        sanitized = sanitize_url(url)

        # Assert
        assert "user:password" not in sanitized
        assert "postgres://[MASKED]@localhost:5432/database" == sanitized

    def test_sanitize_url_no_credentials(self):
        """Test sanitizing URLs without credentials."""
        # Arrange
        url = "https://api.example.com/endpoint"

        # Act
        sanitized = sanitize_url(url)

        # Assert
        assert sanitized == url  # Should remain unchanged

    def test_sanitize_url_empty(self):
        """Test sanitizing empty URL."""
        # Act
        result = sanitize_url("")

        # Assert
        assert result == ""

    def test_is_sensitive_key(self):
        """Test identifying sensitive keys."""
        # Act & Assert
        assert is_sensitive_key("api_key") is True
        assert is_sensitive_key("password") is True
        assert is_sensitive_key("secret_key") is True
        assert is_sensitive_key("authorization") is True
        assert is_sensitive_key("normal_field") is False
        assert is_sensitive_key("user_name") is False

    def test_is_sensitive_key_case_insensitive(self):
        """Test that sensitive key detection is case insensitive."""
        # Act & Assert
        assert is_sensitive_key("API_KEY") is True
        assert is_sensitive_key("Password") is True
        assert is_sensitive_key("SECRET_KEY") is True

    def test_is_sensitive_key_non_string(self):
        """Test sensitive key detection with non-string input."""
        # Act & Assert
        assert is_sensitive_key(123) is False
        assert is_sensitive_key(None) is False


@pytest.mark.unit
class TestLogDataSanitization:
    """Test log data sanitization."""

    def test_sanitize_log_data_dict(self):
        """Test sanitizing dictionary data."""
        # Arrange
        data = {
            "user_id": "12345",
            "api_key": "secret123",
            "password": "mypassword",
            "email": "user@example.com",
            "normal_field": "normal_value"
        }

        # Act
        sanitized = sanitize_log_data(data)

        # Assert
        assert sanitized["user_id"] == "12345"
        assert "secret123" not in str(sanitized)
        assert "mypassword" not in str(sanitized)
        assert sanitized["normal_field"] == "normal_value"
        assert "secr" in sanitized["api_key"]  # Partially masked
        assert "mypa" in sanitized["password"]  # Partially masked

    def test_sanitize_log_data_list(self):
        """Test sanitizing list data."""
        # Arrange
        data = [
            "normal string",
            "api_key=secret123",
            {"password": "hidden"},
            123
        ]

        # Act
        sanitized = sanitize_log_data(data)

        # Assert
        assert sanitized[0] == "normal string"
        assert "secret123" not in sanitized[1]
        assert "api_key=[MASKED]" in sanitized[1]
        assert "hidden" not in str(sanitized[2])
        assert sanitized[3] == 123

    def test_sanitize_log_data_string(self):
        """Test sanitizing string data."""
        # Arrange
        data = 'Configuration: api_key="secret123" password="mypass"'

        # Act
        sanitized = sanitize_log_data(data)

        # Assert
        assert "secret123" not in sanitized
        assert "mypass" not in sanitized
        assert "api_key=[MASKED]" in sanitized
        assert "password=[MASKED]" in sanitized

    def test_sanitize_log_data_nested_dict(self):
        """Test sanitizing nested dictionary data."""
        # Arrange
        data = {
            "config": {
                "database": {
                    "password": "dbpass123",
                    "host": "localhost"
                },
                "api_key": "secret456"
            },
            "metadata": {
                "version": "1.0"
            }
        }

        # Act
        sanitized = sanitize_log_data(data)

        # Assert
        assert "dbpass123" not in str(sanitized)
        assert "secret456" not in str(sanitized)
        assert sanitized["config"]["database"]["host"] == "localhost"
        assert sanitized["metadata"]["version"] == "1.0"

    def test_sanitize_log_data_object_with_dict(self):
        """Test sanitizing objects with __dict__ attribute."""
        # Arrange
        class TestObject:
            def __init__(self):
                self.api_key = "secret789"
                self.name = "test_object"

        obj = TestObject()

        # Act
        sanitized = sanitize_log_data(obj)

        # Assert
        assert "secret789" not in str(sanitized)
        assert sanitized["name"] == "test_object"

    def test_sanitize_log_data_max_depth(self):
        """Test sanitization respects max depth limit."""
        # Arrange
        # Create deeply nested structure
        data = {"level1": {"level2": {"level3": {"level4": {"level5": {"api_key": "secret"}}}}}}

        # Act
        sanitized = sanitize_log_data(data, max_depth=3)

        # Assert
        # Should reach max depth and stop recursion
        assert "[MAX_DEPTH_REACHED]" in str(sanitized)

    def test_sanitize_log_data_primitive_types(self):
        """Test sanitizing primitive data types."""
        # Assert primitives pass through unchanged
        assert sanitize_log_data(123) == 123
        assert sanitize_log_data(12.34) == 12.34
        assert sanitize_log_data(True) is True
        assert sanitize_log_data(None) is None


@pytest.mark.unit
class TestSensitivePatterns:
    """Test sensitive data patterns."""

    def test_sensitive_patterns_exist(self):
        """Test that sensitive patterns are defined."""
        # Assert
        assert isinstance(SENSITIVE_PATTERNS, dict)
        assert len(SENSITIVE_PATTERNS) > 0
        assert 'api_key' in SENSITIVE_PATTERNS
        assert 'password' in SENSITIVE_PATTERNS
        assert 'email' in SENSITIVE_PATTERNS

    def test_sensitive_patterns_are_compiled_regex(self):
        """Test that sensitive patterns are compiled regex objects."""
        # Assert
        for pattern_name, pattern in SENSITIVE_PATTERNS.items():
            assert hasattr(pattern, 'match')  # Should be compiled regex

    def test_secret_keys_set(self):
        """Test that secret keys set is defined."""
        # Assert
        assert isinstance(SECRET_KEYS, set)
        assert len(SECRET_KEYS) > 0
        assert 'api_key' in SECRET_KEYS
        assert 'password' in SECRET_KEYS
        assert 'authorization' in SECRET_KEYS

    def test_api_key_pattern_matches(self):
        """Test API key pattern matching."""
        # Arrange
        pattern = SENSITIVE_PATTERNS['api_key']
        test_strings = [
            'api_key="abc123"',
            'apikey: def456',
            'access_token = "ghi789"',
            'secret-key="jkl012"'
        ]

        # Act & Assert
        for test_string in test_strings:
            assert pattern.search(test_string) is not None

    def test_password_pattern_matches(self):
        """Test password pattern matching."""
        # Arrange
        pattern = SENSITIVE_PATTERNS['password']
        test_strings = [
            'password="mypass123"',
            'passwd: secretword',
            'pwd = "hidden123"'
        ]

        # Act & Assert
        for test_string in test_strings:
            assert pattern.search(test_string) is not None

    def test_jwt_token_pattern_matches(self):
        """Test JWT token pattern matching."""
        # Arrange
        pattern = SENSITIVE_PATTERNS['jwt_token']
        jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"

        # Act & Assert
        assert pattern.search(jwt_token) is not None

    def test_email_pattern_matches(self):
        """Test email pattern matching."""
        # Arrange
        pattern = SENSITIVE_PATTERNS['email']
        test_emails = [
            "user@example.com",
            "test.email+tag@domain.org",
            "simple@test.co.uk"
        ]

        # Act & Assert
        for email in test_emails:
            assert pattern.search(email) is not None


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security utilities."""

    def test_complete_password_workflow(self):
        """Test complete password workflow: hash and verify."""
        # Arrange
        original_password = "ComplexPassword123!@#"

        # Act
        hashed = hash_password(original_password)
        verify_correct = verify_password(original_password, hashed)
        verify_wrong = verify_password("WrongPassword", hashed)

        # Assert
        assert verify_correct is True
        assert verify_wrong is False
        assert hashed != original_password

    def test_complete_api_key_workflow(self):
        """Test complete API key workflow: generate, hash, verify."""
        # Act
        plain_key, hashed_key = generate_api_key_hash(length=48)
        verify_correct = verify_api_key(plain_key, hashed_key)
        verify_wrong = verify_api_key("wrong_key", hashed_key)

        # Assert
        assert len(plain_key) == 48
        assert verify_correct is True
        assert verify_wrong is False

    def test_comprehensive_log_sanitization(self):
        """Test comprehensive log data sanitization."""
        # Arrange
        complex_data = {
            "request": {
                "headers": {
                    "authorization": "Bearer abc123def456",
                    "user-agent": "MyApp/1.0"
                },
                "body": {
                    "user_email": "user@company.com",
                    "api_key": "secret_key_123456",
                    "preferences": {
                        "theme": "dark",
                        "password": "userpass123"
                    }
                }
            },
            "response": {
                "status": 200,
                "data": "Success"
            },
            "metadata": [
                "Normal log entry",
                "jwt_token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test.signature",
                {"database_url": "postgres://user:pass@localhost/db"}
            ]
        }

        # Act
        sanitized = sanitize_log_data(complex_data)

        # Assert
        sanitized_str = str(sanitized)
        
        # Verify sensitive data is masked
        assert "abc123def456" not in sanitized_str
        assert "secret_key_123456" not in sanitized_str
        assert "userpass123" not in sanitized_str
        assert "user:pass" not in sanitized_str
        
        # Verify non-sensitive data is preserved
        assert sanitized["request"]["headers"]["user-agent"] == "MyApp/1.0"
        assert sanitized["request"]["body"]["preferences"]["theme"] == "dark"
        assert sanitized["response"]["status"] == 200
        assert sanitized["response"]["data"] == "Success"
        
        # Verify email is properly masked
        assert "user@[MASKED]" in sanitized_str

    @patch('chatter.utils.security.settings')
    def test_api_key_hashing_with_settings(self, mock_settings):
        """Test API key hashing uses settings for salt."""
        # Arrange
        mock_settings.secret_key = "test_secret_key_for_salt"
        api_key = "test_api_key"

        # Act
        hashed = hash_api_key(api_key)

        # Assert
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA-256 hex length