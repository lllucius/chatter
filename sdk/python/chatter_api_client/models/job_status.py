from enum import Enum


class JobStatus(str, Enum):
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"
    RETRYING = "retrying"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
