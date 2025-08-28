from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.provider import Provider


T = TypeVar("T", bound="ProviderList")


@_attrs_define
class ProviderList:
    """List of providers with pagination.

    Attributes:
        providers (list['Provider']):
        total (int):
        page (int):
        per_page (int):
    """

    providers: list["Provider"]
    total: int
    page: int
    per_page: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        providers = []
        for providers_item_data in self.providers:
            providers_item = providers_item_data.to_dict()
            providers.append(providers_item)

        total = self.total

        page = self.page

        per_page = self.per_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "providers": providers,
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider import Provider

        d = dict(src_dict)
        providers = []
        _providers = d.pop("providers")
        for providers_item_data in _providers:
            providers_item = Provider.from_dict(providers_item_data)

            providers.append(providers_item)

        total = d.pop("total")

        page = d.pop("page")

        per_page = d.pop("per_page")

        provider_list = cls(
            providers=providers,
            total=total,
            page=page,
            per_page=per_page,
        )

        provider_list.additional_properties = d
        return provider_list

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
