"""Configuration validation tests."""

import os
from unittest.mock import patch

import pytest

from chatter.utils.config_validator import ConfigValidator


@pytest.mark.unit
class TestConfigValidator:
    """Test configuration validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = ConfigValidator()

    def test_weak_secret_key_detection(self):
        """Test detection of weak secret keys."""
        weak_keys = [
            "secret",
            "password",
            "your-secret-key",
            "development",
            "test",
            "admin",
            "default",
            "12345678",
            "secret123",
            "mysecretkey"
        ]

        for weak_key in weak_keys:
            with pytest.raises(ValueError, match="weak|insecure|default"):
                self.validator.validate_secret_key(weak_key)

    def test_short_secret_key_rejection(self):
        """Test rejection of short secret keys."""
        short_keys = [
            "abc",
            "short",
            "1234567",  # Less than 8 characters
            "",
            "a" * 7
        ]

        for short_key in short_keys:
            with pytest.raises(ValueError, match="too short|length"):
                self.validator.validate_secret_key(short_key)

    def test_strong_secret_key_acceptance(self):
        """Test acceptance of strong secret keys."""
        strong_keys = [
            "kJ8#mN2$pQ9@vR4&sT7!uW1%xY3^zB6*",
            "randomly_generated_secure_key_with_32_chars",
            "Pr0duct1on$ecur3K3y2024!@#",
            "s3cur3-r4nd0m-k3y-w1th-sp3c14l-ch4rs!",
            "A" * 32 + "B" * 32  # 64 chars
        ]

        for strong_key in strong_keys:
            # Should not raise any exception
            self.validator.validate_secret_key(strong_key)

    def test_database_credential_validation(self):
        """Test database credential validation."""
        # Test default/weak database credentials
        weak_configs = [
            {"DB_USER": "postgres", "DB_PASSWORD": "password"},
            {"DB_USER": "admin", "DB_PASSWORD": "admin"},
            {"DB_USER": "root", "DB_PASSWORD": "root"},
            {"DB_USER": "user", "DB_PASSWORD": ""},
            {"DB_USER": "postgres", "DB_PASSWORD": "postgres"},
            {"DB_USER": "admin", "DB_PASSWORD": "123456"},
        ]

        for config in weak_configs:
            with pytest.raises(ValueError, match="default|weak|insecure"):
                self.validator.validate_database_config(config)

    def test_secure_database_config_acceptance(self):
        """Test acceptance of secure database configurations."""
        secure_configs = [
            {
                "DB_USER": "chatter_prod_user_2024",
                "DB_PASSWORD": "sUp3r$3cur3P4ssw0rd!2024"
            },
            {
                "DB_USER": "app_service_account",
                "DB_PASSWORD": "kJ8#mN2$pQ9@vR4&sT7!uW1%xY3^zB6*"
            },
            {
                "DB_USER": "production_db_user",
                "DB_PASSWORD": "Pr0duct1on_DB_P4ssw0rd_2024!"
            }
        ]

        for config in secure_configs:
            # Should not raise any exception
            self.validator.validate_database_config(config)

    def test_api_key_validation(self):
        """Test API key validation."""
        # Test weak/demo API keys
        weak_api_keys = [
            "sk-test123",
            "demo_key",
            "your_api_key_here",
            "test_api_key",
            "development_key",
            "sk-1234567890",
            "api_key_placeholder"
        ]

        for api_key in weak_api_keys:
            with pytest.raises(ValueError, match="test|demo|placeholder|weak"):
                self.validator.validate_api_key(api_key)

    def test_secure_api_key_acceptance(self):
        """Test acceptance of secure API keys."""
        secure_api_keys = [
            "sk-proj-abcdef1234567890abcdef1234567890abcdef12",
            "live_pk_1234567890abcdef1234567890abcdef",
            "prod_sk_abcdef1234567890abcdef1234567890abcdef",
            "sk-live-abcdef1234567890abcdef1234567890abcdef"
        ]

        for api_key in secure_api_keys:
            # Should not raise any exception
            self.validator.validate_api_key(api_key)

    def test_redis_configuration_validation(self):
        """Test Redis configuration validation."""
        # Test insecure Redis configs
        insecure_configs = [
            {"REDIS_HOST": "localhost", "REDIS_PASSWORD": ""},
            {"REDIS_HOST": "127.0.0.1", "REDIS_PASSWORD": None},
            {"REDIS_HOST": "redis", "REDIS_PASSWORD": "password"},
            {"REDIS_HOST": "localhost", "REDIS_PASSWORD": "redis"},
        ]

        for config in insecure_configs:
            with pytest.raises(ValueError, match="password|insecure|authentication"):
                self.validator.validate_redis_config(config)

    def test_secure_redis_config_acceptance(self):
        """Test acceptance of secure Redis configurations."""
        secure_configs = [
            {
                "REDIS_HOST": "redis.production.com",
                "REDIS_PASSWORD": "sUp3r$3cur3R3d1sP4ss!"
            },
            {
                "REDIS_HOST": "redis-cluster.internal",
                "REDIS_PASSWORD": "kJ8#mN2$pQ9@vR4&sT7!uW1%",
                "REDIS_TLS": True
            }
        ]

        for config in secure_configs:
            # Should not raise any exception
            self.validator.validate_redis_config(config)

    def test_environment_specific_validation(self):
        """Test environment-specific validation rules."""
        # Production environment should have stricter rules
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            validator = ConfigValidator()

            # Even moderately secure keys should be rejected in production
            with pytest.raises(ValueError):
                validator.validate_secret_key("development_key_but_long_enough")

        # Development environment should be more lenient
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            validator = ConfigValidator()

            # Should accept development keys in dev environment
            validator.validate_secret_key("development_secret_key_123")

    def test_ssl_tls_configuration_validation(self):
        """Test SSL/TLS configuration validation."""
        # Test that production requires SSL/TLS
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            validator = ConfigValidator()

            insecure_configs = [
                {"DATABASE_URL": "postgresql://user:pass@host:5432/db"},
                {"REDIS_URL": "redis://user:pass@host:6379"},
                {"API_BASE_URL": "http://api.example.com"}
            ]

            for config in insecure_configs:
                with pytest.raises(ValueError, match="SSL|TLS|https|secure"):
                    validator.validate_url_security(list(config.values())[0])

        # Test secure URLs are accepted
        secure_urls = [
            "postgresql://user:pass@host:5432/db?sslmode=require",
            "rediss://user:pass@host:6380",  # Redis with SSL
            "https://api.example.com"
        ]

        for url in secure_urls:
            validator.validate_url_security(url)

    def test_configuration_completeness(self):
        """Test that all required configuration is present."""
        required_configs = [
            "SECRET_KEY",
            "DATABASE_URL",
            "OPENAI_API_KEY",
            "REDIS_URL"
        ]

        # Test missing configuration detection
        incomplete_config = {
            "SECRET_KEY": "test_key_123456789",
            "DATABASE_URL": "postgresql://localhost/test"
            # Missing OPENAI_API_KEY and REDIS_URL
        }

        missing = self.validator.validate_completeness(incomplete_config, required_configs)
        assert "OPENAI_API_KEY" in missing
        assert "REDIS_URL" in missing

        # Test complete configuration
        complete_config = {
            "SECRET_KEY": "secure_secret_key_123456789",
            "DATABASE_URL": "postgresql://user:pass@host/db",
            "OPENAI_API_KEY": "sk-proj-1234567890abcdef",
            "REDIS_URL": "redis://localhost:6379"
        }

        missing = self.validator.validate_completeness(complete_config, required_configs)
        assert len(missing) == 0


@pytest.mark.unit
class TestConfigurationPatterns:
    """Test configuration pattern detection."""

    def test_sensitive_data_detection(self):
        """Test detection of sensitive data in configuration."""
        validator = ConfigValidator()

        sensitive_patterns = [
            "password=secret123",
            "api_key=sk-test",
            "token=abcd1234",
            "private_key=-----BEGIN",
            "secret=mysecret"
        ]

        for pattern in sensitive_patterns:
            detected = validator.detect_sensitive_patterns(pattern)
            assert len(detected) > 0

    def test_placeholder_detection(self):
        """Test detection of placeholder values."""
        validator = ConfigValidator()

        placeholders = [
            "your_api_key_here",
            "replace_with_actual_key",
            "TODO: add real password",
            "changeme",
            "example.com",
            "localhost",
            "127.0.0.1"
        ]

        for placeholder in placeholders:
            assert validator.is_placeholder_value(placeholder)

    def test_real_values_not_detected_as_placeholders(self):
        """Test that real values are not detected as placeholders."""
        validator = ConfigValidator()

        real_values = [
            "sk-proj-real1234567890abcdef1234567890abcdef",
            "production.database.com",
            "redis-cluster.internal.com",
            "secure_secret_key_for_production_2024"
        ]

        for value in real_values:
            assert not validator.is_placeholder_value(value)


@pytest.mark.integration
class TestConfigValidationIntegration:
    """Integration tests for configuration validation."""

    def test_full_configuration_validation(self):
        """Test complete configuration validation workflow."""
        validator = ConfigValidator()

        # Test a complete production-like configuration
        production_config = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "prod_secret_key_2024_very_secure_and_long!",
            "DATABASE_URL": "postgresql://prod_user:secure_pass@db.internal:5432/chatter?sslmode=require",
            "REDIS_URL": "rediss://user:secure_redis_pass@redis.internal:6380",
            "OPENAI_API_KEY": "sk-proj-1234567890abcdef1234567890abcdef1234567890",
            "ANTHROPIC_API_KEY": "sk-ant-api03-real_key_here_1234567890abcdef",
            "CORS_ORIGINS": "https://app.chatter.com,https://admin.chatter.com"
        }

        # Should validate without errors
        result = validator.validate_full_config(production_config)
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_development_configuration_validation(self):
        """Test development configuration validation."""
        validator = ConfigValidator()

        # Development config should be more lenient
        dev_config = {
            "ENVIRONMENT": "development",
            "SECRET_KEY": "dev_secret_key_for_local_testing",
            "DATABASE_URL": "postgresql://localhost/chatter_dev",
            "REDIS_URL": "redis://localhost:6379",
            "OPENAI_API_KEY": "sk-test-1234567890abcdef",  # Test key OK in dev
            "CORS_ORIGINS": "*"  # Wildcard OK in dev
        }

        result = validator.validate_full_config(dev_config)
        assert result["valid"] is True

    def test_invalid_configuration_reporting(self):
        """Test that invalid configurations are properly reported."""
        validator = ConfigValidator()

        # Configuration with multiple issues
        invalid_config = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "weak",  # Too weak
            "DATABASE_URL": "postgresql://postgres:password@localhost/db",  # Default creds
            "REDIS_URL": "redis://localhost:6379",  # No password
            "OPENAI_API_KEY": "sk-test-123",  # Test key in production
        }

        result = validator.validate_full_config(invalid_config)
        assert result["valid"] is False
        assert len(result["errors"]) >= 4  # Should catch multiple issues

        # Check specific error categories
        error_messages = " ".join(result["errors"])
        assert "secret" in error_messages.lower()
        assert "password" in error_messages.lower()
        assert "test" in error_messages.lower()
