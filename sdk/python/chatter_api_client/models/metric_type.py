from enum import Enum


class MetricType(str, Enum):
    ACCURACY = "accuracy"
    CONVERSION = "conversion"
    CUSTOM = "custom"
    ENGAGEMENT = "engagement"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    TOKEN_USAGE = "token_usage"
    USER_SATISFACTION = "user_satisfaction"

    def __str__(self) -> str:
        return str(self.value)
