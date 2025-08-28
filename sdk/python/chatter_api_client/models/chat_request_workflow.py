from enum import Enum


class ChatRequestWorkflow(str, Enum):
    FULL = "full"
    PLAIN = "plain"
    RAG = "rag"
    TOOLS = "tools"

    def __str__(self) -> str:
        return str(self.value)
