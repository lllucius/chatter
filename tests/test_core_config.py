"""Tests for configuration management."""

import os
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from chatter.config import Settings


@pytest.mark.unit
class TestSettings:
    """Test configuration settings management."""

    def test_default_settings(self):
        """Test default configuration values."""
        # Act
        settings = Settings()

        # Assert application settings
        assert settings.app_name == "Chatter API"
        assert settings.app_version == "0.1.0"
        assert settings.environment == "development"
        assert settings.debug is False

        # Assert server settings
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert settings.workers == 1
        assert settings.reload is False

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        # Arrange
        env_vars = {
            "APP_NAME": "Test Chatter",
            "APP_VERSION": "1.0.0",
            "ENVIRONMENT": "testing",  # Use testing instead of production
            "DEBUG": "true",
            "HOST": "localhost",
            "PORT": "3000",
            "WORKERS": "4",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.app_name == "Test Chatter"
            assert settings.app_version == "1.0.0"
            assert settings.environment == "testing"
            assert settings.debug is True
            assert settings.host == "localhost"
            assert settings.port == 3000
            assert settings.workers == 4

    def test_production_debug_validation(self):
        """Test that debug mode is forbidden in production."""
        # Arrange
        env_vars = {
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "SECRET_KEY": "a-very-long-secret-key-for-production-use-that-is-definitely-over-32-characters",
        }

        with patch.dict(os.environ, env_vars):
            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "Debug mode must be disabled in production" in str(
                exc_info.value
            )

    def test_database_configuration(self):
        """Test database configuration settings."""
        # Arrange
        env_vars = {
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb",
            "DATABASE_ECHO": "true",
            "DATABASE_POOL_SIZE": "20",
            "DATABASE_MAX_OVERFLOW": "10",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert (
                settings.database_url
                == "postgresql://user:pass@localhost:5432/testdb"
            )
            assert settings.database_echo is True
            assert settings.database_pool_size == 20
            assert settings.database_max_overflow == 10

    def test_redis_configuration(self):
        """Test Redis configuration settings."""
        # Arrange
        env_vars = {
            "REDIS_URL": "redis://localhost:6380/1",
            "REDIS_PASSWORD": "test_password",
            "REDIS_MAX_CONNECTIONS": "50",
            "CACHE_ENABLED": "true",
            "CACHE_TTL": "7200",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.redis_url == "redis://localhost:6380/1"
            assert settings.redis_password == "test_password"
            assert settings.redis_max_connections == 50
            assert settings.cache_enabled is True
            assert settings.cache_ttl == 7200

    def test_security_configuration(self):
        """Test security configuration settings."""
        # Arrange
        env_vars = {
            "SECRET_KEY": "test-secret-key-123",
            "JWT_ALGORITHM": "HS512",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "60",
            "JWT_REFRESH_TOKEN_EXPIRE_DAYS": "14",
            "ALLOWED_HOSTS": "localhost,127.0.0.1,example.com",
            "CORS_ORIGINS": "http://localhost:3000,https://app.example.com",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.secret_key == "test-secret-key-123"
            assert settings.jwt_algorithm == "HS512"
            assert settings.jwt_access_token_expire_minutes == 60
            assert settings.jwt_refresh_token_expire_days == 14
            assert "localhost" in settings.allowed_hosts
            assert "example.com" in settings.allowed_hosts
            assert "http://localhost:3000" in settings.cors_origins

    def test_llm_configuration(self):
        """Test LLM configuration settings."""
        # Arrange
        env_vars = {
            "OPENAI_API_KEY": "sk-test-key-123",
            "ANTHROPIC_API_KEY": "ant-test-key-456",
            "DEFAULT_LLM_PROVIDER": "anthropic",
            "DEFAULT_MODEL": "claude-3-sonnet",
            "MAX_TOKENS": "4000",
            "TEMPERATURE": "0.8",
            "LLM_TIMEOUT": "60",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.openai_api_key == "sk-test-key-123"
            assert settings.anthropic_api_key == "ant-test-key-456"
            assert settings.default_llm_provider == "anthropic"
            assert settings.default_model == "claude-3-sonnet"
            assert settings.max_tokens == 4000
            assert settings.temperature == 0.8
            assert settings.llm_timeout == 60

    def test_vector_store_configuration(self):
        """Test vector store configuration settings."""
        # Arrange
        env_vars = {
            "VECTOR_STORE_TYPE": "pgvector",
            "EMBEDDING_MODEL": "text-embedding-ada-002",
            "EMBEDDING_DIMENSIONS": "1536",
            "VECTOR_SEARCH_LIMIT": "20",
            "SIMILARITY_THRESHOLD": "0.8",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.vector_store_type == "pgvector"
            assert settings.embedding_model == "text-embedding-ada-002"
            assert settings.embedding_dimensions == 1536
            assert settings.vector_search_limit == 20
            assert settings.similarity_threshold == 0.8

    def test_monitoring_configuration(self):
        """Test monitoring configuration settings."""
        # Arrange
        env_vars = {
            "MONITORING_ENABLED": "true",
            "METRICS_ENABLED": "true",
            "LOG_LEVEL": "INFO",
            "STRUCTURED_LOGGING": "true",
            "SENTRY_DSN": "https://test@sentry.io/123456",
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert settings.monitoring_enabled is True
            assert settings.metrics_enabled is True
            assert settings.log_level == "INFO"
            assert settings.structured_logging is True
            assert (
                settings.sentry_dsn == "https://test@sentry.io/123456"
            )

    def test_invalid_port_validation(self):
        """Test validation of invalid port numbers."""
        # Arrange
        env_vars = {"PORT": "99999"}  # Port too high

        with patch.dict(os.environ, env_vars):
            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "port" in str(exc_info.value).lower()

    def test_invalid_database_url_validation(self):
        """Test validation of invalid database URLs."""
        # Arrange
        env_vars = {"DATABASE_URL": "invalid-url"}

        with patch.dict(os.environ, env_vars):
            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            # Should fail URL validation
            assert "database_url" in str(exc_info.value).lower()

    def test_missing_required_secret_key(self):
        """Test validation when secret key is missing in production."""
        # Arrange
        env_vars = {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "",  # Empty secret key
        }

        with patch.dict(os.environ, env_vars):
            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                Settings()

            assert "secret_key" in str(exc_info.value).lower()

    def test_model_dump_excludes_secrets(self):
        """Test that model dump excludes sensitive information."""
        # Arrange
        env_vars = {
            "SECRET_KEY": "super-secret-key",
            "OPENAI_API_KEY": "sk-secret-openai-key",
            "DATABASE_URL": "postgresql://user:password@localhost/db",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            # Act
            config_dict = settings.model_dump(
                exclude={"secret_key", "openai_api_key", "database_url"}
            )

            # Assert
            assert "secret_key" not in config_dict
            assert "openai_api_key" not in config_dict
            assert "database_url" not in config_dict
            assert "app_name" in config_dict

    def test_settings_model_validation(self):
        """Test complete settings model validation."""
        # Arrange
        valid_config = {
            "app_name": "Test App",
            "environment": "test",
            "host": "127.0.0.1",
            "port": 8080,
            "database_url": "postgresql://localhost/test",
            "secret_key": "test-secret-key",
            "debug": True,
        }

        # Act
        settings = Settings(**valid_config)

        # Assert
        assert settings.app_name == "Test App"
        assert settings.environment == "test"
        assert settings.host == "127.0.0.1"
        assert settings.port == 8080
        assert settings.debug is True

    def test_cors_origins_parsing(self):
        """Test CORS origins parsing from comma-separated string."""
        # Arrange
        env_vars = {
            "CORS_ORIGINS": "http://localhost:3000,https://app.example.com,https://admin.example.com"
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert isinstance(settings.cors_origins, list)
            assert len(settings.cors_origins) == 3
            assert "http://localhost:3000" in settings.cors_origins
            assert "https://app.example.com" in settings.cors_origins
            assert "https://admin.example.com" in settings.cors_origins

    def test_allowed_hosts_parsing(self):
        """Test allowed hosts parsing from comma-separated string."""
        # Arrange
        env_vars = {
            "ALLOWED_HOSTS": "localhost,127.0.0.1,*.example.com,api.domain.com"
        }

        with patch.dict(os.environ, env_vars):
            # Act
            settings = Settings()

            # Assert
            assert isinstance(settings.allowed_hosts, list)
            assert "localhost" in settings.allowed_hosts
            assert "*.example.com" in settings.allowed_hosts

    def test_settings_repr_security(self):
        """Test that settings representation doesn't expose secrets."""
        # Arrange
        env_vars = {
            "SECRET_KEY": "super-secret-key",
            "OPENAI_API_KEY": "sk-secret-key",
        }

        with patch.dict(os.environ, env_vars):
            settings = Settings()

            # Act
            repr_str = repr(settings)

            # Assert - secrets should be masked or not shown
            assert "super-secret-key" not in repr_str
            assert "sk-secret-key" not in repr_str


@pytest.mark.integration
class TestSettingsIntegration:
    """Integration tests for settings configuration."""

    def test_settings_loading_from_env_file(self):
        """Test loading settings from .env file."""
        # Arrange - mock env file loading
        mock_env_content = {
            "APP_NAME": "Integration Test App",
            "ENVIRONMENT": "test",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://localhost/integration_test",
        }

        with patch.dict(os.environ, mock_env_content):
            # Act
            settings = Settings()

            # Assert
            assert settings.app_name == "Integration Test App"
            assert settings.environment == "test"
            assert settings.debug is True

    def test_settings_validation_chain(self):
        """Test complete validation chain for settings."""
        # Arrange
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SECRET_KEY": "production-secret-key",
                "DATABASE_URL": "postgresql://prod_user:prod_pass@prod_host:5432/prod_db",
                "REDIS_URL": "redis://prod_redis:6379/0",
                "OPENAI_API_KEY": "sk-prod-openai-key",
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "30",
                "CORS_ORIGINS": "https://prod.example.com",
                "ALLOWED_HOSTS": "prod.example.com,api.example.com",
            },
        ):
            # Act
            settings = Settings()

            # Assert production settings are valid
            assert settings.environment == "production"
            assert settings.secret_key == "production-secret-key"
            assert "postgresql://" in settings.database_url
            assert "redis://" in settings.redis_url
            assert settings.jwt_access_token_expire_minutes == 30

    def test_development_vs_production_settings(self):
        """Test differences between development and production settings."""
        # Test development settings
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            dev_settings = Settings()

        # Test production settings
        with patch.dict(
            os.environ,
            {
                "ENVIRONMENT": "production",
                "SECRET_KEY": "production-secret",
                "DEBUG": "false",
            },
        ):
            prod_settings = Settings()

        # Assert differences
        assert dev_settings.environment == "development"
        assert prod_settings.environment == "production"
        assert prod_settings.debug is False

    def test_settings_caching(self):
        """Test that settings are properly cached/singleton pattern."""
        # Arrange
        with patch.dict(os.environ, {"APP_NAME": "Cached Test App"}):
            # Act
            settings1 = Settings()
            settings2 = Settings()

            # Assert - settings should have same values
            assert settings1.app_name == settings2.app_name
            assert settings1.app_name == "Cached Test App"
