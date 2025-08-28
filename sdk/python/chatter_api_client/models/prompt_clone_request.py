from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_clone_request_modifications_type_0 import PromptCloneRequestModificationsType0


T = TypeVar("T", bound="PromptCloneRequest")


@_attrs_define
class PromptCloneRequest:
    """Schema for prompt clone request.

    Attributes:
        name (str): New prompt name
        description (Union[None, Unset, str]): New prompt description
        modifications (Union['PromptCloneRequestModificationsType0', None, Unset]): Modifications to apply
    """

    name: str
    description: Union[None, Unset, str] = UNSET
    modifications: Union["PromptCloneRequestModificationsType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prompt_clone_request_modifications_type_0 import PromptCloneRequestModificationsType0

        name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        modifications: Union[None, Unset, dict[str, Any]]
        if isinstance(self.modifications, Unset):
            modifications = UNSET
        elif isinstance(self.modifications, PromptCloneRequestModificationsType0):
            modifications = self.modifications.to_dict()
        else:
            modifications = self.modifications

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if modifications is not UNSET:
            field_dict["modifications"] = modifications

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_clone_request_modifications_type_0 import PromptCloneRequestModificationsType0

        d = dict(src_dict)
        name = d.pop("name")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_modifications(data: object) -> Union["PromptCloneRequestModificationsType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                modifications_type_0 = PromptCloneRequestModificationsType0.from_dict(data)

                return modifications_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PromptCloneRequestModificationsType0", None, Unset], data)

        modifications = _parse_modifications(d.pop("modifications", UNSET))

        prompt_clone_request = cls(
            name=name,
            description=description,
            modifications=modifications,
        )

        prompt_clone_request.additional_properties = d
        return prompt_clone_request

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
