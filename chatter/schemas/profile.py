"""Profile management schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from chatter.models.profile import ProfileType


class ProfileBase(BaseModel):
    """Base profile schema."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    profile_type: ProfileType = Field(ProfileType.CUSTOM, description="Profile type")
    
    # LLM Configuration
    llm_provider: str = Field(..., description="LLM provider (openai, anthropic, etc.)")
    llm_model: str = Field(..., description="LLM model name")
    
    # Generation parameters
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for generation")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p sampling parameter")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k sampling parameter")
    max_tokens: int = Field(4096, ge=1, le=100000, description="Maximum tokens to generate")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    
    # Context configuration
    context_window: int = Field(4096, ge=1, le=200000, description="Context window size")
    system_prompt: Optional[str] = Field(None, description="System prompt template")
    
    # Memory and retrieval settings
    memory_enabled: bool = Field(True, description="Enable conversation memory")
    memory_strategy: Optional[str] = Field(None, description="Memory management strategy")
    enable_retrieval: bool = Field(False, description="Enable document retrieval")
    retrieval_limit: int = Field(5, ge=1, le=50, description="Number of documents to retrieve")
    retrieval_score_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum retrieval score")
    
    # Tool calling
    enable_tools: bool = Field(False, description="Enable tool calling")
    available_tools: Optional[List[str]] = Field(None, description="List of available tools")
    tool_choice: Optional[str] = Field(None, description="Tool choice strategy")
    
    # Safety and filtering
    content_filter_enabled: bool = Field(True, description="Enable content filtering")
    safety_level: Optional[str] = Field(None, description="Safety level")
    
    # Response formatting
    response_format: Optional[str] = Field(None, description="Response format (json, text, markdown)")
    stream_response: bool = Field(True, description="Enable streaming responses")
    
    # Advanced settings
    seed: Optional[int] = Field(None, description="Random seed for reproducibility")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias adjustments")
    
    # Embedding configuration
    embedding_provider: Optional[str] = Field(None, description="Embedding provider")
    embedding_model: Optional[str] = Field(None, description="Embedding model")
    
    # Access control
    is_public: bool = Field(False, description="Whether profile is public")
    shared_with_users: Optional[List[str]] = Field(None, description="Users with access")
    
    # Metadata and tags
    tags: Optional[List[str]] = Field(None, description="Profile tags")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    pass


class ProfileUpdate(BaseModel):
    """Schema for updating a profile."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Profile name")
    description: Optional[str] = Field(None, description="Profile description")
    profile_type: Optional[ProfileType] = Field(None, description="Profile type")
    
    # LLM Configuration
    llm_provider: Optional[str] = Field(None, description="LLM provider")
    llm_model: Optional[str] = Field(None, description="LLM model name")
    
    # Generation parameters
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0, description="Temperature")
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0, description="Top-p parameter")
    top_k: Optional[int] = Field(None, ge=1, description="Top-k parameter")
    max_tokens: Optional[int] = Field(None, ge=1, le=100000, description="Maximum tokens")
    presence_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Presence penalty")
    frequency_penalty: Optional[float] = Field(None, ge=-2.0, le=2.0, description="Frequency penalty")
    
    # Context configuration
    context_window: Optional[int] = Field(None, ge=1, le=200000, description="Context window size")
    system_prompt: Optional[str] = Field(None, description="System prompt template")
    
    # Memory and retrieval settings
    memory_enabled: Optional[bool] = Field(None, description="Enable conversation memory")
    memory_strategy: Optional[str] = Field(None, description="Memory management strategy")
    enable_retrieval: Optional[bool] = Field(None, description="Enable document retrieval")
    retrieval_limit: Optional[int] = Field(None, ge=1, le=50, description="Number of documents to retrieve")
    retrieval_score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum retrieval score")
    
    # Tool calling
    enable_tools: Optional[bool] = Field(None, description="Enable tool calling")
    available_tools: Optional[List[str]] = Field(None, description="List of available tools")
    tool_choice: Optional[str] = Field(None, description="Tool choice strategy")
    
    # Safety and filtering
    content_filter_enabled: Optional[bool] = Field(None, description="Enable content filtering")
    safety_level: Optional[str] = Field(None, description="Safety level")
    
    # Response formatting
    response_format: Optional[str] = Field(None, description="Response format")
    stream_response: Optional[bool] = Field(None, description="Enable streaming responses")
    
    # Advanced settings
    seed: Optional[int] = Field(None, description="Random seed")
    stop_sequences: Optional[List[str]] = Field(None, description="Stop sequences")
    logit_bias: Optional[Dict[str, float]] = Field(None, description="Logit bias adjustments")
    
    # Embedding configuration
    embedding_provider: Optional[str] = Field(None, description="Embedding provider")
    embedding_model: Optional[str] = Field(None, description="Embedding model")
    
    # Access control
    is_public: Optional[bool] = Field(None, description="Whether profile is public")
    shared_with_users: Optional[List[str]] = Field(None, description="Users with access")
    
    # Metadata and tags
    tags: Optional[List[str]] = Field(None, description="Profile tags")
    extra_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ProfileResponse(ProfileBase):
    """Schema for profile response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: str = Field(..., description="Profile ID")
    owner_id: str = Field(..., description="Owner user ID")
    usage_count: int = Field(..., description="Number of times used")
    total_tokens_used: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost incurred")
    last_used_at: Optional[datetime] = Field(None, description="Last usage time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class ProfileListRequest(BaseModel):
    """Schema for profile list request."""
    
    profile_type: Optional[ProfileType] = Field(None, description="Filter by profile type")
    llm_provider: Optional[str] = Field(None, description="Filter by LLM provider")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    is_public: Optional[bool] = Field(None, description="Filter by public status")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")


class ProfileListResponse(BaseModel):
    """Schema for profile list response."""
    
    profiles: List[ProfileResponse] = Field(..., description="List of profiles")
    total_count: int = Field(..., description="Total number of profiles")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class ProfileStatsResponse(BaseModel):
    """Schema for profile statistics response."""
    
    total_profiles: int = Field(..., description="Total number of profiles")
    profiles_by_type: Dict[str, int] = Field(..., description="Profiles grouped by type")
    profiles_by_provider: Dict[str, int] = Field(..., description="Profiles grouped by LLM provider")
    most_used_profiles: List[ProfileResponse] = Field(..., description="Most frequently used profiles")
    recent_profiles: List[ProfileResponse] = Field(..., description="Recently created profiles")
    usage_stats: Dict[str, Any] = Field(..., description="Usage statistics")


class ProfileTestRequest(BaseModel):
    """Schema for profile test request."""
    
    test_message: str = Field(..., min_length=1, max_length=1000, description="Test message")
    include_retrieval: bool = Field(False, description="Include retrieval in test")
    include_tools: bool = Field(False, description="Include tools in test")


class ProfileTestResponse(BaseModel):
    """Schema for profile test response."""
    
    profile_id: str = Field(..., description="Profile ID")
    test_message: str = Field(..., description="Test message sent")
    response: str = Field(..., description="Generated response")
    usage_info: Dict[str, Any] = Field(..., description="Token usage and cost information")
    response_time_ms: int = Field(..., description="Response time in milliseconds")
    retrieval_results: Optional[List[Dict[str, Any]]] = Field(None, description="Retrieval results if enabled")
    tools_used: Optional[List[str]] = Field(None, description="Tools used if enabled")


class ProfileCloneRequest(BaseModel):
    """Schema for profile clone request."""
    
    name: str = Field(..., min_length=1, max_length=255, description="New profile name")
    description: Optional[str] = Field(None, description="New profile description")
    modifications: Optional[ProfileUpdate] = Field(None, description="Modifications to apply to cloned profile")


class ProfileImportRequest(BaseModel):
    """Schema for profile import request."""
    
    profile_data: ProfileCreate = Field(..., description="Profile data to import")
    overwrite_existing: bool = Field(False, description="Overwrite if profile with same name exists")


class ProfileExportResponse(BaseModel):
    """Schema for profile export response."""
    
    profile: ProfileResponse = Field(..., description="Profile data")
    export_format: str = Field("json", description="Export format")
    exported_at: datetime = Field(..., description="Export timestamp")
    version: str = Field("1.0", description="Export format version")