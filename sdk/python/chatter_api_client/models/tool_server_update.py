from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.o_auth_config_schema import OAuthConfigSchema
    from ..models.tool_server_update_headers_type_0 import ToolServerUpdateHeadersType0


T = TypeVar("T", bound="ToolServerUpdate")


@_attrs_define
class ToolServerUpdate:
    """Schema for updating a remote tool server.

    Attributes:
        display_name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        base_url (Union[None, Unset, str]):
        transport_type (Union[None, Unset, str]):
        oauth_config (Union['OAuthConfigSchema', None, Unset]):
        headers (Union['ToolServerUpdateHeadersType0', None, Unset]):
        timeout (Union[None, Unset, int]):
        auto_start (Union[None, Unset, bool]):
        auto_update (Union[None, Unset, bool]):
        max_failures (Union[None, Unset, int]):
    """

    display_name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    base_url: Union[None, Unset, str] = UNSET
    transport_type: Union[None, Unset, str] = UNSET
    oauth_config: Union["OAuthConfigSchema", None, Unset] = UNSET
    headers: Union["ToolServerUpdateHeadersType0", None, Unset] = UNSET
    timeout: Union[None, Unset, int] = UNSET
    auto_start: Union[None, Unset, bool] = UNSET
    auto_update: Union[None, Unset, bool] = UNSET
    max_failures: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.o_auth_config_schema import OAuthConfigSchema
        from ..models.tool_server_update_headers_type_0 import ToolServerUpdateHeadersType0

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

        base_url: Union[None, Unset, str]
        if isinstance(self.base_url, Unset):
            base_url = UNSET
        else:
            base_url = self.base_url

        transport_type: Union[None, Unset, str]
        if isinstance(self.transport_type, Unset):
            transport_type = UNSET
        else:
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
        elif isinstance(self.headers, ToolServerUpdateHeadersType0):
            headers = self.headers.to_dict()
        else:
            headers = self.headers

        timeout: Union[None, Unset, int]
        if isinstance(self.timeout, Unset):
            timeout = UNSET
        else:
            timeout = self.timeout

        auto_start: Union[None, Unset, bool]
        if isinstance(self.auto_start, Unset):
            auto_start = UNSET
        else:
            auto_start = self.auto_start

        auto_update: Union[None, Unset, bool]
        if isinstance(self.auto_update, Unset):
            auto_update = UNSET
        else:
            auto_update = self.auto_update

        max_failures: Union[None, Unset, int]
        if isinstance(self.max_failures, Unset):
            max_failures = UNSET
        else:
            max_failures = self.max_failures

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
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
        from ..models.tool_server_update_headers_type_0 import ToolServerUpdateHeadersType0

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

        def _parse_base_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        base_url = _parse_base_url(d.pop("base_url", UNSET))

        def _parse_transport_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        transport_type = _parse_transport_type(d.pop("transport_type", UNSET))

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

        def _parse_headers(data: object) -> Union["ToolServerUpdateHeadersType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                headers_type_0 = ToolServerUpdateHeadersType0.from_dict(data)

                return headers_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ToolServerUpdateHeadersType0", None, Unset], data)

        headers = _parse_headers(d.pop("headers", UNSET))

        def _parse_timeout(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        timeout = _parse_timeout(d.pop("timeout", UNSET))

        def _parse_auto_start(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        auto_start = _parse_auto_start(d.pop("auto_start", UNSET))

        def _parse_auto_update(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        auto_update = _parse_auto_update(d.pop("auto_update", UNSET))

        def _parse_max_failures(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_failures = _parse_max_failures(d.pop("max_failures", UNSET))

        tool_server_update = cls(
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

        tool_server_update.additional_properties = d
        return tool_server_update

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
