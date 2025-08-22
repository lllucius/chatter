"""Base model for all tables."""

import hashlib
import re
import socket
import string
import threading
import time
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class Base(DeclarativeBase):
    """
    Custom SQLAlchemy Declarative Base:
    - 12-char distributed-safe string ID
    - Auto snake_case tablename
    - created_at / updated_at timestamps
    """

    # ----------------------------------------------------------------
    # Monotonic distributed ID generator
    # ----------------------------------------------------------------
    _lock: threading.Lock = threading.Lock()
    _last_timestamp: int = 0
    _counter: int = 0
    _server_hash: int = int(
        hashlib.sha1(socket.gethostname().encode()).hexdigest(), 16
    ) % (62**2)

    @classmethod
    def _encode_base62(cls, num: int, length: int = 12) -> str:
        alphabet = string.digits + string.ascii_uppercase + string.ascii_lowercase
        arr: list[str] = []
        base: int = 62
        while num > 0:
            num, rem = divmod(num, base)
            arr.append(alphabet[rem])
        s: str = ''.join(reversed(arr))
        return s.rjust(length, '0')[:length]

    @classmethod
    def _generate_id(cls) -> str:
        MAX_COUNTER = 62**3 - 1  # 3 chars counter
        with cls._lock:
            timestamp: int = int(time.time() * 1000)
            if timestamp == cls._last_timestamp:
                cls._counter += 1
                if cls._counter > MAX_COUNTER:
                    while timestamp <= cls._last_timestamp:
                        time.sleep(0.0001)
                        timestamp = int(time.time() * 1000)
                    cls._counter = 0
                    cls._last_timestamp = timestamp
            else:
                cls._counter = 0
                cls._last_timestamp = timestamp

            combined: int = (timestamp << 16) | (cls._server_hash << 12) | cls._counter
            return cls._encode_base62(combined, length=12)

    # ----------------------------------------------------------------
    # Automatic tablename in snake_case
    # ----------------------------------------------------------------
    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__
        # CamelCase -> snake_case
        # name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
        return name

    # ----------------------------------------------------------------
    # Common columns
    # ----------------------------------------------------------------
    id: Mapped[str] = mapped_column(
        String(12),
        primary_key=True,
        default=lambda: Base._generate_id(),
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

