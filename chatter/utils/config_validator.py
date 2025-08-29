"""Configuration validation utilities."""

import os
from urllib.parse import urlparse

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ConfigurationError(Exception):
    """Configuration validation error."""
    pass


class ConfigurationValidator:
    """Validates application configuration at startup."""

    def __init__(self):
        """Initialize the validator."""
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def validate_all(self) -> None:
        """Validate all configuration settings.
        
        Raises:
            ConfigurationError: If critical configuration errors are found
        """
        logger.info("Starting configuration validation")

        # Critical validations
        self._validate_database_settings()
        self._validate_security_settings()
        self._validate_api_settings()

        # Warning validations
        self._validate_performance_settings()
        self._validate_logging_settings()
        self._validate_file_settings()

        # Report results
        self._report_validation_results()

        if self.errors:
            raise ConfigurationError(
                f"Configuration validation failed with {len(self.errors)} error(s): " +
                "; ".join(self.errors)
            )

    def _validate_database_settings(self) -> None:
        """Validate database configuration."""
        # Check database URL is provided
        if not settings.database_url:
            self.errors.append("DATABASE_URL is required and cannot be empty")
            return

        # Validate database URL format
        try:
            parsed = urlparse(settings.database_url)
            if not parsed.scheme or not parsed.hostname:
                self.errors.append("DATABASE_URL format is invalid")

            # Check for default/weak credentials
            weak_passwords = ["chatter_password", "password", "admin", "CHANGE_THIS_PASSWORD", "change_me"]
            if (parsed.username in ["chatter", "postgres", "admin"] and
                parsed.password in weak_passwords):
                self.errors.append(
                    "Database is using default/weak credentials. "
                    "Change username and password for security."
                )
        except Exception as e:
            self.errors.append(f"DATABASE_URL parsing failed: {str(e)}")

        # Check connection pool settings
        if settings.db_pool_size <= 0:
            self.errors.append("Database pool size must be positive")

        if settings.db_max_overflow < 0:
            self.errors.append("Database max overflow cannot be negative")

    def _validate_security_settings(self) -> None:
        """Validate security configuration."""
        # Check secret key strength
        default_keys = [
            "your_super_secret_key_here_change_this_in_production",
            "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION",
            "change_me",
            "secret",
            "default"
        ]
        if (settings.secret_key in default_keys or
            len(settings.secret_key) < 32):
            self.errors.append(
                "SECRET_KEY is too weak or using default value. "
                "Use a strong, random key of at least 32 characters."
            )

        # Check token expiration settings
        if settings.access_token_expire_minutes <= 0:
            self.errors.append("Access token expiration must be positive")

        if settings.refresh_token_expire_days <= 0:
            self.errors.append("Refresh token expiration must be positive")

        # Check bcrypt rounds
        if settings.bcrypt_rounds < 10:
            self.warnings.append(
                f"bcrypt rounds ({settings.bcrypt_rounds}) is below recommended minimum (12)"
            )
        elif settings.bcrypt_rounds > 15:
            self.warnings.append(
                f"bcrypt rounds ({settings.bcrypt_rounds}) may cause performance issues"
            )

        # Check CORS settings in production
        if settings.is_production:
            if "*" in settings.cors_origins:
                self.warnings.append(
                    "CORS is configured to allow all origins in production. "
                    "Consider restricting to specific domains."
                )

        # Check rate limiting
        if settings.rate_limit_requests <= 0:
            self.errors.append("Rate limit requests must be positive")

        if settings.rate_limit_window <= 0:
            self.errors.append("Rate limit window must be positive")

    def _validate_api_settings(self) -> None:
        """Validate API configuration."""
        # Check API base URL format
        try:
            parsed = urlparse(settings.api_base_url)
            if not parsed.scheme or not parsed.hostname:
                self.warnings.append("API_BASE_URL format may be invalid")
        except Exception:
            self.warnings.append("API_BASE_URL parsing failed")

        # Check port range
        if not (1 <= settings.port <= 65535):
            self.errors.append(f"Port {settings.port} is outside valid range (1-65535)")

        # Check worker count
        if settings.workers <= 0:
            self.errors.append("Worker count must be positive")
        elif settings.workers > 8:
            self.warnings.append(
                f"High worker count ({settings.workers}) may cause resource issues"
            )

    def _validate_performance_settings(self) -> None:
        """Validate performance-related settings."""
        # Check Redis settings if enabled
        if settings.redis_url:
            try:
                parsed = urlparse(settings.redis_url)
                if not parsed.scheme or not parsed.hostname:
                    self.warnings.append("REDIS_URL format may be invalid")
            except Exception:
                self.warnings.append("REDIS_URL parsing failed")

            if settings.redis_max_connections <= 0:
                self.warnings.append("Redis max connections should be positive")
        else:
            self.warnings.append(
                "Redis not configured. Caching and session storage will be limited."
            )

        # Check cache TTL settings
        if settings.cache_ttl_short <= 0:
            self.warnings.append("Short cache TTL should be positive")

        # Check background processing settings
        if settings.background_worker_concurrency <= 0:
            self.warnings.append("Background worker concurrency should be positive")
        elif settings.background_worker_concurrency > 16:
            self.warnings.append("High background worker concurrency may cause issues")

    def _validate_logging_settings(self) -> None:
        """Validate logging configuration."""
        # Check log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if settings.log_level.upper() not in valid_levels:
            self.warnings.append(f"Log level '{settings.log_level}' is not standard")

        # Check log file path
        if settings.log_file:
            log_dir = os.path.dirname(settings.log_file)
            if log_dir and not os.path.exists(log_dir):
                try:
                    os.makedirs(log_dir, exist_ok=True)
                except Exception as e:
                    self.warnings.append(f"Cannot create log directory: {str(e)}")

    def _validate_file_settings(self) -> None:
        """Validate file handling configuration."""
        # Check max file size
        if settings.max_file_size <= 0:
            self.errors.append("Max file size must be positive")
        elif settings.max_file_size > 100 * 1024 * 1024:  # 100MB
            self.warnings.append(
                f"Large max file size ({settings.max_file_size} bytes) may cause issues"
            )

        # Check document storage path
        if not os.path.exists(settings.document_storage_path):
            try:
                os.makedirs(settings.document_storage_path, exist_ok=True)
                logger.info(f"Created document storage directory: {settings.document_storage_path}")
            except Exception as e:
                self.warnings.append(f"Cannot create document storage directory: {str(e)}")

        # Check allowed file types
        if not settings.allowed_file_types:
            self.warnings.append("No allowed file types configured")

        # Check chunk settings
        if settings.chunk_size <= 0:
            self.errors.append("Chunk size must be positive")

        if settings.chunk_overlap < 0:
            self.warnings.append("Chunk overlap should not be negative")

        if settings.chunk_overlap >= settings.chunk_size:
            self.warnings.append("Chunk overlap should be less than chunk size")

    def _report_validation_results(self) -> None:
        """Report validation results."""
        if self.errors:
            logger.error(
                "Configuration validation errors found",
                error_count=len(self.errors),
                errors=self.errors
            )

        if self.warnings:
            logger.warning(
                "Configuration validation warnings found",
                warning_count=len(self.warnings),
                warnings=self.warnings
            )

        if not self.errors and not self.warnings:
            logger.info("Configuration validation passed without issues")
        else:
            logger.info(
                "Configuration validation completed",
                errors=len(self.errors),
                warnings=len(self.warnings)
            )


def validate_startup_configuration() -> None:
    """Validate configuration at application startup.
    
    Raises:
        ConfigurationError: If critical configuration errors are found
    """
    validator = ConfigurationValidator()
    validator.validate_all()


# Alias for backward compatibility with tests
ConfigValidator = ConfigurationValidator
