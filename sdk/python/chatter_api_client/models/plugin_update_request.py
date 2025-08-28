from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plugin_update_request_configuration_type_0 import PluginUpdateRequestConfigurationType0


T = TypeVar("T", bound="PluginUpdateRequest")


@_attrs_define
class PluginUpdateRequest:
    """Request schema for updating a plugin.

    Attributes:
        enabled (Union[None, Unset, bool]): Enable/disable plugin
        configuration (Union['PluginUpdateRequestConfigurationType0', None, Unset]): Plugin configuration
    """

    enabled: Union[None, Unset, bool] = UNSET
    configuration: Union["PluginUpdateRequestConfigurationType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.plugin_update_request_configuration_type_0 import PluginUpdateRequestConfigurationType0

        enabled: Union[None, Unset, bool]
        if isinstance(self.enabled, Unset):
            enabled = UNSET
        else:
            enabled = self.enabled

        configuration: Union[None, Unset, dict[str, Any]]
        if isinstance(self.configuration, Unset):
            configuration = UNSET
        elif isinstance(self.configuration, PluginUpdateRequestConfigurationType0):
            configuration = self.configuration.to_dict()
        else:
            configuration = self.configuration

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if configuration is not UNSET:
            field_dict["configuration"] = configuration

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plugin_update_request_configuration_type_0 import PluginUpdateRequestConfigurationType0

        d = dict(src_dict)

        def _parse_enabled(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        enabled = _parse_enabled(d.pop("enabled", UNSET))

        def _parse_configuration(data: object) -> Union["PluginUpdateRequestConfigurationType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                configuration_type_0 = PluginUpdateRequestConfigurationType0.from_dict(data)

                return configuration_type_0
            except:  # noqa: E722
                pass
            return cast(Union["PluginUpdateRequestConfigurationType0", None, Unset], data)

        configuration = _parse_configuration(d.pop("configuration", UNSET))

        plugin_update_request = cls(
            enabled=enabled,
            configuration=configuration,
        )

        plugin_update_request.additional_properties = d
        return plugin_update_request

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
