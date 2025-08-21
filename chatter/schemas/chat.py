"""Chat schemas for request/response models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.models.conversation import ConversationStatus, MessageRole


class MessageBase(BaseModel):
    """Base message schema."""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")


class MessageCreate(MessageBase):
    """Schema for creating a message."""
    pass


class MessageResponse(MessageBase):
    """Schema for message response."""
    id: str = Field(..., description="Message ID")
    conversation_id: str = Field(..., description="Conversation ID")
    sequence_number: int = Field(..., description="Message sequence number")
    prompt_tokens: int | None = Field(None, description="Prompt tokens used")
    completion_tokens: int | None = Field(None, description="Completion tokens used")
    total_tokens: int | None = Field(None, description="Total tokens used")
    model_used: str | None = Field(None, description="Model used for generation")
    provider_used: str | None = Field(None, description="Provider used")
    response_time_ms: int | None = Field(None, description="Response time in milliseconds")
    cost: float | None = Field(None, description="Cost of the message")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema."""
    title: str = Field(..., description="Conversation title")
    description: str | None = Field(None, description="Conversation description")


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation."""
    profile_id: str | None = Field(None, description="Profile ID to use")
    system_prompt: str | None = Field(None, description="System prompt")
    enable_retrieval: bool = Field(default=False, description="Enable document retrieval")


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    title: str | None = Field(None, description="Conversation title")
    description: str | None = Field(None, description="Conversation description")
    status: ConversationStatus | None = Field(None, description="Conversation status")


class ConversationResponse(ConversationBase):
    """Schema for conversation response."""
    id: str = Field(..., description="Conversation ID")
    user_id: str = Field(..., description="User ID")
    profile_id: str | None = Field(None, description="Profile ID")
    status: ConversationStatus = Field(..., description="Conversation status")
    llm_provider: str | None = Field(None, description="LLM provider")
    llm_model: str | None = Field(None, description="LLM model")
    temperature: float | None = Field(None, description="Temperature setting")
    max_tokens: int | None = Field(None, description="Max tokens setting")
    enable_retrieval: bool = Field(..., description="Retrieval enabled")
    message_count: int = Field(..., description="Number of messages")
    total_tokens: int = Field(..., description="Total tokens used")
    total_cost: float = Field(..., description="Total cost")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_message_at: datetime | None = Field(None, description="Last message timestamp")

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages."""
    messages: list[MessageResponse] = Field(default=[], description="Conversation messages")


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., description="User message")
    conversation_id: str | None = Field(None, description="Conversation ID for continuing chat")
    profile_id: str | None = Field(None, description="Profile ID to use")
    stream: bool = Field(default=False, description="Enable streaming response")

    # Optional overrides
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Temperature override")
    max_tokens: int | None = Field(None, ge=1, le=8192, description="Max tokens override")
    enable_retrieval: bool | None = Field(None, description="Enable retrieval override")


class ChatResponse(BaseModel):
    """Schema for chat response."""
    conversation_id: str = Field(..., description="Conversation ID")
    message: MessageResponse = Field(..., description="Assistant response message")
    conversation: ConversationResponse = Field(..., description="Updated conversation")


class StreamingChatChunk(BaseModel):
    """Schema for streaming chat chunk."""
    type: str = Field(..., description="Chunk type: 'token', 'usage', 'end'")
    content: str | None = Field(None, description="Token content")
    usage: dict[str, Any] | None = Field(None, description="Token usage information")
    conversation_id: str | None = Field(None, description="Conversation ID")
    message_id: str | None = Field(None, description="Message ID")


class ConversationSearchRequest(BaseModel):
    """Schema for conversation search."""
    query: str | None = Field(None, description="Search query")
    status: ConversationStatus | None = Field(None, description="Filter by status")
    limit: int = Field(default=20, ge=1, le=100, description="Number of results")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")


class ConversationSearchResponse(BaseModel):
    """Schema for conversation search response."""
    conversations: list[ConversationResponse] = Field(..., description="Conversations")
    total: int = Field(..., description="Total number of conversations")
    limit: int = Field(..., description="Request limit")
    offset: int = Field(..., description="Request offset")
