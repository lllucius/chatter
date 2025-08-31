from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.metrics_response_endpoints import MetricsResponseEndpoints
    from ..models.metrics_response_health import MetricsResponseHealth
    from ..models.metrics_response_performance import MetricsResponsePerformance


T = TypeVar("T", bound="MetricsResponse")


@_attrs_define
class MetricsResponse:
    """Schema for application metrics response.

    Attributes:
        timestamp (str): Metrics collection timestamp
        service (str): Service name
        version (str): Service version
        environment (str): Environment
        health (MetricsResponseHealth): Health metrics
        performance (MetricsResponsePerformance): Performance statistics
        endpoints (MetricsResponseEndpoints): Endpoint statistics
    """

    timestamp: str
    service: str
    version: str
    environment: str
    health: "MetricsResponseHealth"
    performance: "MetricsResponsePerformance"
    endpoints: "MetricsResponseEndpoints"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        service = self.service

        version = self.version

        environment = self.environment

        health = self.health.to_dict()

        performance = self.performance.to_dict()

        endpoints = self.endpoints.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "timestamp": timestamp,
                "service": service,
                "version": version,
                "environment": environment,
                "health": health,
                "performance": performance,
                "endpoints": endpoints,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.metrics_response_endpoints import MetricsResponseEndpoints
        from ..models.metrics_response_health import MetricsResponseHealth
        from ..models.metrics_response_performance import MetricsResponsePerformance

        d = dict(src_dict)
        timestamp = d.pop("timestamp")

        service = d.pop("service")

        version = d.pop("version")

        environment = d.pop("environment")

        health = MetricsResponseHealth.from_dict(d.pop("health"))

        performance = MetricsResponsePerformance.from_dict(d.pop("performance"))

        endpoints = MetricsResponseEndpoints.from_dict(d.pop("endpoints"))

        metrics_response = cls(
            timestamp=timestamp,
            service=service,
            version=version,
            environment=environment,
            health=health,
            performance=performance,
            endpoints=endpoints,
        )

        metrics_response.additional_properties = d
        return metrics_response

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
