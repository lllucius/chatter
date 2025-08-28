import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.server_status import ServerStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="ToolServerMetrics")


@_attrs_define
class ToolServerMetrics:
    """Schema for tool server metrics.

    Attributes:
        server_id (str): Server ID
        server_name (str): Server name
        status (ServerStatus): Enumeration for server status.
        total_tools (int): Total number of tools
        enabled_tools (int): Number of enabled tools
        total_calls (int): Total tool calls
        total_errors (int): Total errors
        success_rate (float): Success rate
        avg_response_time_ms (Union[None, Unset, float]): Average response time
        last_activity (Union[None, Unset, datetime.datetime]): Last activity timestamp
        uptime_percentage (Union[None, Unset, float]): Uptime percentage
    """

    server_id: str
    server_name: str
    status: ServerStatus
    total_tools: int
    enabled_tools: int
    total_calls: int
    total_errors: int
    success_rate: float
    avg_response_time_ms: Union[None, Unset, float] = UNSET
    last_activity: Union[None, Unset, datetime.datetime] = UNSET
    uptime_percentage: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        server_id = self.server_id

        server_name = self.server_name

        status = self.status.value

        total_tools = self.total_tools

        enabled_tools = self.enabled_tools

        total_calls = self.total_calls

        total_errors = self.total_errors

        success_rate = self.success_rate

        avg_response_time_ms: Union[None, Unset, float]
        if isinstance(self.avg_response_time_ms, Unset):
            avg_response_time_ms = UNSET
        else:
            avg_response_time_ms = self.avg_response_time_ms

        last_activity: Union[None, Unset, str]
        if isinstance(self.last_activity, Unset):
            last_activity = UNSET
        elif isinstance(self.last_activity, datetime.datetime):
            last_activity = self.last_activity.isoformat()
        else:
            last_activity = self.last_activity

        uptime_percentage: Union[None, Unset, float]
        if isinstance(self.uptime_percentage, Unset):
            uptime_percentage = UNSET
        else:
            uptime_percentage = self.uptime_percentage

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_id": server_id,
                "server_name": server_name,
                "status": status,
                "total_tools": total_tools,
                "enabled_tools": enabled_tools,
                "total_calls": total_calls,
                "total_errors": total_errors,
                "success_rate": success_rate,
            }
        )
        if avg_response_time_ms is not UNSET:
            field_dict["avg_response_time_ms"] = avg_response_time_ms
        if last_activity is not UNSET:
            field_dict["last_activity"] = last_activity
        if uptime_percentage is not UNSET:
            field_dict["uptime_percentage"] = uptime_percentage

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        server_id = d.pop("server_id")

        server_name = d.pop("server_name")

        status = ServerStatus(d.pop("status"))

        total_tools = d.pop("total_tools")

        enabled_tools = d.pop("enabled_tools")

        total_calls = d.pop("total_calls")

        total_errors = d.pop("total_errors")

        success_rate = d.pop("success_rate")

        def _parse_avg_response_time_ms(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        avg_response_time_ms = _parse_avg_response_time_ms(d.pop("avg_response_time_ms", UNSET))

        def _parse_last_activity(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_activity_type_0 = isoparse(data)

                return last_activity_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_activity = _parse_last_activity(d.pop("last_activity", UNSET))

        def _parse_uptime_percentage(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        uptime_percentage = _parse_uptime_percentage(d.pop("uptime_percentage", UNSET))

        tool_server_metrics = cls(
            server_id=server_id,
            server_name=server_name,
            status=status,
            total_tools=total_tools,
            enabled_tools=enabled_tools,
            total_calls=total_calls,
            total_errors=total_errors,
            success_rate=success_rate,
            avg_response_time_ms=avg_response_time_ms,
            last_activity=last_activity,
            uptime_percentage=uptime_percentage,
        )

        tool_server_metrics.additional_properties = d
        return tool_server_metrics

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
