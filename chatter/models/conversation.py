"""Conversation and message models."""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base, Keys
from chatter.models.user import User  # Import User from correct module

if TYPE_CHECKING:
    from chatter.models.profile import Profile


class MessageRole(str, Enum):
    """Enumeration for message roles."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ConversationStatus(str, Enum):
    """Enumeration for conversation status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(Base):
    """Conversation model for chat sessions."""

    # Add table constraints
    __table_args__ = (
        CheckConstraint(
            'temperature IS NULL OR (temperature >= 0.0 AND temperature <= 2.0)',
            name='check_temperature_range',
        ),
        CheckConstraint(
            'max_tokens IS NULL OR max_tokens > 0',
            name='check_max_tokens_positive',
        ),
        CheckConstraint(
            'context_window > 0', name='check_context_window_positive'
        ),
        CheckConstraint(
            'retrieval_limit > 0', name='check_retrieval_limit_positive'
        ),
        CheckConstraint(
            'retrieval_score_threshold >= 0.0 AND retrieval_score_threshold <= 1.0',
            name='check_retrieval_score_threshold_range',
        ),
        CheckConstraint(
            'message_count >= 0',
            name='check_message_count_non_negative',
        ),
        CheckConstraint(
            'total_tokens >= 0', name='check_total_tokens_non_negative'
        ),
        CheckConstraint(
            'total_cost >= 0.0', name='check_total_cost_non_negative'
        ),
        CheckConstraint("title != ''", name='check_title_not_empty'),
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_created', 'user_id', 'created_at'),
    )

    # Foreign keys
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    profile_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey(Keys.PROFILES), nullable=True, index=True
    )

    # Conversation metadata
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Configuration
    llm_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    llm_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    temperature: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    max_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    system_prompt: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Context and memory
    context_window: Mapped[int] = mapped_column(
        Integer, default=4096, nullable=False
    )
    memory_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    memory_strategy: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )

    # Vector search configuration
    enable_retrieval: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    retrieval_limit: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False
    )
    retrieval_score_threshold: Mapped[float] = mapped_column(
        Float, default=0.7, nullable=False
    )

    # Statistics
    message_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_tokens: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_cost: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )

    # Metadata
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Relationships
    user: Mapped[User] = relationship(
        "User", back_populates="conversations"
    )
    profile: Mapped[Profile | None] = relationship(
        "Profile", back_populates="conversations"
    )
    messages: Mapped[list[Message]] = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self) -> str:
        """String representation of conversation."""
        return f"<Conversation(id={self.id}, title={self.title}, user_id={self.user_id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "profile_id": self.profile_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "system_prompt": self.system_prompt,
            "context_window": self.context_window,
            "memory_enabled": self.memory_enabled,
            "memory_strategy": self.memory_strategy,
            "enable_retrieval": self.enable_retrieval,
            "retrieval_limit": self.retrieval_limit,
            "retrieval_score_threshold": self.retrieval_score_threshold,
            "message_count": self.message_count,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "tags": self.tags,
            "extra_metadata": self.extra_metadata,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


class Message(Base):
    """Message model for individual chat messages."""

    # Add table constraints
    __table_args__ = (
        CheckConstraint(
            'prompt_tokens IS NULL OR prompt_tokens >= 0',
            name='check_prompt_tokens_non_negative',
        ),
        CheckConstraint(
            'completion_tokens IS NULL OR completion_tokens >= 0',
            name='check_completion_tokens_non_negative',
        ),
        CheckConstraint(
            'total_tokens IS NULL OR total_tokens >= 0',
            name='check_total_tokens_non_negative',
        ),
        CheckConstraint(
            'response_time_ms IS NULL OR response_time_ms >= 0',
            name='check_response_time_non_negative',
        ),
        CheckConstraint(
            'cost IS NULL OR cost >= 0.0',
            name='check_cost_non_negative',
        ),
        CheckConstraint(
            'retry_count >= 0', name='check_retry_count_non_negative'
        ),
        CheckConstraint(
            'sequence_number >= 0',
            name='check_sequence_number_non_negative',
        ),
        CheckConstraint(
            "content != ''", name='check_content_not_empty'
        ),
        UniqueConstraint(
            'conversation_id',
            'sequence_number',
            name='uq_conversation_sequence',
        ),
        Index(
            'idx_conversation_sequence',
            'conversation_id',
            'sequence_number',
        ),
        Index('idx_conversation_role', 'conversation_id', 'role'),
    )

    # Foreign keys
    conversation_id: Mapped[str] = mapped_column(
        String(26),
        ForeignKey(Keys.CONVERSATIONS),
        nullable=False,
        index=True,
    )

    # Message content
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole), nullable=False, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Tool calling
    tool_calls: Mapped[list[dict[str, Any]] | None] = mapped_column(
        JSON, nullable=True
    )
    tool_call_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    # Token usage
    prompt_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    completion_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    total_tokens: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    # Response metadata
    model_used: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    provider_used: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    finish_reason: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    response_time_ms: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Error handling
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Context and retrieval
    retrieved_documents: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    context_used: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Metadata
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Message ordering
    sequence_number: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )

    # Relationships
    conversation: Mapped[Conversation] = relationship(
        "Conversation", back_populates="messages"
    )

    def __repr__(self) -> str:
        """String representation of message."""
        content_preview = (
            self.content[:50] + "..."
            if len(self.content) > 50
            else self.content
        )
        return f"<Message(id={self.id}, role={self.role}, content={content_preview})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role.value,
            "content": self.content,
            "tool_calls": self.tool_calls,
            "tool_call_id": self.tool_call_id,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "model_used": self.model_used,
            "provider_used": self.provider_used,
            "finish_reason": self.finish_reason,
            "response_time_ms": self.response_time_ms,
            "cost": self.cost,
            "error_message": self.error_message,
            "retry_count": self.retry_count,
            "retrieved_documents": self.retrieved_documents,
            "context_used": self.context_used,
            "extra_metadata": self.extra_metadata,
            "sequence_number": self.sequence_number,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }
