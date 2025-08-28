from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ProfileTestRequest")


@_attrs_define
class ProfileTestRequest:
    """Schema for profile test request.

    Attributes:
        test_message (str): Test message
        include_retrieval (Union[Unset, bool]): Include retrieval in test Default: False.
        include_tools (Union[Unset, bool]): Include tools in test Default: False.
    """

    test_message: str
    include_retrieval: Union[Unset, bool] = False
    include_tools: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        test_message = self.test_message

        include_retrieval = self.include_retrieval

        include_tools = self.include_tools

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "test_message": test_message,
            }
        )
        if include_retrieval is not UNSET:
            field_dict["include_retrieval"] = include_retrieval
        if include_tools is not UNSET:
            field_dict["include_tools"] = include_tools

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        test_message = d.pop("test_message")

        include_retrieval = d.pop("include_retrieval", UNSET)

        include_tools = d.pop("include_tools", UNSET)

        profile_test_request = cls(
            test_message=test_message,
            include_retrieval=include_retrieval,
            include_tools=include_tools,
        )

        profile_test_request.additional_properties = d
        return profile_test_request

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
