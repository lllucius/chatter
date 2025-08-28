import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.distance_metric import DistanceMetric
from ..models.reduction_strategy import ReductionStrategy
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.embedding_space_with_model_index_config import EmbeddingSpaceWithModelIndexConfig
    from ..models.model_def_with_provider import ModelDefWithProvider


T = TypeVar("T", bound="EmbeddingSpaceWithModel")


@_attrs_define
class EmbeddingSpaceWithModel:
    """Embedding space with model and provider information.

    Attributes:
        name (str): Unique space name
        display_name (str): Human-readable name
        base_dimensions (int): Original model dimensions
        effective_dimensions (int): Effective dimensions after reduction
        table_name (str): Database table name
        id (str):
        model_id (str):
        created_at (datetime.datetime):
        updated_at (datetime.datetime):
        model (ModelDefWithProvider): Model definition with provider information.
        description (Union[None, Unset, str]): Space description
        reduction_strategy (Union[Unset, ReductionStrategy]): Dimensionality reduction strategies.
        reducer_path (Union[None, Unset, str]): Path to reducer file
        reducer_version (Union[None, Unset, str]): Reducer version/hash
        normalize_vectors (Union[Unset, bool]): Whether to normalize vectors Default: True.
        distance_metric (Union[Unset, DistanceMetric]): Distance metrics for vector similarity.
        index_type (Union[Unset, str]): Index type Default: 'hnsw'.
        index_config (Union[Unset, EmbeddingSpaceWithModelIndexConfig]): Index configuration
        is_active (Union[Unset, bool]): Whether space is active Default: True.
        is_default (Union[Unset, bool]): Whether this is the default space Default: False.
    """

    name: str
    display_name: str
    base_dimensions: int
    effective_dimensions: int
    table_name: str
    id: str
    model_id: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    model: "ModelDefWithProvider"
    description: Union[None, Unset, str] = UNSET
    reduction_strategy: Union[Unset, ReductionStrategy] = UNSET
    reducer_path: Union[None, Unset, str] = UNSET
    reducer_version: Union[None, Unset, str] = UNSET
    normalize_vectors: Union[Unset, bool] = True
    distance_metric: Union[Unset, DistanceMetric] = UNSET
    index_type: Union[Unset, str] = "hnsw"
    index_config: Union[Unset, "EmbeddingSpaceWithModelIndexConfig"] = UNSET
    is_active: Union[Unset, bool] = True
    is_default: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        display_name = self.display_name

        base_dimensions = self.base_dimensions

        effective_dimensions = self.effective_dimensions

        table_name = self.table_name

        id = self.id

        model_id = self.model_id

        created_at = self.created_at.isoformat()

        updated_at = self.updated_at.isoformat()

        model = self.model.to_dict()

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        reduction_strategy: Union[Unset, str] = UNSET
        if not isinstance(self.reduction_strategy, Unset):
            reduction_strategy = self.reduction_strategy.value

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

        normalize_vectors = self.normalize_vectors

        distance_metric: Union[Unset, str] = UNSET
        if not isinstance(self.distance_metric, Unset):
            distance_metric = self.distance_metric.value

        index_type = self.index_type

        index_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.index_config, Unset):
            index_config = self.index_config.to_dict()

        is_active = self.is_active

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "display_name": display_name,
                "base_dimensions": base_dimensions,
                "effective_dimensions": effective_dimensions,
                "table_name": table_name,
                "id": id,
                "model_id": model_id,
                "created_at": created_at,
                "updated_at": updated_at,
                "model": model,
            }
        )
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
        from ..models.embedding_space_with_model_index_config import EmbeddingSpaceWithModelIndexConfig
        from ..models.model_def_with_provider import ModelDefWithProvider

        d = dict(src_dict)
        name = d.pop("name")

        display_name = d.pop("display_name")

        base_dimensions = d.pop("base_dimensions")

        effective_dimensions = d.pop("effective_dimensions")

        table_name = d.pop("table_name")

        id = d.pop("id")

        model_id = d.pop("model_id")

        created_at = isoparse(d.pop("created_at"))

        updated_at = isoparse(d.pop("updated_at"))

        model = ModelDefWithProvider.from_dict(d.pop("model"))

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        _reduction_strategy = d.pop("reduction_strategy", UNSET)
        reduction_strategy: Union[Unset, ReductionStrategy]
        if isinstance(_reduction_strategy, Unset):
            reduction_strategy = UNSET
        else:
            reduction_strategy = ReductionStrategy(_reduction_strategy)

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

        normalize_vectors = d.pop("normalize_vectors", UNSET)

        _distance_metric = d.pop("distance_metric", UNSET)
        distance_metric: Union[Unset, DistanceMetric]
        if isinstance(_distance_metric, Unset):
            distance_metric = UNSET
        else:
            distance_metric = DistanceMetric(_distance_metric)

        index_type = d.pop("index_type", UNSET)

        _index_config = d.pop("index_config", UNSET)
        index_config: Union[Unset, EmbeddingSpaceWithModelIndexConfig]
        if isinstance(_index_config, Unset):
            index_config = UNSET
        else:
            index_config = EmbeddingSpaceWithModelIndexConfig.from_dict(_index_config)

        is_active = d.pop("is_active", UNSET)

        is_default = d.pop("is_default", UNSET)

        embedding_space_with_model = cls(
            name=name,
            display_name=display_name,
            base_dimensions=base_dimensions,
            effective_dimensions=effective_dimensions,
            table_name=table_name,
            id=id,
            model_id=model_id,
            created_at=created_at,
            updated_at=updated_at,
            model=model,
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

        embedding_space_with_model.additional_properties = d
        return embedding_space_with_model

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
