"""Utility tests."""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
from chatter.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    generate_secure_secret
)
from chatter.utils.logging import get_logger, setup_logging
from chatter.utils.problem import create_problem_detail, ProblemDetailResponse
from chatter.utils.validation import (
    validate_email,
    validate_password,
    validate_username,
    sanitize_input
)


@pytest.mark.unit
class TestAuthenticationUtilities:
    """Test authentication utility functions."""

    def test_password_hashing_and_verification(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        
        # Test hashing
        hashed = hash_password(password)
        assert hashed != password
        assert len(hashed) > 50  # Bcrypt hashes are long
        assert hashed.startswith('$2b$')  # Bcrypt identifier
        
        # Test verification
        assert verify_password(password, hashed)
        assert not verify_password("wrong_password", hashed)
        assert not verify_password("", hashed)
        
        # Test hash uniqueness (salt should make each hash different)
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        assert hash1 != hash2
        
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_jwt_token_creation_and_validation(self):
        """Test JWT token creation and validation."""
        # Test token creation
        payload = {"sub": "user123", "username": "testuser"}
        token = create_access_token(payload)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWT tokens are long
        
        # Test token validation
        decoded_payload = verify_token(token)
        assert decoded_payload is not None
        assert decoded_payload["sub"] == "user123"
        assert decoded_payload["username"] == "testuser"
        assert "exp" in decoded_payload  # Should have expiration
        
        # Test token expiration
        exp_time = datetime.utcnow() + timedelta(hours=1)
        assert decoded_payload["exp"] <= exp_time.timestamp()

    def test_token_expiration_handling(self):
        """Test token expiration handling."""
        # Create expired token
        past_time = datetime.utcnow() - timedelta(hours=1)
        expired_payload = {
            "sub": "user123",
            "exp": past_time.timestamp()
        }
        
        with patch('chatter.utils.security.SECRET_KEY', 'test_secret_key'):
            expired_token = jwt.encode(expired_payload, 'test_secret_key', algorithm='HS256')
            
            # Should return None for expired token
            decoded = verify_token(expired_token)
            assert decoded is None

    def test_invalid_token_handling(self):
        """Test invalid token handling."""
        # Test invalid tokens
        invalid_tokens = [
            "invalid.token.here",
            "not_a_token_at_all",
            "",
            None,
            "header.invalid_payload.signature"
        ]
        
        for invalid_token in invalid_tokens:
            decoded = verify_token(invalid_token)
            assert decoded is None

    def test_secure_secret_generation(self):
        """Test secure secret generation."""
        # Test default length
        secret = generate_secure_secret()
        assert len(secret) >= 32
        assert secret.isalnum() or any(c in secret for c in "!@#$%^&*()_+-=")
        
        # Test custom length
        secret64 = generate_secure_secret(64)
        assert len(secret64) == 64
        
        # Test uniqueness
        secret1 = generate_secure_secret()
        secret2 = generate_secure_secret()
        assert secret1 != secret2
        
        # Test character requirements
        has_upper = any(c.isupper() for c in secret)
        has_lower = any(c.islower() for c in secret)
        has_digit = any(c.isdigit() for c in secret)
        
        # Should have at least 2 of 3 character types
        complexity_score = sum([has_upper, has_lower, has_digit])
        assert complexity_score >= 2

    def test_security_edge_cases(self):
        """Test security edge cases."""
        # Test empty password
        with pytest.raises(ValueError):
            hash_password("")
        
        # Test None password
        with pytest.raises((ValueError, TypeError)):
            hash_password(None)
        
        # Test very long password
        long_password = "a" * 1000
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed)
        
        # Test unicode password
        unicode_password = "παρόλο123!🔒"
        hashed_unicode = hash_password(unicode_password)
        assert verify_password(unicode_password, hashed_unicode)


@pytest.mark.unit
class TestLoggingUtilities:
    """Test logging utility functions."""

    def test_logger_creation_and_configuration(self):
        """Test logger creation and configuration."""
        # Test basic logger creation
        logger = get_logger("test_module")
        assert logger.name == "test_module"
        
        # Test logger with different modules
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1.name == "module1"
        assert logger2.name == "module2"
        assert logger1 != logger2

    def test_logger_hierarchy_management(self):
        """Test logger hierarchy management."""
        # Test parent-child logger relationships
        parent_logger = get_logger("parent")
        child_logger = get_logger("parent.child")
        grandchild_logger = get_logger("parent.child.grandchild")
        
        assert child_logger.parent == parent_logger
        assert grandchild_logger.parent == child_logger

    def test_structured_logging_support(self):
        """Test structured logging support."""
        logger = get_logger("structured_test")
        
        # Test logging with extra fields
        with patch.object(logger, 'info') as mock_info:
            logger.info("Test message", extra={
                "user_id": "123",
                "request_id": "req-456",
                "action": "login"
            })
            
            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert args[0] == "Test message"
            assert "extra" in kwargs
            assert kwargs["extra"]["user_id"] == "123"

    def test_log_level_configuration(self):
        """Test log level configuration."""
        with patch('chatter.utils.logging.setup_logging') as mock_setup:
            # Test different log levels
            setup_logging(level="DEBUG")
            mock_setup.assert_called_with(level="DEBUG")
            
            setup_logging(level="INFO")
            mock_setup.assert_called_with(level="INFO")
            
            setup_logging(level="ERROR")
            mock_setup.assert_called_with(level="ERROR")

    def test_log_formatting(self):
        """Test log message formatting."""
        logger = get_logger("format_test")
        
        # Test that logger handles different data types
        with patch.object(logger, 'info') as mock_info:
            # String message
            logger.info("String message")
            mock_info.assert_called()
            
            # Dictionary message
            logger.info({"key": "value", "number": 123})
            
            # Mixed arguments
            logger.info("User %s performed action %s", "alice", "login")


@pytest.mark.unit  
class TestProblemDetailUtilities:
    """Test RFC 9457 Problem Detail utilities."""

    def test_error_response_formatting(self):
        """Test error response formatting."""
        # Test basic problem detail
        problem = create_problem_detail(
            status=400,
            title="Bad Request",
            detail="The request was malformed"
        )
        
        assert problem["status"] == 400
        assert problem["title"] == "Bad Request"
        assert problem["detail"] == "The request was malformed"
        assert problem["type"] == "about:blank"  # Default type

    def test_http_status_code_mapping(self):
        """Test HTTP status code mapping."""
        # Test common status codes
        status_codes = [400, 401, 403, 404, 409, 422, 500, 503]
        
        for status in status_codes:
            problem = create_problem_detail(
                status=status,
                title=f"Error {status}",
                detail=f"Status code {status} error"
            )
            assert problem["status"] == status

    def test_problem_serialization(self):
        """Test problem detail serialization."""
        problem = create_problem_detail(
            status=422,
            title="Validation Error",
            detail="Request validation failed",
            instance="/api/v1/users",
            field_errors={
                "email": ["Invalid email format"],
                "password": ["Password too weak"]
            }
        )
        
        # Test all fields are present
        assert problem["status"] == 422
        assert problem["title"] == "Validation Error"
        assert problem["detail"] == "Request validation failed"
        assert problem["instance"] == "/api/v1/users"
        assert problem["field_errors"]["email"] == ["Invalid email format"]
        assert problem["field_errors"]["password"] == ["Password too weak"]

    def test_problem_detail_response(self):
        """Test ProblemDetailResponse creation."""
        response = ProblemDetailResponse(
            status=400,
            title="Bad Request",
            detail="Invalid input data",
            validation_errors={"name": "Required field"}
        )
        
        assert response.status_code == 400
        assert response.media_type == "application/problem+json"
        
        # Test response body
        import json
        body_data = json.loads(response.body.decode())
        assert body_data["status"] == 400
        assert body_data["title"] == "Bad Request"
        assert body_data["validation_errors"]["name"] == "Required field"

    def test_custom_problem_types(self):
        """Test custom problem types."""
        problem = create_problem_detail(
            status=409,
            title="Resource Conflict",
            detail="User already exists",
            type_="https://api.example.com/problems/user-exists",
            instance="/api/v1/users/123",
            existing_user_id="456"
        )
        
        assert problem["type"] == "https://api.example.com/problems/user-exists"
        assert problem["instance"] == "/api/v1/users/123"
        assert problem["existing_user_id"] == "456"


@pytest.mark.unit
class TestValidationUtilities:
    """Test validation utility functions."""

    def test_email_format_validation(self):
        """Test email format validation."""
        # Valid emails
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "firstname.lastname@company.com",
            "user123@test-domain.com",
            "valid.email@sub.domain.com"
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
            "",
            None
        ]
        
        for email in invalid_emails:
            assert not validate_email(email), f"Should reject invalid email: {email}"

    def test_username_requirements(self):
        """Test username requirements."""
        # Valid usernames
        valid_usernames = [
            "user123",
            "testuser",
            "user_name",
            "user-name",
            "validuser2024",
            "abc",  # Minimum length
            "a" * 30  # Maximum valid length
        ]
        
        for username in valid_usernames:
            assert validate_username(username), f"Should accept valid username: {username}"

        # Invalid usernames
        invalid_usernames = [
            "ab",  # Too short
            "a" * 31,  # Too long
            "user name",  # Space
            "user@name",  # Invalid character
            "123user",  # Starts with number
            "_username",  # Starts with underscore
            "",
            None
        ]
        
        for username in invalid_usernames:
            assert not validate_username(username), f"Should reject invalid username: {username}"

    def test_password_strength_checking(self):
        """Test password strength checking."""
        # Strong passwords
        strong_passwords = [
            "MySecure123!",
            "C0mpl3x_P@ssw0rd",
            "VerySafe#2024",
            "Super$trong9Pass"
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
            "Password1"  # Common pattern
        ]
        
        for password in weak_passwords:
            result = validate_password(password)
            assert not result["valid"], f"Should reject weak password: {password}"

    def test_input_sanitization(self):
        """Test input sanitization."""
        # XSS attempts
        xss_tests = [
            ("<script>alert('xss')</script>", "alert"),
            ("javascript:alert('xss')", "javascript"),
            ("<img src=x onerror=alert('xss')>", "onerror"),
            ("onclick='alert(1)'", "onclick"),
            ("<svg onload=alert('xss')>", "onload")
        ]
        
        for malicious_input, dangerous_part in xss_tests:
            sanitized = sanitize_input(malicious_input)
            assert dangerous_part not in sanitized.lower()

        # SQL injection attempts
        sql_tests = [
            ("'; DROP TABLE users; --", "DROP TABLE"),
            ("admin'; --", "'; --"),
            ("' OR '1'='1", "OR '1'='1"),
            ("'; INSERT INTO", "INSERT INTO"),
            ("' UNION SELECT", "UNION SELECT")
        ]
        
        for sql_input, dangerous_part in sql_tests:
            sanitized = sanitize_input(sql_input)
            assert dangerous_part not in sanitized.upper()

        # Path traversal attempts
        path_tests = [
            ("../../../etc/passwd", "../"),
            ("..\\..\\..\\windows\\system32", "..\\"),
            ("....//....//....//etc/passwd", "//"),
        ]
        
        for path_input, dangerous_part in path_tests:
            sanitized = sanitize_input(path_input)
            assert dangerous_part not in sanitized

    def test_validation_edge_cases(self):
        """Test validation edge cases."""
        # Test None inputs
        assert not validate_email(None)
        assert not validate_username(None)
        
        # Test empty strings
        assert not validate_email("")
        assert not validate_username("")
        
        # Test very long inputs
        long_string = "a" * 1000
        assert not validate_email(long_string + "@example.com")
        assert not validate_username(long_string)

    def test_custom_validation_rules(self):
        """Test custom validation rules."""
        # Test that validation functions can be extended
        def validate_custom_field(value):
            """Custom validation example."""
            if not value:
                return False
            if len(value) < 5:
                return False
            if not any(c.isdigit() for c in value):
                return False
            return True
        
        assert validate_custom_field("valid123")
        assert not validate_custom_field("short")
        assert not validate_custom_field("nodigits")
        assert not validate_custom_field("")


@pytest.mark.unit
class TestUtilityIntegration:
    """Test utility function integration."""

    def test_authentication_flow_utilities(self):
        """Test authentication flow using multiple utilities."""
        # 1. Validate user input
        email = "test@example.com"
        username = "testuser"
        password = "SecurePass123!"
        
        assert validate_email(email)
        assert validate_username(username)
        password_result = validate_password(password)
        assert password_result["valid"]
        
        # 2. Hash password
        hashed_password = hash_password(password)
        assert verify_password(password, hashed_password)
        
        # 3. Create token
        token_payload = {"sub": "user123", "email": email, "username": username}
        token = create_access_token(token_payload)
        
        # 4. Verify token
        decoded = verify_token(token)
        assert decoded["email"] == email
        assert decoded["username"] == username

    def test_error_handling_utilities(self):
        """Test error handling using multiple utilities."""
        # 1. Create logger
        logger = get_logger("error_test")
        
        # 2. Handle validation error
        try:
            # Simulate validation failure
            if not validate_email("invalid-email"):
                raise ValueError("Invalid email format")
        except ValueError as e:
            # 3. Log error
            logger.error(f"Validation error: {str(e)}")
            
            # 4. Create problem detail response
            problem = create_problem_detail(
                status=400,
                title="Validation Error",
                detail=str(e),
                field_errors={"email": ["Invalid email format"]}
            )
            
            assert problem["status"] == 400
            assert problem["field_errors"]["email"] == ["Invalid email format"]

    def test_input_processing_pipeline(self):
        """Test complete input processing pipeline."""
        # Simulate user input
        raw_input = {
            "email": "  TEST@EXAMPLE.COM  ",
            "username": "TestUser123",
            "password": "MySecurePass123!",
            "bio": "<script>alert('xss')</script>I'm a developer"
        }
        
        # 1. Sanitize and normalize
        processed_input = {
            "email": raw_input["email"].strip().lower(),
            "username": raw_input["username"].lower(),
            "password": raw_input["password"],
            "bio": sanitize_input(raw_input["bio"])
        }
        
        # 2. Validate
        assert validate_email(processed_input["email"])
        assert validate_username(processed_input["username"])
        assert validate_password(processed_input["password"])["valid"]
        
        # 3. Verify sanitization
        assert "<script>" not in processed_input["bio"]
        assert "alert" not in processed_input["bio"]
        assert "I'm a developer" in processed_input["bio"]

    def test_security_utilities_integration(self):
        """Test security utilities working together."""
        # Generate secure secret for app
        app_secret = generate_secure_secret(64)
        assert len(app_secret) == 64
        
        # Use secret in token creation (mock)
        with patch('chatter.utils.security.SECRET_KEY', app_secret):
            # Create token
            payload = {"sub": "user123", "role": "admin"}
            token = create_access_token(payload)
            
            # Verify token with same secret
            decoded = verify_token(token)
            assert decoded["sub"] == "user123"
            assert decoded["role"] == "admin"

    def test_logging_and_monitoring_integration(self):
        """Test logging and monitoring utilities integration."""
        # Create logger with monitoring context
        logger = get_logger("monitoring_test")
        
        # Simulate monitoring data
        monitoring_data = {
            "request_id": "req-123",
            "user_id": "user-456", 
            "endpoint": "/api/v1/test",
            "method": "POST",
            "status_code": 200,
            "response_time": 0.15
        }
        
        # Log with structured data
        with patch.object(logger, 'info') as mock_info:
            logger.info("Request completed", extra=monitoring_data)
            
            mock_info.assert_called_once_with("Request completed", extra=monitoring_data)

    def test_validation_and_error_reporting_integration(self):
        """Test validation and error reporting integration."""
        # Collect validation errors
        validation_errors = {}
        
        test_data = {
            "email": "invalid-email",
            "username": "ab",  # Too short
            "password": "weak"
        }
        
        # Validate each field
        if not validate_email(test_data["email"]):
            validation_errors["email"] = ["Invalid email format"]
        
        if not validate_username(test_data["username"]):
            validation_errors["username"] = ["Username too short"]
        
        password_result = validate_password(test_data["password"])
        if not password_result["valid"]:
            validation_errors["password"] = ["Password too weak"]
        
        # Create comprehensive error response
        if validation_errors:
            problem = create_problem_detail(
                status=422,
                title="Validation Failed",
                detail="Multiple validation errors occurred",
                field_errors=validation_errors
            )
            
            assert problem["status"] == 422
            assert len(problem["field_errors"]) == 3
            assert "email" in problem["field_errors"]
            assert "username" in problem["field_errors"]
            assert "password" in problem["field_errors"]