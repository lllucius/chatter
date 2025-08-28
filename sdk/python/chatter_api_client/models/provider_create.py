from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.provider_type import ProviderType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.provider_create_default_config import ProviderCreateDefaultConfig


T = TypeVar("T", bound="ProviderCreate")


@_attrs_define
class ProviderCreate:
    """Schema for creating a provider.

    Attributes:
        name (str): Unique provider name
        provider_type (ProviderType): Types of AI providers.
        display_name (str): Human-readable name
        description (Union[None, Unset, str]): Provider description
        api_key_required (Union[Unset, bool]): Whether API key is required Default: True.
        base_url (Union[None, Unset, str]): Base URL for API
        default_config (Union[Unset, ProviderCreateDefaultConfig]): Default configuration
        is_active (Union[Unset, bool]): Whether provider is active Default: True.
        is_default (Union[Unset, bool]): Whether this is the default provider Default: False.
    """

    name: str
    provider_type: ProviderType
    display_name: str
    description: Union[None, Unset, str] = UNSET
    api_key_required: Union[Unset, bool] = True
    base_url: Union[None, Unset, str] = UNSET
    default_config: Union[Unset, "ProviderCreateDefaultConfig"] = UNSET
    is_active: Union[Unset, bool] = True
    is_default: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        provider_type = self.provider_type.value

        display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        api_key_required = self.api_key_required

        base_url: Union[None, Unset, str]
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        default_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.default_config, Unset):
            default_config = self.default_config.to_dict()

        is_active = self.is_active

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "provider_type": provider_type,
                "display_name": display_name,
            }
        )
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
        from ..models.provider_create_default_config import ProviderCreateDefaultConfig

        d = dict(src_dict)
        name = d.pop("name")

        provider_type = ProviderType(d.pop("provider_type"))

        display_name = d.pop("display_name")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        api_key_required = d.pop("api_key_required", UNSET)

        def _parse_base_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        _default_config = d.pop("default_config", UNSET)
        default_config: Union[Unset, ProviderCreateDefaultConfig]
        if isinstance(_default_config, Unset):
            default_config = UNSET
        else:
            default_config = ProviderCreateDefaultConfig.from_dict(_default_config)

        is_active = d.pop("is_active", UNSET)

        is_default = d.pop("is_default", UNSET)

        provider_create = cls(
            name=name,
            provider_type=provider_type,
            display_name=display_name,
            description=description,
            api_key_required=api_key_required,
            base_url=base_url,
            default_config=default_config,
            is_active=is_active,
            is_default=is_default,
        )

        provider_create.additional_properties = d
        return provider_create

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
