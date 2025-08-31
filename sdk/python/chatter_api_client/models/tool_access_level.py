from enum import Enum


class ToolAccessLevel(str, Enum):
    ADMIN = "admin"
    EXECUTE = "execute"
    NONE = "none"
    READ = "read"

    def __str__(self) -> str:
        return str(self.value)
