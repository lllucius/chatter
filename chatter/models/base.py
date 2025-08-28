"""Base model for all tables."""

import hashlib
import re
import socket
import string
import threading
import time

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

import hashlib
import socket
import string
import threading
import time
from datetime import datetime

class IDGenerator:
    _lock = threading.Lock()
    _last_timestamp = 0
    _counter = 0

    # Server ID: stable per machine, 0–15 (4 bits)
    _server_id = int(
        hashlib.sha1(socket.gethostname().encode()).hexdigest(), 16
    ) % 16

    # Custom epoch (Jan 1, 2025)
    _epoch_ms = int(datetime(2025, 1, 1).timestamp() * 1000)

    @classmethod
    def _encode_base62(cls, num: int) -> str:
        alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
        base = len(alphabet)
        arr = []
        while num > 0:
            num, rem = divmod(num, base)
            arr.append(alphabet[rem])
        return ''.join(reversed(arr)) or "0"

    @classmethod
    def generate_id(cls, length: int = 12) -> str:
        """
        12-char base62 ID
        - 35 bits: timestamp (ms since Jan 1, 2025 → good for ~34 years)
        - 4 bits:  server ID (up to 16 machines)
        - 20 bits: counter (1,048,576 IDs/ms per server)
        """
        with cls._lock:
            now_ms = int(time.time() * 1000) - cls._epoch_ms

            if now_ms == cls._last_timestamp:
                cls._counter = (cls._counter + 1) & ((1 << 20) - 1)
            else:
                cls._counter = 0

            cls._last_timestamp = now_ms

            combined = (now_ms << (4 + 20)) | (cls._server_id << 20) | cls._counter
            encoded = cls._encode_base62(combined)
            return encoded.rjust(length, "0")


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
        String(12),
        primary_key=True,
        default=lambda: IDGenerator.generate_id(),
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
