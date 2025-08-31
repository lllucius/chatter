import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tool_access_level import ToolAccessLevel
from ..models.user_role import UserRole
from ..types import UNSET, Unset

T = TypeVar("T", bound="RoleToolAccessResponse")


@_attrs_define
class RoleToolAccessResponse:
    """Schema for role-based tool access response.

    Attributes:
        role (UserRole): User roles for tool access.
        access_level (ToolAccessLevel): Access levels for tools.
        id (str): Access rule ID
        created_by (str): Creator user ID
        created_at (datetime.datetime): Creation timestamp
        tool_pattern (Union[None, Unset, str]): Tool name pattern
        server_pattern (Union[None, Unset, str]): Server name pattern
        default_rate_limit_per_hour (Union[None, Unset, int]):
        default_rate_limit_per_day (Union[None, Unset, int]):
        allowed_hours (Union[None, Unset, list[int]]):
        allowed_days (Union[None, Unset, list[int]]):
    """

    role: UserRole
    access_level: ToolAccessLevel
    id: str
    created_by: str
    created_at: datetime.datetime
    tool_pattern: Union[None, Unset, str] = UNSET
    server_pattern: Union[None, Unset, str] = UNSET
    default_rate_limit_per_hour: Union[None, Unset, int] = UNSET
    default_rate_limit_per_day: Union[None, Unset, int] = UNSET
    allowed_hours: Union[None, Unset, list[int]] = UNSET
    allowed_days: Union[None, Unset, list[int]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        role = self.role.value

        access_level = self.access_level.value

        id = self.id

        created_by = self.created_by

        created_at = self.created_at.isoformat()

        tool_pattern: Union[None, Unset, str]
        if isinstance(self.tool_pattern, Unset):
            tool_pattern = UNSET
        else:
            tool_pattern = self.tool_pattern

        server_pattern: Union[None, Unset, str]
        if isinstance(self.server_pattern, Unset):
            server_pattern = UNSET
        else:
            server_pattern = self.server_pattern

        default_rate_limit_per_hour: Union[None, Unset, int]
        if isinstance(self.default_rate_limit_per_hour, Unset):
            default_rate_limit_per_hour = UNSET
        else:
            default_rate_limit_per_hour = self.default_rate_limit_per_hour

        default_rate_limit_per_day: Union[None, Unset, int]
        if isinstance(self.default_rate_limit_per_day, Unset):
            default_rate_limit_per_day = UNSET
        else:
            default_rate_limit_per_day = self.default_rate_limit_per_day

        allowed_hours: Union[None, Unset, list[int]]
        if isinstance(self.allowed_hours, Unset):
            allowed_hours = UNSET
        elif isinstance(self.allowed_hours, list):
            allowed_hours = self.allowed_hours

        else:
            allowed_hours = self.allowed_hours

        allowed_days: Union[None, Unset, list[int]]
        if isinstance(self.allowed_days, Unset):
            allowed_days = UNSET
        elif isinstance(self.allowed_days, list):
            allowed_days = self.allowed_days

        else:
            allowed_days = self.allowed_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "role": role,
                "access_level": access_level,
                "id": id,
                "created_by": created_by,
                "created_at": created_at,
            }
        )
        if tool_pattern is not UNSET:
            field_dict["tool_pattern"] = tool_pattern
        if server_pattern is not UNSET:
            field_dict["server_pattern"] = server_pattern
        if default_rate_limit_per_hour is not UNSET:
            field_dict["default_rate_limit_per_hour"] = default_rate_limit_per_hour
        if default_rate_limit_per_day is not UNSET:
            field_dict["default_rate_limit_per_day"] = default_rate_limit_per_day
        if allowed_hours is not UNSET:
            field_dict["allowed_hours"] = allowed_hours
        if allowed_days is not UNSET:
            field_dict["allowed_days"] = allowed_days

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        role = UserRole(d.pop("role"))

        access_level = ToolAccessLevel(d.pop("access_level"))

        id = d.pop("id")

        created_by = d.pop("created_by")

        created_at = isoparse(d.pop("created_at"))

        def _parse_tool_pattern(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tool_pattern = _parse_tool_pattern(d.pop("tool_pattern", UNSET))

        def _parse_server_pattern(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        server_pattern = _parse_server_pattern(d.pop("server_pattern", UNSET))

        def _parse_default_rate_limit_per_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        default_rate_limit_per_hour = _parse_default_rate_limit_per_hour(d.pop("default_rate_limit_per_hour", UNSET))

        def _parse_default_rate_limit_per_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        default_rate_limit_per_day = _parse_default_rate_limit_per_day(d.pop("default_rate_limit_per_day", UNSET))

        def _parse_allowed_hours(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_hours_type_0 = cast(list[int], data)

                return allowed_hours_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        allowed_hours = _parse_allowed_hours(d.pop("allowed_hours", UNSET))

        def _parse_allowed_days(data: object) -> Union[None, Unset, list[int]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                allowed_days_type_0 = cast(list[int], data)

                return allowed_days_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[int]], data)

        allowed_days = _parse_allowed_days(d.pop("allowed_days", UNSET))

        role_tool_access_response = cls(
            role=role,
            access_level=access_level,
            id=id,
            created_by=created_by,
            created_at=created_at,
            tool_pattern=tool_pattern,
            server_pattern=server_pattern,
            default_rate_limit_per_hour=default_rate_limit_per_hour,
            default_rate_limit_per_day=default_rate_limit_per_day,
            allowed_hours=allowed_hours,
            allowed_days=allowed_days,
        )

        role_tool_access_response.additional_properties = d
        return role_tool_access_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
