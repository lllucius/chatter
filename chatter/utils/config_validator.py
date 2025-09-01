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

    def validate_secret_key(self, secret_key: str) -> None:
        """Validate a secret key for strength and security.
        
        Args:
            secret_key: The secret key to validate
            
        Raises:
            ValueError: If the secret key is weak, insecure, or too short
        """
        # Check for weak/default keys and common patterns
        weak_keys = [
            "secret",
            "password", 
            "your-secret-key",
            "development",
            "test",
            "admin",
            "default",
            "mysecretkey",
            "your_super_secret_key_here_change_this_in_production",
            "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION",
            "change_me"
        ]
        
        # Check exact matches (case-insensitive)
        if secret_key.lower() in [key.lower() for key in weak_keys]:
            raise ValueError(f"Secret key is weak or using default value: {secret_key}")
        
        # Check for keys that start with common weak patterns  
        weak_patterns = ["secret", "password", "admin", "test", "default"]
        for pattern in weak_patterns:
            if secret_key.lower().startswith(pattern.lower()):
                raise ValueError(f"Secret key is weak or contains insecure pattern: {secret_key}")
        
        # Check minimum length
        if len(secret_key) < 8:
            raise ValueError(f"Secret key is too short: {len(secret_key)} characters (minimum 8)")
        
        # Check for simple patterns (all same character, simple sequences)
        if len(set(secret_key)) == 1:  # All same character
            raise ValueError("Secret key contains only repeated characters (insecure)")
        
        if secret_key.isdigit() and len(secret_key) <= 12:  # Simple number sequences
            raise ValueError("Secret key is a simple numeric sequence (insecure)")

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

    def validate_database_config(self, config: dict) -> dict:
        """Validate database configuration.
        
        Args:
            config: Database configuration dictionary
            
        Returns:
            dict: Validation result with 'valid' and 'errors' keys
        """
        errors = []
        
        database_url = config.get('DATABASE_URL', '')
        if not database_url:
            errors.append("DATABASE_URL is required")
        else:
            # Check for weak credentials
            weak_passwords = ["chatter_password", "password", "admin", "CHANGE_THIS_PASSWORD", "change_me"]
            try:
                parsed = urlparse(database_url)
                if (parsed.username in ["chatter", "postgres", "admin"] and
                    parsed.password in weak_passwords):
                    errors.append("Database is using weak/default credentials")
            except Exception as e:
                errors.append(f"Invalid DATABASE_URL format: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def validate_api_key(self, api_key: str, provider: str = "unknown") -> dict:
        """Validate API key format and strength.
        
        Args:
            api_key: The API key to validate
            provider: The provider name (openai, anthropic, etc.)
            
        Returns:
            dict: Validation result with 'valid' and 'errors' keys
        """
        errors = []
        
        if not api_key:
            errors.append(f"{provider} API key is required")
        elif len(api_key) < 10:
            errors.append(f"{provider} API key appears too short")
        elif api_key in ["your-api-key", "sk-test", "test-key"]:
            errors.append(f"{provider} API key appears to be a placeholder")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def validate_redis_config(self, config: dict) -> dict:
        """Validate Redis configuration.
        
        Args:
            config: Redis configuration dictionary
            
        Returns:
            dict: Validation result with 'valid' and 'errors' keys
        """
        errors = []
        
        redis_url = config.get('REDIS_URL', '')
        if redis_url:
            try:
                parsed = urlparse(redis_url)
                if not parsed.scheme:
                    errors.append("Redis URL must include scheme (redis:// or rediss://)")
                if parsed.password in ["password", "redis", "admin"]:
                    errors.append("Redis is using weak/default password")
            except Exception as e:
                errors.append(f"Invalid REDIS_URL format: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def validate_url_security(self, url: str, require_ssl: bool = False) -> dict:
        """Validate URL security settings.
        
        Args:
            url: URL to validate
            require_ssl: Whether SSL/TLS is required
            
        Returns:
            dict: Validation result with 'valid' and 'errors' keys
        """
        errors = []
        
        if not url:
            errors.append("URL is required")
            return {'valid': False, 'errors': errors}
        
        try:
            parsed = urlparse(url)
            if require_ssl and parsed.scheme not in ['https', 'rediss']:
                errors.append("SSL/TLS is required (use https:// or rediss://)")
        except Exception as e:
            errors.append(f"Invalid URL format: {str(e)}")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def validate_completeness(self, config: dict, required_configs: list) -> list:
        """Validate that all required configuration is present.
        
        Args:
            config: Configuration dictionary
            required_configs: List of required configuration keys
            
        Returns:
            list: List of missing configuration keys
        """
        missing = []
        for key in required_configs:
            if key not in config or not config[key]:
                missing.append(key)
        return missing

    def detect_sensitive_patterns(self, value: str) -> bool:
        """Detect if a value contains sensitive data patterns.
        
        Args:
            value: Value to check
            
        Returns:
            bool: True if sensitive patterns are detected
        """
        if not isinstance(value, str):
            return False
            
        sensitive_patterns = [
            'password', 'secret', 'key', 'token', 'credential',
            'private', 'auth', 'signature', 'hash', 'salt'
        ]
        
        value_lower = value.lower()
        return any(pattern in value_lower for pattern in sensitive_patterns)

    def is_placeholder_value(self, value: str) -> bool:
        """Check if a value is a placeholder.
        
        Args:
            value: Value to check
            
        Returns:
            bool: True if the value appears to be a placeholder
        """
        if not isinstance(value, str):
            return False
            
        placeholder_patterns = [
            'change_me', 'change_this', 'replace_me', 'your_', 'placeholder',
            'example', 'test', 'demo', 'sample', 'xxx', 'TODO',
            'CHANGE_THIS_PASSWORD', 'your_super_secret_key_here'
        ]
        
        value_lower = value.lower()
        return any(pattern.lower() in value_lower for pattern in placeholder_patterns)

    def validate_full_config(self, config: dict) -> dict:
        """Perform complete configuration validation.
        
        Args:
            config: Full configuration dictionary
            
        Returns:
            dict: Validation result with 'valid', 'errors', and 'warnings' keys
        """
        errors = []
        warnings = []
        
        # Validate database
        db_result = self.validate_database_config(config)
        if not db_result['valid']:
            errors.extend(db_result['errors'])
        
        # Validate API keys
        if 'OPENAI_API_KEY' in config:
            openai_result = self.validate_api_key(config['OPENAI_API_KEY'], 'OpenAI')
            if not openai_result['valid']:
                errors.extend(openai_result['errors'])
        
        if 'ANTHROPIC_API_KEY' in config:
            anthropic_result = self.validate_api_key(config['ANTHROPIC_API_KEY'], 'Anthropic')
            if not anthropic_result['valid']:
                errors.extend(anthropic_result['errors'])
        
        # Validate Redis if present
        redis_result = self.validate_redis_config(config)
        if not redis_result['valid']:
            warnings.extend(redis_result['errors'])  # Redis is optional, so warnings
        
        # Check for placeholders
        for key, value in config.items():
            if isinstance(value, str) and self.is_placeholder_value(value):
                warnings.append(f"{key} appears to contain a placeholder value")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


def validate_startup_configuration() -> None:
    """Validate configuration at application startup.

    Raises:
        ConfigurationError: If critical configuration errors are found
    """
    validator = ConfigurationValidator()
    validator.validate_all()
