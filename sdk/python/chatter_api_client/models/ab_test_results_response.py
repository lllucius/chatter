import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.test_status import TestStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ab_test_results_response_confidence_intervals import ABTestResultsResponseConfidenceIntervals
    from ..models.ab_test_results_response_statistical_significance import ABTestResultsResponseStatisticalSignificance
    from ..models.test_metric import TestMetric


T = TypeVar("T", bound="ABTestResultsResponse")


@_attrs_define
class ABTestResultsResponse:
    """Response schema for A/B test results.

    Attributes:
        test_id (str): Test ID
        test_name (str): Test name
        status (TestStatus): A/B test status.
        metrics (list['TestMetric']): Metric results by variant
        statistical_significance (ABTestResultsResponseStatisticalSignificance): Statistical significance by metric
        confidence_intervals (ABTestResultsResponseConfidenceIntervals): Confidence intervals
        recommendation (str): Action recommendation
        generated_at (datetime.datetime): Results generation timestamp
        sample_size (int): Total sample size
        duration_days (int): Test duration so far
        winning_variant (Union[None, Unset, str]): Recommended winning variant
    """

    test_id: str
    test_name: str
    status: TestStatus
    metrics: list["TestMetric"]
    statistical_significance: "ABTestResultsResponseStatisticalSignificance"
    confidence_intervals: "ABTestResultsResponseConfidenceIntervals"
    recommendation: str
    generated_at: datetime.datetime
    sample_size: int
    duration_days: int
    winning_variant: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        test_id = self.test_id

        test_name = self.test_name

        status = self.status.value

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        statistical_significance = self.statistical_significance.to_dict()

        confidence_intervals = self.confidence_intervals.to_dict()

        recommendation = self.recommendation

        generated_at = self.generated_at.isoformat()

        sample_size = self.sample_size

        duration_days = self.duration_days

        winning_variant: Union[None, Unset, str]
        if isinstance(self.winning_variant, Unset):
            winning_variant = UNSET
        else:
            winning_variant = self.winning_variant

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "test_id": test_id,
                "test_name": test_name,
                "status": status,
                "metrics": metrics,
                "statistical_significance": statistical_significance,
                "confidence_intervals": confidence_intervals,
                "recommendation": recommendation,
                "generated_at": generated_at,
                "sample_size": sample_size,
                "duration_days": duration_days,
            }
        )
        if winning_variant is not UNSET:
            field_dict["winning_variant"] = winning_variant

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ab_test_results_response_confidence_intervals import ABTestResultsResponseConfidenceIntervals
        from ..models.ab_test_results_response_statistical_significance import (
            ABTestResultsResponseStatisticalSignificance,
        )
        from ..models.test_metric import TestMetric

        d = dict(src_dict)
        test_id = d.pop("test_id")

        test_name = d.pop("test_name")

        status = TestStatus(d.pop("status"))

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = TestMetric.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        statistical_significance = ABTestResultsResponseStatisticalSignificance.from_dict(
            d.pop("statistical_significance")
        )

        confidence_intervals = ABTestResultsResponseConfidenceIntervals.from_dict(d.pop("confidence_intervals"))

        recommendation = d.pop("recommendation")

        generated_at = isoparse(d.pop("generated_at"))

        sample_size = d.pop("sample_size")

        duration_days = d.pop("duration_days")

        def _parse_winning_variant(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        winning_variant = _parse_winning_variant(d.pop("winning_variant", UNSET))

        ab_test_results_response = cls(
            test_id=test_id,
            test_name=test_name,
            status=status,
            metrics=metrics,
            statistical_significance=statistical_significance,
            confidence_intervals=confidence_intervals,
            recommendation=recommendation,
            generated_at=generated_at,
            sample_size=sample_size,
            duration_days=duration_days,
            winning_variant=winning_variant,
        )

        ab_test_results_response.additional_properties = d
        return ab_test_results_response

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
