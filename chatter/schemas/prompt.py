"""Prompt management schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from chatter.models.prompt import PromptCategory, PromptType
from chatter.schemas.common import (
    DeleteRequestBase,
    GetRequestBase,
    ListRequestBase,
)


class PromptBase(BaseModel):
    """Base prompt schema."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Prompt name"
    )
    description: str | None = Field(
        None, description="Prompt description"
    )
    prompt_type: PromptType = Field(
        PromptType.TEMPLATE, description="Prompt type"
    )
    category: PromptCategory = Field(
        PromptCategory.GENERAL, description="Prompt category"
    )

    # Prompt content
    content: str = Field(
        ..., 
        min_length=1, 
        max_length=100000,  # Reasonable limit for prompt content
        description="Prompt content/template"
    )
    variables: list[str] | None = Field(
        None, description="Template variables"
    )

    # Template configuration
    template_format: str = Field(
        "f-string",
        description="Template format (f-string, jinja2, mustache)",
    )
    input_schema: dict[str, Any] | None = Field(
        None, description="JSON schema for input validation"
    )
    output_schema: dict[str, Any] | None = Field(
        None, description="JSON schema for output validation"
    )

    # Validation and constraints
    max_length: int | None = Field(
        None, ge=1, description="Maximum content length"
    )
    min_length: int | None = Field(
        None, ge=1, description="Minimum content length"
    )
    required_variables: list[str] | None = Field(
        None, description="Required template variables"
    )

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(
        None, description="Usage examples"
    )
    test_cases: list[dict[str, Any]] | None = Field(
        None, description="Test cases"
    )

    # LLM configuration hints
    suggested_temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Suggested temperature"
    )
    suggested_max_tokens: int | None = Field(
        None, ge=1, description="Suggested max tokens"
    )
    suggested_providers: list[str] | None = Field(
        None, description="Suggested LLM providers"
    )

    # Chain configuration
    is_chain: bool = Field(
        False, description="Whether this is a chain prompt"
    )
    chain_steps: list[dict[str, Any]] | None = Field(
        None, description="Chain execution steps"
    )
    parent_prompt_id: str | None = Field(
        None, description="Parent prompt ID for chains"
    )

    # Access control
    is_public: bool = Field(
        False, description="Whether prompt is public"
    )

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )

    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate and sanitize prompt content."""
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        
        # Basic sanitization - remove potentially dangerous patterns
        dangerous_patterns = [
            '__import__', 'exec(', 'eval(', 'compile(',
            'subprocess', 'os.system', 'os.popen',
            'open(', 'file(', '__builtins__'
        ]
        
        content_lower = v.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                raise ValueError(f"Content contains potentially dangerous pattern: {pattern}")
        
        return v.strip()

    @field_validator('template_format')
    @classmethod
    def validate_template_format(cls, v: str) -> str:
        """Validate template format."""
        allowed_formats = {'f-string', 'jinja2', 'mustache', 'simple'}
        if v not in allowed_formats:
            raise ValueError(f"Template format must be one of: {allowed_formats}")
        return v

    @field_validator('variables')
    @classmethod
    def validate_variables(cls, v: list[str] | None) -> list[str] | None:
        """Validate variable names."""
        if v is None:
            return v
        
        for var in v:
            if not var.isidentifier():
                raise ValueError(f"Invalid variable name: {var}")
        
        return v


class PromptCreate(PromptBase):
    """Schema for creating a prompt."""

    @model_validator(mode='after')
    def validate_prompt_create(self) -> 'PromptCreate':
        """Validate prompt creation data."""
        # Validate chain configuration
        if self.is_chain and not self.chain_steps:
            raise ValueError("Chain prompts must have chain_steps defined")
        
        if not self.is_chain and self.chain_steps:
            raise ValueError("Non-chain prompts cannot have chain_steps")
        
        # Validate JSON schemas if provided
        if self.input_schema:
            self._validate_json_schema(self.input_schema, "input_schema")
        
        if self.output_schema:
            self._validate_json_schema(self.output_schema, "output_schema")
        
        # Validate required variables are in variables list
        if self.required_variables and self.variables:
            missing_vars = set(self.required_variables) - set(self.variables)
            if missing_vars:
                raise ValueError(f"Required variables not in variables list: {missing_vars}")
        
        # Validate suggested temperature range
        if self.suggested_temperature is not None:
            if not 0.0 <= self.suggested_temperature <= 2.0:
                raise ValueError("Suggested temperature must be between 0.0 and 2.0")
        
        return self
    
    def _validate_json_schema(self, schema: dict, field_name: str) -> None:
        """Validate that a dictionary is a valid JSON schema."""
        try:
            import jsonschema
            # This will raise SchemaError if invalid
            jsonschema.Draft7Validator.check_schema(schema)
        except ImportError:
            # If jsonschema not available, do basic validation
            if not isinstance(schema, dict):
                raise ValueError(f"{field_name} must be a valid JSON object")
        except Exception as e:
            raise ValueError(f"Invalid {field_name}: {e}")

    pass


class PromptUpdate(BaseModel):
    """Schema for updating a prompt."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Prompt name"
    )
    description: str | None = Field(
        None, description="Prompt description"
    )
    prompt_type: PromptType | None = Field(
        None, description="Prompt type"
    )
    category: PromptCategory | None = Field(
        None, description="Prompt category"
    )

    # Prompt content
    content: str | None = Field(
        None, min_length=1, description="Prompt content/template"
    )
    variables: list[str] | None = Field(
        None, description="Template variables"
    )

    # Template configuration
    template_format: str | None = Field(
        None, description="Template format"
    )
    input_schema: dict[str, Any] | None = Field(
        None, description="Input validation schema"
    )
    output_schema: dict[str, Any] | None = Field(
        None, description="Output validation schema"
    )

    # Validation and constraints
    max_length: int | None = Field(
        None, ge=1, description="Maximum content length"
    )
    min_length: int | None = Field(
        None, ge=1, description="Minimum content length"
    )
    required_variables: list[str] | None = Field(
        None, description="Required template variables"
    )

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(
        None, description="Usage examples"
    )
    test_cases: list[dict[str, Any]] | None = Field(
        None, description="Test cases"
    )

    # LLM configuration hints
    suggested_temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Suggested temperature"
    )
    suggested_max_tokens: int | None = Field(
        None, ge=1, description="Suggested max tokens"
    )
    suggested_providers: list[str] | None = Field(
        None, description="Suggested LLM providers"
    )

    # Chain configuration
    is_chain: bool | None = Field(
        None, description="Whether this is a chain prompt"
    )
    chain_steps: list[dict[str, Any]] | None = Field(
        None, description="Chain execution steps"
    )
    parent_prompt_id: str | None = Field(
        None, description="Parent prompt ID"
    )

    # Access control
    is_public: bool | None = Field(
        None, description="Whether prompt is public"
    )

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )

    @model_validator(mode='after')
    def validate_prompt_update(self) -> 'PromptUpdate':
        """Validate prompt update data."""
        # Validate chain configuration consistency
        if self.is_chain is not None and self.chain_steps is not None:
            if self.is_chain and not self.chain_steps:
                raise ValueError("Chain prompts must have chain_steps defined")
            if not self.is_chain and self.chain_steps:
                raise ValueError("Non-chain prompts cannot have chain_steps")
        
        # Validate JSON schemas if provided
        if self.input_schema:
            self._validate_json_schema(self.input_schema, "input_schema")
        
        if self.output_schema:
            self._validate_json_schema(self.output_schema, "output_schema")
        
        # Validate required variables are in variables list
        if self.required_variables and self.variables:
            missing_vars = set(self.required_variables) - set(self.variables)
            if missing_vars:
                raise ValueError(f"Required variables not in variables list: {missing_vars}")
        
        # Validate length constraints
        if self.min_length is not None and self.max_length is not None:
            if self.min_length > self.max_length:
                raise ValueError("min_length cannot be greater than max_length")
        
        return self
    
    def _validate_json_schema(self, schema: dict, field_name: str) -> None:
        """Validate that a dictionary is a valid JSON schema."""
        try:
            import jsonschema
            # This will raise SchemaError if invalid
            jsonschema.Draft7Validator.check_schema(schema)
        except ImportError:
            # If jsonschema not available, do basic validation
            if not isinstance(schema, dict):
                raise ValueError(f"{field_name} must be a valid JSON object")
        except Exception as e:
            raise ValueError(f"Invalid {field_name}: {e}")


class PromptResponse(BaseModel):
    """Schema for prompt response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Prompt ID")
    owner_id: str = Field(..., description="Owner user ID")
    name: str = Field(..., description="Prompt name")
    description: str | None = Field(
        None, description="Prompt description"
    )
    prompt_type: PromptType = Field(..., description="Prompt type")
    category: PromptCategory = Field(..., description="Prompt category")

    # Prompt content
    content: str = Field(..., description="Prompt content/template")
    variables: list[str] | None = Field(
        None, description="Template variables"
    )

    # Template configuration
    template_format: str = Field(..., description="Template format")
    input_schema: dict[str, Any] | None = Field(
        None, description="Input validation schema"
    )
    output_schema: dict[str, Any] | None = Field(
        None, description="Output validation schema"
    )

    # Validation and constraints
    max_length: int | None = Field(
        None, description="Maximum content length"
    )
    min_length: int | None = Field(
        None, description="Minimum content length"
    )
    required_variables: list[str] | None = Field(
        None, description="Required template variables"
    )

    # Examples and testing
    examples: list[dict[str, Any]] | None = Field(
        None, description="Usage examples"
    )
    test_cases: list[dict[str, Any]] | None = Field(
        None, description="Test cases"
    )

    # LLM configuration hints
    suggested_temperature: float | None = Field(
        None, description="Suggested temperature"
    )
    suggested_max_tokens: int | None = Field(
        None, description="Suggested max tokens"
    )
    suggested_providers: list[str] | None = Field(
        None, description="Suggested LLM providers"
    )

    # Chain configuration
    is_chain: bool = Field(
        ..., description="Whether this is a chain prompt"
    )
    chain_steps: list[dict[str, Any]] | None = Field(
        None, description="Chain execution steps"
    )
    parent_prompt_id: str | None = Field(
        None, description="Parent prompt ID"
    )

    # Version control
    version: int = Field(..., description="Prompt version")
    is_latest: bool = Field(
        ..., description="Whether this is the latest version"
    )
    changelog: str | None = Field(None, description="Version changelog")

    # Access control
    is_public: bool = Field(..., description="Whether prompt is public")

    # Quality and ratings
    rating: float | None = Field(None, description="Average rating")
    rating_count: int = Field(..., description="Number of ratings")

    # Usage statistics
    usage_count: int = Field(..., description="Usage count")
    success_rate: float | None = Field(None, description="Success rate")
    avg_response_time_ms: int | None = Field(
        None, description="Average response time"
    )
    last_used_at: datetime | None = Field(
        None, description="Last used timestamp"
    )

    # Performance metrics
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    avg_tokens_per_use: float | None = Field(
        None, description="Average tokens per use"
    )

    # Metadata and tags
    tags: list[str] | None = Field(None, description="Prompt tags")
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )

    # Content analysis
    content_hash: str = Field(..., description="Content hash")
    estimated_tokens: int | None = Field(
        None, description="Estimated token count"
    )
    language: str | None = Field(None, description="Content language")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )


class PromptListRequest(ListRequestBase):
    """Schema for prompt list request."""

    prompt_type: PromptType | None = Field(
        None, description="Filter by prompt type"
    )
    category: PromptCategory | None = Field(
        None, description="Filter by category"
    )
    tags: list[str] | None = Field(None, description="Filter by tags")
    is_public: bool | None = Field(
        None, description="Filter by public status"
    )
    is_chain: bool | None = Field(
        None, description="Filter by chain status"
    )

    # Pagination and sorting fields
    limit: int = Field(
        50, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


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

    prompts: list[PromptResponse] = Field(
        ..., description="List of prompts"
    )
    total_count: int = Field(..., description="Total number of prompts")
    limit: int = Field(..., description="Requested limit")
    offset: int = Field(..., description="Requested offset")


class PromptTestRequest(BaseModel):
    """Schema for prompt test request."""

    variables: dict[str, Any] = Field(
        ..., description="Variables to test with"
    )
    validate_only: bool = Field(
        False, description="Only validate, don't render"
    )


class PromptTestResponse(BaseModel):
    """Schema for prompt test response."""

    rendered_content: str | None = Field(
        None, description="Rendered prompt content"
    )
    validation_result: dict[str, Any] = Field(
        ..., description="Validation results"
    )
    estimated_tokens: int | None = Field(
        None, description="Estimated token count"
    )
    test_duration_ms: int = Field(
        ..., description="Test execution time"
    )


class PromptCloneRequest(BaseModel):
    """Schema for prompt clone request."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="New prompt name"
    )
    description: str | None = Field(
        None, description="New prompt description"
    )
    modifications: dict[str, Any] | None = Field(
        None, description="Modifications to apply"
    )


class PromptStatsResponse(BaseModel):
    """Schema for prompt statistics response."""

    total_prompts: int = Field(
        ..., description="Total number of prompts"
    )
    prompts_by_type: dict[str, int] = Field(
        ..., description="Prompts by type"
    )
    prompts_by_category: dict[str, int] = Field(
        ..., description="Prompts by category"
    )
    most_used_prompts: list[PromptResponse] = Field(
        ..., description="Most used prompts"
    )
    recent_prompts: list[PromptResponse] = Field(
        ..., description="Recently created prompts"
    )
    usage_stats: dict[str, Any] = Field(
        ..., description="Usage statistics"
    )


class PromptDeleteResponse(BaseModel):
    """Schema for prompt delete response."""

    message: str = Field(..., description="Success message")
