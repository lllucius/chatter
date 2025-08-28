from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_def_update_default_config_type_0 import ModelDefUpdateDefaultConfigType0


T = TypeVar("T", bound="ModelDefUpdate")


@_attrs_define
class ModelDefUpdate:
    """Schema for updating a model definition.

    Attributes:
        display_name (Union[None, Unset, str]):
        description (Union[None, Unset, str]):
        model_name (Union[None, Unset, str]):
        max_tokens (Union[None, Unset, int]):
        context_length (Union[None, Unset, int]):
        dimensions (Union[None, Unset, int]):
        chunk_size (Union[None, Unset, int]):
        supports_batch (Union[None, Unset, bool]):
        max_batch_size (Union[None, Unset, int]):
        default_config (Union['ModelDefUpdateDefaultConfigType0', None, Unset]):
        is_active (Union[None, Unset, bool]):
        is_default (Union[None, Unset, bool]):
    """

    display_name: Union[None, Unset, str] = UNSET
    description: Union[None, Unset, str] = UNSET
    model_name: Union[None, Unset, str] = UNSET
    max_tokens: Union[None, Unset, int] = UNSET
    context_length: Union[None, Unset, int] = UNSET
    dimensions: Union[None, Unset, int] = UNSET
    chunk_size: Union[None, Unset, int] = UNSET
    supports_batch: Union[None, Unset, bool] = UNSET
    max_batch_size: Union[None, Unset, int] = UNSET
    default_config: Union["ModelDefUpdateDefaultConfigType0", None, Unset] = UNSET
    is_active: Union[None, Unset, bool] = UNSET
    is_default: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_def_update_default_config_type_0 import ModelDefUpdateDefaultConfigType0

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

        model_name: Union[None, Unset, str]
        if isinstance(self.model_name, Unset):
            model_name = UNSET
        else:
            model_name = self.model_name

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

        supports_batch: Union[None, Unset, bool]
        if isinstance(self.supports_batch, Unset):
            supports_batch = UNSET
        else:
            supports_batch = self.supports_batch

        max_batch_size: Union[None, Unset, int]
        if isinstance(self.max_batch_size, Unset):
            max_batch_size = UNSET
        else:
            max_batch_size = self.max_batch_size

        default_config: Union[None, Unset, dict[str, Any]]
        if isinstance(self.default_config, Unset):
            default_config = UNSET
        elif isinstance(self.default_config, ModelDefUpdateDefaultConfigType0):
            default_config = self.default_config.to_dict()
        else:
            default_config = self.default_config

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
        if model_name is not UNSET:
            field_dict["model_name"] = model_name
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
        from ..models.model_def_update_default_config_type_0 import ModelDefUpdateDefaultConfigType0

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

        def _parse_model_name(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        model_name = _parse_model_name(d.pop("model_name", UNSET))

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

        def _parse_supports_batch(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        supports_batch = _parse_supports_batch(d.pop("supports_batch", UNSET))

        def _parse_max_batch_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        max_batch_size = _parse_max_batch_size(d.pop("max_batch_size", UNSET))

        def _parse_default_config(data: object) -> Union["ModelDefUpdateDefaultConfigType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                default_config_type_0 = ModelDefUpdateDefaultConfigType0.from_dict(data)

                return default_config_type_0
            except:  # noqa: E722
                pass
            return cast(Union["ModelDefUpdateDefaultConfigType0", None, Unset], data)

        default_config = _parse_default_config(d.pop("default_config", UNSET))

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

        model_def_update = cls(
            display_name=display_name,
            description=description,
            model_name=model_name,
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

        model_def_update.additional_properties = d
        return model_def_update

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
