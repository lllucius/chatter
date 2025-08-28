from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.distance_metric import DistanceMetric
from ..models.reduction_strategy import ReductionStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.embedding_space_update_index_config_type_0 import EmbeddingSpaceUpdateIndexConfigType0


T = TypeVar("T", bound="EmbeddingSpaceUpdate")


@_attrs_define
class EmbeddingSpaceUpdate:
    """Schema for updating an embedding space.

    Attributes:
        display_name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        reduction_strategy (Union[None, ReductionStrategy, Unset]):
        reducer_path (Union[None, Unset, str]):
        reducer_version (Union[None, Unset, str]):
        normalize_vectors (Union[None, Unset, bool]):
        distance_metric (Union[DistanceMetric, None, Unset]):
        index_type (Union[None, Unset, str]):
        index_config (Union['EmbeddingSpaceUpdateIndexConfigType0', None, Unset]):
        is_active (Union[None, Unset, bool]):
        is_default (Union[None, Unset, bool]):
    """

    display_name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    reduction_strategy: Union[None, ReductionStrategy, Unset] = UNSET
    reducer_path: Union[None, Unset, str] = UNSET
    reducer_version: Union[None, Unset, str] = UNSET
    normalize_vectors: Union[None, Unset, bool] = UNSET
    distance_metric: Union[DistanceMetric, None, Unset] = UNSET
    index_type: Union[None, Unset, str] = UNSET
    index_config: Union["EmbeddingSpaceUpdateIndexConfigType0", None, Unset] = UNSET
    is_active: Union[None, Unset, bool] = UNSET
    is_default: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.embedding_space_update_index_config_type_0 import EmbeddingSpaceUpdateIndexConfigType0

        display_name: Union[None, Unset, str]
        if isinstance(self.display_name, Unset):
            display_name = UNSET
        else:
            display_name = self.display_name

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        reduction_strategy: Union[None, Unset, str]
        if isinstance(self.reduction_strategy, Unset):
            reduction_strategy = UNSET
        elif isinstance(self.reduction_strategy, ReductionStrategy):
            reduction_strategy = self.reduction_strategy.value
        else:
            reduction_strategy = self.reduction_strategy

        reducer_path: Union[None, Unset, str]
        if isinstance(self.reducer_path, Unset):
            reducer_path = UNSET
        else:
            reducer_path = self.reducer_path

        reducer_version: Union[None, Unset, str]
        if isinstance(self.reducer_version, Unset):
            reducer_version = UNSET
        else:
            reducer_version = self.reducer_version

        normalize_vectors: Union[None, Unset, bool]
        if isinstance(self.normalize_vectors, Unset):
            normalize_vectors = UNSET
        else:
            normalize_vectors = self.normalize_vectors

        distance_metric: Union[None, Unset, str]
        if isinstance(self.distance_metric, Unset):
            distance_metric = UNSET
        elif isinstance(self.distance_metric, DistanceMetric):
            distance_metric = self.distance_metric.value
        else:
            distance_metric = self.distance_metric

        index_type: Union[None, Unset, str]
        if isinstance(self.index_type, Unset):
            index_type = UNSET
        else:
            index_type = self.index_type

        index_config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.index_config, Unset):
            index_config = UNSET
        elif isinstance(self.index_config, EmbeddingSpaceUpdateIndexConfigType0):
            index_config = self.index_config.to_dict()
        else:
            index_config = self.index_config

        is_active: Union[None, Unset, bool]
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        is_default: Union[None, Unset, bool]
        if isinstance(self.is_default, Unset):
            is_default = UNSET
        else:
            is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if display_name is not UNSET:
            field_dict["display_name"] = display_name
        if description is not UNSET:
            field_dict["description"] = description
        if reduction_strategy is not UNSET:
            field_dict["reduction_strategy"] = reduction_strategy
        if reducer_path is not UNSET:
            field_dict["reducer_path"] = reducer_path
        if reducer_version is not UNSET:
            field_dict["reducer_version"] = reducer_version
        if normalize_vectors is not UNSET:
            field_dict["normalize_vectors"] = normalize_vectors
        if distance_metric is not UNSET:
            field_dict["distance_metric"] = distance_metric
        if index_type is not UNSET:
            field_dict["index_type"] = index_type
        if index_config is not UNSET:
            field_dict["index_config"] = index_config
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.embedding_space_update_index_config_type_0 import EmbeddingSpaceUpdateIndexConfigType0

        d = dict(src_dict)

        def _parse_display_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        display_name = _parse_display_name(d.pop("display_name", UNSET))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_reduction_strategy(data: object) -> Union[None, ReductionStrategy, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                reduction_strategy_type_0 = ReductionStrategy(data)

                return reduction_strategy_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, ReductionStrategy, Unset], data)

        reduction_strategy = _parse_reduction_strategy(d.pop("reduction_strategy", UNSET))

        def _parse_reducer_path(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reducer_path = _parse_reducer_path(d.pop("reducer_path", UNSET))

        def _parse_reducer_version(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        reducer_version = _parse_reducer_version(d.pop("reducer_version", UNSET))

        def _parse_normalize_vectors(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        normalize_vectors = _parse_normalize_vectors(d.pop("normalize_vectors", UNSET))

        def _parse_distance_metric(data: object) -> Union[DistanceMetric, None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                distance_metric_type_0 = DistanceMetric(data)

                return distance_metric_type_0
            except:  # noqa: E722
                pass
            return cast(Union[DistanceMetric, None, Unset], data)

        distance_metric = _parse_distance_metric(d.pop("distance_metric", UNSET))

        def _parse_index_type(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        index_type = _parse_index_type(d.pop("index_type", UNSET))

        def _parse_index_config(data: object) -> Union["EmbeddingSpaceUpdateIndexConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                index_config_type_0 = EmbeddingSpaceUpdateIndexConfigType0.from_dict(data)

                return index_config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["EmbeddingSpaceUpdateIndexConfigType0", None, Unset], data)

        index_config = _parse_index_config(d.pop("index_config", UNSET))

        def _parse_is_active(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_is_default(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_default = _parse_is_default(d.pop("is_default", UNSET))

        embedding_space_update = cls(
            display_name=display_name,
            description=description,
            reduction_strategy=reduction_strategy,
            reducer_path=reducer_path,
            reducer_version=reducer_version,
            normalize_vectors=normalize_vectors,
            distance_metric=distance_metric,
            index_type=index_type,
            index_config=index_config,
            is_active=is_active,
            is_default=is_default,
        )

        embedding_space_update.additional_properties = d
        return embedding_space_update

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
