from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="SSEStatsResponse")


@_attrs_define
class SSEStatsResponse:
    """Response schema for SSE service statistics.

    Attributes:
        total_connections (int): Total active connections
        your_connections (int): Your active connections
    """

    total_connections: int
    your_connections: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_connections = self.total_connections

        your_connections = self.your_connections

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_connections": total_connections,
                "your_connections": your_connections,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_connections = d.pop("total_connections")

        your_connections = d.pop("your_connections")

        sse_stats_response = cls(
            total_connections=total_connections,
            your_connections=your_connections,
        )

        sse_stats_response.additional_properties = d
        return sse_stats_response

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
