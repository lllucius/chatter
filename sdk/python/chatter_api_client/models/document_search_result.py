from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.document_response import DocumentResponse
    from ..models.document_search_result_metadata_type_0 import DocumentSearchResultMetadataType0


T = TypeVar("T", bound="DocumentSearchResult")


@_attrs_define
class DocumentSearchResult:
    """Schema for document search result.

    Attributes:
        document_id (str): Document ID
        chunk_id (str): Chunk ID
        score (float): Similarity score
        content (str): Matching content
        document (DocumentResponse): Schema for document response.
        metadata (Union['DocumentSearchResultMetadataType0', None, Unset]): Chunk metadata
    """

    document_id: str
    chunk_id: str
    score: float
    content: str
    document: "DocumentResponse"
    metadata: Union["DocumentSearchResultMetadataType0", None, Unset] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.document_search_result_metadata_type_0 import DocumentSearchResultMetadataType0

        document_id = self.document_id

        chunk_id = self.chunk_id

        score = self.score

        content = self.content

        document = self.document.to_dict()

        metadata: Union[None, Unset, dict[str, Any]]
        if isinstance(self.metadata, Unset):
            metadata = UNSET
        elif isinstance(self.metadata, DocumentSearchResultMetadataType0):
            metadata = self.metadata.to_dict()
        else:
            metadata = self.metadata

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "document_id": document_id,
                "chunk_id": chunk_id,
                "score": score,
                "content": content,
                "document": document,
            }
        )
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_response import DocumentResponse
        from ..models.document_search_result_metadata_type_0 import DocumentSearchResultMetadataType0

        d = dict(src_dict)
        document_id = d.pop("document_id")

        chunk_id = d.pop("chunk_id")

        score = d.pop("score")

        content = d.pop("content")

        document = DocumentResponse.from_dict(d.pop("document"))

        def _parse_metadata(data: object) -> Union["DocumentSearchResultMetadataType0", None, Unset]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metadata_type_0 = DocumentSearchResultMetadataType0.from_dict(data)

                return metadata_type_0
            except:  # noqa: E722
                pass
            return cast(Union["DocumentSearchResultMetadataType0", None, Unset], data)

        metadata = _parse_metadata(d.pop("metadata", UNSET))

        document_search_result = cls(
            document_id=document_id,
            chunk_id=chunk_id,
            score=score,
            content=content,
            document=document,
            metadata=metadata,
        )

        document_search_result.additional_properties = d
        return document_search_result

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
