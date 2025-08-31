from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.workflow_templates_response_templates import WorkflowTemplatesResponseTemplates


T = TypeVar("T", bound="WorkflowTemplatesResponse")


@_attrs_define
class WorkflowTemplatesResponse:
    """Schema for workflow templates response.

    Attributes:
        templates (WorkflowTemplatesResponseTemplates): Available templates
        total_count (int): Total number of templates
    """

    templates: "WorkflowTemplatesResponseTemplates"
    total_count: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        templates = self.templates.to_dict()

        total_count = self.total_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "templates": templates,
                "total_count": total_count,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.workflow_templates_response_templates import WorkflowTemplatesResponseTemplates

        d = dict(src_dict)
        templates = WorkflowTemplatesResponseTemplates.from_dict(d.pop("templates"))

        total_count = d.pop("total_count")

        workflow_templates_response = cls(
            templates=templates,
            total_count=total_count,
        )

        workflow_templates_response.additional_properties = d
        return workflow_templates_response

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
