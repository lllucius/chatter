from enum import Enum


class PluginStatus(str, Enum):
    ACTIVE = "active"
    ERROR = "error"
    INACTIVE = "inactive"
    INSTALLED = "installed"
    UPDATING = "updating"

    def __str__(self) -> str:
        return str(self.value)
