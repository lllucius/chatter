from enum import Enum


class AgentStatus(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    TRAINING = "training"

    def __str__(self) -> str:
        return str(self.value)
