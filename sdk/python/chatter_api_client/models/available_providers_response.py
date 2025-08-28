from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.available_providers_response_providers import AvailableProvidersResponseProviders
    from ..models.available_providers_response_supported_features import AvailableProvidersResponseSupportedFeatures


T = TypeVar("T", bound="AvailableProvidersResponse")


@_attrs_define
class AvailableProvidersResponse:
    """Schema for available providers response.

    Attributes:
        providers (AvailableProvidersResponseProviders): Available LLM providers with their configurations
        total_providers (int): Total number of available providers
        supported_features (AvailableProvidersResponseSupportedFeatures): Features supported by each provider
    """

    providers: "AvailableProvidersResponseProviders"
    total_providers: int
    supported_features: "AvailableProvidersResponseSupportedFeatures"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        providers = self.providers.to_dict()

        total_providers = self.total_providers

        supported_features = self.supported_features.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "providers": providers,
                "total_providers": total_providers,
                "supported_features": supported_features,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.available_providers_response_providers import AvailableProvidersResponseProviders
        from ..models.available_providers_response_supported_features import AvailableProvidersResponseSupportedFeatures

        d = dict(src_dict)
        providers = AvailableProvidersResponseProviders.from_dict(d.pop("providers"))

        total_providers = d.pop("total_providers")

        supported_features = AvailableProvidersResponseSupportedFeatures.from_dict(d.pop("supported_features"))

        available_providers_response = cls(
            providers=providers,
            total_providers=total_providers,
            supported_features=supported_features,
        )

        available_providers_response.additional_properties = d
        return available_providers_response

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
