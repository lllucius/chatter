from enum import Enum


class PromptCategory(str, Enum):
    ANALYTICAL = "analytical"
    BUSINESS = "business"
    CODING = "coding"
    CREATIVE = "creative"
    CUSTOM = "custom"
    EDUCATIONAL = "educational"
    GENERAL = "general"
    TECHNICAL = "technical"

    def __str__(self) -> str:
        return str(self.value)
