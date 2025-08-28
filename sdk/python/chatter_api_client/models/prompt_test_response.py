from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prompt_test_response_validation_result import PromptTestResponseValidationResult


T = TypeVar("T", bound="PromptTestResponse")


@_attrs_define
class PromptTestResponse:
    """Schema for prompt test response.

    Attributes:
        validation_result (PromptTestResponseValidationResult): Validation results
        test_duration_ms (int): Test execution time
        rendered_content (Union[None, Unset, str]): Rendered prompt content
        estimated_tokens (Union[None, Unset, int]): Estimated token count
    """

    validation_result: "PromptTestResponseValidationResult"
    test_duration_ms: int
    rendered_content: Union[None, Unset, str] = UNSET
    estimated_tokens: Union[None, Unset, int] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        validation_result = self.validation_result.to_dict()

        test_duration_ms = self.test_duration_ms

        rendered_content: Union[None, Unset, str]
        if isinstance(self.rendered_content, Unset):
            rendered_content = UNSET
        else:
            rendered_content = self.rendered_content

        estimated_tokens: Union[None, Unset, int]
        if isinstance(self.estimated_tokens, Unset):
            estimated_tokens = UNSET
        else:
            estimated_tokens = self.estimated_tokens

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "validation_result": validation_result,
                "test_duration_ms": test_duration_ms,
            }
        )
        if rendered_content is not UNSET:
            field_dict["rendered_content"] = rendered_content
        if estimated_tokens is not UNSET:
            field_dict["estimated_tokens"] = estimated_tokens

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prompt_test_response_validation_result import PromptTestResponseValidationResult

        d = dict(src_dict)
        validation_result = PromptTestResponseValidationResult.from_dict(d.pop("validation_result"))

        test_duration_ms = d.pop("test_duration_ms")

        def _parse_rendered_content(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        rendered_content = _parse_rendered_content(d.pop("rendered_content", UNSET))

        def _parse_estimated_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        estimated_tokens = _parse_estimated_tokens(d.pop("estimated_tokens", UNSET))

        prompt_test_response = cls(
            validation_result=validation_result,
            test_duration_ms=test_duration_ms,
            rendered_content=rendered_content,
            estimated_tokens=estimated_tokens,
        )

        prompt_test_response.additional_properties = d
        return prompt_test_response

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
