from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.model_type import ModelType

T = TypeVar("T", bound="DefaultProvider")


@_attrs_define
class DefaultProvider:
    """Schema for setting default provider.

    Attributes:
        provider_id (str):
        model_type (ModelType): Types of AI models.
    """

    provider_id: str
    model_type: ModelType
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        provider_id = self.provider_id

        model_type = self.model_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "provider_id": provider_id,
                "model_type": model_type,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        provider_id = d.pop("provider_id")

        model_type = ModelType(d.pop("model_type"))

        default_provider = cls(
            provider_id=provider_id,
            model_type=model_type,
        )

        default_provider.additional_properties = d
        return default_provider

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
