"""Database models for AI agents."""

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from chatter.models.base import Base
from chatter.schemas.agents import AgentStatus, AgentType


class AgentDB(Base):
    """Database model for AI agents."""

    __tablename__ = "agents"

    # Basic agent information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType), nullable=False
    )
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus), default=AgentStatus.INACTIVE
    )

    # Behavior configuration
    system_message: Mapped[str] = mapped_column(Text, nullable=False)
    personality_traits: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )
    knowledge_domains: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )
    response_style: Mapped[str] = mapped_column(
        String(100), default="professional"
    )

    # Capabilities
    capabilities: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )
    available_tools: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )

    # Model configuration
    primary_llm: Mapped[str] = mapped_column(
        String(100), default="openai"
    )
    fallback_llm: Mapped[str] = mapped_column(
        String(100), default="anthropic"
    )
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)

    # Performance settings
    max_conversation_length: Mapped[int] = mapped_column(
        Integer, default=50
    )
    context_window_size: Mapped[int] = mapped_column(
        Integer, default=4000
    )
    response_timeout: Mapped[int] = mapped_column(Integer, default=30)

    # Learning and adaptation
    learning_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    feedback_weight: Mapped[float] = mapped_column(Float, default=0.1)
    adaptation_threshold: Mapped[float] = mapped_column(
        Float, default=0.8
    )

    # Metadata
    created_by: Mapped[str] = mapped_column(
        String(26), nullable=False, default="system"
    )
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    agent_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict
    )


class AgentInteractionDB(Base):
    """Database model for agent interactions."""

    __tablename__ = "agent_interactions"

    # Relationship identifiers
    agent_id: Mapped[str] = mapped_column(String(26), nullable=False)
    conversation_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # Interaction data
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    agent_response: Mapped[str] = mapped_column(Text, nullable=False)
    tools_used: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )

    # Performance metrics
    confidence_score: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    response_time: Mapped[float] = mapped_column(Float, nullable=False)
    feedback_score: Mapped[float] = mapped_column(Float, nullable=True)

    # Additional data
    interaction_metadata: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict
    )
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
