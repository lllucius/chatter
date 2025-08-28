from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.profile_response import ProfileResponse
    from ..models.profile_stats_response_profiles_by_provider import ProfileStatsResponseProfilesByProvider
    from ..models.profile_stats_response_profiles_by_type import ProfileStatsResponseProfilesByType
    from ..models.profile_stats_response_usage_stats import ProfileStatsResponseUsageStats


T = TypeVar("T", bound="ProfileStatsResponse")


@_attrs_define
class ProfileStatsResponse:
    """Schema for profile statistics response.

    Attributes:
        total_profiles (int): Total number of profiles
        profiles_by_type (ProfileStatsResponseProfilesByType): Profiles grouped by type
        profiles_by_provider (ProfileStatsResponseProfilesByProvider): Profiles grouped by LLM provider
        most_used_profiles (list['ProfileResponse']): Most frequently used profiles
        recent_profiles (list['ProfileResponse']): Recently created profiles
        usage_stats (ProfileStatsResponseUsageStats): Usage statistics
    """

    total_profiles: int
    profiles_by_type: "ProfileStatsResponseProfilesByType"
    profiles_by_provider: "ProfileStatsResponseProfilesByProvider"
    most_used_profiles: list["ProfileResponse"]
    recent_profiles: list["ProfileResponse"]
    usage_stats: "ProfileStatsResponseUsageStats"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_profiles = self.total_profiles

        profiles_by_type = self.profiles_by_type.to_dict()

        profiles_by_provider = self.profiles_by_provider.to_dict()

        most_used_profiles = []
        for most_used_profiles_item_data in self.most_used_profiles:
            most_used_profiles_item = most_used_profiles_item_data.to_dict()
            most_used_profiles.append(most_used_profiles_item)

        recent_profiles = []
        for recent_profiles_item_data in self.recent_profiles:
            recent_profiles_item = recent_profiles_item_data.to_dict()
            recent_profiles.append(recent_profiles_item)

        usage_stats = self.usage_stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_profiles": total_profiles,
                "profiles_by_type": profiles_by_type,
                "profiles_by_provider": profiles_by_provider,
                "most_used_profiles": most_used_profiles,
                "recent_profiles": recent_profiles,
                "usage_stats": usage_stats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_response import ProfileResponse
        from ..models.profile_stats_response_profiles_by_provider import ProfileStatsResponseProfilesByProvider
        from ..models.profile_stats_response_profiles_by_type import ProfileStatsResponseProfilesByType
        from ..models.profile_stats_response_usage_stats import ProfileStatsResponseUsageStats

        d = dict(src_dict)
        total_profiles = d.pop("total_profiles")

        profiles_by_type = ProfileStatsResponseProfilesByType.from_dict(d.pop("profiles_by_type"))

        profiles_by_provider = ProfileStatsResponseProfilesByProvider.from_dict(d.pop("profiles_by_provider"))

        most_used_profiles = []
        _most_used_profiles = d.pop("most_used_profiles")
        for most_used_profiles_item_data in _most_used_profiles:
            most_used_profiles_item = ProfileResponse.from_dict(most_used_profiles_item_data)

            most_used_profiles.append(most_used_profiles_item)

        recent_profiles = []
        _recent_profiles = d.pop("recent_profiles")
        for recent_profiles_item_data in _recent_profiles:
            recent_profiles_item = ProfileResponse.from_dict(recent_profiles_item_data)

            recent_profiles.append(recent_profiles_item)

        usage_stats = ProfileStatsResponseUsageStats.from_dict(d.pop("usage_stats"))

        profile_stats_response = cls(
            total_profiles=total_profiles,
            profiles_by_type=profiles_by_type,
            profiles_by_provider=profiles_by_provider,
            most_used_profiles=most_used_profiles,
            recent_profiles=recent_profiles,
            usage_stats=usage_stats,
        )

        profile_stats_response.additional_properties = d
        return profile_stats_response

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
