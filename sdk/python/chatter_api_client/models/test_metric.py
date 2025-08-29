from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.metric_type import MetricType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TestMetric")


@_attrs_define
class TestMetric:
    """Test metric data.

    Attributes:
        metric_type (MetricType): Types of metrics to track.
        variant_name (str): Variant name
        value (float): Metric value
        sample_size (int): Sample size
        confidence_interval (Union[None, Unset, list[float]]): 95% confidence interval
    """

    metric_type: MetricType
    variant_name: str
    value: float
    sample_size: int
    confidence_interval: Union[None, Unset, list[float]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        metric_type = self.metric_type.value

        variant_name = self.variant_name

        value = self.value

        sample_size = self.sample_size

        confidence_interval: Union[None, Unset, list[float]]
        if isinstance(self.confidence_interval, Unset):
            confidence_interval = UNSET
        elif isinstance(self.confidence_interval, list):
            confidence_interval = self.confidence_interval

        else:
            confidence_interval = self.confidence_interval

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "metric_type": metric_type,
                "variant_name": variant_name,
                "value": value,
                "sample_size": sample_size,
            }
        )
        if confidence_interval is not UNSET:
            field_dict["confidence_interval"] = confidence_interval

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        metric_type = MetricType(d.pop("metric_type"))

        variant_name = d.pop("variant_name")

        value = d.pop("value")

        sample_size = d.pop("sample_size")

        def _parse_confidence_interval(data: object) -> Union[None, Unset, list[float]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                confidence_interval_type_0 = cast(list[float], data)

                return confidence_interval_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[float]], data)

        confidence_interval = _parse_confidence_interval(d.pop("confidence_interval", UNSET))

        test_metric = cls(
            metric_type=metric_type,
            variant_name=variant_name,
            value=value,
            sample_size=sample_size,
            confidence_interval=confidence_interval,
        )

        test_metric.additional_properties = d
        return test_metric

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
