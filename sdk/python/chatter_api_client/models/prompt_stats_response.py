from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.prompt_response import PromptResponse
    from ..models.prompt_stats_response_prompts_by_category import PromptStatsResponsePromptsByCategory
    from ..models.prompt_stats_response_prompts_by_type import PromptStatsResponsePromptsByType
    from ..models.prompt_stats_response_usage_stats import PromptStatsResponseUsageStats


T = TypeVar("T", bound="PromptStatsResponse")


@_attrs_define
class PromptStatsResponse:
    """Schema for prompt statistics response.

    Attributes:
        total_prompts (int): Total number of prompts
        prompts_by_type (PromptStatsResponsePromptsByType): Prompts by type
        prompts_by_category (PromptStatsResponsePromptsByCategory): Prompts by category
        most_used_prompts (list['PromptResponse']): Most used prompts
        recent_prompts (list['PromptResponse']): Recently created prompts
        usage_stats (PromptStatsResponseUsageStats): Usage statistics
    """

    total_prompts: int
    prompts_by_type: "PromptStatsResponsePromptsByType"
    prompts_by_category: "PromptStatsResponsePromptsByCategory"
    most_used_prompts: list["PromptResponse"]
    recent_prompts: list["PromptResponse"]
    usage_stats: "PromptStatsResponseUsageStats"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_prompts = self.total_prompts

        prompts_by_type = self.prompts_by_type.to_dict()

        prompts_by_category = self.prompts_by_category.to_dict()

        most_used_prompts = []
        for most_used_prompts_item_data in self.most_used_prompts:
            most_used_prompts_item = most_used_prompts_item_data.to_dict()
            most_used_prompts.append(most_used_prompts_item)

        recent_prompts = []
        for recent_prompts_item_data in self.recent_prompts:
            recent_prompts_item = recent_prompts_item_data.to_dict()
            recent_prompts.append(recent_prompts_item)

        usage_stats = self.usage_stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_prompts": total_prompts,
                "prompts_by_type": prompts_by_type,
                "prompts_by_category": prompts_by_category,
                "most_used_prompts": most_used_prompts,
                "recent_prompts": recent_prompts,
                "usage_stats": usage_stats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_response import PromptResponse
        from ..models.prompt_stats_response_prompts_by_category import PromptStatsResponsePromptsByCategory
        from ..models.prompt_stats_response_prompts_by_type import PromptStatsResponsePromptsByType
        from ..models.prompt_stats_response_usage_stats import PromptStatsResponseUsageStats

        d = dict(src_dict)
        total_prompts = d.pop("total_prompts")

        prompts_by_type = PromptStatsResponsePromptsByType.from_dict(d.pop("prompts_by_type"))

        prompts_by_category = PromptStatsResponsePromptsByCategory.from_dict(d.pop("prompts_by_category"))

        most_used_prompts = []
        _most_used_prompts = d.pop("most_used_prompts")
        for most_used_prompts_item_data in _most_used_prompts:
            most_used_prompts_item = PromptResponse.from_dict(most_used_prompts_item_data)

            most_used_prompts.append(most_used_prompts_item)

        recent_prompts = []
        _recent_prompts = d.pop("recent_prompts")
        for recent_prompts_item_data in _recent_prompts:
            recent_prompts_item = PromptResponse.from_dict(recent_prompts_item_data)

            recent_prompts.append(recent_prompts_item)

        usage_stats = PromptStatsResponseUsageStats.from_dict(d.pop("usage_stats"))

        prompt_stats_response = cls(
            total_prompts=total_prompts,
            prompts_by_type=prompts_by_type,
            prompts_by_category=prompts_by_category,
            most_used_prompts=most_used_prompts,
            recent_prompts=recent_prompts,
            usage_stats=usage_stats,
        )

        prompt_stats_response.additional_properties = d
        return prompt_stats_response

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
