from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.ab_test_response import ABTestResponse


T = TypeVar("T", bound="ABTestListResponse")


@_attrs_define
class ABTestListResponse:
    """Response schema for A/B test list.

    Attributes:
        tests (list['ABTestResponse']): List of tests
        total (int): Total number of tests
    """

    tests: list["ABTestResponse"]
    total: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tests = []
        for tests_item_data in self.tests:
            tests_item = tests_item_data.to_dict()
            tests.append(tests_item)

        total = self.total

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tests": tests,
                "total": total,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ab_test_response import ABTestResponse

        d = dict(src_dict)
        tests = []
        _tests = d.pop("tests")
        for tests_item_data in _tests:
            tests_item = ABTestResponse.from_dict(tests_item_data)

            tests.append(tests_item)

        total = d.pop("total")

        ab_test_list_response = cls(
            tests=tests,
            total=total,
        )

        ab_test_list_response.additional_properties = d
        return ab_test_list_response

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
