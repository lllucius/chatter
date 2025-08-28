from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.prompt_response import PromptResponse


T = TypeVar("T", bound="PromptListResponse")


@_attrs_define
class PromptListResponse:
    """Schema for prompt list response.

    Attributes:
        prompts (list['PromptResponse']): List of prompts
        total_count (int): Total number of prompts
        limit (int): Requested limit
        offset (int): Requested offset
    """

    prompts: list["PromptResponse"]
    total_count: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        prompts = []
        for prompts_item_data in self.prompts:
            prompts_item = prompts_item_data.to_dict()
            prompts.append(prompts_item)

        total_count = self.total_count

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompts": prompts,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_response import PromptResponse

        d = dict(src_dict)
        prompts = []
        _prompts = d.pop("prompts")
        for prompts_item_data in _prompts:
            prompts_item = PromptResponse.from_dict(prompts_item_data)

            prompts.append(prompts_item)

        total_count = d.pop("total_count")

        limit = d.pop("limit")

        offset = d.pop("offset")

        prompt_list_response = cls(
            prompts=prompts,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

        prompt_list_response.additional_properties = d
        return prompt_list_response

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
