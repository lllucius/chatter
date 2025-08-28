import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.server_status import ServerStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.server_tool_response import ServerToolResponse
    from ..models.tool_server_response_env_type_0 import ToolServerResponseEnvType0


T = TypeVar("T", bound="ToolServerResponse")


@_attrs_define
class ToolServerResponse:
    """Schema for tool server response.

    Attributes:
        name (str): Server name
        display_name (str): Display name
        command (str): Command to start server
        id (str): Server ID
        status (ServerStatus): Enumeration for server status.
        is_builtin (bool): Whether server is built-in
        consecutive_failures (int): Consecutive failure count
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        description (Union[None, Unset, str]): Server description
        args (Union[Unset, list[str]]): Command arguments
        env (Union['ToolServerResponseEnvType0', None, Unset]): Environment variables
        auto_start (Union[Unset, bool]): Auto-start server on system startup Default: True.
        auto_update (Union[Unset, bool]): Auto-update server capabilities Default: True.
        max_failures (Union[Unset, int]): Maximum consecutive failures before disabling Default: 3.
        last_health_check (Union[None, Unset, datetime.datetime]): Last health check
        last_startup_success (Union[None, Unset, datetime.datetime]): Last successful startup
        last_startup_error (Union[None, Unset, str]): Last startup error
        created_by (Union[None, Unset, str]): Creator user ID
        tools (Union[Unset, list['ServerToolResponse']]): Server tools
    """

    name: str
    display_name: str
    command: str
    id: str
    status: ServerStatus
    is_builtin: bool
    consecutive_failures: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    args: Union[Unset, list[str]] = UNSET
    env: Union["ToolServerResponseEnvType0", None, Unset] = UNSET
    auto_start: Union[Unset, bool] = True
    auto_update: Union[Unset, bool] = True
    max_failures: Union[Unset, int] = 3
    last_health_check: Union[None, Unset, datetime.datetime] = UNSET
    last_startup_success: Union[None, Unset, datetime.datetime] = UNSET
    last_startup_error: Union[None, Unset, str] = UNSET
    created_by: Union[None, Unset, str] = UNSET
    tools: Union[Unset, list["ServerToolResponse"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_server_response_env_type_0 import ToolServerResponseEnvType0

        name = self.name

        display_name = self.display_name

        command = self.command

        id = self.id

        status = self.status.value

        is_builtin = self.is_builtin

        consecutive_failures = self.consecutive_failures

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        args: Union[Unset, list[str]] = UNSET
        if not isinstance(self.args, Unset):
            args = self.args

        env: Union[None, Unset, dict[str, Any]]
        if isinstance(self.env, Unset):
            env = UNSET
        elif isinstance(self.env, ToolServerResponseEnvType0):
            env = self.env.to_dict()
        else:
            env = self.env

        auto_start = self.auto_start

        auto_update = self.auto_update

        max_failures = self.max_failures

        last_health_check: Union[None, Unset, str]
        if isinstance(self.last_health_check, Unset):
            last_health_check = UNSET
        elif isinstance(self.last_health_check, datetime.datetime):
            last_health_check = self.last_health_check.isoformat()
        else:
            last_health_check = self.last_health_check

        last_startup_success: Union[None, Unset, str]
        if isinstance(self.last_startup_success, Unset):
            last_startup_success = UNSET
        elif isinstance(self.last_startup_success, datetime.datetime):
            last_startup_success = self.last_startup_success.isoformat()
        else:
            last_startup_success = self.last_startup_success

        last_startup_error: Union[None, Unset, str]
        if isinstance(self.last_startup_error, Unset):
            last_startup_error = UNSET
        else:
            last_startup_error = self.last_startup_error

        created_by: Union[None, Unset, str]
        if isinstance(self.created_by, Unset):
            created_by = UNSET
        else:
            created_by = self.created_by

        tools: Union[Unset, list[dict[str, Any]]] = UNSET
        if not isinstance(self.tools, Unset):
            tools = []
            for tools_item_data in self.tools:
                tools_item = tools_item_data.to_dict()
                tools.append(tools_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "command": command,
                "id": id,
                "status": status,
                "is_builtin": is_builtin,
                "consecutive_failures": consecutive_failures,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if args is not UNSET:
            field_dict["args"] = args
        if env is not UNSET:
            field_dict["env"] = env
        if auto_start is not UNSET:
            field_dict["auto_start"] = auto_start
        if auto_update is not UNSET:
            field_dict["auto_update"] = auto_update
        if max_failures is not UNSET:
            field_dict["max_failures"] = max_failures
        if last_health_check is not UNSET:
            field_dict["last_health_check"] = last_health_check
        if last_startup_success is not UNSET:
            field_dict["last_startup_success"] = last_startup_success
        if last_startup_error is not UNSET:
            field_dict["last_startup_error"] = last_startup_error
        if created_by is not UNSET:
            field_dict["created_by"] = created_by
        if tools is not UNSET:
            field_dict["tools"] = tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_tool_response import ServerToolResponse
        from ..models.tool_server_response_env_type_0 import ToolServerResponseEnvType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        command = d.pop("command")

        id = d.pop("id")

        status = ServerStatus(d.pop("status"))

        is_builtin = d.pop("is_builtin")

        consecutive_failures = d.pop("consecutive_failures")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        args = cast(list[str], d.pop("args", UNSET))

        def _parse_env(data: object) -> Union["ToolServerResponseEnvType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                env_type_0 = ToolServerResponseEnvType0.from_dict(data)

                return env_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ToolServerResponseEnvType0", None, Unset], data)

        env = _parse_env(d.pop("env", UNSET))

        auto_start = d.pop("auto_start", UNSET)

        auto_update = d.pop("auto_update", UNSET)

        max_failures = d.pop("max_failures", UNSET)

        def _parse_last_health_check(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_health_check_type_0 = isoparse(data)

                return last_health_check_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_health_check = _parse_last_health_check(d.pop("last_health_check", UNSET))

        def _parse_last_startup_success(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_startup_success_type_0 = isoparse(data)

                return last_startup_success_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_startup_success = _parse_last_startup_success(d.pop("last_startup_success", UNSET))

        def _parse_last_startup_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_startup_error = _parse_last_startup_error(d.pop("last_startup_error", UNSET))

        def _parse_created_by(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        created_by = _parse_created_by(d.pop("created_by", UNSET))

        tools = []
        _tools = d.pop("tools", UNSET)
        for tools_item_data in _tools or []:
            tools_item = ServerToolResponse.from_dict(tools_item_data)

            tools.append(tools_item)

        tool_server_response = cls(
            name=name,
            display_name=display_name,
            command=command,
            id=id,
            status=status,
            is_builtin=is_builtin,
            consecutive_failures=consecutive_failures,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            args=args,
            env=env,
            auto_start=auto_start,
            auto_update=auto_update,
            max_failures=max_failures,
            last_health_check=last_health_check,
            last_startup_success=last_startup_success,
            last_startup_error=last_startup_error,
            created_by=created_by,
            tools=tools,
        )

        tool_server_response.additional_properties = d
        return tool_server_response

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
