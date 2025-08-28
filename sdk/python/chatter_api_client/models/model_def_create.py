from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.model_type import ModelType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_def_create_default_config import ModelDefCreateDefaultConfig


T = TypeVar("T", bound="ModelDefCreate")


@_attrs_define
class ModelDefCreate:
    """Schema for creating a model definition.

    Attributes:
        name (str): Model name
        model_type (ModelType): Types of AI models.
        display_name (str): Human-readable name
        model_name (str): Actual model name for API calls
        provider_id (str): Provider ID
        description (Union[None, Unset, str]): Model description
        max_tokens (Union[None, Unset, int]): Maximum tokens
        context_length (Union[None, Unset, int]): Context length
        dimensions (Union[None, Unset, int]): Embedding dimensions
        chunk_size (Union[None, Unset, int]): Default chunk size
        supports_batch (Union[Unset, bool]): Supports batch processing Default: True.
        max_batch_size (Union[None, Unset, int]): Maximum batch size
        default_config (Union[Unset, ModelDefCreateDefaultConfig]): Default configuration
        is_active (Union[Unset, bool]): Whether model is active Default: True.
        is_default (Union[Unset, bool]): Whether this is the default model Default: False.
    """

    name: str
    model_type: ModelType
    display_name: str
    model_name: str
    provider_id: str
    description: Union[None, Unset, str] = UNSET
    max_tokens: Union[None, Unset, int] = UNSET
    context_length: Union[None, Unset, int] = UNSET
    dimensions: Union[None, Unset, int] = UNSET
    chunk_size: Union[None, Unset, int] = UNSET
    supports_batch: Union[Unset, bool] = True
    max_batch_size: Union[None, Unset, int] = UNSET
    default_config: Union[Unset, "ModelDefCreateDefaultConfig"] = UNSET
    is_active: Union[Unset, bool] = True
    is_default: Union[Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        model_type = self.model_type.value

        display_name = self.display_name

        model_name = self.model_name

        provider_id = self.provider_id

        description: Union[None, Unset, str]
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        max_tokens: Union[None, Unset, int]
        if isinstance(self.max_tokens, Unset):
            max_tokens = UNSET
        else:
            max_tokens = self.max_tokens

        context_length: Union[None, Unset, int]
        if isinstance(self.context_length, Unset):
            context_length = UNSET
        else:
            context_length = self.context_length

        dimensions: Union[None, Unset, int]
        if isinstance(self.dimensions, Unset):
            dimensions = UNSET
        else:
            dimensions = self.dimensions

        chunk_size: Union[None, Unset, int]
        if isinstance(self.chunk_size, Unset):
            chunk_size = UNSET
        else:
            chunk_size = self.chunk_size

        supports_batch = self.supports_batch

        max_batch_size: Union[None, Unset, int]
        if isinstance(self.max_batch_size, Unset):
            max_batch_size = UNSET
        else:
            max_batch_size = self.max_batch_size

        default_config: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.default_config, Unset):
            default_config = self.default_config.to_dict()

        is_active = self.is_active

        is_default = self.is_default

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "model_type": model_type,
                "display_name": display_name,
                "model_name": model_name,
                "provider_id": provider_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if max_tokens is not UNSET:
            field_dict["max_tokens"] = max_tokens
        if context_length is not UNSET:
            field_dict["context_length"] = context_length
        if dimensions is not UNSET:
            field_dict["dimensions"] = dimensions
        if chunk_size is not UNSET:
            field_dict["chunk_size"] = chunk_size
        if supports_batch is not UNSET:
            field_dict["supports_batch"] = supports_batch
        if max_batch_size is not UNSET:
            field_dict["max_batch_size"] = max_batch_size
        if default_config is not UNSET:
            field_dict["default_config"] = default_config
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if is_default is not UNSET:
            field_dict["is_default"] = is_default

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_def_create_default_config import ModelDefCreateDefaultConfig

        d = dict(src_dict)
        name = d.pop("name")

        model_type = ModelType(d.pop("model_type"))

        display_name = d.pop("display_name")

        model_name = d.pop("model_name")

        provider_id = d.pop("provider_id")

        def _parse_description(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_max_tokens(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_tokens = _parse_max_tokens(d.pop("max_tokens", UNSET))

        def _parse_context_length(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        context_length = _parse_context_length(d.pop("context_length", UNSET))

        def _parse_dimensions(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        dimensions = _parse_dimensions(d.pop("dimensions", UNSET))

        def _parse_chunk_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        chunk_size = _parse_chunk_size(d.pop("chunk_size", UNSET))

        supports_batch = d.pop("supports_batch", UNSET)

        def _parse_max_batch_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_batch_size = _parse_max_batch_size(d.pop("max_batch_size", UNSET))

        _default_config = d.pop("default_config", UNSET)
        default_config: Union[Unset, ModelDefCreateDefaultConfig]
        if isinstance(_default_config, Unset):
            default_config = UNSET
        else:
            default_config = ModelDefCreateDefaultConfig.from_dict(_default_config)

        is_active = d.pop("is_active", UNSET)

        is_default = d.pop("is_default", UNSET)

        model_def_create = cls(
            name=name,
            model_type=model_type,
            display_name=display_name,
            model_name=model_name,
            provider_id=provider_id,
            description=description,
            max_tokens=max_tokens,
            context_length=context_length,
            dimensions=dimensions,
            chunk_size=chunk_size,
            supports_batch=supports_batch,
            max_batch_size=max_batch_size,
            default_config=default_config,
            is_active=is_active,
            is_default=is_default,
        )

        model_def_create.additional_properties = d
        return model_def_create

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
