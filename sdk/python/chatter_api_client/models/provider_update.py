from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_update_default_config_type_0 import ProviderUpdateDefaultConfigType0


T = TypeVar("T", bound="ProviderUpdate")


@_attrs_define
class ProviderUpdate:
    """Schema for updating a provider.

    Attributes:
        display_name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        api_key_required (Union[None, Unset, bool]):
        base_url (Union[None, Unset, str]):
        default_config (Union['ProviderUpdateDefaultConfigType0', None, Unset]):
        is_active (Union[None, Unset, bool]):
        is_default (Union[None, Unset, bool]):
    """

    display_name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    api_key_required: Union[None, Unset, bool] = UNSET
    base_url: Union[None, Unset, str] = UNSET
    default_config: Union["ProviderUpdateDefaultConfigType0", None, Unset] = UNSET
    is_active: Union[None, Unset, bool] = UNSET
    is_default: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.provider_update_default_config_type_0 import ProviderUpdateDefaultConfigType0

        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        api_key_required: Union[None, Unset, bool]
        if isinstance(self.api_key_required, Unset):
            api_key_required = UNSET
        else:
            api_key_required = self.api_key_required

        base_url: Union[None, Unset, str]
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        default_config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.default_config, Unset):
            default_config = UNSET
        elif isinstance(self.default_config, ProviderUpdateDefaultConfigType0):
            default_config = self.default_config.to_dict()
        else:
            default_config = self.default_config

        is_active: Union[None, Unset, bool]
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        is_default: Union[None, Unset, bool]
        if isinstance(self.is_default, Unset):
            is_default = UNSET
        else:
            is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if api_key_required is not UNSET:
            field_dict["api_key_required"] = api_key_required
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if default_config is not UNSET:
            field_dict["default_config"] = default_config
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.provider_update_default_config_type_0 import ProviderUpdateDefaultConfigType0

        d = dict(src_dict)

        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_api_key_required(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        api_key_required = _parse_api_key_required(d.pop("api_key_required", UNSET))

        def _parse_base_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_default_config(data: object) -> Union["ProviderUpdateDefaultConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                default_config_type_0 = ProviderUpdateDefaultConfigType0.from_dict(data)

                return default_config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ProviderUpdateDefaultConfigType0", None, Unset], data)

        default_config = _parse_default_config(d.pop("default_config", UNSET))

        def _parse_is_active(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_is_default(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_default = _parse_is_default(d.pop("is_default", UNSET))

        provider_update = cls(
            display_name=display_name,
            description=description,
            api_key_required=api_key_required,
            base_url=base_url,
            default_config=default_config,
            is_active=is_active,
            is_default=is_default,
        )

        provider_update.additional_properties = d
        return provider_update

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
