"""User model for authentication and user management."""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base, Keys

if TYPE_CHECKING:
    from chatter.models.conversation import Conversation
    from chatter.models.document import Document
    from chatter.models.profile import Profile
    from chatter.models.prompt import Prompt


import os

# Check if we're using SQLite (for testing) to skip PostgreSQL-specific constraints
_database_url = os.environ.get("DATABASE_URL", "")
_is_sqlite = "sqlite" in _database_url.lower() or os.environ.get("TESTING", "").lower() == "true"

if _is_sqlite:
    # Use constraints compatible with SQLite
    _table_args = (
        CheckConstraint(
            'daily_message_limit IS NULL OR daily_message_limit > 0',
            name='check_daily_message_limit_positive',
        ),
        CheckConstraint(
            'monthly_message_limit IS NULL OR monthly_message_limit > 0',
            name='check_monthly_message_limit_positive',
        ),
        CheckConstraint(
            'max_file_size_mb IS NULL OR max_file_size_mb > 0',
            name='check_max_file_size_positive',
        ),
    )
else:
    # Use PostgreSQL-specific constraints with regex
    _table_args = (
        CheckConstraint(
            'daily_message_limit IS NULL OR daily_message_limit > 0',
            name='check_daily_message_limit_positive',
        ),
        CheckConstraint(
            'monthly_message_limit IS NULL OR monthly_message_limit > 0',
            name='check_monthly_message_limit_positive',
        ),
        CheckConstraint(
            'max_file_size_mb IS NULL OR max_file_size_mb > 0',
            name='check_max_file_size_positive',
        ),
        CheckConstraint(
            "email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'",
            name='check_email_format',
        ),
        CheckConstraint(
            "username ~ '^[a-zA-Z0-9_-]{3,50}$'",
            name='check_username_format',
        ),
    )


class User(Base):
    """User model for authentication and profile management."""

    # Add table constraints (conditional based on database)
    __table_args__ = _table_args

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # Profile fields
    full_name: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )

    # Status fields
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # API access
    api_key: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True, index=True
    )
    api_key_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # Preferences
    default_llm_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    default_profile_id: Mapped[str | None] = mapped_column(
        String(26), ForeignKey(Keys.PROFILES), nullable=True, index=True
    )

    # Usage limits
    daily_message_limit: Mapped[int | None] = mapped_column(
        nullable=True
    )
    monthly_message_limit: Mapped[int | None] = mapped_column(
        nullable=True
    )
    max_file_size_mb: Mapped[int | None] = mapped_column(nullable=True)

    # Timestamps
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="owner", cascade="all, delete-orphan"
    )

    profiles: Mapped[list["Profile"]] = relationship(
        "Profile",
        back_populates="owner",
        foreign_keys="Profile.owner_id",
        cascade="all, delete-orphan",
    )

    prompts: Mapped[list["Prompt"]] = relationship(
        "Prompt", back_populates="owner", cascade="all, delete-orphan"
    )

    default_profile: Mapped[Optional["Profile"]] = relationship(
        "Profile", foreign_keys=[default_profile_id], post_update=True
    )

    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"

    @property
    def display_name(self) -> str:
        """Get display name for the user."""
        return self.full_name or self.username

    def to_dict(self) -> dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "bio": self.bio,
            "avatar_url": self.avatar_url,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "default_llm_provider": self.default_llm_provider,
            "default_profile_id": self.default_profile_id,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            "last_login_at": (
                self.last_login_at.isoformat()
                if self.last_login_at
                else None
            ),
        }
