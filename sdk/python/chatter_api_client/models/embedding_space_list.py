from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.embedding_space_with_model import EmbeddingSpaceWithModel


T = TypeVar("T", bound="EmbeddingSpaceList")


@_attrs_define
class EmbeddingSpaceList:
    """List of embedding spaces with pagination.

    Attributes:
        spaces (list['EmbeddingSpaceWithModel']):
        total (int):
        page (int):
        per_page (int):
    """

    spaces: list["EmbeddingSpaceWithModel"]
    total: int
    page: int
    per_page: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        spaces = []
        for spaces_item_data in self.spaces:
            spaces_item = spaces_item_data.to_dict()
            spaces.append(spaces_item)

        total = self.total

        page = self.page

        per_page = self.per_page

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "spaces": spaces,
                "total": total,
                "page": page,
                "per_page": per_page,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.embedding_space_with_model import EmbeddingSpaceWithModel

        d = dict(src_dict)
        spaces = []
        _spaces = d.pop("spaces")
        for spaces_item_data in _spaces:
            spaces_item = EmbeddingSpaceWithModel.from_dict(spaces_item_data)

            spaces.append(spaces_item)

        total = d.pop("total")

        page = d.pop("page")

        per_page = d.pop("per_page")

        embedding_space_list = cls(
            spaces=spaces,
            total=total,
            page=page,
            per_page=per_page,
        )

        embedding_space_list.additional_properties = d
        return embedding_space_list

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
