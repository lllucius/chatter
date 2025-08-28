from enum import Enum


class DataFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    PARQUET = "parquet"
    SQL = "sql"
    XML = "xml"

    def __str__(self) -> str:
        return str(self.value)
