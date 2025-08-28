from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_server_create_env_type_0 import ToolServerCreateEnvType0


T = TypeVar("T", bound="ToolServerCreate")


@_attrs_define
class ToolServerCreate:
    """Schema for creating a tool server.

    Attributes:
        name (str): Server name
        display_name (str): Display name
        command (str): Command to start server
        description (Union[None, Unset, str]): Server description
        args (Union[Unset, list[str]]): Command arguments
        env (Union['ToolServerCreateEnvType0', None, Unset]): Environment variables
        auto_start (Union[Unset, bool]): Auto-start server on system startup Default: True.
        auto_update (Union[Unset, bool]): Auto-update server capabilities Default: True.
        max_failures (Union[Unset, int]): Maximum consecutive failures before disabling Default: 3.
    """

    name: str
    display_name: str
    command: str
    description: Union[None, Unset, str] = UNSET
    args: Union[Unset, list[str]] = UNSET
    env: Union["ToolServerCreateEnvType0", None, Unset] = UNSET
    auto_start: Union[Unset, bool] = True
    auto_update: Union[Unset, bool] = True
    max_failures: Union[Unset, int] = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.tool_server_create_env_type_0 import ToolServerCreateEnvType0

        name = self.name

        display_name = self.display_name

        command = self.command

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
        elif isinstance(self.env, ToolServerCreateEnvType0):
            env = self.env.to_dict()
        else:
            env = self.env

        auto_start = self.auto_start

        auto_update = self.auto_update

        max_failures = self.max_failures

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "command": command,
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_server_create_env_type_0 import ToolServerCreateEnvType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        command = d.pop("command")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        args = cast(list[str], d.pop("args", UNSET))

        def _parse_env(data: object) -> Union["ToolServerCreateEnvType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                env_type_0 = ToolServerCreateEnvType0.from_dict(data)

                return env_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ToolServerCreateEnvType0", None, Unset], data)

        env = _parse_env(d.pop("env", UNSET))

        auto_start = d.pop("auto_start", UNSET)

        auto_update = d.pop("auto_update", UNSET)

        max_failures = d.pop("max_failures", UNSET)

        tool_server_create = cls(
            name=name,
            display_name=display_name,
            command=command,
            description=description,
            args=args,
            env=env,
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
