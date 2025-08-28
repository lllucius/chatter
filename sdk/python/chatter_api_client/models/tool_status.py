from enum import Enum


class ToolStatus(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"
    UNAVAILABLE = "unavailable"

    def __str__(self) -> str:
        return str(self.value)
