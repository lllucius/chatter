from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.server_tool_response import ServerToolResponse


T = TypeVar("T", bound="ServerToolsResponse")


@_attrs_define
class ServerToolsResponse:
    """Schema for server tools response with pagination.

    Attributes:
        tools (list['ServerToolResponse']): List of server tools
        total_count (int): Total number of tools
        limit (int): Applied limit
        offset (int): Applied offset
    """

    tools: list["ServerToolResponse"]
    total_count: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tools = []
        for tools_item_data in self.tools:
            tools_item = tools_item_data.to_dict()
            tools.append(tools_item)

        total_count = self.total_count

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tools": tools,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_tool_response import ServerToolResponse

        d = dict(src_dict)
        tools = []
        _tools = d.pop("tools")
        for tools_item_data in _tools:
            tools_item = ServerToolResponse.from_dict(tools_item_data)

            tools.append(tools_item)

        total_count = d.pop("total_count")

        limit = d.pop("limit")

        offset = d.pop("offset")

        server_tools_response = cls(
            tools=tools,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

        server_tools_response.additional_properties = d
        return server_tools_response

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
