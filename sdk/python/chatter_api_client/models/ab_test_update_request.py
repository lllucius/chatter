from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.test_status import TestStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.ab_test_update_request_metadata_type_0 import ABTestUpdateRequestMetadataType0


T = TypeVar("T", bound="ABTestUpdateRequest")


@_attrs_define
class ABTestUpdateRequest:
    """Request schema for updating an A/B test.

    Attributes:
        name (Union[None, Unset, str]): Test name
        description (Union[None, Unset, str]): Test description
        status (Union[None, TestStatus, Unset]): Test status
        duration_days (Union[None, Unset, int]): Test duration in days
        min_sample_size (Union[None, Unset, int]): Minimum sample size
        confidence_level (Union[None, Unset, float]): Statistical confidence level
        traffic_percentage (Union[None, Unset, float]): Traffic percentage
        tags (Union[None, Unset, list[str]]): Test tags
        metadata (Union['ABTestUpdateRequestMetadataType0', None, Unset]): Additional metadata
    """

    name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    status: Union[None, TestStatus, Unset] = UNSET
    duration_days: Union[None, Unset, int] = UNSET
    min_sample_size: Union[None, Unset, int] = UNSET
    confidence_level: Union[None, Unset, float] = UNSET
    traffic_percentage: Union[None, Unset, float] = UNSET
    tags: Union[None, Unset, list[str]] = UNSET
    metadata: Union["ABTestUpdateRequestMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.ab_test_update_request_metadata_type_0 import ABTestUpdateRequestMetadataType0

        name: Union[None, Unset, str]
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        status: Union[None, Unset, str]
        if isinstance(self.status, Unset):
            status = UNSET
        elif isinstance(self.status, TestStatus):
            status = self.status.value
        else:
            status = self.status

        duration_days: Union[None, Unset, int]
        if isinstance(self.duration_days, Unset):
            duration_days = UNSET
        else:
            duration_days = self.duration_days

        min_sample_size: Union[None, Unset, int]
        if isinstance(self.min_sample_size, Unset):
            min_sample_size = UNSET
        else:
            min_sample_size = self.min_sample_size

        confidence_level: Union[None, Unset, float]
        if isinstance(self.confidence_level, Unset):
            confidence_level = UNSET
        else:
            confidence_level = self.confidence_level

        traffic_percentage: Union[None, Unset, float]
        if isinstance(self.traffic_percentage, Unset):
            traffic_percentage = UNSET
        else:
            traffic_percentage = self.traffic_percentage

        tags: Union[None, Unset, list[str]]
        if isinstance(self.tags, Unset):
            tags = UNSET
        elif isinstance(self.tags, list):
            tags = self.tags

        else:
            tags = self.tags

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, ABTestUpdateRequestMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if status is not UNSET:
            field_dict["status"] = status
        if duration_days is not UNSET:
            field_dict["duration_days"] = duration_days
        if min_sample_size is not UNSET:
            field_dict["min_sample_size"] = min_sample_size
        if confidence_level is not UNSET:
            field_dict["confidence_level"] = confidence_level
        if traffic_percentage is not UNSET:
            field_dict["traffic_percentage"] = traffic_percentage
        if tags is not UNSET:
            field_dict["tags"] = tags
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.ab_test_update_request_metadata_type_0 import ABTestUpdateRequestMetadataType0

        d = dict(src_dict)

        def _parse_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_status(data: object) -> Union[None, TestStatus, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                status_type_0 = TestStatus(data)

                return status_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, TestStatus, Unset], data)

        status = _parse_status(d.pop("status", UNSET))

        def _parse_duration_days(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        duration_days = _parse_duration_days(d.pop("duration_days", UNSET))

        def _parse_min_sample_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        min_sample_size = _parse_min_sample_size(d.pop("min_sample_size", UNSET))

        def _parse_confidence_level(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        confidence_level = _parse_confidence_level(d.pop("confidence_level", UNSET))

        def _parse_traffic_percentage(data: object) -> Union[None, Unset, float]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float], data)

        traffic_percentage = _parse_traffic_percentage(d.pop("traffic_percentage", UNSET))

        def _parse_tags(data: object) -> Union[None, Unset, list[str]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                tags_type_0 = cast(list[str], data)

                return tags_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, list[str]], data)

        tags = _parse_tags(d.pop("tags", UNSET))

        def _parse_metadata(data: object) -> Union["ABTestUpdateRequestMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = ABTestUpdateRequestMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ABTestUpdateRequestMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        ab_test_update_request = cls(
            name=name,
            description=description,
            status=status,
            duration_days=duration_days,
            min_sample_size=min_sample_size,
            confidence_level=confidence_level,
            traffic_percentage=traffic_percentage,
            tags=tags,
            metadata=metadata,
        )

        ab_test_update_request.additional_properties = d
        return ab_test_update_request

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
