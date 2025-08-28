from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentCapability")


@_attrs_define
class AgentCapability:
    """Agent capability definition.

    Attributes:
        name (str):
        description (str):
        required_tools (Union[Unset, list[str]]):
        required_models (Union[Unset, list[str]]):
        confidence_threshold (Union[Unset, float]):  Default: 0.7.
        enabled (Union[Unset, bool]):  Default: True.
    """

    name: str
    description: str
    required_tools: Union[Unset, list[str]] = UNSET
    required_models: Union[Unset, list[str]] = UNSET
    confidence_threshold: Union[Unset, float] = 0.7
    enabled: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        required_tools: Union[Unset, list[str]] = UNSET
        if not isinstance(self.required_tools, Unset):
            required_tools = self.required_tools

        required_models: Union[Unset, list[str]] = UNSET
        if not isinstance(self.required_models, Unset):
            required_models = self.required_models

        confidence_threshold = self.confidence_threshold

        enabled = self.enabled

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
            }
        )
        if required_tools is not UNSET:
            field_dict["required_tools"] = required_tools
        if required_models is not UNSET:
            field_dict["required_models"] = required_models
        if confidence_threshold is not UNSET:
            field_dict["confidence_threshold"] = confidence_threshold
        if enabled is not UNSET:
            field_dict["enabled"] = enabled

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        required_tools = cast(list[str], d.pop("required_tools", UNSET))

        required_models = cast(list[str], d.pop("required_models", UNSET))

        confidence_threshold = d.pop("confidence_threshold", UNSET)

        enabled = d.pop("enabled", UNSET)

        agent_capability = cls(
            name=name,
            description=description,
            required_tools=required_tools,
            required_models=required_models,
            confidence_threshold=confidence_threshold,
            enabled=enabled,
        )

        agent_capability.additional_properties = d
        return agent_capability

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
