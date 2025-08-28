from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.available_tool_response_args_schema import AvailableToolResponseArgsSchema


T = TypeVar("T", bound="AvailableToolResponse")


@_attrs_define
class AvailableToolResponse:
    """Schema for individual available tool.

    Attributes:
        name (str): Tool name
        description (str): Tool description
        type_ (str): Tool type (mcp, builtin)
        args_schema (AvailableToolResponseArgsSchema): Tool arguments schema
    """

    name: str
    description: str
    type_: str
    args_schema: "AvailableToolResponseArgsSchema"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        type_ = self.type_

        args_schema = self.args_schema.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "type": type_,
                "args_schema": args_schema,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.available_tool_response_args_schema import AvailableToolResponseArgsSchema

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        type_ = d.pop("type")

        args_schema = AvailableToolResponseArgsSchema.from_dict(d.pop("args_schema"))

        available_tool_response = cls(
            name=name,
            description=description,
            type_=type_,
            args_schema=args_schema,
        )

        available_tool_response.additional_properties = d
        return available_tool_response

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
