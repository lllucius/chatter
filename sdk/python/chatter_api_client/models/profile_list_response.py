from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.profile_response import ProfileResponse


T = TypeVar("T", bound="ProfileListResponse")


@_attrs_define
class ProfileListResponse:
    """Schema for profile list response.

    Attributes:
        profiles (list['ProfileResponse']): List of profiles
        total_count (int): Total number of profiles
        limit (int): Applied limit
        offset (int): Applied offset
    """

    profiles: list["ProfileResponse"]
    total_count: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        profiles = []
        for profiles_item_data in self.profiles:
            profiles_item = profiles_item_data.to_dict()
            profiles.append(profiles_item)

        total_count = self.total_count

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "profiles": profiles,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.profile_response import ProfileResponse

        d = dict(src_dict)
        profiles = []
        _profiles = d.pop("profiles")
        for profiles_item_data in _profiles:
            profiles_item = ProfileResponse.from_dict(profiles_item_data)

            profiles.append(profiles_item)

        total_count = d.pop("total_count")

        limit = d.pop("limit")

        offset = d.pop("offset")

        profile_list_response = cls(
            profiles=profiles,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

        profile_list_response.additional_properties = d
        return profile_list_response

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
