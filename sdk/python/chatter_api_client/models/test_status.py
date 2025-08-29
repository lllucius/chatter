from enum import Enum


class TestStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    DRAFT = "draft"
    PAUSED = "paused"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
