from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar(
    "T",
    bound="RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostResponseRefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost",
)


@_attrs_define
class RefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPostResponseRefreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost:
    """ """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post_response_refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post = cls()

        refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post_response_refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post.additional_properties = d
        return refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post_response_refresh_server_tools_api_v1_toolservers_servers_server_id_refresh_tools_post

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
