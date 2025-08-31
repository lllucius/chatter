from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.correlation_trace_response_requests_item import CorrelationTraceResponseRequestsItem


T = TypeVar("T", bound="CorrelationTraceResponse")


@_attrs_define
class CorrelationTraceResponse:
    """Schema for correlation trace response.

    Attributes:
        correlation_id (str): Correlation ID
        trace_length (int): Number of requests in trace
        requests (list['CorrelationTraceResponseRequestsItem']): List of requests in trace
    """

    correlation_id: str
    trace_length: int
    requests: list["CorrelationTraceResponseRequestsItem"]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        correlation_id = self.correlation_id

        trace_length = self.trace_length

        requests = []
        for requests_item_data in self.requests:
            requests_item = requests_item_data.to_dict()
            requests.append(requests_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "correlation_id": correlation_id,
                "trace_length": trace_length,
                "requests": requests,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.correlation_trace_response_requests_item import CorrelationTraceResponseRequestsItem

        d = dict(src_dict)
        correlation_id = d.pop("correlation_id")

        trace_length = d.pop("trace_length")

        requests = []
        _requests = d.pop("requests")
        for requests_item_data in _requests:
            requests_item = CorrelationTraceResponseRequestsItem.from_dict(requests_item_data)

            requests.append(requests_item)

        correlation_trace_response = cls(
            correlation_id=correlation_id,
            trace_length=trace_length,
            requests=requests,
        )

        correlation_trace_response.additional_properties = d
        return correlation_trace_response

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
