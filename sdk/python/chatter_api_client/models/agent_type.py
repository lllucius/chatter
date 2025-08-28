from enum import Enum


class AgentType(str, Enum):
    ANALYTICAL = "analytical"
    CONVERSATIONAL = "conversational"
    CREATIVE = "creative"
    RESEARCH = "research"
    SPECIALIST = "specialist"
    SUPPORT = "support"
    TASK_ORIENTED = "task_oriented"

    def __str__(self) -> str:
        return str(self.value)
