"""Enhanced input validation and sanitization utilities.

DEPRECATED: This module has been replaced by the unified validation system.
Import from chatter.core.validation.compat for backwards compatibility.
"""

import warnings
from chatter.core.validation.compat import (
    ValidationError,
    validate_name_field,
    validate_display_name,
    validate_description,
    validate_positive_integer,
    validate_model_consistency,
    validate_embedding_space_consistency,
)

# Import ValidationConfig for backwards compatibility
class ValidationConfig:
    """Legacy ValidationConfig for backwards compatibility."""
    MAX_NAME_LENGTH = 100
    MAX_DISPLAY_NAME_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_URL_LENGTH = 500
    MAX_PATH_LENGTH = 500
    MAX_VERSION_LENGTH = 100
    MAX_INDEX_TYPE_LENGTH = 50
    MAX_TOKENS = 1000000
    MAX_CONTEXT_LENGTH = 10000000
    MAX_DIMENSIONS = 10000
    MAX_CHUNK_SIZE = 100000
    MAX_BATCH_SIZE = 1000

warnings.warn(
    "chatter.utils.enhanced_validation is deprecated. Use chatter.core.validation instead.",
    DeprecationWarning,
    stacklevel=2
)
