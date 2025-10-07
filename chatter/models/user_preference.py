"""User preferences model for storing workflow and tool configurations."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from chatter.models.base import Base, generate_ulid


class UserPreference(Base):
    """User preferences for memory and tool configurations.
    
    Stores user-specific configurations with JSON fields for flexibility.
    Supports versioning and audit trails.
    """

    __tablename__ = "user_preferences"

    id: Mapped[str] = mapped_column(
        String(26), primary_key=True, default=generate_ulid
    )
    user_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    
    # Preference type: 'memory' or 'tool'
    preference_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    
    # Flexible JSON configuration
    config: Mapped[dict[str, Any]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    
    # Optional description
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    
    # Version for migration support
    version: Mapped[int] = mapped_column(
        default=1, nullable=False
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        # Index for fast lookup by user_id and type
        Index("ix_user_preferences_user_type", "user_id", "preference_type"),
        # Index for recent preferences
        Index("ix_user_preferences_updated", "updated_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<UserPreference(id={self.id}, user_id={self.user_id}, "
            f"type={self.preference_type})>"
        )
