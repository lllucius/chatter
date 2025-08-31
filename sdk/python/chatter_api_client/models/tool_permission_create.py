import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tool_access_level import ToolAccessLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolPermissionCreate")


@_attrs_define
class ToolPermissionCreate:
    """Schema for creating tool permissions.

    Attributes:
        user_id (str): User ID
        access_level (ToolAccessLevel): Access levels for tools.
        tool_id (Union[None, Unset, str]): Specific tool ID
        server_id (Union[None, Unset, str]): Server ID (for all tools)
        rate_limit_per_hour (Union[None, Unset, int]): Hourly rate limit
        rate_limit_per_day (Union[None, Unset, int]): Daily rate limit
        allowed_hours (Union[None, Unset, list[int]]): Allowed hours (0-23)
        allowed_days (Union[None, Unset, list[int]]): Allowed weekdays (0-6)
        expires_at (Union[None, Unset, datetime.datetime]): Permission expiry
    """

    user_id: str
    access_level: ToolAccessLevel
    tool_id: Union[None, Unset, str] = UNSET
    server_id: Union[None, Unset, str] = UNSET
    rate_limit_per_hour: Union[None, Unset, int] = UNSET
    rate_limit_per_day: Union[None, Unset, int] = UNSET
    allowed_hours: Union[None, Unset, list[int]] = UNSET
    allowed_days: Union[None, Unset, list[int]] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        access_level = self.access_level.value

        tool_id: Union[None, Unset, str]
        if isinstance(self.tool_id, Unset):
            tool_id = UNSET
        else:
            tool_id = self.tool_id

        server_id: Union[None, Unset, str]
        if isinstance(self.server_id, Unset):
            server_id = UNSET
        else:
            server_id = self.server_id

        rate_limit_per_hour: Union[None, Unset, int]
        if isinstance(self.rate_limit_per_hour, Unset):
            rate_limit_per_hour = UNSET
        else:
            rate_limit_per_hour = self.rate_limit_per_hour

        rate_limit_per_day: Union[None, Unset, int]
        if isinstance(self.rate_limit_per_day, Unset):
            rate_limit_per_day = UNSET
        else:
            rate_limit_per_day = self.rate_limit_per_day

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

        expires_at: Union[None, Unset, str]
        if isinstance(self.expires_at, Unset):
            expires_at = UNSET
        elif isinstance(self.expires_at, datetime.datetime):
            expires_at = self.expires_at.isoformat()
        else:
            expires_at = self.expires_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "access_level": access_level,
            }
        )
        if tool_id is not UNSET:
            field_dict["tool_id"] = tool_id
        if server_id is not UNSET:
            field_dict["server_id"] = server_id
        if rate_limit_per_hour is not UNSET:
            field_dict["rate_limit_per_hour"] = rate_limit_per_hour
        if rate_limit_per_day is not UNSET:
            field_dict["rate_limit_per_day"] = rate_limit_per_day
        if allowed_hours is not UNSET:
            field_dict["allowed_hours"] = allowed_hours
        if allowed_days is not UNSET:
            field_dict["allowed_days"] = allowed_days
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        access_level = ToolAccessLevel(d.pop("access_level"))

        def _parse_tool_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        tool_id = _parse_tool_id(d.pop("tool_id", UNSET))

        def _parse_server_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        server_id = _parse_server_id(d.pop("server_id", UNSET))

        def _parse_rate_limit_per_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        rate_limit_per_hour = _parse_rate_limit_per_hour(d.pop("rate_limit_per_hour", UNSET))

        def _parse_rate_limit_per_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        rate_limit_per_day = _parse_rate_limit_per_day(d.pop("rate_limit_per_day", UNSET))

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

        def _parse_expires_at(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                expires_at_type_0 = isoparse(data)

                return expires_at_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        expires_at = _parse_expires_at(d.pop("expires_at", UNSET))

        tool_permission_create = cls(
            user_id=user_id,
            access_level=access_level,
            tool_id=tool_id,
            server_id=server_id,
            rate_limit_per_hour=rate_limit_per_hour,
            rate_limit_per_day=rate_limit_per_day,
            allowed_hours=allowed_hours,
            allowed_days=allowed_days,
            expires_at=expires_at,
        )

        tool_permission_create.additional_properties = d
        return tool_permission_create

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
