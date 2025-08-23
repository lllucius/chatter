"""Prompt management schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from chatter.models.prompt import PromptCategory, PromptType
from chatter.schemas.common import ListRequestBase, GetRequestBase, DeleteRequestBase


class PromptBase(BaseModel):
    """Base prompt schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Prompt name")
    description: str | None = Field(None, description="Prompt description")
    prompt_type: PromptType = Field(PromptType.TEMPLATE, description="Prompt type")
    category: PromptCategory = Field(PromptCategory.GENERAL, description="Prompt category")

    # Prompt content
    content: str = Field(..., min_length=1, description="Prompt content/template")
    variables: list[str] | None = Field(None, description="Template variables")

    # Template configuration
    template_format: str = Field("f-string", description="Template format (f-string, jinja2, mustache)")
    input_schema: dict[str, Any] | None = Field(None, description="JSON schema for input validation")
    output_schema: dict[str, Any] | None = Field(None, description="JSON schema for output validation")

    # Validation and constraints
    max_length: int | None = Field(None, ge=1, description="Maximum content length")
    min_length: int | None = Field(None, ge=1, description="Minimum content length")
    required_variables: list[str] | None = Field(None, description="Required template variables")

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(None, description="Usage examples")
    test_cases: list[dict[str, Any]] | None = Field(None, description="Test cases")

    # LLM configuration hints
    suggested_temperature: float | None = Field(None, ge=0.0, le=2.0, description="Suggested temperature")
    suggested_max_tokens: int | None = Field(None, ge=1, description="Suggested max tokens")
    suggested_providers: list[str] | None = Field(None, description="Suggested LLM providers")

    # Chain configuration
    is_chain: bool = Field(False, description="Whether this is a chain prompt")
    chain_steps: list[dict[str, Any]] | None = Field(None, description="Chain execution steps")
    parent_prompt_id: str | None = Field(None, description="Parent prompt ID for chains")

    # Access control
    is_public: bool = Field(False, description="Whether prompt is public")

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class PromptCreate(PromptBase):
    """Schema for creating a prompt."""
    pass


class PromptUpdate(BaseModel):
    """Schema for updating a prompt."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Prompt name")
    description: str | None = Field(None, description="Prompt description")
    prompt_type: PromptType | None = Field(None, description="Prompt type")
    category: PromptCategory | None = Field(None, description="Prompt category")

    # Prompt content
    content: str | None = Field(None, min_length=1, description="Prompt content/template")
    variables: list[str] | None = Field(None, description="Template variables")

    # Template configuration
    template_format: str | None = Field(None, description="Template format")
    input_schema: dict[str, Any] | None = Field(None, description="Input validation schema")
    output_schema: dict[str, Any] | None = Field(None, description="Output validation schema")

    # Validation and constraints
    max_length: int | None = Field(None, ge=1, description="Maximum content length")
    min_length: int | None = Field(None, ge=1, description="Minimum content length")
    required_variables: list[str] | None = Field(None, description="Required template variables")

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(None, description="Usage examples")
    test_cases: list[dict[str, Any]] | None = Field(None, description="Test cases")

    # LLM configuration hints
    suggested_temperature: float | None = Field(None, ge=0.0, le=2.0, description="Suggested temperature")
    suggested_max_tokens: int | None = Field(None, ge=1, description="Suggested max tokens")
    suggested_providers: list[str] | None = Field(None, description="Suggested LLM providers")

    # Chain configuration
    is_chain: bool | None = Field(None, description="Whether this is a chain prompt")
    chain_steps: list[dict[str, Any]] | None = Field(None, description="Chain execution steps")
    parent_prompt_id: str | None = Field(None, description="Parent prompt ID")

    # Access control
    is_public: bool | None = Field(None, description="Whether prompt is public")

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class PromptResponse(BaseModel):
    """Schema for prompt response."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Prompt ID")
    owner_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Prompt name")
    description: str | None = Field(None, description="Prompt description")
    prompt_type: PromptType = Field(..., description="Prompt type")
    category: PromptCategory = Field(..., description="Prompt category")

    # Prompt content
    content: str = Field(..., description="Prompt content/template")
    variables: list[str] | None = Field(None, description="Template variables")

    # Template configuration
    template_format: str = Field(..., description="Template format")
    input_schema: dict[str, Any] | None = Field(None, description="Input validation schema")
    output_schema: dict[str, Any] | None = Field(None, description="Output validation schema")

    # Validation and constraints
    max_length: int | None = Field(None, description="Maximum content length")
    min_length: int | None = Field(None, description="Minimum content length")
    required_variables: list[str] | None = Field(None, description="Required template variables")

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(None, description="Usage examples")
    test_cases: list[dict[str, Any]] | None = Field(None, description="Test cases")

    # LLM configuration hints
    suggested_temperature: float | None = Field(None, description="Suggested temperature")
    suggested_max_tokens: int | None = Field(None, description="Suggested max tokens")
    suggested_providers: list[str] | None = Field(None, description="Suggested LLM providers")

    # Chain configuration
    is_chain: bool = Field(..., description="Whether this is a chain prompt")
    chain_steps: list[dict[str, Any]] | None = Field(None, description="Chain execution steps")
    parent_prompt_id: str | None = Field(None, description="Parent prompt ID")

    # Version control
    version: int = Field(..., description="Prompt version")
    is_latest: bool = Field(..., description="Whether this is the latest version")
    changelog: str | None = Field(None, description="Version changelog")

    # Access control
    is_public: bool = Field(..., description="Whether prompt is public")

    # Quality and ratings
    rating: float | None = Field(None, description="Average rating")
    rating_count: int = Field(..., description="Number of ratings")

    # Usage statistics
    usage_count: int = Field(..., description="Usage count")
    success_rate: float | None = Field(None, description="Success rate")
    avg_response_time_ms: int | None = Field(None, description="Average response time")
    last_used_at: datetime | None = Field(None, description="Last used timestamp")

    # Performance metrics
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    avg_tokens_per_use: float | None = Field(None, description="Average tokens per use")

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(None, description="Additional metadata")

    # Content analysis
    content_hash: str = Field(..., description="Content hash")
    estimated_tokens: int | None = Field(None, description="Estimated token count")
    language: str | None = Field(None, description="Content language")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class PromptListRequest(ListRequestBase):
    """Schema for prompt list request."""

    prompt_type: PromptType | None = Field(None, description="Filter by prompt type")
    category: PromptCategory | None = Field(None, description="Filter by category")
    tags: list[str] | None = Field(None, description="Filter by tags")
    is_public: bool | None = Field(None, description="Filter by public status")
    is_chain: bool | None = Field(None, description="Filter by chain status")


class PromptGetRequest(GetRequestBase):
    """Schema for prompt get request."""
    pass


class PromptDeleteRequest(DeleteRequestBase):
    """Schema for prompt delete request."""
    pass


class PromptStatsRequest(GetRequestBase):
    """Schema for prompt stats request."""
    pass


class PromptListResponse(BaseModel):
    """Schema for prompt list response."""

    prompts: list[PromptResponse] = Field(..., description="List of prompts")
    total_count: int = Field(..., description="Total number of prompts")
    limit: int = Field(..., description="Requested limit")
    offset: int = Field(..., description="Requested offset")


class PromptTestRequest(BaseModel):
    """Schema for prompt test request."""

    variables: dict[str, Any] = Field(..., description="Variables to test with")
    validate_only: bool = Field(False, description="Only validate, don't render")


class PromptTestResponse(BaseModel):
    """Schema for prompt test response."""

    rendered_content: str | None = Field(None, description="Rendered prompt content")
    validation_result: dict[str, Any] = Field(..., description="Validation results")
    estimated_tokens: int | None = Field(None, description="Estimated token count")
    test_duration_ms: int = Field(..., description="Test execution time")


class PromptCloneRequest(BaseModel):
    """Schema for prompt clone request."""

    name: str = Field(..., min_length=1, max_length=255, description="New prompt name")
    description: str | None = Field(None, description="New prompt description")
    modifications: dict[str, Any] | None = Field(None, description="Modifications to apply")


class PromptStatsResponse(BaseModel):
    """Schema for prompt statistics response."""

    total_prompts: int = Field(..., description="Total number of prompts")
    prompts_by_type: dict[str, int] = Field(..., description="Prompts by type")
    prompts_by_category: dict[str, int] = Field(..., description="Prompts by category")
    most_used_prompts: list[PromptResponse] = Field(..., description="Most used prompts")
    recent_prompts: list[PromptResponse] = Field(..., description="Recently created prompts")
    usage_stats: dict[str, Any] = Field(..., description="Usage statistics")
