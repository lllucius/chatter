"""Utility schemas for validation, versioning, and problem details."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ValidationRule(BaseModel):
    """Input validation rule definition."""
    name: str
    pattern: str | None = None
    max_length: int | None = None
    min_length: int | None = None
    allowed_chars: str | None = None
    forbidden_patterns: list[str] = []
    required: bool = False
    sanitize: bool = True


class ProblemDetail(BaseModel):
    """RFC 9457 Problem Detail model."""

    type: str = Field(
        default="about:blank",
        description="A URI reference that identifies the problem type",
    )
    title: str = Field(
        description="A short, human-readable summary of the problem type"
    )
    status: int = Field(description="The HTTP status code")
    detail: str | None = Field(
        default=None,
        description="A human-readable explanation specific to this occurrence",
    )
    instance: str | None = Field(
        default=None,
        description="A URI reference that identifies the specific occurrence",
    )

    # Additional fields can be included for context
    class Config:
        extra = "allow"


class APIVersion(str, Enum):
    """Supported API versions."""
    V1 = "v1"
    V2 = "v2"
    # Future versions can be added here


class VersionStatus(str, Enum):
    """API version status."""
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    SUNSET = "sunset"


class EndpointChange(str, Enum):
    """Types of endpoint changes between versions."""
    ADDED = "added"
    MODIFIED = "modified"
    DEPRECATED = "deprecated"
    REMOVED = "removed"


class VersionInfo(BaseModel):
    """API version information."""
    version: APIVersion
    status: VersionStatus
    release_date: str
    sunset_date: str | None = None
    changelog_url: str | None = None
    documentation_url: str | None = None
    breaking_changes: list[str] = []
    new_features: list[str] = []
    deprecated_features: list[str] = []


class EndpointVersioning(BaseModel):
    """Endpoint versioning information."""
    path: str
    method: str
    introduced_in: APIVersion
    deprecated_in: APIVersion | None = None
    removed_in: APIVersion | None = None
    changes: dict[APIVersion, list[str]] = {}