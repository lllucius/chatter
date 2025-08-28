from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_test_request_variables import PromptTestRequestVariables


T = TypeVar("T", bound="PromptTestRequest")


@_attrs_define
class PromptTestRequest:
    """Schema for prompt test request.

    Attributes:
        variables (PromptTestRequestVariables): Variables to test with
        validate_only (Union[Unset, bool]): Only validate, don't render Default: False.
    """

    variables: "PromptTestRequestVariables"
    validate_only: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        variables = self.variables.to_dict()

        validate_only = self.validate_only

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "variables": variables,
            }
        )
        if validate_only is not UNSET:
            field_dict["validate_only"] = validate_only

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_test_request_variables import PromptTestRequestVariables

        d = dict(src_dict)
        variables = PromptTestRequestVariables.from_dict(d.pop("variables"))

        validate_only = d.pop("validate_only", UNSET)

        prompt_test_request = cls(
            variables=variables,
            validate_only=validate_only,
        )

        prompt_test_request.additional_properties = d
        return prompt_test_request

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
