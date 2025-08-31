from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_auth_config_schema import OAuthConfigSchema
    from ..models.tool_server_create_headers_type_0 import ToolServerCreateHeadersType0


T = TypeVar("T", bound="ToolServerCreate")


@_attrs_define
class ToolServerCreate:
    """Schema for creating a tool server.

    Attributes:
        name (str): Server name
        display_name (str): Display name
        description (Union[None, Unset, str]): Server description
        base_url (Union[None, Unset, str]): Base URL for the remote server (null for built-in servers)
        transport_type (Union[Unset, str]): Transport type: http, sse, or stdio Default: 'http'.
        oauth_config (Union['OAuthConfigSchema', None, Unset]): OAuth configuration if required
        headers (Union['ToolServerCreateHeadersType0', None, Unset]): Additional HTTP headers
        timeout (Union[Unset, int]): Request timeout in seconds Default: 30.
        auto_start (Union[Unset, bool]): Auto-connect to server on system startup Default: True.
        auto_update (Union[Unset, bool]): Auto-update server capabilities Default: True.
        max_failures (Union[Unset, int]): Maximum consecutive failures before disabling Default: 3.
    """

    name: str
    display_name: str
    description: Union[None, Unset, str] = UNSET
    base_url: Union[None, Unset, str] = UNSET
    transport_type: Union[Unset, str] = "http"
    oauth_config: Union["OAuthConfigSchema", None, Unset] = UNSET
    headers: Union["ToolServerCreateHeadersType0", None, Unset] = UNSET
    timeout: Union[Unset, int] = 30
    auto_start: Union[Unset, bool] = True
    auto_update: Union[Unset, bool] = True
    max_failures: Union[Unset, int] = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.o_auth_config_schema import OAuthConfigSchema
        from ..models.tool_server_create_headers_type_0 import ToolServerCreateHeadersType0

        name = self.name

        display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        base_url: Union[None, Unset, str]
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        transport_type = self.transport_type

        oauth_config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.oauth_config, Unset):
            oauth_config = UNSET
        elif isinstance(self.oauth_config, OAuthConfigSchema):
            oauth_config = self.oauth_config.to_dict()
        else:
            oauth_config = self.oauth_config

        headers: Union[None, Unset, dict[str, Any]]
        if isinstance(self.headers, Unset):
            headers = UNSET
        elif isinstance(self.headers, ToolServerCreateHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        timeout = self.timeout

        auto_start = self.auto_start

        auto_update = self.auto_update

        max_failures = self.max_failures

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if base_url is not UNSET:
            field_dict["base_url"] = base_url
        if transport_type is not UNSET:
            field_dict["transport_type"] = transport_type
        if oauth_config is not UNSET:
            field_dict["oauth_config"] = oauth_config
        if headers is not UNSET:
            field_dict["headers"] = headers
        if timeout is not UNSET:
            field_dict["timeout"] = timeout
        if auto_start is not UNSET:
            field_dict["auto_start"] = auto_start
        if auto_update is not UNSET:
            field_dict["auto_update"] = auto_update
        if max_failures is not UNSET:
            field_dict["max_failures"] = max_failures

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.o_auth_config_schema import OAuthConfigSchema
        from ..models.tool_server_create_headers_type_0 import ToolServerCreateHeadersType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_base_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        transport_type = d.pop("transport_type", UNSET)

        def _parse_oauth_config(data: object) -> Union["OAuthConfigSchema", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                oauth_config_type_0 = OAuthConfigSchema.from_dict(data)

                return oauth_config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["OAuthConfigSchema", None, Unset], data)

        oauth_config = _parse_oauth_config(d.pop("oauth_config", UNSET))

        def _parse_headers(data: object) -> Union["ToolServerCreateHeadersType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = ToolServerCreateHeadersType0.from_dict(data)

                return headers_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ToolServerCreateHeadersType0", None, Unset], data)

        headers = _parse_headers(d.pop("headers", UNSET))

        timeout = d.pop("timeout", UNSET)

        auto_start = d.pop("auto_start", UNSET)

        auto_update = d.pop("auto_update", UNSET)

        max_failures = d.pop("max_failures", UNSET)

        tool_server_create = cls(
            name=name,
            display_name=display_name,
            description=description,
            base_url=base_url,
            transport_type=transport_type,
            oauth_config=oauth_config,
            headers=headers,
            timeout=timeout,
            auto_start=auto_start,
            auto_update=auto_update,
            max_failures=max_failures,
        )

        tool_server_create.additional_properties = d
        return tool_server_create

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
