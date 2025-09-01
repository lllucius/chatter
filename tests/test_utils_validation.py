"""Tests for validation utility functions."""

import re
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from chatter.utils.validation import (
    validate_email,
    validate_password,
    validate_url,
    validate_uuid,
    validate_phone_number,
    validate_file_size,
    validate_file_type,
    validate_json_schema,
    sanitize_filename,
    sanitize_html,
    validate_sql_identifier,
    ValidationError,
)


class TestEmailValidation:
    """Test email validation functionality."""

    def test_validate_email_valid(self):
        """Test validation of valid email addresses."""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com",
            "a@b.co",
            "very.long.email.address@very.long.domain.name.com"
        ]
        
        for email in valid_emails:
            result = validate_email(email)
            assert result is True, f"Valid email {email} was rejected"

    def test_validate_email_invalid(self):
        """Test validation of invalid email addresses."""
        invalid_emails = [
            "notanemail",
            "@example.com",
            "user@",
            "user..user@example.com",
            "user@.com",
            "user@com",
            "user name@example.com",
            "",
            None,
            "user@example..com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError):
                validate_email(email)

    def test_validate_email_edge_cases(self):
        """Test email validation edge cases."""
        # Very long email
        long_email = "a" * 50 + "@" + "b" * 50 + ".com"
        with pytest.raises(ValidationError):
            validate_email(long_email)
        
        # Email with special characters
        special_email = "user@exam-ple.com"
        assert validate_email(special_email) is True


class TestPasswordValidation:
    """Test password validation functionality."""

    def test_validate_password_valid(self):
        """Test validation of valid passwords."""
        valid_passwords = [
            "SecurePass123!",
            "P@ssw0rd",
            "MyStr0ng!Pass",
            "ComplexP@ss1"
        ]
        
        for password in valid_passwords:
            result = validate_password(password)
            assert result is True, f"Valid password was rejected"

    def test_validate_password_too_short(self):
        """Test validation of too short passwords."""
        short_passwords = [
            "Pass1!",
            "a1B!",
            "",
            "1234567"
        ]
        
        for password in short_passwords:
            with pytest.raises(ValidationError, match="too short"):
                validate_password(password)

    def test_validate_password_missing_requirements(self):
        """Test validation of passwords missing requirements."""
        # No uppercase
        with pytest.raises(ValidationError, match="uppercase"):
            validate_password("password123!")
        
        # No lowercase
        with pytest.raises(ValidationError, match="lowercase"):
            validate_password("PASSWORD123!")
        
        # No digits
        with pytest.raises(ValidationError, match="digit"):
            validate_password("Password!")
        
        # No special characters
        with pytest.raises(ValidationError, match="special"):
            validate_password("Password123")

    def test_validate_password_none_or_empty(self):
        """Test validation of None or empty passwords."""
        with pytest.raises(ValidationError):
            validate_password(None)
        
        with pytest.raises(ValidationError):
            validate_password("")

    def test_validate_password_custom_min_length(self):
        """Test password validation with custom minimum length."""
        short_but_valid = "Abc1!"
        
        # Should fail with default min length (8)
        with pytest.raises(ValidationError):
            validate_password(short_but_valid)
        
        # Should pass with lower min length
        result = validate_password(short_but_valid, min_length=5)
        assert result is True


class TestUrlValidation:
    """Test URL validation functionality."""

    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://test.org",
            "https://api.example.com/v1/users",
            "https://subdomain.example.co.uk",
            "http://localhost:8080",
            "https://example.com:443/path?param=value#section"
        ]
        
        for url in valid_urls:
            result = validate_url(url)
            assert result is True, f"Valid URL {url} was rejected"

    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        invalid_urls = [
            "notaurl",
            "ftp://example.com",  # Wrong scheme
            "example.com",  # No scheme
            "https://",  # No domain
            "",
            None,
            "javascript:alert('xss')"
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                validate_url(url)

    def test_validate_url_custom_schemes(self):
        """Test URL validation with custom allowed schemes."""
        # Should fail with default schemes
        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")
        
        # Should pass with custom schemes
        result = validate_url("ftp://example.com", allowed_schemes=["http", "https", "ftp"])
        assert result is True


class TestUuidValidation:
    """Test UUID validation functionality."""

    def test_validate_uuid_valid(self):
        """Test validation of valid UUIDs."""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
            "01234567-89ab-cdef-0123-456789abcdef"
        ]
        
        for uuid_str in valid_uuids:
            result = validate_uuid(uuid_str)
            assert result is True, f"Valid UUID {uuid_str} was rejected"

    def test_validate_uuid_invalid(self):
        """Test validation of invalid UUIDs."""
        invalid_uuids = [
            "not-a-uuid",
            "550e8400-e29b-41d4-a716",  # Too short
            "550e8400-e29b-41d4-a716-446655440000-extra",  # Too long
            "550e8400e29b41d4a716446655440000",  # No dashes
            "",
            None,
            "gggggggg-gggg-gggg-gggg-gggggggggggg"  # Invalid characters
        ]
        
        for uuid_str in invalid_uuids:
            with pytest.raises(ValidationError):
                validate_uuid(uuid_str)


class TestPhoneNumberValidation:
    """Test phone number validation functionality."""

    def test_validate_phone_number_valid(self):
        """Test validation of valid phone numbers."""
        valid_phones = [
            "+1234567890",
            "+1-234-567-8900",
            "+44 20 7946 0958",
            "+33 1 42 86 83 26",
            "1234567890",
            "(123) 456-7890"
        ]
        
        for phone in valid_phones:
            result = validate_phone_number(phone)
            assert result is True, f"Valid phone {phone} was rejected"

    def test_validate_phone_number_invalid(self):
        """Test validation of invalid phone numbers."""
        invalid_phones = [
            "123",  # Too short
            "abcdefghij",  # Letters
            "",
            None,
            "+",  # Just plus sign
            "123-45-6789-0123-4567",  # Too long
        ]
        
        for phone in invalid_phones:
            with pytest.raises(ValidationError):
                validate_phone_number(phone)


class TestFileSizeValidation:
    """Test file size validation functionality."""

    def test_validate_file_size_valid(self):
        """Test validation of valid file sizes."""
        # 1MB limit
        max_size = 1024 * 1024
        
        valid_sizes = [0, 1024, 512 * 1024, max_size]
        
        for size in valid_sizes:
            result = validate_file_size(size, max_size_bytes=max_size)
            assert result is True

    def test_validate_file_size_invalid(self):
        """Test validation of invalid file sizes."""
        max_size = 1024 * 1024  # 1MB
        
        invalid_sizes = [
            max_size + 1,
            max_size * 2,
            -1
        ]
        
        for size in invalid_sizes:
            with pytest.raises(ValidationError):
                validate_file_size(size, max_size_bytes=max_size)

    def test_validate_file_size_none(self):
        """Test file size validation with None."""
        with pytest.raises(ValidationError):
            validate_file_size(None)


class TestFileTypeValidation:
    """Test file type validation functionality."""

    def test_validate_file_type_valid(self):
        """Test validation of valid file types."""
        allowed_types = ["image/jpeg", "image/png", "text/plain"]
        
        for file_type in allowed_types:
            result = validate_file_type(file_type, allowed_types=allowed_types)
            assert result is True

    def test_validate_file_type_invalid(self):
        """Test validation of invalid file types."""
        allowed_types = ["image/jpeg", "image/png"]
        
        invalid_types = [
            "application/pdf",
            "text/html",
            "video/mp4",
            "",
            None
        ]
        
        for file_type in invalid_types:
            with pytest.raises(ValidationError):
                validate_file_type(file_type, allowed_types=allowed_types)


class TestJsonSchemaValidation:
    """Test JSON schema validation functionality."""

    def test_validate_json_schema_valid(self):
        """Test validation with valid JSON against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        valid_data = {"name": "John", "age": 30}
        result = validate_json_schema(valid_data, schema)
        assert result is True

    def test_validate_json_schema_invalid(self):
        """Test validation with invalid JSON against schema."""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0}
            },
            "required": ["name"]
        }
        
        invalid_data_cases = [
            {"age": 30},  # Missing required field
            {"name": "John", "age": -1},  # Age below minimum
            {"name": 123},  # Wrong type for name
            "not an object"  # Wrong type entirely
        ]
        
        for data in invalid_data_cases:
            with pytest.raises(ValidationError):
                validate_json_schema(data, schema)


class TestSanitizeFilename:
    """Test filename sanitization functionality."""

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file_with_spaces.txt"),
            ("file/with\\slashes.txt", "file_with_slashes.txt"),
            ("file:with*special?.txt", "file_with_special_.txt"),
            ("file|with<dangerous>.txt", "file_with_dangerous_.txt")
        ]
        
        for input_name, expected in test_cases:
            result = sanitize_filename(input_name)
            assert result == expected

    def test_sanitize_filename_edge_cases(self):
        """Test filename sanitization edge cases."""
        # Empty filename
        assert sanitize_filename("") == "unnamed"
        
        # None input
        assert sanitize_filename(None) == "unnamed"
        
        # Only special characters
        assert sanitize_filename("!!!") == "unnamed"
        
        # Very long filename
        long_name = "a" * 300 + ".txt"
        result = sanitize_filename(long_name)
        assert len(result) <= 255

    def test_sanitize_filename_preserve_extension(self):
        """Test that file extensions are preserved."""
        result = sanitize_filename("my file.pdf")
        assert result.endswith(".pdf")
        
        result = sanitize_filename("file with.multiple.dots.txt")
        assert result.endswith(".txt")


class TestSanitizeHtml:
    """Test HTML sanitization functionality."""

    def test_sanitize_html_basic(self):
        """Test basic HTML sanitization."""
        test_cases = [
            ("Hello <b>world</b>", "Hello world"),
            ("<script>alert('xss')</script>", "alert('xss')"),
            ("<p>Safe paragraph</p>", "Safe paragraph"),
            ("Text & entities", "Text & entities"),
            ("<img src='x' onerror='alert()'>", "")
        ]
        
        for input_html, expected in test_cases:
            result = sanitize_html(input_html)
            assert result == expected

    def test_sanitize_html_none_and_empty(self):
        """Test HTML sanitization with None and empty input."""
        assert sanitize_html(None) == ""
        assert sanitize_html("") == ""

    def test_sanitize_html_preserve_text(self):
        """Test that text content is preserved."""
        html_with_text = "<div>Important <em>information</em> here</div>"
        result = sanitize_html(html_with_text)
        assert "Important" in result
        assert "information" in result
        assert "here" in result


class TestSqlIdentifierValidation:
    """Test SQL identifier validation functionality."""

    def test_validate_sql_identifier_valid(self):
        """Test validation of valid SQL identifiers."""
        valid_identifiers = [
            "table_name",
            "column123",
            "user_id",
            "ValidName",
            "_private",
            "a",
            "table1"
        ]
        
        for identifier in valid_identifiers:
            result = validate_sql_identifier(identifier)
            assert result is True

    def test_validate_sql_identifier_invalid(self):
        """Test validation of invalid SQL identifiers."""
        invalid_identifiers = [
            "123table",  # Starts with number
            "table name",  # Contains space
            "table-name",  # Contains hyphen
            "",  # Empty
            None,  # None
            "select",  # SQL keyword
            "DROP",  # SQL keyword (case insensitive)
            "table;",  # Contains semicolon
            "table/*comment*/"  # Contains comment
        ]
        
        for identifier in invalid_identifiers:
            with pytest.raises(ValidationError):
                validate_sql_identifier(identifier)


class TestValidationError:
    """Test ValidationError exception."""

    def test_validation_error_creation(self):
        """Test ValidationError creation and attributes."""
        error = ValidationError("Test validation failed")
        assert str(error) == "Test validation failed"
        assert isinstance(error, Exception)

    def test_validation_error_with_details(self):
        """Test ValidationError with additional details."""
        error = ValidationError("Validation failed", field="email", value="invalid")
        assert "Validation failed" in str(error)


class TestValidationUtilityIntegration:
    """Test integration of validation utilities."""

    def test_multiple_validations_success(self):
        """Test multiple validations passing."""
        email = "user@example.com"
        password = "SecurePass123!"
        url = "https://api.example.com"
        
        assert validate_email(email) is True
        assert validate_password(password) is True
        assert validate_url(url) is True

    def test_validation_chain_failure(self):
        """Test validation chain where one fails."""
        email = "user@example.com"  # Valid
        password = "weak"  # Invalid
        
        assert validate_email(email) is True
        
        with pytest.raises(ValidationError):
            validate_password(password)

    def test_validation_with_custom_params(self):
        """Test validations with custom parameters."""
        # Password with custom min length
        short_password = "Abc1!"
        assert validate_password(short_password, min_length=4) is True
        
        # URL with custom schemes
        ftp_url = "ftp://files.example.com"
        assert validate_url(ftp_url, allowed_schemes=["ftp"]) is True
        
        # File size with custom limit
        large_size = 5 * 1024 * 1024  # 5MB
        assert validate_file_size(large_size, max_size_bytes=10 * 1024 * 1024) is True
