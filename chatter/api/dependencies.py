"""Common API dependencies for validation and request handling."""

from typing import Annotated, Any

from fastapi import Path, Query
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from ulid import ULID

from chatter.utils.logging import get_logger
from chatter.utils.problem import BadRequestProblem

logger = get_logger(__name__)


class ValidatedULID(str):
    """ULID string that validates format on creation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Generate Pydantic v2 core schema for OpenAPI compatibility."""

        def validate_ulid(v: str) -> str:
            """Validate ULID format, with temporary allowance for stream IDs."""
            if not isinstance(v, str):
                raise BadRequestProblem(
                    detail="Invalid ULID format: must be a string"
                )

            # Temporary allowance for stream-prefixed IDs during streaming
            # This appears to be legacy code - streaming should provide proper ULIDs
            # Investigate if this is still needed and remove if possible
            if v.startswith("stream-"):
                logger.warning(
                    f"Accepting legacy stream-prefixed ID: {v}"
                )
                return v

            try:
                ULID.from_str(v)
                return v
            except ValueError as e:
                # Check for common patterns that suggest names are being used as IDs
                if " " in v:
                    raise BadRequestProblem(
                        detail=f"Invalid ULID format: '{v}' appears to be a name or title, not a ULID. ULIDs must be exactly 26 characters without spaces. If you're seeing this error, there may be a bug where a workflow/resource name is being used as an ID instead of the proper ULID."
                    ) from e
                elif len(v) != 26:
                    # Handle empty string and very short strings first
                    if len(v) == 0:
                        raise BadRequestProblem(
                            detail="Invalid ULID format: must be exactly 26 characters, got 0 characters: ''"
                        ) from e
                    elif (
                        len(v) < 10
                    ):  # Very short strings, likely not names
                        raise BadRequestProblem(
                            detail=f"Invalid ULID format: must be exactly 26 characters, got {len(v)} characters: '{v}'"
                        ) from e
                    else:
                        # Check for known problematic patterns for longer strings
                        common_names = [
                            "untitled",
                            "default",
                            "new",
                            "test",
                            "sample",
                            "example",
                        ]
                        v_lower = v.lower()
                        is_likely_name = (
                            any(
                                name in v_lower for name in common_names
                            )
                            or not v.isupper()
                        )

                        if is_likely_name:
                            raise BadRequestProblem(
                                detail=f"Invalid ULID format: '{v}' (length: {len(v)}) appears to be a descriptive name rather than a ULID. ULIDs must be exactly 26 characters long and contain only uppercase alphanumeric characters. This suggests a bug where a name is being passed instead of the proper resource ID."
                            ) from e
                        else:
                            raise BadRequestProblem(
                                detail=f"Invalid ULID format: must be exactly 26 characters, got {len(v)} characters: '{v}'"
                            ) from e
                else:
                    raise BadRequestProblem(
                        detail=f"Invalid ULID format: contains invalid characters: '{v}'"
                    ) from e

        return core_schema.chain_schema(
            [
                core_schema.str_schema(min_length=1),
                core_schema.no_info_plain_validator_function(
                    validate_ulid
                ),
            ]
        )

    @classmethod
    def validate(cls, v):
        """Validate ULID format (for backward compatibility)."""
        if isinstance(v, str):
            try:
                ULID.from_str(v)
                return v
            except ValueError as e:
                # Check for common patterns that suggest names are being used as IDs
                if " " in v:
                    raise BadRequestProblem(
                        detail=f"Invalid ULID format: '{v}' appears to be a name or title, not a ULID. ULIDs must be exactly 26 characters without spaces. If you're seeing this error, there may be a bug where a workflow/resource name is being used as an ID instead of the proper ULID."
                    ) from e
                elif len(v) != 26:
                    # Handle empty string and very short strings first
                    if len(v) == 0:
                        raise BadRequestProblem(
                            detail="Invalid ULID format: must be exactly 26 characters, got 0 characters: ''"
                        ) from e
                    elif (
                        len(v) < 10
                    ):  # Very short strings, likely not names
                        raise BadRequestProblem(
                            detail=f"Invalid ULID format: must be exactly 26 characters, got {len(v)} characters: '{v}'"
                        ) from e
                    else:
                        # Check for known problematic patterns for longer strings
                        common_names = [
                            "untitled",
                            "default",
                            "new",
                            "test",
                            "sample",
                            "example",
                        ]
                        v_lower = v.lower()
                        is_likely_name = (
                            any(
                                name in v_lower for name in common_names
                            )
                            or not v.isupper()
                        )

                        if is_likely_name:
                            raise BadRequestProblem(
                                detail=f"Invalid ULID format: '{v}' (length: {len(v)}) appears to be a descriptive name rather than a ULID. ULIDs must be exactly 26 characters long and contain only uppercase alphanumeric characters. This suggests a bug where a name is being passed instead of the proper resource ID."
                            ) from e
                        else:
                            raise BadRequestProblem(
                                detail=f"Invalid ULID format: must be exactly 26 characters, got {len(v)} characters: '{v}'"
                            ) from e
                else:
                    raise BadRequestProblem(
                        detail=f"Invalid ULID format: contains invalid characters: '{v}'"
                    ) from e
        raise BadRequestProblem(
            detail="Invalid ULID format: must be a string"
        )


# Type aliases for common path/query parameters
ConversationId = Annotated[
    ValidatedULID, Path(description="Conversation ID")
]
MessageId = Annotated[ValidatedULID, Path(description="Message ID")]
TemplateId = Annotated[str, Path(description="Template identifier")]
WorkflowId = Annotated[ValidatedULID, Path(description="Workflow ID")]

# Common query parameters
PaginationLimit = Annotated[
    int, Query(ge=1, description="Number of results per page")
]
PaginationOffset = Annotated[
    int, Query(ge=0, description="Number of results to skip")
]
