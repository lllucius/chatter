from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DocumentProcessingRequest")


@_attrs_define
class DocumentProcessingRequest:
    """Schema for document processing request.

    Attributes:
        reprocess (Union[Unset, bool]): Force reprocessing Default: False.
        chunk_size (Union[None, Unset, int]): Override chunk size
        chunk_overlap (Union[None, Unset, int]): Override chunk overlap
        generate_embeddings (Union[Unset, bool]): Generate embeddings for chunks Default: True.
    """

    reprocess: Union[Unset, bool] = False
    chunk_size: Union[None, Unset, int] = UNSET
    chunk_overlap: Union[None, Unset, int] = UNSET
    generate_embeddings: Union[Unset, bool] = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reprocess = self.reprocess

        chunk_size: Union[None, Unset, int]
        if isinstance(self.chunk_size, Unset):
            chunk_size = UNSET
        else:
            chunk_size = self.chunk_size

        chunk_overlap: Union[None, Unset, int]
        if isinstance(self.chunk_overlap, Unset):
            chunk_overlap = UNSET
        else:
            chunk_overlap = self.chunk_overlap

        generate_embeddings = self.generate_embeddings

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reprocess is not UNSET:
            field_dict["reprocess"] = reprocess
        if chunk_size is not UNSET:
            field_dict["chunk_size"] = chunk_size
        if chunk_overlap is not UNSET:
            field_dict["chunk_overlap"] = chunk_overlap
        if generate_embeddings is not UNSET:
            field_dict["generate_embeddings"] = generate_embeddings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        reprocess = d.pop("reprocess", UNSET)

        def _parse_chunk_size(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        chunk_size = _parse_chunk_size(d.pop("chunk_size", UNSET))

        def _parse_chunk_overlap(data: object) -> Union[None, Unset, int]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, int], data)

        chunk_overlap = _parse_chunk_overlap(d.pop("chunk_overlap", UNSET))

        generate_embeddings = d.pop("generate_embeddings", UNSET)

        document_processing_request = cls(
            reprocess=reprocess,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            generate_embeddings=generate_embeddings,
        )

        document_processing_request.additional_properties = d
        return document_processing_request

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
