from enum import Enum


class PluginType(str, Enum):
    EXTENSION = "extension"
    HANDLER = "handler"
    INTEGRATION = "integration"
    MIDDLEWARE = "middleware"
    TOOL = "tool"
    WORKFLOW = "workflow"

    def __str__(self) -> str:
        return str(self.value)
