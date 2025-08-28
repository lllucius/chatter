from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserUpdate")


@_attrs_define
class UserUpdate:
    """Schema for user profile updates.

    Attributes:
        full_name (Union[None, Unset, str]): Full name
        bio (Union[None, Unset, str]): User bio
        avatar_url (Union[None, Unset, str]): Avatar URL
        default_llm_provider (Union[None, Unset, str]): Default LLM provider
        default_profile_id (Union[None, Unset, str]): Default profile ID
    """

    full_name: Union[None, Unset, str] = UNSET
    bio: Union[None, Unset, str] = UNSET
    avatar_url: Union[None, Unset, str] = UNSET
    default_llm_provider: Union[None, Unset, str] = UNSET
    default_profile_id: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        full_name: Union[None, Unset, str]
        if isinstance(self.full_name, Unset):
            full_name = UNSET
        else:
            full_name = self.full_name

        bio: Union[None, Unset, str]
        if isinstance(self.bio, Unset):
            bio = UNSET
        else:
            bio = self.bio

        avatar_url: Union[None, Unset, str]
        if isinstance(self.avatar_url, Unset):
            avatar_url = UNSET
        else:
            avatar_url = self.avatar_url

        default_llm_provider: Union[None, Unset, str]
        if isinstance(self.default_llm_provider, Unset):
            default_llm_provider = UNSET
        else:
            default_llm_provider = self.default_llm_provider

        default_profile_id: Union[None, Unset, str]
        if isinstance(self.default_profile_id, Unset):
            default_profile_id = UNSET
        else:
            default_profile_id = self.default_profile_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if full_name is not UNSET:
            field_dict["full_name"] = full_name
        if bio is not UNSET:
            field_dict["bio"] = bio
        if avatar_url is not UNSET:
            field_dict["avatar_url"] = avatar_url
        if default_llm_provider is not UNSET:
            field_dict["default_llm_provider"] = default_llm_provider
        if default_profile_id is not UNSET:
            field_dict["default_profile_id"] = default_profile_id

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_full_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        full_name = _parse_full_name(d.pop("full_name", UNSET))

        def _parse_bio(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        bio = _parse_bio(d.pop("bio", UNSET))

        def _parse_avatar_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        avatar_url = _parse_avatar_url(d.pop("avatar_url", UNSET))

        def _parse_default_llm_provider(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        default_llm_provider = _parse_default_llm_provider(d.pop("default_llm_provider", UNSET))

        def _parse_default_profile_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        default_profile_id = _parse_default_profile_id(d.pop("default_profile_id", UNSET))

        user_update = cls(
            full_name=full_name,
            bio=bio,
            avatar_url=avatar_url,
            default_llm_provider=default_llm_provider,
            default_profile_id=default_profile_id,
        )

        user_update.additional_properties = d
        return user_update

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
