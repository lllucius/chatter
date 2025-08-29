from enum import Enum


class TestType(str, Enum):
    MODEL = "model"
    PARAMETER = "parameter"
    PROMPT = "prompt"
    TEMPLATE = "template"
    WORKFLOW = "workflow"

    def __str__(self) -> str:
        return str(self.value)
