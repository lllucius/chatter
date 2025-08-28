import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.plugin_status import PluginStatus
from ..models.plugin_type import PluginType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.plugin_response_capabilities_item import PluginResponseCapabilitiesItem
    from ..models.plugin_response_metadata import PluginResponseMetadata


T = TypeVar("T", bound="PluginResponse")


@_attrs_define
class PluginResponse:
    """Response schema for plugin data.

    Attributes:
        id (str): Plugin ID
        name (str): Plugin name
        version (str): Plugin version
        description (str): Plugin description
        author (str): Plugin author
        plugin_type (PluginType): Types of plugins.
        status (PluginStatus): Plugin status.
        entry_point (str): Plugin entry point
        capabilities (list['PluginResponseCapabilitiesItem']): Plugin capabilities
        dependencies (list[str]): Plugin dependencies
        permissions (list[str]): Required permissions
        enabled (bool): Whether plugin is enabled
        installed_at (datetime.datetime): Installation timestamp
        updated_at (datetime.datetime): Last update timestamp
        metadata (PluginResponseMetadata): Additional metadata
        error_message (Union[None, Unset, str]): Error message if any
    """

    id: str
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    status: PluginStatus
    entry_point: str
    capabilities: list["PluginResponseCapabilitiesItem"]
    dependencies: list[str]
    permissions: list[str]
    enabled: bool
    installed_at: datetime.datetime
    updated_at: datetime.datetime
    metadata: "PluginResponseMetadata"
    error_message: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        version = self.version

        description = self.description

        author = self.author

        plugin_type = self.plugin_type.value

        status = self.status.value

        entry_point = self.entry_point

        capabilities = []
        for capabilities_item_data in self.capabilities:
            capabilities_item = capabilities_item_data.to_dict()
            capabilities.append(capabilities_item)

        dependencies = self.dependencies

        permissions = self.permissions

        enabled = self.enabled

        installed_at = self.installed_at.isoformat()

        updated_at = self.updated_at.isoformat()

        metadata = self.metadata.to_dict()

        error_message: Union[None, Unset, str]
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "version": version,
                "description": description,
                "author": author,
                "plugin_type": plugin_type,
                "status": status,
                "entry_point": entry_point,
                "capabilities": capabilities,
                "dependencies": dependencies,
                "permissions": permissions,
                "enabled": enabled,
                "installed_at": installed_at,
                "updated_at": updated_at,
                "metadata": metadata,
            }
        )
        if error_message is not UNSET:
            field_dict["error_message"] = error_message

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.plugin_response_capabilities_item import PluginResponseCapabilitiesItem
        from ..models.plugin_response_metadata import PluginResponseMetadata

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        version = d.pop("version")

        description = d.pop("description")

        author = d.pop("author")

        plugin_type = PluginType(d.pop("plugin_type"))

        status = PluginStatus(d.pop("status"))

        entry_point = d.pop("entry_point")

        capabilities = []
        _capabilities = d.pop("capabilities")
        for capabilities_item_data in _capabilities:
            capabilities_item = PluginResponseCapabilitiesItem.from_dict(capabilities_item_data)

            capabilities.append(capabilities_item)

        dependencies = cast(list[str], d.pop("dependencies"))

        permissions = cast(list[str], d.pop("permissions"))

        enabled = d.pop("enabled")

        installed_at = isoparse(d.pop("installed_at"))

        updated_at = isoparse(d.pop("updated_at"))

        metadata = PluginResponseMetadata.from_dict(d.pop("metadata"))

        def _parse_error_message(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        plugin_response = cls(
            id=id,
            name=name,
            version=version,
            description=description,
            author=author,
            plugin_type=plugin_type,
            status=status,
            entry_point=entry_point,
            capabilities=capabilities,
            dependencies=dependencies,
            permissions=permissions,
            enabled=enabled,
            installed_at=installed_at,
            updated_at=updated_at,
            metadata=metadata,
            error_message=error_message,
        )

        plugin_response.additional_properties = d
        return plugin_response

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
