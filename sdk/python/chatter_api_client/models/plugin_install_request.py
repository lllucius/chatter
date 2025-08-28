from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PluginInstallRequest")


@_attrs_define
class PluginInstallRequest:
    """Request schema for installing a plugin.

    Attributes:
        plugin_path (str): Path to plugin file or directory
        enable_on_install (Union[Unset, bool]): Enable plugin after installation Default: True.
    """

    plugin_path: str
    enable_on_install: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plugin_path = self.plugin_path

        enable_on_install = self.enable_on_install

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plugin_path": plugin_path,
            }
        )
        if enable_on_install is not UNSET:
            field_dict["enable_on_install"] = enable_on_install

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plugin_path = d.pop("plugin_path")

        enable_on_install = d.pop("enable_on_install", UNSET)

        plugin_install_request = cls(
            plugin_path=plugin_path,
            enable_on_install=enable_on_install,
        )

        plugin_install_request.additional_properties = d
        return plugin_install_request

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
