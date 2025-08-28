from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="HealthCheckResponse")


@_attrs_define
class HealthCheckResponse:
    """Schema for health check response.

    Attributes:
        status (str): Health status
        service (str): Service name
        version (str): Service version
        environment (str): Environment
    """

    status: str
    service: str
    version: str
    environment: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        service = self.service

        version = self.version

        environment = self.environment

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "service": service,
                "version": version,
                "environment": environment,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        status = d.pop("status")

        service = d.pop("service")

        version = d.pop("version")

        environment = d.pop("environment")

        health_check_response = cls(
            status=status,
            service=service,
            version=version,
            environment=environment,
        )

        health_check_response.additional_properties = d
        return health_check_response

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
