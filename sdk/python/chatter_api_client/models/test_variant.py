from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.test_variant_configuration import TestVariantConfiguration


T = TypeVar("T", bound="TestVariant")


@_attrs_define
class TestVariant:
    """Test variant definition.

    Attributes:
        name (str): Variant name
        description (str): Variant description
        configuration (TestVariantConfiguration): Variant configuration
        weight (Union[Unset, float]): Variant weight for allocation Default: 1.0.
    """

    name: str
    description: str
    configuration: "TestVariantConfiguration"
    weight: Union[Unset, float] = 1.0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        configuration = self.configuration.to_dict()

        weight = self.weight

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "configuration": configuration,
            }
        )
        if weight is not UNSET:
            field_dict["weight"] = weight

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_variant_configuration import TestVariantConfiguration

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        configuration = TestVariantConfiguration.from_dict(d.pop("configuration"))

        weight = d.pop("weight", UNSET)

        test_variant = cls(
            name=name,
            description=description,
            configuration=configuration,
            weight=weight,
        )

        test_variant.additional_properties = d
        return test_variant

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
