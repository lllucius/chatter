from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.metric_type import MetricType
from ..models.test_type import TestType
from ..models.variant_allocation import VariantAllocation
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ab_test_create_request_metadata import ABTestCreateRequestMetadata
    from ..models.ab_test_create_request_target_audience_type_0 import ABTestCreateRequestTargetAudienceType0
    from ..models.test_variant import TestVariant


T = TypeVar("T", bound="ABTestCreateRequest")


@_attrs_define
class ABTestCreateRequest:
    """Request schema for creating an A/B test.

    Attributes:
        name (str): Test name
        description (str): Test description
        test_type (TestType): Types of A/B tests.
        allocation_strategy (VariantAllocation): Variant allocation strategies.
        variants (list['TestVariant']): Test variants
        metrics (list[MetricType]): Metrics to track
        duration_days (Union[Unset, int]): Test duration in days Default: 7.
        min_sample_size (Union[Unset, int]): Minimum sample size Default: 100.
        confidence_level (Union[Unset, float]): Statistical confidence level Default: 0.95.
        target_audience (Union['ABTestCreateRequestTargetAudienceType0', None, Unset]): Target audience criteria
        traffic_percentage (Union[Unset, float]): Percentage of traffic to include Default: 100.0.
        tags (Union[Unset, list[str]]): Test tags
        metadata (Union[Unset, ABTestCreateRequestMetadata]): Additional metadata
    """

    name: str
    description: str
    test_type: TestType
    allocation_strategy: VariantAllocation
    variants: list["TestVariant"]
    metrics: list[MetricType]
    duration_days: Union[Unset, int] = 7
    min_sample_size: Union[Unset, int] = 100
    confidence_level: Union[Unset, float] = 0.95
    target_audience: Union["ABTestCreateRequestTargetAudienceType0", None, Unset] = UNSET
    traffic_percentage: Union[Unset, float] = 100.0
    tags: Union[Unset, list[str]] = UNSET
    metadata: Union[Unset, "ABTestCreateRequestMetadata"] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ab_test_create_request_target_audience_type_0 import ABTestCreateRequestTargetAudienceType0

        name = self.name

        description = self.description

        test_type = self.test_type.value

        allocation_strategy = self.allocation_strategy.value

        variants = []
        for variants_item_data in self.variants:
            variants_item = variants_item_data.to_dict()
            variants.append(variants_item)

        metrics = []
        for metrics_item_data in self.metrics:
            metrics_item = metrics_item_data.value
            metrics.append(metrics_item)

        duration_days = self.duration_days

        min_sample_size = self.min_sample_size

        confidence_level = self.confidence_level

        target_audience: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_audience, Unset):
            target_audience = UNSET
        elif isinstance(self.target_audience, ABTestCreateRequestTargetAudienceType0):
            target_audience = self.target_audience.to_dict()
        else:
            target_audience = self.target_audience

        traffic_percentage = self.traffic_percentage

        tags: Union[Unset, list[str]] = UNSET
        if not isinstance(self.tags, Unset):
            tags = self.tags

        metadata: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "description": description,
                "test_type": test_type,
                "allocation_strategy": allocation_strategy,
                "variants": variants,
                "metrics": metrics,
            }
        )
        if duration_days is not UNSET:
            field_dict["duration_days"] = duration_days
        if min_sample_size is not UNSET:
            field_dict["min_sample_size"] = min_sample_size
        if confidence_level is not UNSET:
            field_dict["confidence_level"] = confidence_level
        if target_audience is not UNSET:
            field_dict["target_audience"] = target_audience
        if traffic_percentage is not UNSET:
            field_dict["traffic_percentage"] = traffic_percentage
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ab_test_create_request_metadata import ABTestCreateRequestMetadata
        from ..models.ab_test_create_request_target_audience_type_0 import ABTestCreateRequestTargetAudienceType0
        from ..models.test_variant import TestVariant

        d = dict(src_dict)
        name = d.pop("name")

        description = d.pop("description")

        test_type = TestType(d.pop("test_type"))

        allocation_strategy = VariantAllocation(d.pop("allocation_strategy"))

        variants = []
        _variants = d.pop("variants")
        for variants_item_data in _variants:
            variants_item = TestVariant.from_dict(variants_item_data)

            variants.append(variants_item)

        metrics = []
        _metrics = d.pop("metrics")
        for metrics_item_data in _metrics:
            metrics_item = MetricType(metrics_item_data)

            metrics.append(metrics_item)

        duration_days = d.pop("duration_days", UNSET)

        min_sample_size = d.pop("min_sample_size", UNSET)

        confidence_level = d.pop("confidence_level", UNSET)

        def _parse_target_audience(data: object) -> Union["ABTestCreateRequestTargetAudienceType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_audience_type_0 = ABTestCreateRequestTargetAudienceType0.from_dict(data)

                return target_audience_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ABTestCreateRequestTargetAudienceType0", None, Unset], data)

        target_audience = _parse_target_audience(d.pop("target_audience", UNSET))

        traffic_percentage = d.pop("traffic_percentage", UNSET)

        tags = cast(list[str], d.pop("tags", UNSET))

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, ABTestCreateRequestMetadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = ABTestCreateRequestMetadata.from_dict(_metadata)

        ab_test_create_request = cls(
            name=name,
            description=description,
            test_type=test_type,
            allocation_strategy=allocation_strategy,
            variants=variants,
            metrics=metrics,
            duration_days=duration_days,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            target_audience=target_audience,
            traffic_percentage=traffic_percentage,
            tags=tags,
            metadata=metadata,
        )

        ab_test_create_request.additional_properties = d
        return ab_test_create_request

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
