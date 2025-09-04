"""Input validation middleware for API security.

DEPRECATED: This module has been replaced by the unified validation system.
Import from chatter.core.validation.compat for backwards compatibility.
"""

import warnings
import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import HTTPException, Request
from starlette.responses import Response

from chatter.config import settings
from chatter.schemas.utilities import ValidationRule
from chatter.utils.logging import get_logger

# Import unified validation system with compatibility layer
from chatter.core.validation.compat import (
    ValidationError,
    InputValidator,
    SecurityValidator,
    input_validator,
    security_validator,
    validate_chat_message,
    validate_user_input,
    sanitize_input,
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
    validate_email_format,
    validate_username_format,
    validate_url_format,
    validate_api_key_format,
    validate_json_structure,
    validate_sql_identifier,
    validate_request_middleware,
    ValidationMiddleware,
)

logger = get_logger(__name__)

# Issue deprecation warning when this module is imported
warnings.warn(
    "chatter.utils.validation is deprecated. Use chatter.core.validation instead.",
    DeprecationWarning,
    stacklevel=2
)

# All functions and classes are now imported from the compatibility layer above
