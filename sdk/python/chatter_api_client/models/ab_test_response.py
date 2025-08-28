import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.metric_type import MetricType
from ..models.test_status import TestStatus
from ..models.test_type import TestType
from ..models.variant_allocation import VariantAllocation
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ab_test_response_metadata import ABTestResponseMetadata
    from ..models.ab_test_response_target_audience_type_0 import ABTestResponseTargetAudienceType0
    from ..models.test_variant import TestVariant


T = TypeVar("T", bound="ABTestResponse")


@_attrs_define
class ABTestResponse:
    """Response schema for A/B test data.

    Attributes:
        id (str): Test ID
        name (str): Test name
        description (str): Test description
        test_type (TestType): Types of A/B tests.
        status (TestStatus): A/B test status.
        allocation_strategy (VariantAllocation): Variant allocation strategies.
        variants (list['TestVariant']): Test variants
        metrics (list[MetricType]): Metrics being tracked
        duration_days (int): Test duration in days
        min_sample_size (int): Minimum sample size
        confidence_level (float): Statistical confidence level
        traffic_percentage (float): Percentage of traffic included
        created_at (datetime.datetime): Creation timestamp
        updated_at (datetime.datetime): Last update timestamp
        created_by (str): Creator
        tags (list[str]): Test tags
        metadata (ABTestResponseMetadata): Additional metadata
        target_audience (Union['ABTestResponseTargetAudienceType0', None, Unset]): Target audience criteria
        start_date (Union[None, Unset, datetime.datetime]): Test start date
        end_date (Union[None, Unset, datetime.datetime]): Test end date
        participant_count (Union[Unset, int]): Number of participants Default: 0.
    """

    id: str
    name: str
    description: str
    test_type: TestType
    status: TestStatus
    allocation_strategy: VariantAllocation
    variants: list["TestVariant"]
    metrics: list[MetricType]
    duration_days: int
    min_sample_size: int
    confidence_level: float
    traffic_percentage: float
    created_at: datetime.datetime
    updated_at: datetime.datetime
    created_by: str
    tags: list[str]
    metadata: "ABTestResponseMetadata"
    target_audience: Union["ABTestResponseTargetAudienceType0", None, Unset] = UNSET
    start_date: Union[None, Unset, datetime.datetime] = UNSET
    end_date: Union[None, Unset, datetime.datetime] = UNSET
    participant_count: Union[Unset, int] = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ab_test_response_target_audience_type_0 import ABTestResponseTargetAudienceType0

        id = self.id

        name = self.name

        description = self.description

        test_type = self.test_type.value

        status = self.status.value

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

        traffic_percentage = self.traffic_percentage

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        created_by = self.created_by

        tags = self.tags

        metadata = self.metadata.to_dict()

        target_audience: Union[None, Unset, dict[str, Any]]
        if isinstance(self.target_audience, Unset):
            target_audience = UNSET
        elif isinstance(self.target_audience, ABTestResponseTargetAudienceType0):
            target_audience = self.target_audience.to_dict()
        else:
            target_audience = self.target_audience

        start_date: Union[None, Unset, str]
        if isinstance(self.start_date, Unset):
            start_date = UNSET
        elif isinstance(self.start_date, datetime.datetime):
            start_date = self.start_date.isoformat()
        else:
            start_date = self.start_date

        end_date: Union[None, Unset, str]
        if isinstance(self.end_date, Unset):
            end_date = UNSET
        elif isinstance(self.end_date, datetime.datetime):
            end_date = self.end_date.isoformat()
        else:
            end_date = self.end_date

        participant_count = self.participant_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "description": description,
                "test_type": test_type,
                "status": status,
                "allocation_strategy": allocation_strategy,
                "variants": variants,
                "metrics": metrics,
                "duration_days": duration_days,
                "min_sample_size": min_sample_size,
                "confidence_level": confidence_level,
                "traffic_percentage": traffic_percentage,
                "created_at": created_at,
                "updated_at": updated_at,
                "created_by": created_by,
                "tags": tags,
                "metadata": metadata,
            }
        )
        if target_audience is not UNSET:
            field_dict["target_audience"] = target_audience
        if start_date is not UNSET:
            field_dict["start_date"] = start_date
        if end_date is not UNSET:
            field_dict["end_date"] = end_date
        if participant_count is not UNSET:
            field_dict["participant_count"] = participant_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ab_test_response_metadata import ABTestResponseMetadata
        from ..models.ab_test_response_target_audience_type_0 import ABTestResponseTargetAudienceType0
        from ..models.test_variant import TestVariant

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        description = d.pop("description")

        test_type = TestType(d.pop("test_type"))

        status = TestStatus(d.pop("status"))

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

        duration_days = d.pop("duration_days")

        min_sample_size = d.pop("min_sample_size")

        confidence_level = d.pop("confidence_level")

        traffic_percentage = d.pop("traffic_percentage")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        created_by = d.pop("created_by")

        tags = cast(list[str], d.pop("tags"))

        metadata = ABTestResponseMetadata.from_dict(d.pop("metadata"))

        def _parse_target_audience(data: object) -> Union["ABTestResponseTargetAudienceType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                target_audience_type_0 = ABTestResponseTargetAudienceType0.from_dict(data)

                return target_audience_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ABTestResponseTargetAudienceType0", None, Unset], data)

        target_audience = _parse_target_audience(d.pop("target_audience", UNSET))

        def _parse_start_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                start_date_type_0 = isoparse(data)

                return start_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        start_date = _parse_start_date(d.pop("start_date", UNSET))

        def _parse_end_date(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                end_date_type_0 = isoparse(data)

                return end_date_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        end_date = _parse_end_date(d.pop("end_date", UNSET))

        participant_count = d.pop("participant_count", UNSET)

        ab_test_response = cls(
            id=id,
            name=name,
            description=description,
            test_type=test_type,
            status=status,
            allocation_strategy=allocation_strategy,
            variants=variants,
            metrics=metrics,
            duration_days=duration_days,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            traffic_percentage=traffic_percentage,
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            tags=tags,
            metadata=metadata,
            target_audience=target_audience,
            start_date=start_date,
            end_date=end_date,
            participant_count=participant_count,
        )

        ab_test_response.additional_properties = d
        return ab_test_response

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
