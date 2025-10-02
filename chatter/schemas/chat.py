"""Chat schemas for request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.models.conversation import ConversationStatus, MessageRole
from chatter.schemas.common import (
    DeleteRequestBase,
    GetRequestBase,
    ListRequestBase,
)


class MessageBase(BaseModel):
    """Base message schema."""

    role: MessageRole = Field(..., description="Message role")
    content: str = Field(
        ..., min_length=1, description="Message content"
    )


class MessageCreate(MessageBase):
    """Schema for creating a message."""

    pass


class MessageResponse(MessageBase):
    """Schema for message response."""

    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sequence_number: int = Field(
        ..., description="Message sequence number"
    )
    prompt_tokens: int | None = Field(
        None, description="Prompt tokens used"
    )
    completion_tokens: int | None = Field(
        None, description="Completion tokens used"
    )
    total_tokens: int | None = Field(
        None, description="Total tokens used"
    )
    model_used: str | None = Field(
        None, description="Model used for generation"
    )
    provider_used: str | None = Field(
        default=None, description="Provider used"
    )
    response_time_ms: int | None = Field(
        None, description="Response time in milliseconds"
    )
    cost: float | None = Field(
        default=None, description="Cost of the message"
    )
    finish_reason: str | None = Field(
        None, description="Reason for completion"
    )
    rating: float | None = Field(
        None, ge=0.0, le=5.0, description="User rating for the message"
    )
    rating_count: int = Field(
        default=0, ge=0, description="Number of ratings for the message"
    )
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema."""

    title: str = Field(..., description="Conversation title")
    description: str | None = Field(
        None, description="Conversation description"
    )


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""

    profile_id: str | None = Field(
        None, description="Profile ID to use"
    )
    system_prompt: str | None = Field(
        default=None, description="System prompt"
    )
    enable_retrieval: bool = Field(
        default=False, description="Enable document retrieval"
    )
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature setting"
    )
    max_tokens: int | None = Field(
        None, ge=1, description="Max tokens setting"
    )
    workflow_config: dict[str, Any] | None = Field(
        None, description="Workflow configuration"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(
        default=None, description="Conversation title"
    )
    description: str | None = Field(
        None, description="Conversation description"
    )
    status: ConversationStatus | None = Field(
        None, description="Conversation status"
    )
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature setting"
    )
    max_tokens: int | None = Field(
        None, ge=1, description="Max tokens setting"
    )
    workflow_config: dict[str, Any] | None = Field(
        None, description="Workflow configuration"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""

    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    profile_id: str | None = Field(
        default=None, description="Profile ID"
    )
    status: ConversationStatus = Field(
        ..., description="Conversation status"
    )
    llm_provider: str | None = Field(
        default=None, description="LLM provider"
    )
    llm_model: str | None = Field(default=None, description="LLM model")
    temperature: float | None = Field(
        None, description="Temperature setting"
    )
    max_tokens: int | None = Field(
        None, description="Max tokens setting"
    )
    enable_retrieval: bool = Field(..., description="Retrieval enabled")
    message_count: int = Field(..., description="Number of messages")
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")

    # Configuration fields that were missing
    system_prompt: str | None = Field(
        default=None, description="System prompt"
    )
    context_window: int = Field(..., description="Context window size")
    memory_enabled: bool = Field(..., description="Memory enabled")
    memory_strategy: str | None = Field(
        None, description="Memory strategy"
    )
    retrieval_limit: int = Field(..., description="Retrieval limit")
    retrieval_score_threshold: float = Field(
        ..., description="Retrieval score threshold"
    )

    # Metadata fields that were missing
    tags: list[str] | None = Field(
        None, description="Conversation tags"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Extra metadata"
    )
    workflow_config: dict[str, Any] | None = Field(
        None, description="Workflow configuration"
    )

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(
        ..., description="Last update timestamp"
    )
    last_message_at: datetime | None = Field(
        None, description="Last message timestamp"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages."""

    messages: list[MessageResponse] = Field(
        default_factory=list, description="Conversation messages"
    )


class WorkflowTemplateInfo(BaseModel):
    """Schema for workflow template information."""

    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    required_tools: list[str] = Field(..., description="Required tools")
    required_retrievers: list[str] = Field(
        ..., description="Required retrievers"
    )
    default_params: dict[str, Any] = Field(
        ..., description="Default parameters"
    )


class WorkflowTemplatesResponse(BaseModel):
    """Schema for workflow templates response."""

    templates: dict[str, WorkflowTemplateInfo] = Field(
        ..., description="Available templates"
    )
    total_count: int = Field(
        ..., description="Total number of templates"
    )


class PerformanceStatsResponse(BaseModel):
    """Schema for performance statistics response."""

    total_executions: int = Field(
        ..., description="Total number of executions"
    )
    avg_execution_time_ms: int = Field(
        ..., description="Average execution time in milliseconds"
    )
    min_execution_time_ms: int = Field(
        ..., description="Minimum execution time in milliseconds"
    )
    max_execution_time_ms: int = Field(
        ..., description="Maximum execution time in milliseconds"
    )
    error_counts: dict[str, int] = Field(
        ..., description="Error count by type"
    )
    cache_stats: dict[str, Any] = Field(
        ..., description="Cache statistics"
    )
    tool_stats: dict[str, Any] = Field(
        ..., description="Tool usage statistics"
    )
    timestamp: float = Field(..., description="Statistics timestamp")


class ChatRequest(BaseModel):
    """Schema for chat request.
    
    This unified schema supports both simple chat and workflow execution,
    eliminating the need for separate ChatWorkflowRequest type.
    """

    message: str = Field(..., description="User message")
    conversation_id: str | None = Field(
        None, description="Conversation ID for continuing chat"
    )
    profile_id: str | None = Field(
        None, description="Profile ID to use"
    )

    # Workflow specification (optional - for workflow execution)
    workflow_config: dict[str, Any] | None = Field(
        None, description="Dynamic workflow configuration"
    )
    workflow_definition_id: str | None = Field(
        None, description="Existing workflow definition ID"
    )
    workflow_template_name: str | None = Field(
        None, description="Workflow template name"
    )

    # Workflow capability flags
    enable_retrieval: bool = Field(
        default=False, description="Enable retrieval capabilities"
    )
    enable_tools: bool = Field(
        default=False, description="Enable tool calling capabilities"
    )
    enable_memory: bool = Field(
        default=True, description="Enable memory capabilities"
    )
    enable_web_search: bool = Field(
        default=False, description="Enable web search capabilities"
    )

    # Provider override (optional)
    provider: str | None = Field(
        None, description="Override LLM provider for this request"
    )
    model: str | None = Field(
        None, description="Override LLM model for this request"
    )

    # Optional overrides
    temperature: float | None = Field(
        None, ge=0.0, le=2.0, description="Temperature override"
    )
    max_tokens: int | None = Field(
        None, ge=1, le=8192, description="Max tokens override"
    )
    context_limit: int | None = Field(
        None, ge=1, description="Context limit override"
    )
    document_ids: list[str] | None = Field(
        None, description="Document IDs to include in context"
    )
    prompt_id: str | None = Field(
        None, description="Prompt template ID to use for this request"
    )
    system_prompt_override: str | None = Field(
        None, description="Override system prompt for this request"
    )
    
    # Debug configuration
    enable_tracing: bool = Field(
        default=False, description="Enable backend workflow tracing"
    )


class ChatResponse(BaseModel):
    """Schema for chat response."""

    conversation_id: str = Field(..., description="Conversation ID")
    message: MessageResponse = Field(
        ..., description="Assistant response message"
    )
    conversation: ConversationResponse = Field(
        ..., description="Updated conversation"
    )


class StreamingChatChunk(BaseModel):
    """Schema for streaming chat chunk."""

    type: str = Field(
        ..., description="Chunk type: 'token', 'usage', 'end'"
    )
    content: str | None = Field(
        default=None, description="Token content"
    )
    usage: dict[str, Any] | None = Field(
        default=None, description="Token usage information"
    )
    conversation_id: str | None = Field(
        default=None, description="Conversation ID"
    )
    message_id: str | None = Field(
        default=None, description="Message ID"
    )
    correlation_id: str | None = Field(
        default=None, description="Correlation ID"
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Additional metadata"
    )


class ConversationListRequest(ListRequestBase):
    """Schema for conversation list request."""

    status: ConversationStatus | None = Field(
        None, description="Filter by conversation status"
    )
    llm_provider: str | None = Field(
        None, description="Filter by LLM provider"
    )
    llm_model: str | None = Field(
        None, description="Filter by LLM model"
    )
    tags: list[str] | None = Field(
        default=None, description="Filter by tags"
    )
    enable_retrieval: bool | None = Field(
        None, description="Filter by retrieval enabled status"
    )

    # Pagination and sorting fields
    limit: int = Field(
        50, ge=1, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )
    sort_by: str = Field("updated_at", description="Sort field")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


class ConversationGetRequest(GetRequestBase):
    """Schema for conversation get request."""

    pass


class ConversationDeleteRequest(DeleteRequestBase):
    """Schema for conversation delete request."""

    pass


class ConversationMessagesRequest(GetRequestBase):
    """Schema for conversation messages request."""

    pass


class AvailableToolsRequest(GetRequestBase):
    """Schema for available tools request."""

    pass


class McpStatusRequest(GetRequestBase):
    """Schema for MCP status request."""

    pass


class ConversationListResponse(BaseModel):
    """Schema for conversation list response."""

    conversations: list[ConversationResponse] = Field(
        ..., description="List of conversations"
    )
    total_count: int = Field(
        ..., description="Total number of conversations"
    )
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class ConversationDeleteResponse(BaseModel):
    """Schema for conversation delete response."""

    message: str = Field(..., description="Success message")


class MessageDeleteResponse(BaseModel):
    """Response schema for message deletion."""

    message: str = Field(..., description="Deletion result message")


class MessageRatingUpdate(BaseModel):
    """Schema for updating message rating."""

    rating: float = Field(
        ..., ge=0.0, le=5.0, description="Rating value from 0.0 to 5.0"
    )


class MessageRatingResponse(BaseModel):
    """Response schema for message rating update."""

    message: str = Field(
        ..., description="Rating update result message"
    )
    rating: float = Field(..., description="Updated rating value")
    rating_count: int = Field(
        ..., description="Total number of ratings"
    )


class AvailableToolResponse(BaseModel):
    """Schema for individual available tool."""

    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    type: str = Field(..., description="Tool type (mcp, builtin)")
    args_schema: dict[str, Any] = Field(
        ..., description="Tool arguments schema"
    )


class AvailableToolsResponse(BaseModel):
    """Schema for available tools response."""

    tools: list[AvailableToolResponse] = Field(
        ..., description="Available tools"
    )


class McpStatusResponse(BaseModel):
    """Schema for MCP status response."""

    status: str = Field(..., description="MCP service status")
    servers: list[dict[str, Any]] = Field(
        ..., description="Connected servers"
    )
    last_check: datetime | None = Field(
        None, description="Last health check time"
    )
    errors: list[str] = Field(
        default_factory=list, description="Any error messages"
    )
