from enum import Enum


class ExportScope(str, Enum):
    ANALYTICS = "analytics"
    CONVERSATION = "conversation"
    CUSTOM = "custom"
    DOCUMENT = "document"
    FULL = "full"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
