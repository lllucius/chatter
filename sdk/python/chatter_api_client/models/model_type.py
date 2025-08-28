from enum import Enum


class ModelType(str, Enum):
    EMBEDDING = "embedding"
    LLM = "llm"

    def __str__(self) -> str:
        return str(self.value)
