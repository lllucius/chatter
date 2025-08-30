"""Profile model for LLM configuration management."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base, Keys


class ProfileType(str, Enum):
    """Enumeration for profile types."""

    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    TECHNICAL = "technical"
    CUSTOM = "custom"


class Profile(Base):
    """Profile model for LLM parameter management."""

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # Profile metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile_type: Mapped[ProfileType] = mapped_column(
        SQLEnum(ProfileType),
        default=ProfileType.CUSTOM,
        nullable=False,
        index=True,
    )

    # LLM Configuration
    llm_provider: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    llm_model: Mapped[str] = mapped_column(String(100), nullable=False)

    # Generation parameters
    temperature: Mapped[float] = mapped_column(
        Float, default=0.7, nullable=False
    )
    top_p: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_k: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_tokens: Mapped[int] = mapped_column(
        Integer, default=4096, nullable=False
    )
    presence_penalty: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    frequency_penalty: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    # Context configuration
    context_window: Mapped[int] = mapped_column(
        Integer, default=4096, nullable=False
    )
    system_prompt: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Memory and retrieval settings
    memory_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    memory_strategy: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    enable_retrieval: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    retrieval_limit: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False
    )
    retrieval_score_threshold: Mapped[float] = mapped_column(
        Float, default=0.7, nullable=False
    )

    # Tool calling
    enable_tools: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    available_tools: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    tool_choice: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # auto, none, specific tool

    # Safety and filtering
    content_filter_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    safety_level: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )

    # Response formatting
    response_format: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # json, text, markdown
    stream_response: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # Advanced settings
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stop_sequences: Mapped[list[str] | None] = mapped_column(
        JSON, nullable=True
    )
    logit_bias: Mapped[dict[str, float] | None] = mapped_column(
        JSON, nullable=True
    )

    # Embedding configuration (for retrieval)
    embedding_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Usage statistics
    usage_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_tokens_used: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    total_cost: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    last_used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Metadata and tags
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User", back_populates="profiles", foreign_keys=[owner_id]
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation", back_populates="profile"
    )

    def __repr__(self) -> str:
        """String representation of profile."""
        return f"<Profile(id={self.id}, name={self.name}, model={self.llm_model})>"

    @property
    def model_display_name(self) -> str:
        """Get display name for the model."""
        return f"{self.llm_provider}/{self.llm_model}"

    def get_generation_config(self) -> dict[str, Any]:
        """Get generation configuration for LLM calls."""
        config = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        # Add optional parameters if set
        if self.top_p is not None:
            config["top_p"] = self.top_p
        if self.top_k is not None:
            config["top_k"] = self.top_k
        if self.presence_penalty is not None:
            config["presence_penalty"] = self.presence_penalty
        if self.frequency_penalty is not None:
            config["frequency_penalty"] = self.frequency_penalty
        if self.seed is not None:
            config["seed"] = self.seed
        if self.stop_sequences:
            config["stop"] = self.stop_sequences
        if self.logit_bias:
            config["logit_bias"] = self.logit_bias

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.name,
            "description": self.description,
            "profile_type": self.profile_type.value,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "max_tokens": self.max_tokens,
            "presence_penalty": self.presence_penalty,
            "frequency_penalty": self.frequency_penalty,
            "context_window": self.context_window,
            "system_prompt": self.system_prompt,
            "memory_enabled": self.memory_enabled,
            "memory_strategy": self.memory_strategy,
            "enable_retrieval": self.enable_retrieval,
            "retrieval_limit": self.retrieval_limit,
            "retrieval_score_threshold": self.retrieval_score_threshold,
            "enable_tools": self.enable_tools,
            "available_tools": self.available_tools,
            "tool_choice": self.tool_choice,
            "content_filter_enabled": self.content_filter_enabled,
            "safety_level": self.safety_level,
            "response_format": self.response_format,
            "stream_response": self.stream_response,
            "seed": self.seed,
            "stop_sequences": self.stop_sequences,
            "logit_bias": self.logit_bias,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "total_tokens_used": self.total_tokens_used,
            "total_cost": self.total_cost,
            "last_used_at": self.last_used_at.isoformat()
            if self.last_used_at
            else None,
            "tags": self.tags,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
        }
