from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.test_status import TestStatus

T = TypeVar("T", bound="ABTestActionResponse")


@_attrs_define
class ABTestActionResponse:
    """Response schema for test actions (start, pause, complete).

    Attributes:
        success (bool): Whether action was successful
        message (str): Action result message
        test_id (str): Test ID
        new_status (TestStatus): A/B test status.
    """

    success: bool
    message: str
    test_id: str
    new_status: TestStatus
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        success = self.success

        message = self.message

        test_id = self.test_id

        new_status = self.new_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "success": success,
                "message": message,
                "test_id": test_id,
                "new_status": new_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        success = d.pop("success")

        message = d.pop("message")

        test_id = d.pop("test_id")

        new_status = TestStatus(d.pop("new_status"))

        ab_test_action_response = cls(
            success=success,
            message=message,
            test_id=test_id,
            new_status=new_status,
        )

        ab_test_action_response.additional_properties = d
        return ab_test_action_response

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
