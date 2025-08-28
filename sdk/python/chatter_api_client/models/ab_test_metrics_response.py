import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from ..models.test_metric import TestMetric


T = TypeVar("T", bound="ABTestMetricsResponse")


@_attrs_define
class ABTestMetricsResponse:
    """Response schema for A/B test metrics.

    Attributes:
        test_id (str): Test ID
        metrics (list['TestMetric']): Current metrics
        participant_count (int): Current participant count
        last_updated (datetime.datetime): Last metrics update
    """

    test_id: str
    metrics: list["TestMetric"]
    participant_count: int
    last_updated: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        test_id = self.test_id

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.to_dict()
            metrics.append(metrics_item)

        participant_count = self.participant_count

        last_updated = self.last_updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "test_id": test_id,
                "metrics": metrics,
                "participant_count": participant_count,
                "last_updated": last_updated,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.test_metric import TestMetric

        d = dict(src_dict)
        test_id = d.pop("test_id")

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = TestMetric.from_dict(metrics_item_data)

            metrics.append(metrics_item)

        participant_count = d.pop("participant_count")

        last_updated = isoparse(d.pop("last_updated"))

        ab_test_metrics_response = cls(
            test_id=test_id,
            metrics=metrics,
            participant_count=participant_count,
            last_updated=last_updated,
        )

        ab_test_metrics_response.additional_properties = d
        return ab_test_metrics_response

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
