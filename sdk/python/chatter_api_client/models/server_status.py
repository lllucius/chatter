from enum import Enum


class ServerStatus(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    ERROR = "error"
    STARTING = "starting"
    STOPPING = "stopping"

    def __str__(self) -> str:
        return str(self.value)
