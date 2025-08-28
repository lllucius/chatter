from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.document_analytics_response_documents_by_access_level import (
        DocumentAnalyticsResponseDocumentsByAccessLevel,
    )
    from ..models.document_analytics_response_documents_by_status import DocumentAnalyticsResponseDocumentsByStatus
    from ..models.document_analytics_response_documents_by_type import DocumentAnalyticsResponseDocumentsByType
    from ..models.document_analytics_response_most_viewed_documents_item import (
        DocumentAnalyticsResponseMostViewedDocumentsItem,
    )
    from ..models.document_analytics_response_popular_search_terms import DocumentAnalyticsResponsePopularSearchTerms
    from ..models.document_analytics_response_storage_by_type import DocumentAnalyticsResponseStorageByType


T = TypeVar("T", bound="DocumentAnalyticsResponse")


@_attrs_define
class DocumentAnalyticsResponse:
    """Schema for document analytics response.

    Attributes:
        total_documents (int): Total number of documents
        documents_by_status (DocumentAnalyticsResponseDocumentsByStatus): Documents by processing status
        documents_by_type (DocumentAnalyticsResponseDocumentsByType): Documents by file type
        avg_processing_time_seconds (float): Average processing time
        processing_success_rate (float): Processing success rate
        total_chunks (int): Total number of chunks
        avg_chunks_per_document (float): Average chunks per document
        total_storage_bytes (int): Total storage used
        avg_document_size_bytes (float): Average document size
        storage_by_type (DocumentAnalyticsResponseStorageByType): Storage usage by document type
        total_searches (int): Total number of searches
        avg_search_results (float): Average search results returned
        popular_search_terms (DocumentAnalyticsResponsePopularSearchTerms): Popular search terms
        total_views (int): Total document views
        most_viewed_documents (list['DocumentAnalyticsResponseMostViewedDocumentsItem']): Most viewed documents
        documents_by_access_level (DocumentAnalyticsResponseDocumentsByAccessLevel): Documents by access level
    """

    total_documents: int
    documents_by_status: "DocumentAnalyticsResponseDocumentsByStatus"
    documents_by_type: "DocumentAnalyticsResponseDocumentsByType"
    avg_processing_time_seconds: float
    processing_success_rate: float
    total_chunks: int
    avg_chunks_per_document: float
    total_storage_bytes: int
    avg_document_size_bytes: float
    storage_by_type: "DocumentAnalyticsResponseStorageByType"
    total_searches: int
    avg_search_results: float
    popular_search_terms: "DocumentAnalyticsResponsePopularSearchTerms"
    total_views: int
    most_viewed_documents: list["DocumentAnalyticsResponseMostViewedDocumentsItem"]
    documents_by_access_level: "DocumentAnalyticsResponseDocumentsByAccessLevel"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total_documents = self.total_documents

        documents_by_status = self.documents_by_status.to_dict()

        documents_by_type = self.documents_by_type.to_dict()

        avg_processing_time_seconds = self.avg_processing_time_seconds

        processing_success_rate = self.processing_success_rate

        total_chunks = self.total_chunks

        avg_chunks_per_document = self.avg_chunks_per_document

        total_storage_bytes = self.total_storage_bytes

        avg_document_size_bytes = self.avg_document_size_bytes

        storage_by_type = self.storage_by_type.to_dict()

        total_searches = self.total_searches

        avg_search_results = self.avg_search_results

        popular_search_terms = self.popular_search_terms.to_dict()

        total_views = self.total_views

        most_viewed_documents = []
        for most_viewed_documents_item_data in self.most_viewed_documents:
            most_viewed_documents_item = most_viewed_documents_item_data.to_dict()
            most_viewed_documents.append(most_viewed_documents_item)

        documents_by_access_level = self.documents_by_access_level.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "total_documents": total_documents,
                "documents_by_status": documents_by_status,
                "documents_by_type": documents_by_type,
                "avg_processing_time_seconds": avg_processing_time_seconds,
                "processing_success_rate": processing_success_rate,
                "total_chunks": total_chunks,
                "avg_chunks_per_document": avg_chunks_per_document,
                "total_storage_bytes": total_storage_bytes,
                "avg_document_size_bytes": avg_document_size_bytes,
                "storage_by_type": storage_by_type,
                "total_searches": total_searches,
                "avg_search_results": avg_search_results,
                "popular_search_terms": popular_search_terms,
                "total_views": total_views,
                "most_viewed_documents": most_viewed_documents,
                "documents_by_access_level": documents_by_access_level,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.document_analytics_response_documents_by_access_level import (
            DocumentAnalyticsResponseDocumentsByAccessLevel,
        )
        from ..models.document_analytics_response_documents_by_status import DocumentAnalyticsResponseDocumentsByStatus
        from ..models.document_analytics_response_documents_by_type import DocumentAnalyticsResponseDocumentsByType
        from ..models.document_analytics_response_most_viewed_documents_item import (
            DocumentAnalyticsResponseMostViewedDocumentsItem,
        )
        from ..models.document_analytics_response_popular_search_terms import (
            DocumentAnalyticsResponsePopularSearchTerms,
        )
        from ..models.document_analytics_response_storage_by_type import DocumentAnalyticsResponseStorageByType

        d = dict(src_dict)
        total_documents = d.pop("total_documents")

        documents_by_status = DocumentAnalyticsResponseDocumentsByStatus.from_dict(d.pop("documents_by_status"))

        documents_by_type = DocumentAnalyticsResponseDocumentsByType.from_dict(d.pop("documents_by_type"))

        avg_processing_time_seconds = d.pop("avg_processing_time_seconds")

        processing_success_rate = d.pop("processing_success_rate")

        total_chunks = d.pop("total_chunks")

        avg_chunks_per_document = d.pop("avg_chunks_per_document")

        total_storage_bytes = d.pop("total_storage_bytes")

        avg_document_size_bytes = d.pop("avg_document_size_bytes")

        storage_by_type = DocumentAnalyticsResponseStorageByType.from_dict(d.pop("storage_by_type"))

        total_searches = d.pop("total_searches")

        avg_search_results = d.pop("avg_search_results")

        popular_search_terms = DocumentAnalyticsResponsePopularSearchTerms.from_dict(d.pop("popular_search_terms"))

        total_views = d.pop("total_views")

        most_viewed_documents = []
        _most_viewed_documents = d.pop("most_viewed_documents")
        for most_viewed_documents_item_data in _most_viewed_documents:
            most_viewed_documents_item = DocumentAnalyticsResponseMostViewedDocumentsItem.from_dict(
                most_viewed_documents_item_data
            )

            most_viewed_documents.append(most_viewed_documents_item)

        documents_by_access_level = DocumentAnalyticsResponseDocumentsByAccessLevel.from_dict(
            d.pop("documents_by_access_level")
        )

        document_analytics_response = cls(
            total_documents=total_documents,
            documents_by_status=documents_by_status,
            documents_by_type=documents_by_type,
            avg_processing_time_seconds=avg_processing_time_seconds,
            processing_success_rate=processing_success_rate,
            total_chunks=total_chunks,
            avg_chunks_per_document=avg_chunks_per_document,
            total_storage_bytes=total_storage_bytes,
            avg_document_size_bytes=avg_document_size_bytes,
            storage_by_type=storage_by_type,
            total_searches=total_searches,
            avg_search_results=avg_search_results,
            popular_search_terms=popular_search_terms,
            total_views=total_views,
            most_viewed_documents=most_viewed_documents,
            documents_by_access_level=documents_by_access_level,
        )

        document_analytics_response.additional_properties = d
        return document_analytics_response

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
