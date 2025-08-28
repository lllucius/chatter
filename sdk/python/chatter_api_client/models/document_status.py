from enum import Enum


class DocumentStatus(str, Enum):
    ARCHIVED = "archived"
    FAILED = "failed"
    PENDING = "pending"
    PROCESSED = "processed"
    PROCESSING = "processing"

    def __str__(self) -> str:
        return str(self.value)
