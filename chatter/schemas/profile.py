"""Profile management schemas."""

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from chatter.models.profile import ProfileType
from chatter.schemas.common import (
    DeleteRequestBase,
    GetRequestBase,
    ListRequestBase,
)

if TYPE_CHECKING:
    pass


class ProfileBase(BaseModel):
    """Base profile schema."""

    name: str = Field(
        ..., min_length=1, max_length=255, description="Profile name"
    )
    description: str | None = Field(
        None, max_length=2000, description="Profile description"
    )
    profile_type: ProfileType = Field(
        ProfileType.CUSTOM, description="Profile type"
    )

    # LLM Configuration
    llm_provider: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="LLM provider (openai, anthropic, etc.)",
    )
    llm_model: str = Field(
        ..., min_length=1, max_length=100, description="LLM model name"
    )

    # Generation parameters
    temperature: float = Field(
        0.7, ge=0.0, le=2.0, description="Temperature for generation"
    )
    top_p: float | None = Field(
        None, ge=0.0, le=1.0, description="Top-p sampling parameter"
    )
    top_k: int | None = Field(
        None, ge=1, le=1000, description="Top-k sampling parameter"
    )
    max_tokens: int = Field(
        4096, ge=1, le=100000, description="Maximum tokens to generate"
    )
    presence_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Presence penalty"
    )
    frequency_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )

    # Context configuration
    context_window: int = Field(
        4096, ge=1, le=200000, description="Context window size"
    )
    system_prompt: str | None = Field(
        None, max_length=10000, description="System prompt template"
    )

    # Memory and retrieval settings
    memory_enabled: bool = Field(
        True, description="Enable conversation memory"
    )
    memory_strategy: str | None = Field(
        None, max_length=50, description="Memory management strategy"
    )
    enable_retrieval: bool = Field(
        False, description="Enable document retrieval"
    )
    retrieval_limit: int = Field(
        5, ge=1, le=50, description="Number of documents to retrieve"
    )
    retrieval_score_threshold: float = Field(
        0.7, ge=0.0, le=1.0, description="Minimum retrieval score"
    )

    # Tool calling
    enable_tools: bool = Field(False, description="Enable tool calling")
    available_tools: list[str] | None = Field(
        None, max_length=20, description="List of available tools"
    )
    tool_choice: str | None = Field(
        None, max_length=50, description="Tool choice strategy"
    )

    # Safety and filtering
    content_filter_enabled: bool = Field(
        True, description="Enable content filtering"
    )
    safety_level: str | None = Field(
        None, max_length=20, description="Safety level"
    )

    # Response formatting
    response_format: str | None = Field(
        None,
        max_length=20,
        description="Response format (json, text, markdown)",
    )
    stream_response: bool = Field(
        True, description="Enable streaming responses"
    )

    # Advanced settings
    seed: int | None = Field(
        None,
        ge=0,
        le=2147483647,
        description="Random seed for reproducibility",
    )
    stop_sequences: list[str] | None = Field(
        None, max_length=10, description="Stop sequences"
    )
    logit_bias: dict[str, float] | None = Field(
        None, description="Logit bias adjustments"
    )

    # Embedding configuration
    embedding_provider: str | None = Field(
        None, max_length=50, description="Embedding provider"
    )
    embedding_model: str | None = Field(
        None, max_length=100, description="Embedding model"
    )

    # Access control
    is_public: bool = Field(
        False, description="Whether profile is public"
    )

    # Metadata and tags
    tags: list[str] | None = Field(
        None, max_length=10, description="Profile tags"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )

    @field_validator("name", "description")
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        """Validate text fields for security threats."""
        if v is not None:
            # Use unified validation system for security validation
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            result = validation_engine.validate_security(
                v, DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise ValueError(
                    f"Security validation failed: {result.errors[0].message}"
                )
        return v

    @field_validator("system_prompt")
    @classmethod
    def validate_system_prompt(cls, v: str | None) -> str | None:
        """Validate system prompt - less strict than other text fields."""
        if v is not None:
            # Only check for XSS attacks, not SQL injection for system prompts
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            result = validation_engine.validate_security(
                v, DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise ValueError(
                    f"Security validation failed: {result.errors[0].message}"
                )
        return v

    @field_validator(
        "llm_provider",
        "llm_model",
        "embedding_provider",
        "embedding_model",
    )
    @classmethod
    def validate_provider_model(cls, v: str | None) -> str | None:
        """Validate provider and model names."""
        if v:
            # Basic validation for provider/model names
            if (
                not v.replace("-", "")
                .replace("_", "")
                .replace(".", "")
                .isalnum()
            ):
                raise ValueError(
                    "Provider/model names can only contain alphanumeric characters, hyphens, underscores, and dots"
                )
            # Use unified validation system for security validation
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            result = validation_engine.validate_security(
                v, DEFAULT_CONTEXT
            )
            if not result.is_valid:
                raise ValueError(
                    f"Security validation failed: {result.errors[0].message}"
                )
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        """Validate tags for security."""
        if v:
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            for tag in v:
                if len(tag) > 50:
                    raise ValueError(
                        "Tag length cannot exceed 50 characters"
                    )
                result = validation_engine.validate_security(
                    tag, DEFAULT_CONTEXT
                )
                if not result.is_valid:
                    raise ValueError(
                        f"Tag security validation failed: {result.errors[0].message}"
                    )
        return v

    @field_validator("available_tools")
    @classmethod
    def validate_tools(cls, v: list[str] | None) -> list[str] | None:
        """Validate available tools."""
        if v:
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            for tool in v:
                if len(tool) > 100:
                    raise ValueError(
                        "Tool name length cannot exceed 100 characters"
                    )
                result = validation_engine.validate_security(
                    tool, DEFAULT_CONTEXT
                )
                if not result.is_valid:
                    raise ValueError(
                        f"Tool security validation failed: {result.errors[0].message}"
                    )
        return v

    @field_validator("stop_sequences")
    @classmethod
    def validate_stop_sequences(
        cls, v: list[str] | None
    ) -> list[str] | None:
        """Validate stop sequences."""
        if v:
            from chatter.core.validation import (
                DEFAULT_CONTEXT,
                validation_engine,
            )

            for seq in v:
                if len(seq) > 20:
                    raise ValueError(
                        "Stop sequence length cannot exceed 20 characters"
                    )
                result = validation_engine.validate_security(
                    seq, DEFAULT_CONTEXT
                )
                if not result.is_valid:
                    raise ValueError(
                        f"Stop sequence security validation failed: {result.errors[0].message}"
                    )
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Validate temperature is not too extreme."""
        if v <= 0.01:
            raise ValueError(
                "Temperature must be greater than 0.01 for reasonable outputs"
            )
        return v

    @field_validator("max_tokens")
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        """Validate max tokens is reasonable."""
        if v < 10:
            raise ValueError(
                "max_tokens must be at least 10 for meaningful outputs"
            )
        return v


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""

    # For profile creation, we can add specific validation that differs from updates
    # For now, it inherits all validation from ProfileBase, but this allows
    # for future customization of creation-specific validation rules

    @field_validator("llm_provider", "llm_model")
    @classmethod
    def validate_required_llm_fields(cls, v: str) -> str:
        """Ensure LLM provider and model are provided for new profiles."""
        if not v or not v.strip():
            raise ValueError(
                "LLM provider and model are required for new profiles"
            )
        return v.strip()


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Profile name"
    )
    description: str | None = Field(
        None, description="Profile description"
    )
    profile_type: ProfileType | None = Field(
        None, description="Profile type"
    )

    # LLM Configuration
    llm_provider: str | None = Field(
        default=None, description="LLM provider"
    )
    llm_model: str | None = Field(
        default=None, description="LLM model name"
    )

    # Generation parameters
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature"
    )
    top_p: float | None = Field(
        None, ge=0.0, le=1.0, description="Top-p parameter"
    )
    top_k: int | None = Field(
        default=None, ge=1, description="Top-k parameter"
    )
    max_tokens: int | None = Field(
        None, ge=1, le=100000, description="Maximum tokens"
    )
    presence_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Presence penalty"
    )
    frequency_penalty: float | None = Field(
        None, ge=-2.0, le=2.0, description="Frequency penalty"
    )

    # Context configuration
    context_window: int | None = Field(
        None, ge=1, le=200000, description="Context window size"
    )
    system_prompt: str | None = Field(
        None, description="System prompt template"
    )

    # Memory and retrieval settings
    memory_enabled: bool | None = Field(
        None, description="Enable conversation memory"
    )
    memory_strategy: str | None = Field(
        None, description="Memory management strategy"
    )
    enable_retrieval: bool | None = Field(
        None, description="Enable document retrieval"
    )
    retrieval_limit: int | None = Field(
        None, ge=1, le=50, description="Number of documents to retrieve"
    )
    retrieval_score_threshold: float | None = Field(
        None, ge=0.0, le=1.0, description="Minimum retrieval score"
    )

    # Tool calling
    enable_tools: bool | None = Field(
        None, description="Enable tool calling"
    )
    available_tools: list[str] | None = Field(
        None, description="List of available tools"
    )
    tool_choice: str | None = Field(
        None, description="Tool choice strategy"
    )

    # Safety and filtering
    content_filter_enabled: bool | None = Field(
        None, description="Enable content filtering"
    )
    safety_level: str | None = Field(
        default=None, description="Safety level"
    )

    # Response formatting
    response_format: str | None = Field(
        None, description="Response format"
    )
    stream_response: bool | None = Field(
        None, description="Enable streaming responses"
    )

    # Advanced settings
    seed: int | None = Field(default=None, description="Random seed")
    stop_sequences: list[str] | None = Field(
        None, description="Stop sequences"
    )
    logit_bias: dict[str, float] | None = Field(
        None, description="Logit bias adjustments"
    )

    # Embedding configuration
    embedding_provider: str | None = Field(
        None, description="Embedding provider"
    )
    embedding_model: str | None = Field(
        None, description="Embedding model"
    )

    # Access control
    is_public: bool | None = Field(
        None, description="Whether profile is public"
    )

    # Metadata and tags
    tags: list[str] | None = Field(
        default=None, description="Profile tags"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ProfileResponse(ProfileBase):
    """Schema for profile response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Profile ID")
    owner_id: str = Field(..., description="Owner user ID")
    usage_count: int = Field(..., description="Number of times used")
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost incurred")
    last_used_at: datetime | None = Field(
        None, description="Last usage time"
    )
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class ProfileListRequest(ListRequestBase):
    """Schema for profile list request."""

    profile_type: ProfileType | None = Field(
        None, description="Filter by profile type"
    )
    llm_provider: str | None = Field(
        None, description="Filter by LLM provider"
    )
    tags: list[str] | None = Field(
        default=None, description="Filter by tags"
    )
    is_public: bool | None = Field(
        None, description="Filter by public status"
    )

    # Pagination and sorting fields
    limit: int = Field(
        50, ge=1, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


class ProfileGetRequest(GetRequestBase):
    """Schema for profile get request."""

    pass


class ProfileDeleteRequest(DeleteRequestBase):
    """Schema for profile delete request."""

    pass


class ProfileStatsRequest(GetRequestBase):
    """Schema for profile stats request."""

    pass


class ProfileProvidersRequest(GetRequestBase):
    """Schema for profile providers request."""

    pass


class ProfileListResponse(BaseModel):
    """Schema for profile list response."""

    profiles: list[ProfileResponse] = Field(
        ..., description="List of profiles"
    )
    total_count: int = Field(
        ..., description="Total number of profiles"
    )
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class ProfileStatsResponse(BaseModel):
    """Schema for profile statistics response."""

    total_profiles: int = Field(
        ..., description="Total number of profiles"
    )
    profiles_by_type: dict[str, int] = Field(
        ..., description="Profiles grouped by type"
    )
    profiles_by_provider: dict[str, int] = Field(
        ..., description="Profiles grouped by LLM provider"
    )
    most_used_profiles: list[ProfileResponse] = Field(
        ..., description="Most frequently used profiles"
    )
    recent_profiles: list[ProfileResponse] = Field(
        ..., description="Recently created profiles"
    )
    usage_stats: dict[str, Any] = Field(
        ..., description="Usage statistics"
    )


class ProfileTestRequest(BaseModel):
    """Schema for profile test request."""

    test_message: str = Field(
        ..., min_length=1, max_length=1000, description="Test message"
    )
    include_retrieval: bool = Field(
        False, description="Include retrieval in test"
    )
    include_tools: bool = Field(
        False, description="Include tools in test"
    )

    @field_validator("test_message")
    @classmethod
    def validate_test_message(cls, v: str) -> str:
        """Validate test message for security threats."""
        from chatter.core.validation import (
            DEFAULT_CONTEXT,
            validation_engine,
        )

        result = validation_engine.validate_security(v, DEFAULT_CONTEXT)
        if not result.is_valid:
            raise ValueError(
                f"Test message security validation failed: {result.errors[0].message}"
            )
        return v


class ProfileTestResponse(BaseModel):
    """Schema for profile test response."""

    profile_id: str = Field(..., description="Profile ID")
    test_message: str = Field(..., description="Test message sent")
    response: str = Field(..., description="Generated response")
    usage_info: dict[str, Any] = Field(
        ..., description="Token usage and cost information"
    )
    response_time_ms: int = Field(
        ..., description="Response time in milliseconds"
    )
    retrieval_results: list[dict[str, Any]] | None = Field(
        None, description="Retrieval results if enabled"
    )
    tools_used: list[str] | None = Field(
        None, description="Tools used if enabled"
    )


class ProfileCloneRequest(BaseModel):
    """Schema for profile clone request."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="New profile name",
    )
    description: str | None = Field(
        None, description="New profile description"
    )
    modifications: ProfileUpdate | None = Field(
        None, description="Modifications to apply to cloned profile"
    )


class ProfileImportRequest(BaseModel):
    """Schema for profile import request."""

    profile_data: ProfileCreate = Field(
        ..., description="Profile data to import"
    )
    overwrite_existing: bool = Field(
        False, description="Overwrite if profile with same name exists"
    )


class ProfileExportResponse(BaseModel):
    """Schema for profile export response."""

    profile: ProfileResponse = Field(..., description="Profile data")
    export_format: str = Field("json", description="Export format")
    exported_at: datetime = Field(..., description="Export timestamp")
    version: str = Field("1.0", description="Export format version")


class ProfileDeleteResponse(BaseModel):
    """Schema for profile delete response."""

    message: str = Field(..., description="Success message")


class AvailableProvidersResponse(BaseModel):
    """Schema for available providers response."""

    providers: dict[str, Any] = Field(
        ...,
        description="Available LLM providers with their configurations",
    )
    total_providers: int = Field(
        ..., description="Total number of available providers"
    )
    supported_features: dict[str, list[str]] = Field(
        ..., description="Features supported by each provider"
    )
