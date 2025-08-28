import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.tool_status import ToolStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.server_tool_response_args_schema_type_0 import ServerToolResponseArgsSchemaType0


T = TypeVar("T", bound="ServerToolResponse")


@_attrs_define
class ServerToolResponse:
    """Schema for server tool response.

    Attributes:
        name (str): Tool name
        display_name (str): Display name
        id (str): Tool ID
        server_id (str): Server ID
        status (ToolStatus): Enumeration for tool status.
        is_available (bool): Tool availability
        total_calls (int): Total number of calls
        total_errors (int): Total number of errors
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        description (Union[None, Unset, str]): Tool description
        args_schema (Union['ServerToolResponseArgsSchemaType0', None, Unset]): Tool arguments schema
        bypass_when_unavailable (Union[Unset, bool]): Bypass when tool is unavailable Default: False.
        last_called (Union[None, Unset, datetime.datetime]): Last call timestamp
        last_error (Union[None, Unset, str]): Last error message
        avg_response_time_ms (Union[None, Unset, float]): Average response time
    """

    name: str
    display_name: str
    id: str
    server_id: str
    status: ToolStatus
    is_available: bool
    total_calls: int
    total_errors: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    description: Union[None, Unset, str] = UNSET
    args_schema: Union["ServerToolResponseArgsSchemaType0", None, Unset] = UNSET
    bypass_when_unavailable: Union[Unset, bool] = False
    last_called: Union[None, Unset, datetime.datetime] = UNSET
    last_error: Union[None, Unset, str] = UNSET
    avg_response_time_ms: Union[None, Unset, float] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.server_tool_response_args_schema_type_0 import ServerToolResponseArgsSchemaType0

        name = self.name

        display_name = self.display_name

        id = self.id

        server_id = self.server_id

        status = self.status.value

        is_available = self.is_available

        total_calls = self.total_calls

        total_errors = self.total_errors

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        args_schema: Union[None, Unset, dict[str, Any]]
        if isinstance(self.args_schema, Unset):
            args_schema = UNSET
        elif isinstance(self.args_schema, ServerToolResponseArgsSchemaType0):
            args_schema = self.args_schema.to_dict()
        else:
            args_schema = self.args_schema

        bypass_when_unavailable = self.bypass_when_unavailable

        last_called: Union[None, Unset, str]
        if isinstance(self.last_called, Unset):
            last_called = UNSET
        elif isinstance(self.last_called, datetime.datetime):
            last_called = self.last_called.isoformat()
        else:
            last_called = self.last_called

        last_error: Union[None, Unset, str]
        if isinstance(self.last_error, Unset):
            last_error = UNSET
        else:
            last_error = self.last_error

        avg_response_time_ms: Union[None, Unset, float]
        if isinstance(self.avg_response_time_ms, Unset):
            avg_response_time_ms = UNSET
        else:
            avg_response_time_ms = self.avg_response_time_ms

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "id": id,
                "server_id": server_id,
                "status": status,
                "is_available": is_available,
                "total_calls": total_calls,
                "total_errors": total_errors,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if args_schema is not UNSET:
            field_dict["args_schema"] = args_schema
        if bypass_when_unavailable is not UNSET:
            field_dict["bypass_when_unavailable"] = bypass_when_unavailable
        if last_called is not UNSET:
            field_dict["last_called"] = last_called
        if last_error is not UNSET:
            field_dict["last_error"] = last_error
        if avg_response_time_ms is not UNSET:
            field_dict["avg_response_time_ms"] = avg_response_time_ms

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.server_tool_response_args_schema_type_0 import ServerToolResponseArgsSchemaType0

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        id = d.pop("id")

        server_id = d.pop("server_id")

        status = ToolStatus(d.pop("status"))

        is_available = d.pop("is_available")

        total_calls = d.pop("total_calls")

        total_errors = d.pop("total_errors")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_args_schema(data: object) -> Union["ServerToolResponseArgsSchemaType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                args_schema_type_0 = ServerToolResponseArgsSchemaType0.from_dict(data)

                return args_schema_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ServerToolResponseArgsSchemaType0", None, Unset], data)

        args_schema = _parse_args_schema(d.pop("args_schema", UNSET))

        bypass_when_unavailable = d.pop("bypass_when_unavailable", UNSET)

        def _parse_last_called(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                last_called_type_0 = isoparse(data)

                return last_called_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        last_called = _parse_last_called(d.pop("last_called", UNSET))

        def _parse_last_error(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        last_error = _parse_last_error(d.pop("last_error", UNSET))

        def _parse_avg_response_time_ms(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        avg_response_time_ms = _parse_avg_response_time_ms(d.pop("avg_response_time_ms", UNSET))

        server_tool_response = cls(
            name=name,
            display_name=display_name,
            id=id,
            server_id=server_id,
            status=status,
            is_available=is_available,
            total_calls=total_calls,
            total_errors=total_errors,
            created_at=created_at,
            updated_at=updated_at,
            description=description,
            args_schema=args_schema,
            bypass_when_unavailable=bypass_when_unavailable,
            last_called=last_called,
            last_error=last_error,
            avg_response_time_ms=avg_response_time_ms,
        )

        server_tool_response.additional_properties = d
        return server_tool_response

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
