from enum import Enum


class ReductionStrategy(str, Enum):
    NONE = "none"
    REDUCER = "reducer"
    TRUNCATE = "truncate"

    def __str__(self) -> str:
        return str(self.value)
