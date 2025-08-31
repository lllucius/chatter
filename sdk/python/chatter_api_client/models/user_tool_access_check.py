from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserToolAccessCheck")


@_attrs_define
class UserToolAccessCheck:
    """Schema for checking user tool access.

    Attributes:
        user_id (str): User ID
        tool_name (str): Tool name
        server_name (Union[None, Unset, str]): Server name
    """

    user_id: str
    tool_name: str
    server_name: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_id = self.user_id

        tool_name = self.tool_name

        server_name: Union[None, Unset, str]
        if isinstance(self.server_name, Unset):
            server_name = UNSET
        else:
            server_name = self.server_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_id": user_id,
                "tool_name": tool_name,
            }
        )
        if server_name is not UNSET:
            field_dict["server_name"] = server_name

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_id = d.pop("user_id")

        tool_name = d.pop("tool_name")

        def _parse_server_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        server_name = _parse_server_name(d.pop("server_name", UNSET))

        user_tool_access_check = cls(
            user_id=user_id,
            tool_name=tool_name,
            server_name=server_name,
        )

        user_tool_access_check.additional_properties = d
        return user_tool_access_check

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
