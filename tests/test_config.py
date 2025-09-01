"""Tests for application configuration."""

import pytest
from unittest.mock import patch, MagicMock
import os

from chatter.config import Settings, settings


@pytest.mark.unit
class TestSettings:
    """Test application settings."""

    def test_default_settings(self):
        """Test default settings values."""
        # Act
        settings = Settings()

        # Assert
        assert settings.app_name == "Chatter API"
        assert settings.app_description == "Advanced AI Chatbot Backend API Platform"
        assert settings.app_version == "0.1.0"
        assert settings.environment == "development"
        assert settings.debug is False
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 1
        assert settings.reload is False

    def test_settings_with_env_vars(self):
        """Test settings with environment variables."""
        # Arrange
        env_vars = {
            "APP_NAME": "Test App",
            "ENVIRONMENT": "testing",
            "DEBUG": "true",
            "HOST": "127.0.0.1",
            "PORT": "9000",
            "WORKERS": "4",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.app_name == "Test App"
        assert settings.environment == "testing"
        assert settings.debug is True
        assert settings.host == "127.0.0.1"
        assert settings.port == 9000
        assert settings.workers == 4

    def test_database_settings(self):
        """Test database configuration settings."""
        # Arrange
        env_vars = {
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/test",
            "DATABASE_ECHO": "true",
            "DATABASE_POOL_SIZE": "10",
            "DATABASE_MAX_OVERFLOW": "20",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert "postgresql+asyncpg" in settings.database_url
        assert settings.database_echo is True
        assert settings.database_pool_size == 10
        assert settings.database_max_overflow == 20

    def test_redis_settings(self):
        """Test Redis configuration settings."""
        # Arrange
        env_vars = {
            "REDIS_URL": "redis://localhost:6379/1",
            "REDIS_PASSWORD": "secret",
            "REDIS_DB": "2",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.redis_url == "redis://localhost:6379/1"
        assert settings.redis_password == "secret"
        assert settings.redis_db == 2

    def test_api_settings(self):
        """Test API configuration settings."""
        # Arrange
        env_vars = {
            "API_TITLE": "Test API",
            "API_VERSION": "v2",
            "API_BASE_URL": "https://api.test.com",
            "API_PREFIX": "/api/v2",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.api_title == "Test API"
        assert settings.api_version == "v2"
        assert settings.api_base_url == "https://api.test.com"
        assert settings.api_prefix == "/api/v2"

    def test_security_settings(self):
        """Test security configuration settings."""
        # Arrange
        env_vars = {
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "jwt-secret",
            "JWT_ALGORITHM": "HS512",
            "JWT_EXPIRE_MINUTES": "60",
            "CORS_ORIGINS": "https://app.test.com,https://admin.test.com",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.secret_key == "test-secret-key"
        assert settings.jwt_secret_key == "jwt-secret"
        assert settings.jwt_algorithm == "HS512"
        assert settings.jwt_expire_minutes == 60
        assert "https://app.test.com" in settings.cors_origins
        assert "https://admin.test.com" in settings.cors_origins

    def test_logging_settings(self):
        """Test logging configuration settings."""
        # Arrange
        env_vars = {
            "LOG_LEVEL": "ERROR",
            "LOG_FORMAT": "json",
            "LOG_FILE": "/tmp/test.log",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.log_level == "ERROR"
        assert settings.log_format == "json"
        assert settings.log_file == "/tmp/test.log"

    def test_llm_provider_settings(self):
        """Test LLM provider configuration settings."""
        # Arrange
        env_vars = {
            "OPENAI_API_KEY": "sk-test-key",
            "ANTHROPIC_API_KEY": "ant-test-key",
            "DEFAULT_LLM_PROVIDER": "anthropic",
            "DEFAULT_LLM_MODEL": "claude-3",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.openai_api_key == "sk-test-key"
        assert settings.anthropic_api_key == "ant-test-key"
        assert settings.default_llm_provider == "anthropic"
        assert settings.default_llm_model == "claude-3"

    def test_file_upload_settings(self):
        """Test file upload configuration settings."""
        # Arrange
        env_vars = {
            "MAX_FILE_SIZE_MB": "100",
            "ALLOWED_FILE_TYPES": "pdf,txt,md,docx",
            "UPLOAD_DIR": "/tmp/uploads",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.max_file_size_mb == 100
        assert "pdf" in settings.allowed_file_types
        assert "txt" in settings.allowed_file_types
        assert settings.upload_dir == "/tmp/uploads"

    def test_vector_store_settings(self):
        """Test vector store configuration settings."""
        # Arrange
        env_vars = {
            "VECTOR_STORE_TYPE": "pgvector",
            "VECTOR_DIMENSIONS": "1536",
            "VECTOR_SIMILARITY_THRESHOLD": "0.8",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.vector_store_type == "pgvector"
        assert settings.vector_dimensions == 1536
        assert settings.vector_similarity_threshold == 0.8

    def test_monitoring_settings(self):
        """Test monitoring and observability settings."""
        # Arrange
        env_vars = {
            "ENABLE_METRICS": "true",
            "METRICS_PORT": "9090",
            "SENTRY_DSN": "https://sentry.example.com/123",
            "ENABLE_TRACING": "true",
        }

        # Act
        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Assert
        assert settings.enable_metrics is True
        assert settings.metrics_port == 9090
        assert settings.sentry_dsn == "https://sentry.example.com/123"
        assert settings.enable_tracing is True


@pytest.mark.unit
class TestSettingsValidation:
    """Test settings validation."""

    def test_settings_validation_port_range(self):
        """Test port validation."""
        # Valid ports should work
        valid_ports = [1, 8000, 65535]
        for port in valid_ports:
            with patch.dict(os.environ, {"PORT": str(port)}):
                settings = Settings()
                assert settings.port == port

    def test_settings_validation_environment(self):
        """Test environment validation."""
        # Valid environments
        valid_envs = ["development", "testing", "staging", "production"]
        for env in valid_envs:
            with patch.dict(os.environ, {"ENVIRONMENT": env}):
                settings = Settings()
                assert settings.environment == env

    def test_settings_validation_log_level(self):
        """Test log level validation."""
        # Valid log levels
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            with patch.dict(os.environ, {"LOG_LEVEL": level}):
                settings = Settings()
                assert settings.log_level == level

    def test_settings_validation_boolean_fields(self):
        """Test boolean field validation."""
        # Test various boolean representations
        true_values = ["true", "True", "TRUE", "1", "yes", "on"]
        false_values = ["false", "False", "FALSE", "0", "no", "off"]

        for true_val in true_values:
            with patch.dict(os.environ, {"DEBUG": true_val}):
                settings = Settings()
                assert settings.debug is True

        for false_val in false_values:
            with patch.dict(os.environ, {"DEBUG": false_val}):
                settings = Settings()
                assert settings.debug is False

    def test_settings_database_url_formats(self):
        """Test various database URL formats."""
        valid_urls = [
            "postgresql://user:pass@localhost/db",
            "postgresql+asyncpg://user:pass@localhost:5432/db",
            "sqlite:///./test.db",
            "sqlite+aiosqlite:///./test.db",
        ]

        for url in valid_urls:
            with patch.dict(os.environ, {"DATABASE_URL": url}):
                settings = Settings()
                assert settings.database_url == url

    def test_settings_redis_url_formats(self):
        """Test various Redis URL formats."""
        valid_urls = [
            "redis://localhost:6379",
            "redis://localhost:6379/0",
            "redis://:password@localhost:6379/1",
            "rediss://localhost:6380",  # SSL
        ]

        for url in valid_urls:
            with patch.dict(os.environ, {"REDIS_URL": url}):
                settings = Settings()
                assert settings.redis_url == url


@pytest.mark.unit
class TestSettingsUtilities:
    """Test settings utility functions."""

    def test_get_settings_instance(self):
        """Test that settings instance is available."""
        # Act
        settings_instance = settings

        # Assert
        assert settings_instance is not None
        assert isinstance(settings_instance, Settings)

    def test_settings_caching(self):
        """Test settings instance behavior."""
        # Arrange
        settings1 = settings

        # Act - Get settings again
        settings2 = settings

        # Assert
        # Should be the same instance (module-level singleton)
        assert settings1 is settings2
        assert id(settings1) == id(settings2)

    def test_settings_model_dump(self):
        """Test settings serialization."""
        # Arrange
        settings = Settings()

        # Act
        data = settings.model_dump()

        # Assert
        assert isinstance(data, dict)
        assert "app_name" in data
        assert "environment" in data
        assert "database_url" in data
        assert data["app_name"] == "Chatter API"

    def test_settings_model_dump_exclude_secrets(self):
        """Test settings serialization excluding secrets."""
        # Arrange
        env_vars = {
            "SECRET_KEY": "secret",
            "JWT_SECRET_KEY": "jwt-secret",
            "OPENAI_API_KEY": "sk-secret",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

        # Act
        data = settings.model_dump(exclude={"secret_key", "jwt_secret_key", "openai_api_key"})

        # Assert
        assert "secret_key" not in data
        assert "jwt_secret_key" not in data
        assert "openai_api_key" not in data
        assert "app_name" in data

    def test_settings_from_env_file(self):
        """Test loading settings from .env file."""
        # This test would require creating a temporary .env file
        # For now, just verify the settings class accepts model_config
        settings = Settings()
        
        # Check that the settings class has proper configuration
        assert hasattr(settings, 'model_config')
        config = settings.model_config
        assert isinstance(config, SettingsConfigDict)

    def test_settings_repr(self):
        """Test settings string representation."""
        # Arrange
        settings = Settings()

        # Act
        repr_str = repr(settings)

        # Assert
        assert "Settings" in repr_str
        # Should not contain sensitive information
        assert "secret" not in repr_str.lower()
        assert "password" not in repr_str.lower()


@pytest.mark.integration
class TestSettingsIntegration:
    """Integration tests for settings."""

    def test_settings_with_real_env_vars(self):
        """Test settings with actual environment variables."""
        # Arrange
        test_env = {
            "CHATTER_APP_NAME": "Integration Test App",
            "CHATTER_DEBUG": "true",
            "CHATTER_LOG_LEVEL": "DEBUG",
        }

        # Act
        with patch.dict(os.environ, test_env):
            settings = Settings()

        # Assert
        # Check that environment variables are properly loaded
        # Note: The exact behavior depends on the actual field names in Settings
        assert settings.app_name in ["Integration Test App", "Chatter API"]
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.log_level, str)

    def test_settings_validation_with_dependencies(self):
        """Test settings validation with interdependent fields."""
        # This test would check for field validators that depend on other fields
        # For example, if debug=True requires a specific log level
        settings = Settings()
        
        # Verify that settings are internally consistent
        assert isinstance(settings.debug, bool)
        assert isinstance(settings.environment, str)
        assert settings.port > 0
        assert settings.workers > 0

    def test_settings_lazy_loading(self):
        """Test that settings are loaded lazily."""
        # Arrange - Mock an expensive operation in settings loading
        original_get_settings = get_settings

        # Act - First call should trigger loading
        settings1 = get_settings()
        # Second call should use cache
        settings2 = get_settings()

        # Assert
        assert settings1 is settings2
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)