"""Analytics models for usage statistics and performance metrics."""

import uuid
from datetime import datetime, timezone, date
from typing import Any, Dict, Optional

from sqlalchemy import (
    Date, DateTime, Float, ForeignKey, Integer, 
    JSON, String, UUID
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.utils.database import Base


class ConversationStats(Base):
    """Model for conversation-level statistics."""
    
    __tablename__ = "conversation_stats"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Foreign keys
    conversation_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("conversations.id"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Time period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Message statistics
    total_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    assistant_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    system_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tool_messages: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Token statistics
    total_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Performance metrics
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_cost_per_message: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Error tracking
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Tool usage
    tool_calls_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unique_tools_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Retrieval statistics
    retrieval_queries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    documents_retrieved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_retrieval_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Session information
    session_duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    active_time_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Provider and model usage
    provider_usage: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)
    model_usage: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        """String representation of conversation stats."""
        return f"<ConversationStats(conversation_id={self.conversation_id}, date={self.date})>"


class DocumentStats(Base):
    """Model for document-level statistics."""
    
    __tablename__ = "document_stats"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Foreign keys
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("documents.id"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Time period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Access statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    search_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retrieval_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Search performance
    avg_search_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    min_search_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_search_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Usage metrics
    unique_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_chunks_retrieved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    avg_chunks_per_retrieval: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Processing metrics
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    embedding_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    indexing_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Quality metrics
    user_feedback_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship("Document")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        """String representation of document stats."""
        return f"<DocumentStats(document_id={self.document_id}, date={self.date})>"


class PromptStats(Base):
    """Model for prompt usage statistics."""
    
    __tablename__ = "prompt_stats"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Foreign keys
    prompt_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("prompts.id"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Time period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Usage statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Performance metrics
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    avg_tokens_used: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    avg_cost_per_use: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Quality metrics
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_rating: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rating_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Provider distribution
    provider_usage: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)
    model_usage: Mapped[Optional[Dict[str, int]]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    prompt: Mapped["Prompt"] = relationship("Prompt")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        """String representation of prompt stats."""
        return f"<PromptStats(prompt_id={self.prompt_id}, date={self.date})>"


class ProfileStats(Base):
    """Model for profile usage statistics."""
    
    __tablename__ = "profile_stats"
    
    # Primary key
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Foreign keys
    profile_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("profiles.id"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    
    # Time period
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # Usage statistics
    conversations_started: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    messages_generated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Performance metrics
    avg_response_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    success_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    error_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Cost tracking
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    cost_per_message: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cost_per_token: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Quality metrics
    user_satisfaction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Usage patterns
    peak_usage_hour: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    avg_session_duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Relationships
    profile: Mapped["Profile"] = relationship("Profile")
    user: Mapped["User"] = relationship("User")
    
    def __repr__(self) -> str:
        """String representation of profile stats."""
        return f"<ProfileStats(profile_id={self.profile_id}, date={self.date})>"