from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workflow_template_info_default_params import WorkflowTemplateInfoDefaultParams


T = TypeVar("T", bound="WorkflowTemplateInfo")


@_attrs_define
class WorkflowTemplateInfo:
    """Schema for workflow template information.

    Attributes:
        name (str): Template name
        workflow_type (str): Workflow type
        description (str): Template description
        required_tools (list[str]): Required tools
        required_retrievers (list[str]): Required retrievers
        default_params (WorkflowTemplateInfoDefaultParams): Default parameters
    """

    name: str
    workflow_type: str
    description: str
    required_tools: list[str]
    required_retrievers: list[str]
    default_params: "WorkflowTemplateInfoDefaultParams"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        workflow_type = self.workflow_type

        description = self.description

        required_tools = self.required_tools

        required_retrievers = self.required_retrievers

        default_params = self.default_params.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "workflow_type": workflow_type,
                "description": description,
                "required_tools": required_tools,
                "required_retrievers": required_retrievers,
                "default_params": default_params,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_template_info_default_params import WorkflowTemplateInfoDefaultParams

        d = dict(src_dict)
        name = d.pop("name")

        workflow_type = d.pop("workflow_type")

        description = d.pop("description")

        required_tools = cast(list[str], d.pop("required_tools"))

        required_retrievers = cast(list[str], d.pop("required_retrievers"))

        default_params = WorkflowTemplateInfoDefaultParams.from_dict(d.pop("default_params"))

        workflow_template_info = cls(
            name=name,
            workflow_type=workflow_type,
            description=description,
            required_tools=required_tools,
            required_retrievers=required_retrievers,
            default_params=default_params,
        )

        workflow_template_info.additional_properties = d
        return workflow_template_info

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
