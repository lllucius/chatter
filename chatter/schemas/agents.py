"""Agent management schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.core.agents import AgentCapability, AgentStatus, AgentType
from chatter.schemas.common import (
    DeleteRequestBase,
    GetRequestBase,
    ListRequestBase,
)


class AgentCreateRequest(BaseModel):
    """Request schema for creating an agent."""

    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: AgentType = Field(..., description="Type of agent")
    system_prompt: str = Field(..., description="System prompt for the agent")

    # Optional configuration
    personality_traits: list[str] = Field(default_factory=list, description="Agent personality traits")
    knowledge_domains: list[str] = Field(default_factory=list, description="Knowledge domains")
    response_style: str = Field("professional", description="Response style")
    capabilities: list[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    available_tools: list[str] = Field(default_factory=list, description="Available tools")

    # Model configuration
    primary_llm: str = Field("openai", description="Primary LLM provider")
    fallback_llm: str = Field("anthropic", description="Fallback LLM provider")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature for responses")
    max_tokens: int = Field(4096, ge=1, le=32000, description="Maximum tokens")

    # Performance settings
    max_conversation_length: int = Field(50, ge=1, le=1000, description="Maximum conversation length")
    context_window_size: int = Field(4000, ge=100, le=32000, description="Context window size")
    response_timeout: int = Field(30, ge=1, le=300, description="Response timeout in seconds")

    # Learning settings
    learning_enabled: bool = Field(True, description="Enable learning from feedback")
    feedback_weight: float = Field(0.1, ge=0.0, le=1.0, description="Weight for feedback learning")
    adaptation_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Adaptation threshold")

    # Metadata
    tags: list[str] = Field(default_factory=list, description="Agent tags")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class AgentUpdateRequest(BaseModel):
    """Request schema for updating an agent."""

    name: str | None = Field(None, description="Agent name")
    description: str | None = Field(None, description="Agent description")
    system_prompt: str | None = Field(None, description="System prompt for the agent")
    status: AgentStatus | None = Field(None, description="Agent status")

    # Optional configuration
    personality_traits: list[str] | None = Field(None, description="Agent personality traits")
    knowledge_domains: list[str] | None = Field(None, description="Knowledge domains")
    response_style: str | None = Field(None, description="Response style")
    capabilities: list[AgentCapability] | None = Field(None, description="Agent capabilities")
    available_tools: list[str] | None = Field(None, description="Available tools")

    # Model configuration
    primary_llm: str | None = Field(None, description="Primary LLM provider")
    fallback_llm: str | None = Field(None, description="Fallback LLM provider")
    temperature: float | None = Field(None, ge=0.0, le=2.0, description="Temperature for responses")
    max_tokens: int | None = Field(None, ge=1, le=32000, description="Maximum tokens")

    # Performance settings
    max_conversation_length: int | None = Field(None, ge=1, le=1000, description="Maximum conversation length")
    context_window_size: int | None = Field(None, ge=100, le=32000, description="Context window size")
    response_timeout: int | None = Field(None, ge=1, le=300, description="Response timeout in seconds")

    # Learning settings
    learning_enabled: bool | None = Field(None, description="Enable learning from feedback")
    feedback_weight: float | None = Field(None, ge=0.0, le=1.0, description="Weight for feedback learning")
    adaptation_threshold: float | None = Field(None, ge=0.0, le=1.0, description="Adaptation threshold")

    # Metadata
    tags: list[str] | None = Field(None, description="Agent tags")
    metadata: dict[str, Any] | None = Field(None, description="Additional metadata")


class AgentResponse(BaseModel):
    """Response schema for agent data."""

    id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    agent_type: AgentType = Field(..., description="Type of agent")
    status: AgentStatus = Field(..., description="Agent status")

    # Behavior configuration
    system_prompt: str = Field(..., description="System prompt")
    personality_traits: list[str] = Field(..., description="Agent personality traits")
    knowledge_domains: list[str] = Field(..., description="Knowledge domains")
    response_style: str = Field(..., description="Response style")

    # Capabilities
    capabilities: list[AgentCapability] = Field(..., description="Agent capabilities")
    available_tools: list[str] = Field(..., description="Available tools")

    # Model configuration
    primary_llm: str = Field(..., description="Primary LLM provider")
    fallback_llm: str = Field(..., description="Fallback LLM provider")
    temperature: float = Field(..., description="Temperature for responses")
    max_tokens: int = Field(..., description="Maximum tokens")

    # Performance settings
    max_conversation_length: int = Field(..., description="Maximum conversation length")
    context_window_size: int = Field(..., description="Context window size")
    response_timeout: int = Field(..., description="Response timeout in seconds")

    # Learning and adaptation
    learning_enabled: bool = Field(..., description="Learning enabled")
    feedback_weight: float = Field(..., description="Feedback weight")
    adaptation_threshold: float = Field(..., description="Adaptation threshold")

    # Metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator")
    tags: list[str] = Field(..., description="Agent tags")
    metadata: dict[str, Any] = Field(..., description="Additional metadata")


class AgentListRequest(ListRequestBase):
    """Request schema for listing agents."""

    agent_type: AgentType | None = Field(None, description="Filter by agent type")
    status: AgentStatus | None = Field(None, description="Filter by status")
    tags: list[str] | None = Field(None, description="Filter by tags")


class AgentListResponse(BaseModel):
    """Response schema for agent list."""

    agents: list[AgentResponse] = Field(..., description="List of agents")
    total: int = Field(..., description="Total number of agents")


class AgentGetRequest(GetRequestBase):
    """Request schema for getting an agent."""
    pass


class AgentDeleteRequest(DeleteRequestBase):
    """Request schema for deleting an agent."""
    pass


class AgentDeleteResponse(BaseModel):
    """Response schema for agent deletion."""

    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Deletion result message")


class AgentInteractRequest(BaseModel):
    """Request schema for interacting with an agent."""

    message: str = Field(..., description="Message to send to the agent")
    conversation_id: str = Field(..., description="Conversation ID")
    context: dict[str, Any] | None = Field(None, description="Additional context")


class AgentInteractResponse(BaseModel):
    """Response schema for agent interaction."""

    agent_id: str = Field(..., description="Agent ID")
    response: str = Field(..., description="Agent response")
    conversation_id: str = Field(..., description="Conversation ID")
    tools_used: list[str] = Field(..., description="Tools used in response")
    confidence_score: float = Field(..., description="Confidence score")
    response_time: float = Field(..., description="Response time in seconds")
    timestamp: datetime = Field(..., description="Response timestamp")


class AgentStatsResponse(BaseModel):
    """Response schema for agent statistics."""

    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Number of active agents")
    agent_types: dict[str, int] = Field(..., description="Agents by type")
    total_interactions: int = Field(..., description="Total interactions across all agents")
