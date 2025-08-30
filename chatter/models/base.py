"""Base model for all tables."""

import re
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)
from ulid import ULID


def generate_ulid() -> str:
    """
    Generate a ULID (Universally Unique Lexicographically Sortable Identifier).

    ULIDs are 26 character strings that are:
    - Lexicographically sortable
    - Canonically encoded as a 26 character string
    - Uses Crockford's base32 for better efficiency and readability
    - Case insensitive
    - No special characters (URL safe)
    - Monotonically increasing when generated on the same machine

    Returns:
        str: A 26-character ULID string
    """
    return str(ULID())


class Base(DeclarativeBase):
    """
    Custom SQLAlchemy Declarative Base:
    - 12-char distributed-safe string ID
    - Auto snake_case tablename
    - created_at / updated_at timestamps
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name from class name using snake_case and plural form."""
        # Convert CamelCase to snake_case
        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
        # Handle pluralization
        if name.endswith("s"):
            return name  # Already plural
        elif name.endswith("y"):
            return name[:-1] + "ies"  # e.g., 'category' -> 'categories'
        elif name.endswith(("ch", "sh", "x", "z")):
            return name + "es"  # e.g., 'box' -> 'boxes'
        elif name.endswith("f"):
            return name[:-1] + "ves"  # e.g., 'shelf' -> 'shelves'
        elif name.endswith("fe"):
            return name[:-2] + "ves"  # e.g., 'life' -> 'lives'
        else:
            return name + "s"  # Default: add 's'

    # ----------------------------------------------------------------
    # Common columns
    # ----------------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String(26),  # ULIDs are 26 characters
        primary_key=True,
        default=generate_ulid,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Keys(str, Enum):
    """Centralized foreign key references."""

    USERS = "users.id"
    CONVERSATIONS = "conversations.id"
    MESSAGES = "messages.id"
    DOCUMENTS = "documents.id"
    DOCUMENT_CHUNKS = "document_chunks.id"
    PROFILES = "profiles.id"
    PROMPTS = "prompts.id"
    TOOL_SERVERS = "tool_servers.id"
    SERVER_TOOLS = "server_tools.id"
    TOOL_USAGE = "tool_usage.id"
    CONVERSATION_STATS = "conversation_stats.id"
    DOCUMENT_STATS = "document_stats.id"
    PROMPT_STATS = "prompt_stats.id"
    PROFILE_STATS = "profile_stats.id"
    PROVIDERS = "providers.id"
    MODEL_DEFS = "model_defs.id"
    EMBEDDING_SPACES = "embedding_spaces.id"
