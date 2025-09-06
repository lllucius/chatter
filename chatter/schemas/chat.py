"""Chat schemas for request/response models."""

from datetime import datetime
from typing import Any, Literal

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
    provider_used: str | None = Field(None, description="Provider used")
    response_time_ms: int | None = Field(
        None, description="Response time in milliseconds"
    )
    cost: float | None = Field(None, description="Cost of the message")
    finish_reason: str | None = Field(
        None, description="Reason for completion"
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
    system_prompt: str | None = Field(None, description="System prompt")
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
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""

    title: str | None = Field(None, description="Conversation title")
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
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""

    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    profile_id: str | None = Field(None, description="Profile ID")
    status: ConversationStatus = Field(
        ..., description="Conversation status"
    )
    llm_provider: str | None = Field(None, description="LLM provider")
    llm_model: str | None = Field(None, description="LLM model")
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


WorkflowType = Literal["plain", "rag", "tools", "full"]


class WorkflowTemplateInfo(BaseModel):
    """Schema for workflow template information."""

    name: str = Field(..., description="Template name")
    workflow_type: str = Field(..., description="Workflow type")
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
    workflow_types: dict[str, int] = Field(
        ..., description="Execution count by workflow type"
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
    """Schema for chat request."""

    message: str = Field(..., description="User message")
    conversation_id: str | None = Field(
        None, description="Conversation ID for continuing chat"
    )
    profile_id: str | None = Field(
        None, description="Profile ID to use"
    )
    stream: bool = Field(
        default=False, description="Enable streaming response"
    )

    # Workflow selection (preferred)
    workflow: WorkflowType = Field(
        default="plain",
        description="Workflow type: plain, rag, tools, or full (rag + tools)",
    )

    # Provider override (optional)
    provider: str | None = Field(
        None, description="Override LLM provider for this request"
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
    enable_retrieval: bool | None = Field(
        None, description="Enable retrieval override"
    )
    document_ids: list[str] | None = Field(
        None, description="Document IDs to include in context"
    )
    system_prompt_override: str | None = Field(
        None, description="Override system prompt for this request"
    )
    workflow_config: dict[str, Any] | None = Field(
        None, description="Workflow configuration"
    )

    # Internal field set by API processing
    workflow_type: str | None = Field(
        None,
        description="Internal workflow type (set by API processing)",
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
    content: str | None = Field(None, description="Token content")
    usage: dict[str, Any] | None = Field(
        None, description="Token usage information"
    )
    conversation_id: str | None = Field(
        None, description="Conversation ID"
    )
    message_id: str | None = Field(None, description="Message ID")
    correlation_id: str | None = Field(
        None, description="Correlation ID"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )


class ConversationSearchRequest(ListRequestBase):
    """Schema for conversation search."""

    limit: int = Field(
        50, ge=1, le=100, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )
    search: str | None = Field(None, description="Search query")
    query: str | None = Field(None, description="Search query")
    status: ConversationStatus | None = Field(
        None, description="Filter by status"
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


class ConversationSearchResponse(BaseModel):
    """Schema for conversation search response."""

    conversations: list[ConversationResponse] = Field(
        ..., description="Conversations"
    )
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Request limit")
    offset: int = Field(..., description="Request offset")


class ConversationDeleteResponse(BaseModel):
    """Schema for conversation delete response."""

    message: str = Field(..., description="Success message")


class MessageDeleteResponse(BaseModel):
    """Response schema for message deletion."""

    message: str = Field(..., description="Deletion result message")


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
