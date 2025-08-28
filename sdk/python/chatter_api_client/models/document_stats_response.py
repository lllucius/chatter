from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_stats_response_documents_by_status import DocumentStatsResponseDocumentsByStatus
    from ..models.document_stats_response_documents_by_type import DocumentStatsResponseDocumentsByType
    from ..models.document_stats_response_processing_stats import DocumentStatsResponseProcessingStats


T = TypeVar("T", bound="DocumentStatsResponse")


@_attrs_define
class DocumentStatsResponse:
    """Schema for document statistics response.

    Attributes:
        total_documents (int): Total number of documents
        total_chunks (int): Total number of chunks
        total_size_bytes (int): Total size in bytes
        documents_by_status (DocumentStatsResponseDocumentsByStatus): Documents grouped by status
        documents_by_type (DocumentStatsResponseDocumentsByType): Documents grouped by type
        processing_stats (DocumentStatsResponseProcessingStats): Processing statistics
    """

    total_documents: int
    total_chunks: int
    total_size_bytes: int
    documents_by_status: "DocumentStatsResponseDocumentsByStatus"
    documents_by_type: "DocumentStatsResponseDocumentsByType"
    processing_stats: "DocumentStatsResponseProcessingStats"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_documents = self.total_documents

        total_chunks = self.total_chunks

        total_size_bytes = self.total_size_bytes

        documents_by_status = self.documents_by_status.to_dict()

        documents_by_type = self.documents_by_type.to_dict()

        processing_stats = self.processing_stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_documents": total_documents,
                "total_chunks": total_chunks,
                "total_size_bytes": total_size_bytes,
                "documents_by_status": documents_by_status,
                "documents_by_type": documents_by_type,
                "processing_stats": processing_stats,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_stats_response_documents_by_status import DocumentStatsResponseDocumentsByStatus
        from ..models.document_stats_response_documents_by_type import DocumentStatsResponseDocumentsByType
        from ..models.document_stats_response_processing_stats import DocumentStatsResponseProcessingStats

        d = dict(src_dict)
        total_documents = d.pop("total_documents")

        total_chunks = d.pop("total_chunks")

        total_size_bytes = d.pop("total_size_bytes")

        documents_by_status = DocumentStatsResponseDocumentsByStatus.from_dict(d.pop("documents_by_status"))

        documents_by_type = DocumentStatsResponseDocumentsByType.from_dict(d.pop("documents_by_type"))

        processing_stats = DocumentStatsResponseProcessingStats.from_dict(d.pop("processing_stats"))

        document_stats_response = cls(
            total_documents=total_documents,
            total_chunks=total_chunks,
            total_size_bytes=total_size_bytes,
            documents_by_status=documents_by_status,
            documents_by_type=documents_by_type,
            processing_stats=processing_stats,
        )

        document_stats_response.additional_properties = d
        return document_stats_response

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
