from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.bulk_operation_result_results_item import BulkOperationResultResultsItem


T = TypeVar("T", bound="BulkOperationResult")


@_attrs_define
class BulkOperationResult:
    """Schema for bulk operation results.

    Attributes:
        total_requested (int): Total servers requested
        successful (int): Successfully processed
        failed (int): Failed to process
        results (list['BulkOperationResultResultsItem']): Detailed results
        errors (Union[Unset, list[str]]): Error messages
    """

    total_requested: int
    successful: int
    failed: int
    results: list["BulkOperationResultResultsItem"]
    errors: Union[Unset, list[str]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_requested = self.total_requested

        successful = self.successful

        failed = self.failed

        results = []
        for results_item_data in self.results:
            results_item = results_item_data.to_dict()
            results.append(results_item)

        errors: Union[Unset, list[str]] = UNSET
        if not isinstance(self.errors, Unset):
            errors = self.errors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_requested": total_requested,
                "successful": successful,
                "failed": failed,
                "results": results,
            }
        )
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.bulk_operation_result_results_item import BulkOperationResultResultsItem

        d = dict(src_dict)
        total_requested = d.pop("total_requested")

        successful = d.pop("successful")

        failed = d.pop("failed")

        results = []
        _results = d.pop("results")
        for results_item_data in _results:
            results_item = BulkOperationResultResultsItem.from_dict(results_item_data)

            results.append(results_item)

        errors = cast(list[str], d.pop("errors", UNSET))

        bulk_operation_result = cls(
            total_requested=total_requested,
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
        )

        bulk_operation_result.additional_properties = d
        return bulk_operation_result

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
