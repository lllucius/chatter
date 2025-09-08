"""Common API dependencies for validation and request handling."""

from typing import Annotated, Any

from fastapi import Path, Query
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from ulid import ULID

from chatter.utils.problem import BadRequestProblem


class ValidatedULID(str):
    """ULID string that validates format on creation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Generate Pydantic v2 core schema for OpenAPI compatibility."""

        def validate_ulid(v: str) -> str:
            """Validate ULID format."""
            if not isinstance(v, str):
                raise BadRequestProblem(
                    detail="Invalid ULID format: must be a string"
                )
            try:
                ULID.from_str(v)
                return v
            except ValueError as e:
                raise BadRequestProblem(
                    detail="Invalid ULID format: must be a valid ULID"
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
                raise BadRequestProblem(
                    detail="Invalid ULID format: must be a valid ULID"
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
    int, Query(ge=1, le=100, description="Number of results per page")
]
PaginationOffset = Annotated[
    int, Query(ge=0, description="Number of results to skip")
]
