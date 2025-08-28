from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_chunk_response import DocumentChunkResponse


T = TypeVar("T", bound="DocumentChunksResponse")


@_attrs_define
class DocumentChunksResponse:
    """Schema for document chunks response with pagination.

    Attributes:
        chunks (list['DocumentChunkResponse']): List of document chunks
        total_count (int): Total number of chunks
        limit (int): Applied limit
        offset (int): Applied offset
    """

    chunks: list["DocumentChunkResponse"]
    total_count: int
    limit: int
    offset: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        chunks = []
        for chunks_item_data in self.chunks:
            chunks_item = chunks_item_data.to_dict()
            chunks.append(chunks_item)

        total_count = self.total_count

        limit = self.limit

        offset = self.offset

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "chunks": chunks,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_chunk_response import DocumentChunkResponse

        d = dict(src_dict)
        chunks = []
        _chunks = d.pop("chunks")
        for chunks_item_data in _chunks:
            chunks_item = DocumentChunkResponse.from_dict(chunks_item_data)

            chunks.append(chunks_item)

        total_count = d.pop("total_count")

        limit = d.pop("limit")

        offset = d.pop("offset")

        document_chunks_response = cls(
            chunks=chunks,
            total_count=total_count,
            limit=limit,
            offset=offset,
        )

        document_chunks_response.additional_properties = d
        return document_chunks_response

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
