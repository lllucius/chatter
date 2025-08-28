from enum import Enum


class ProfileType(str, Enum):
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    CREATIVE = "creative"
    CUSTOM = "custom"
    TECHNICAL = "technical"

    def __str__(self) -> str:
        return str(self.value)
