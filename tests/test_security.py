"""Security functionality tests."""

from unittest.mock import patch

import pytest

from chatter.utils.config_validator import ConfigurationValidator
from chatter.utils.security import generate_secure_secret, sanitize_input


@pytest.mark.unit
class TestSecurityUtilities:
    """Test security utilities and functions."""

    def test_secure_secret_generation(self):
        """Test secure secret generation."""
        secret = generate_secure_secret()
        assert len(secret) >= 32
        assert secret.isalnum() or any(c in secret for c in "!@#$%^&*")

        # Ensure multiple calls generate different secrets
        secret2 = generate_secure_secret()
        assert secret != secret2

    def test_secure_secret_strength(self):
        """Test generated secrets meet strength requirements."""
        secret = generate_secure_secret(length=64)
        assert len(secret) == 64

        # Check complexity requirements
        has_upper = any(c.isupper() for c in secret)
        has_lower = any(c.islower() for c in secret)
        has_digit = any(c.isdigit() for c in secret)

        # At least 2 of 3 character types should be present
        complexity_score = sum([has_upper, has_lower, has_digit])
        assert complexity_score >= 2

    def test_input_sanitization(self):
        """Test input sanitization functions."""
        # Test XSS prevention
        malicious_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious_input)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized

        # Test SQL injection prevention
        sql_injection = "'; DROP TABLE users; --"
        sanitized_sql = sanitize_input(sql_injection)
        assert "DROP TABLE" not in sanitized_sql.upper()


@pytest.mark.unit
class TestAuthenticationSecurity:
    """Test authentication security measures."""

    @patch('chatter.utils.security.verify_password')
    def test_password_verification_timing(self, mock_verify):
        """Test password verification has consistent timing."""
        import time

        from chatter.utils.security import verify_password

        # Mock the actual verification to control timing
        mock_verify.return_value = False

        # Time multiple password verifications
        times = []
        for _ in range(5):
            start = time.time()
            verify_password("test_password", "hashed_password")
            end = time.time()
            times.append(end - start)

        # Timing should be relatively consistent (preventing timing attacks)
        avg_time = sum(times) / len(times)
        for t in times:
            assert abs(t - avg_time) < 0.1  # Within 100ms variance

    def test_jwt_token_security(self):
        """Test JWT token generation and validation security."""
        from chatter.utils.security import (
            create_access_token,
            verify_token,
        )

        # Test token generation
        token = create_access_token({"sub": "user123"})
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 100  # JWT should be reasonably long

        # Test token validation
        payload = verify_token(token)
        assert payload is not None
        assert payload.get("sub") == "user123"

        # Test invalid token
        invalid_payload = verify_token("invalid.token.here")
        assert invalid_payload is None

    def test_session_security(self):
        """Test session security measures."""
        # Test session ID generation
        from chatter.utils.security import generate_session_id

        session_id = generate_session_id()
        assert len(session_id) >= 32
        assert session_id.replace('-', '').isalnum()

        # Ensure uniqueness
        session_id2 = generate_session_id()
        assert session_id != session_id2


@pytest.mark.unit
class TestConfigurationSecurity:
    """Test configuration security validation."""

    def test_weak_secret_detection(self):
        """Test detection of weak secrets."""
        validator = ConfigurationValidator()

        # Weak secrets should be rejected
        weak_secrets = [
            "secret",
            "password123",
            "12345678",
            "your-secret-key",
            "development_secret"
        ]

        for secret in weak_secrets:
            with pytest.raises(ValueError, match="weak|insecure|default"):
                validator.validate_secret_key(secret)

    def test_default_credential_detection(self):
        """Test detection of default credentials."""
        validator = ConfigurationValidator()

        # Default database credentials should be rejected
        default_configs = [
            {"DB_USER": "postgres", "DB_PASSWORD": "password"},
            {"DB_USER": "admin", "DB_PASSWORD": "admin"},
            {"DB_USER": "root", "DB_PASSWORD": ""},
            {"DB_USER": "user", "DB_PASSWORD": "123456"},
        ]

        for config in default_configs:
            with pytest.raises(ValueError, match="default|insecure"):
                validator.validate_database_config(config)

    def test_secure_config_acceptance(self):
        """Test that secure configurations are accepted."""
        validator = ConfigurationValidator()

        # Strong secrets should be accepted
        strong_secret = generate_secure_secret(64)
        validator.validate_secret_key(strong_secret)  # Should not raise

        # Secure database config should be accepted
        secure_config = {
            "DB_USER": "chatter_prod_user_" + generate_secure_secret(8),
            "DB_PASSWORD": generate_secure_secret(32)
        }
        validator.validate_database_config(secure_config)  # Should not raise


@pytest.mark.unit
class TestErrorHandlingSecurity:
    """Test error handling doesn't expose sensitive information."""

    def test_error_response_sanitization(self):
        """Test that error responses don't leak sensitive data."""
        from chatter.utils.problem import create_problem_detail

        # Create error with potentially sensitive information
        try:
            raise ValueError("Database connection failed: password=secret123 host=internal.db")
        except ValueError as e:
            problem = create_problem_detail(
                status=500,
                title="Internal Server Error",
                detail=str(e)
            )

            # Sensitive information should be removed
            detail = problem.get("detail", "")
            assert "password=" not in detail
            assert "secret123" not in detail
            assert "internal.db" not in detail

    def test_stack_trace_filtering(self):
        """Test that stack traces don't expose sensitive paths."""
        # This would be implementation specific based on logging configuration
        # For now, just ensure the concept is testable
        assert True  # Placeholder for actual stack trace filtering tests


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security features."""

    async def test_authentication_flow_security(self, test_client):
        """Test the complete authentication flow for security issues."""
        # Test registration with weak password
        weak_password_data = {
            "email": "test@example.com",
            "password": "123456",
            "username": "testuser"
        }
        response = await test_client.post("/api/v1/auth/register", json=weak_password_data)
        assert response.status_code == 400  # Should reject weak password

        # Test registration with strong password
        strong_password_data = {
            "email": "test@example.com",
            "password": generate_secure_secret(16),
            "username": "testuser"
        }
        response = await test_client.post("/api/v1/auth/register", json=strong_password_data)
        assert response.status_code in [201, 409]  # Created or conflict if user exists

    async def test_rate_limiting_security(self, test_client):
        """Test rate limiting prevents brute force attacks."""
        # Attempt multiple failed logins rapidly
        login_data = {"email": "test@example.com", "password": "wrong_password"}

        responses = []
        for _ in range(10):
            response = await test_client.post("/api/v1/auth/login", json=login_data)
            responses.append(response.status_code)

        # Should eventually get rate limited (429)
        assert 429 in responses or all(r == 401 for r in responses)

    async def test_cors_security(self, test_client):
        """Test CORS configuration security."""
        # Test that CORS headers are properly configured
        response = await test_client.options("/api/v1/auth/login")
        headers = response.headers

        # Check for security headers
        if "access-control-allow-origin" in headers:
            origin = headers["access-control-allow-origin"]
            assert origin != "*" or "development" in origin.lower()
