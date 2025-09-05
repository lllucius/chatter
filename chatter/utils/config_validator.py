"""Configuration validation utilities."""

from typing import Any, Dict

from chatter.config import settings
from chatter.core.validation.engine import ValidationEngine
from chatter.core.validation.context import ValidationContext
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


def validate_startup_configuration() -> None:
    """Validate startup configuration settings.
    
    Raises:
        ValueError: If configuration is invalid
    """
    try:
        # Use existing validation engine
        engine = ValidationEngine()
        context = ValidationContext(user_id=None, request_id="startup")
        
        # Create config dict from settings
        config_dict = {
            "DATABASE_URL": settings.database_url,
            "SECRET_KEY": settings.secret_key,
            "DEBUG": settings.debug,
            "ENVIRONMENT": settings.environment,
        }
        
        # Validate configuration
        result = engine.validate_configuration(config_dict, context)
        
        if not result.is_valid:
            error_msg = f"Configuration validation failed: {result.errors}"
            logger.error("Configuration validation failed", errors=str(result.errors))
            raise ValueError(error_msg)
            
        logger.debug("Configuration validation passed")
        
    except Exception as e:
        logger.error("Configuration validation error", error=str(e))
        if "ValidationEngine" in str(e):
            # Fallback if validation engine isn't available
            logger.warning("Using fallback validation - ValidationEngine not available")
            _validate_basic_config()
        else:
            raise


def _validate_basic_config() -> None:
    """Basic fallback configuration validation."""
    errors = []
    
    if not settings.database_url:
        errors.append("DATABASE_URL is required")
        
    if not settings.secret_key or len(settings.secret_key) < 32:
        errors.append("SECRET_KEY must be at least 32 characters")
        
    if errors:
        error_msg = f"Configuration validation failed: {', '.join(errors)}"
        logger.error("Basic configuration validation failed", errors=errors)
        raise ValueError(error_msg)
