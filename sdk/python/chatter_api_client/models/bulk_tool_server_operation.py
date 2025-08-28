from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bulk_tool_server_operation_parameters_type_0 import BulkToolServerOperationParametersType0


T = TypeVar("T", bound="BulkToolServerOperation")


@_attrs_define
class BulkToolServerOperation:
    """Schema for bulk operations on tool servers.

    Attributes:
        server_ids (list[str]): List of server IDs
        operation (str): Operation to perform
        parameters (Union['BulkToolServerOperationParametersType0', None, Unset]): Operation parameters
    """

    server_ids: list[str]
    operation: str
    parameters: Union["BulkToolServerOperationParametersType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.bulk_tool_server_operation_parameters_type_0 import BulkToolServerOperationParametersType0

        server_ids = self.server_ids

        operation = self.operation

        parameters: Union[None, Unset, dict[str, Any]]
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, BulkToolServerOperationParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "server_ids": server_ids,
                "operation": operation,
            }
        )
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bulk_tool_server_operation_parameters_type_0 import BulkToolServerOperationParametersType0

        d = dict(src_dict)
        server_ids = cast(list[str], d.pop("server_ids"))

        operation = d.pop("operation")

        def _parse_parameters(data: object) -> Union["BulkToolServerOperationParametersType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = BulkToolServerOperationParametersType0.from_dict(data)

                return parameters_type_0
            except:  # noqa: E722
                pass
            return cast(Union["BulkToolServerOperationParametersType0", None, Unset], data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))

        bulk_tool_server_operation = cls(
            server_ids=server_ids,
            operation=operation,
            parameters=parameters,
        )

        bulk_tool_server_operation.additional_properties = d
        return bulk_tool_server_operation

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
