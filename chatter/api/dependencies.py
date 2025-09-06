"""Common API dependencies for validation and request handling."""

from typing import Annotated
from uuid import UUID

from fastapi import Path, Query

from chatter.utils.problem import BadRequestProblem


class ValidatedUUID(str):
    """UUID string that validates format on creation."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate UUID format."""
        if isinstance(v, str):
            try:
                UUID(v)
                return v
            except ValueError:
                raise BadRequestProblem(
                    detail="Invalid UUID format: must be a valid UUID"
                )
        raise BadRequestProblem(
            detail="Invalid UUID format: must be a string"
        )


# Type aliases for common path/query parameters
ConversationId = Annotated[
    ValidatedUUID, Path(description="Conversation ID")
]
MessageId = Annotated[ValidatedUUID, Path(description="Message ID")]
TemplateId = Annotated[str, Path(description="Template identifier")]

# Common query parameters
PaginationLimit = Annotated[
    int, Query(ge=1, le=100, description="Number of results per page")
]
PaginationOffset = Annotated[
    int, Query(ge=0, description="Number of results to skip")
]
