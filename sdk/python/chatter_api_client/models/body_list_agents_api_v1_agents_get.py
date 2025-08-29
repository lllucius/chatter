from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.pagination_request import PaginationRequest
    from ..models.sorting_request import SortingRequest


T = TypeVar("T", bound="BodyListAgentsApiV1AgentsGet")


@_attrs_define
class BodyListAgentsApiV1AgentsGet:
    """
    Attributes:
        pagination (Union[Unset, PaginationRequest]): Common pagination request schema.
        sorting (Union[Unset, SortingRequest]): Common sorting request schema.
        tags (Union[None, Unset, list[str]]):
    """

    pagination: Union[Unset, "PaginationRequest"] = UNSET
    sorting: Union[Unset, "SortingRequest"] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        pagination: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.pagination, Unset):
            pagination = self.pagination.to_dict()

        sorting: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.sorting, Unset):
            sorting = self.sorting.to_dict()

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if pagination is not UNSET:
            field_dict["pagination"] = pagination
        if sorting is not UNSET:
            field_dict["sorting"] = sorting
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.pagination_request import PaginationRequest
        from ..models.sorting_request import SortingRequest

        d = dict(src_dict)
        _pagination = d.pop("pagination", UNSET)
        pagination: Union[Unset, PaginationRequest]
        if isinstance(_pagination, Unset):
            pagination = UNSET
        else:
            pagination = PaginationRequest.from_dict(_pagination)

        _sorting = d.pop("sorting", UNSET)
        sorting: Union[Unset, SortingRequest]
        if isinstance(_sorting, Unset):
            sorting = UNSET
        else:
            sorting = SortingRequest.from_dict(_sorting)

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        body_list_agents_api_v1_agents_get = cls(
            pagination=pagination,
            sorting=sorting,
            tags=tags,
        )

        body_list_agents_api_v1_agents_get.additional_properties = d
        return body_list_agents_api_v1_agents_get

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
