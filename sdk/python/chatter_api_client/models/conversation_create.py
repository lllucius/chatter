from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConversationCreate")


@_attrs_define
class ConversationCreate:
    """Schema for creating a conversation.

    Attributes:
        title (str): Conversation title
        description (Union[None, Unset, str]): Conversation description
        profile_id (Union[None, Unset, str]): Profile ID to use
        system_prompt (Union[None, Unset, str]): System prompt
        enable_retrieval (Union[Unset, bool]): Enable document retrieval Default: False.
    """

    title: str
    description: Union[None, Unset, str] = UNSET
    profile_id: Union[None, Unset, str] = UNSET
    system_prompt: Union[None, Unset, str] = UNSET
    enable_retrieval: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        profile_id: Union[None, Unset, str]
        if isinstance(self.profile_id, Unset):
            profile_id = UNSET
        else:
            profile_id = self.profile_id

        system_prompt: Union[None, Unset, str]
        if isinstance(self.system_prompt, Unset):
            system_prompt = UNSET
        else:
            system_prompt = self.system_prompt

        enable_retrieval = self.enable_retrieval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "title": title,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if profile_id is not UNSET:
            field_dict["profile_id"] = profile_id
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if enable_retrieval is not UNSET:
            field_dict["enable_retrieval"] = enable_retrieval

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        title = d.pop("title")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_profile_id(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        profile_id = _parse_profile_id(d.pop("profile_id", UNSET))

        def _parse_system_prompt(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        system_prompt = _parse_system_prompt(d.pop("system_prompt", UNSET))

        enable_retrieval = d.pop("enable_retrieval", UNSET)

        conversation_create = cls(
            title=title,
            description=description,
            profile_id=profile_id,
            system_prompt=system_prompt,
            enable_retrieval=enable_retrieval,
        )

        conversation_create.additional_properties = d
        return conversation_create

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
