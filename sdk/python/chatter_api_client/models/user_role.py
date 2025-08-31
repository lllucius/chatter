from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    GUEST = "guest"
    POWER_USER = "power_user"
    SUPER_ADMIN = "super_admin"
    USER = "user"

    def __str__(self) -> str:
        return str(self.value)
