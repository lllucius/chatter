import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tool_access_level import ToolAccessLevel
from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolAccessResult")


@_attrs_define
class ToolAccessResult:
    """Schema for tool access check result.

    Attributes:
        allowed (bool): Whether access is allowed
        access_level (ToolAccessLevel): Access levels for tools.
        rate_limit_remaining_hour (Union[None, Unset, int]): Remaining hourly calls
        rate_limit_remaining_day (Union[None, Unset, int]): Remaining daily calls
        restriction_reason (Union[None, Unset, str]): Reason if restricted
        expires_at (Union[None, Unset, datetime.datetime]): Permission expiry
    """

    allowed: bool
    access_level: ToolAccessLevel
    rate_limit_remaining_hour: Union[None, Unset, int] = UNSET
    rate_limit_remaining_day: Union[None, Unset, int] = UNSET
    restriction_reason: Union[None, Unset, str] = UNSET
    expires_at: Union[None, Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed = self.allowed

        access_level = self.access_level.value

        rate_limit_remaining_hour: Union[None, Unset, int]
        if isinstance(self.rate_limit_remaining_hour, Unset):
            rate_limit_remaining_hour = UNSET
        else:
            rate_limit_remaining_hour = self.rate_limit_remaining_hour

        rate_limit_remaining_day: Union[None, Unset, int]
        if isinstance(self.rate_limit_remaining_day, Unset):
            rate_limit_remaining_day = UNSET
        else:
            rate_limit_remaining_day = self.rate_limit_remaining_day

        restriction_reason: Union[None, Unset, str]
        if isinstance(self.restriction_reason, Unset):
            restriction_reason = UNSET
        else:
            restriction_reason = self.restriction_reason

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
                "allowed": allowed,
                "access_level": access_level,
            }
        )
        if rate_limit_remaining_hour is not UNSET:
            field_dict["rate_limit_remaining_hour"] = rate_limit_remaining_hour
        if rate_limit_remaining_day is not UNSET:
            field_dict["rate_limit_remaining_day"] = rate_limit_remaining_day
        if restriction_reason is not UNSET:
            field_dict["restriction_reason"] = restriction_reason
        if expires_at is not UNSET:
            field_dict["expires_at"] = expires_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        allowed = d.pop("allowed")

        access_level = ToolAccessLevel(d.pop("access_level"))

        def _parse_rate_limit_remaining_hour(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        rate_limit_remaining_hour = _parse_rate_limit_remaining_hour(d.pop("rate_limit_remaining_hour", UNSET))

        def _parse_rate_limit_remaining_day(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        rate_limit_remaining_day = _parse_rate_limit_remaining_day(d.pop("rate_limit_remaining_day", UNSET))

        def _parse_restriction_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        restriction_reason = _parse_restriction_reason(d.pop("restriction_reason", UNSET))

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

        tool_access_result = cls(
            allowed=allowed,
            access_level=access_level,
            rate_limit_remaining_hour=rate_limit_remaining_hour,
            rate_limit_remaining_day=rate_limit_remaining_day,
            restriction_reason=restriction_reason,
            expires_at=expires_at,
        )

        tool_access_result.additional_properties = d
        return tool_access_result

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
