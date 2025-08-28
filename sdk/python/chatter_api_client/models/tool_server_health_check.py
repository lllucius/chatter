import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.server_status import ServerStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolServerHealthCheck")


@_attrs_define
class ToolServerHealthCheck:
    """Schema for tool server health check.

    Attributes:
        server_id (str): Server ID
        server_name (str): Server name
        status (ServerStatus): Enumeration for server status.
        is_running (bool): Whether server is running
        is_responsive (bool): Whether server is responsive
        tools_count (int): Number of available tools
        last_check (datetime.datetime): Last health check time
        error_message (Union[None, Unset, str]): Error message if unhealthy
    """

    server_id: str
    server_name: str
    status: ServerStatus
    is_running: bool
    is_responsive: bool
    tools_count: int
    last_check: datetime.datetime
    error_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        server_id = self.server_id

        server_name = self.server_name

        status = self.status.value

        is_running = self.is_running

        is_responsive = self.is_responsive

        tools_count = self.tools_count

        last_check = self.last_check.isoformat()

        error_message: Union[None, Unset, str]
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_id": server_id,
                "server_name": server_name,
                "status": status,
                "is_running": is_running,
                "is_responsive": is_responsive,
                "tools_count": tools_count,
                "last_check": last_check,
            }
        )
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_id = d.pop("server_id")

        server_name = d.pop("server_name")

        status = ServerStatus(d.pop("status"))

        is_running = d.pop("is_running")

        is_responsive = d.pop("is_responsive")

        tools_count = d.pop("tools_count")

        last_check = isoparse(d.pop("last_check"))

        def _parse_error_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        tool_server_health_check = cls(
            server_id=server_id,
            server_name=server_name,
            status=status,
            is_running=is_running,
            is_responsive=is_responsive,
            tools_count=tools_count,
            last_check=last_check,
            error_message=error_message,
        )

        tool_server_health_check.additional_properties = d
        return tool_server_health_check

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
