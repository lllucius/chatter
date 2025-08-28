from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.model_def_with_provider import ModelDefWithProvider


T = TypeVar("T", bound="ModelDefList")


@_attrs_define
class ModelDefList:
    """List of model definitions with pagination.

    Attributes:
        models (list['ModelDefWithProvider']):
        total (int):
        page (int):
        per_page (int):
    """

    models: list["ModelDefWithProvider"]
    total: int
    page: int
    per_page: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        models = []
        for models_item_data in self.models:
            models_item = models_item_data.to_dict()
            models.append(models_item)

        total = self.total

        page = self.page

        per_page = self.per_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "models": models,
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_def_with_provider import ModelDefWithProvider

        d = dict(src_dict)
        models = []
        _models = d.pop("models")
        for models_item_data in _models:
            models_item = ModelDefWithProvider.from_dict(models_item_data)

            models.append(models_item)

        total = d.pop("total")

        page = d.pop("page")

        per_page = d.pop("per_page")

        model_def_list = cls(
            models=models,
            total=total,
            page=page,
            per_page=per_page,
        )

        model_def_list.additional_properties = d
        return model_def_list

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
