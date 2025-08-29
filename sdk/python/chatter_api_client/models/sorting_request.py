from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SortingRequest")


@_attrs_define
class SortingRequest:
    """Common sorting request schema.

    Attributes:
        sort_by (Union[Unset, str]): Sort field Default: 'created_at'.
        sort_order (Union[Unset, str]): Sort order Default: 'desc'.
    """

    sort_by: Union[Unset, str] = "created_at"
    sort_order: Union[Unset, str] = "desc"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sort_by = self.sort_by

        sort_order = self.sort_order

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sort_by is not UNSET:
            field_dict["sort_by"] = sort_by
        if sort_order is not UNSET:
            field_dict["sort_order"] = sort_order

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sort_by = d.pop("sort_by", UNSET)

        sort_order = d.pop("sort_order", UNSET)

        sorting_request = cls(
            sort_by=sort_by,
            sort_order=sort_order,
        )

        sorting_request.additional_properties = d
        return sorting_request

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
