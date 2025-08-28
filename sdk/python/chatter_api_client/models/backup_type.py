from enum import Enum


class BackupType(str, Enum):
    DIFFERENTIAL = "differential"
    FULL = "full"
    INCREMENTAL = "incremental"

    def __str__(self) -> str:
        return str(self.value)
