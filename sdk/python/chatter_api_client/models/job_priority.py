from enum import Enum


class JobPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    LOW = "low"
    NORMAL = "normal"

    def __str__(self) -> str:
        return str(self.value)
