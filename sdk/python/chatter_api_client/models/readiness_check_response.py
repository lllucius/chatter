from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.readiness_check_response_checks import ReadinessCheckResponseChecks


T = TypeVar("T", bound="ReadinessCheckResponse")


@_attrs_define
class ReadinessCheckResponse:
    """Schema for readiness check response.

    Attributes:
        status (str): Readiness status
        service (str): Service name
        version (str): Service version
        environment (str): Environment
        checks (ReadinessCheckResponseChecks): Health check results
    """

    status: str
    service: str
    version: str
    environment: str
    checks: "ReadinessCheckResponseChecks"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        service = self.service

        version = self.version

        environment = self.environment

        checks = self.checks.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
                "service": service,
                "version": version,
                "environment": environment,
                "checks": checks,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.readiness_check_response_checks import ReadinessCheckResponseChecks

        d = dict(src_dict)
        status = d.pop("status")

        service = d.pop("service")

        version = d.pop("version")

        environment = d.pop("environment")

        checks = ReadinessCheckResponseChecks.from_dict(d.pop("checks"))

        readiness_check_response = cls(
            status=status,
            service=service,
            version=version,
            environment=environment,
            checks=checks,
        )

        readiness_check_response.additional_properties = d
        return readiness_check_response

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
