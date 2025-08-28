from enum import Enum


class VariantAllocation(str, Enum):
    EQUAL = "equal"
    GRADUAL_ROLLOUT = "gradual_rollout"
    USER_ATTRIBUTE = "user_attribute"
    WEIGHTED = "weighted"

    def __str__(self) -> str:
        return str(self.value)
