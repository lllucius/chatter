from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="BulkDeleteResponse")


@_attrs_define
class BulkDeleteResponse:
    """Response schema for bulk delete operations.

    Attributes:
        total_requested (int): Total number of items requested for deletion
        successful_deletions (int): Number of successful deletions
        failed_deletions (int): Number of failed deletions
        errors (list[str]): List of error messages for failed deletions
    """

    total_requested: int
    successful_deletions: int
    failed_deletions: int
    errors: list[str]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_requested = self.total_requested

        successful_deletions = self.successful_deletions

        failed_deletions = self.failed_deletions

        errors = self.errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_requested": total_requested,
                "successful_deletions": successful_deletions,
                "failed_deletions": failed_deletions,
                "errors": errors,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        total_requested = d.pop("total_requested")

        successful_deletions = d.pop("successful_deletions")

        failed_deletions = d.pop("failed_deletions")

        errors = cast(list[str], d.pop("errors"))

        bulk_delete_response = cls(
            total_requested=total_requested,
            successful_deletions=successful_deletions,
            failed_deletions=failed_deletions,
            errors=errors,
        )

        bulk_delete_response.additional_properties = d
        return bulk_delete_response

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
