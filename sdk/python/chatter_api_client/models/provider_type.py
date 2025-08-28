from enum import Enum


class ProviderType(str, Enum):
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    GOOGLE = "google"
    MISTRAL = "mistral"
    OPENAI = "openai"

    def __str__(self) -> str:
        return str(self.value)
