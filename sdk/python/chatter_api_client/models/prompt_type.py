from enum import Enum


class PromptType(str, Enum):
    ASSISTANT = "assistant"
    CHAIN = "chain"
    SYSTEM = "system"
    TEMPLATE = "template"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
