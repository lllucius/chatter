"""Document management schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from chatter.models.document import DocumentStatus, DocumentType
from chatter.schemas.common import (
    DeleteRequestBase,
    GetRequestBase,
    ListRequestBase,
)


class DocumentBase(BaseModel):
    """Base document schema."""

    title: str | None = Field(
        default=None, description="Document title"
    )
    description: str | None = Field(
        None, description="Document description"
    )
    tags: list[str] | None = Field(
        default=None, description="Document tags"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )
    is_public: bool = Field(
        False, description="Whether document is public"
    )


class DocumentCreate(DocumentBase):
    """Schema for creating a document."""

    chunk_size: int = Field(
        1000,
        ge=100,
        le=10000,
        description="Chunk size for text splitting",
    )
    chunk_overlap: int = Field(
        200, ge=0, le=2000, description="Overlap between chunks"
    )


class DocumentUploadRequest(BaseModel):
    """Schema for document upload request."""

    title: str | None = Field(
        default=None, description="Document title"
    )
    description: str | None = Field(
        None, description="Document description"
    )
    tags: list[str] | None = Field(
        default=None, description="Document tags"
    )
    chunk_size: int = Field(
        1000,
        ge=100,
        le=10000,
        description="Chunk size for text splitting",
    )
    chunk_overlap: int = Field(
        200, ge=0, le=2000, description="Overlap between chunks"
    )
    is_public: bool = Field(
        False, description="Whether document is public"
    )


class DocumentUpdate(BaseModel):
    """Schema for updating a document."""

    title: str | None = Field(
        default=None, description="Document title"
    )
    description: str | None = Field(
        None, description="Document description"
    )
    tags: list[str] | None = Field(
        default=None, description="Document tags"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Additional metadata"
    )
    is_public: bool | None = Field(
        None, description="Whether document is public"
    )


class DocumentResponse(DocumentBase):
    """Schema for document response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Document ID")
    owner_id: str = Field(..., description="Owner user ID")
    filename: str = Field(..., description="Document filename")
    original_filename: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    file_hash: str = Field(..., description="File hash (SHA-256)")
    mime_type: str = Field(..., description="MIME type")
    document_type: DocumentType = Field(
        ..., description="Document type"
    )
    status: DocumentStatus = Field(..., description="Processing status")
    processing_started_at: datetime | None = Field(
        None, description="Processing start time"
    )
    processing_completed_at: datetime | None = Field(
        None, description="Processing completion time"
    )
    processing_error: str | None = Field(
        None, description="Processing error message"
    )
    chunk_size: int = Field(..., description="Chunk size")
    chunk_overlap: int = Field(..., description="Chunk overlap")
    chunk_count: int = Field(..., description="Number of chunks")
    version: int = Field(..., description="Document version")
    parent_document_id: str | None = Field(
        None, description="Parent document ID"
    )
    view_count: int = Field(..., description="View count")
    search_count: int = Field(..., description="Search count")
    last_accessed_at: datetime | None = Field(
        None, description="Last access time"
    )
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class DocumentSearchRequest(BaseModel):
    """Schema for document search request."""

    query: str = Field(
        ..., min_length=1, max_length=1000, description="Search query"
    )
    limit: int = Field(
        10, ge=1, description="Maximum number of results"
    )
    score_threshold: float = Field(
        0.5, ge=0.0, le=1.0, description="Minimum similarity score"
    )
    document_types: list[DocumentType] | None = Field(
        None, description="Filter by document types"
    )
    tags: list[str] | None = Field(
        default=None, description="Filter by tags"
    )
    include_content: bool = Field(
        False, description="Include document content in results"
    )


class DocumentSearchResult(BaseModel):
    """Schema for document search result."""

    document_id: str = Field(..., description="Document ID")
    chunk_id: str = Field(..., description="Chunk ID")
    score: float = Field(..., description="Similarity score")
    content: str = Field(..., description="Matching content")
    metadata: dict[str, Any] | None = Field(
        None, description="Chunk metadata"
    )
    document: DocumentResponse = Field(
        ..., description="Document information"
    )


class DocumentSearchResponse(BaseModel):
    """Schema for document search response."""

    results: list[DocumentSearchResult] = Field(
        ..., description="Search results"
    )
    total_results: int = Field(
        ..., description="Total number of matching results"
    )
    query: str = Field(..., description="Original search query")
    score_threshold: float = Field(
        ..., description="Applied score threshold"
    )


class DocumentListRequest(ListRequestBase):
    """Schema for document list request."""

    status: DocumentStatus | None = Field(
        None, description="Filter by status"
    )
    document_type: DocumentType | None = Field(
        None, description="Filter by document type"
    )
    tags: list[str] | None = Field(
        default=None, description="Filter by tags"
    )
    owner_id: str | None = Field(
        None, description="Filter by owner (admin only)"
    )

    # Pagination and sorting fields
    limit: int = Field(
        50, ge=1, description="Maximum number of results"
    )
    offset: int = Field(
        0, ge=0, description="Number of results to skip"
    )
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field(
        "desc", pattern="^(asc|desc)$", description="Sort order"
    )


class DocumentGetRequest(GetRequestBase):
    """Schema for document get request."""

    pass


class DocumentDeleteRequest(DeleteRequestBase):
    """Schema for document delete request."""

    pass


class DocumentDeleteResponse(BaseModel):
    """Response schema for document deletion."""

    message: str = Field(..., description="Deletion result message")


class DocumentStatsRequest(GetRequestBase):
    """Schema for document stats request."""

    pass


class DocumentListResponse(BaseModel):
    """Schema for document list response."""

    documents: list[DocumentResponse] = Field(
        ..., description="List of documents"
    )
    total_count: int = Field(
        ..., description="Total number of documents"
    )
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk response."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Chunk index")
    start_char: int | None = Field(
        None, description="Start character position"
    )
    end_char: int | None = Field(
        None, description="End character position"
    )
    extra_metadata: dict[str, Any] | None = Field(
        None, description="Chunk metadata"
    )
    token_count: int | None = Field(
        default=None, description="Token count"
    )
    language: str | None = Field(
        default=None, description="Detected language"
    )
    embedding_model: str | None = Field(
        None, description="Embedding model used"
    )
    embedding_provider: str | None = Field(
        None, description="Embedding provider"
    )
    embedding_created_at: datetime | None = Field(
        None, description="Embedding creation time"
    )
    content_hash: str = Field(..., description="Content hash")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")


class DocumentProcessingRequest(BaseModel):
    """Schema for document processing request."""

    reprocess: bool = Field(False, description="Force reprocessing")
    chunk_size: int | None = Field(
        None, ge=100, le=10000, description="Override chunk size"
    )
    chunk_overlap: int | None = Field(
        None, ge=0, le=2000, description="Override chunk overlap"
    )
    generate_embeddings: bool = Field(
        True, description="Generate embeddings"
    )


class SearchResultResponse(BaseModel):
    """Schema for individual search result."""

    chunk_id: str = Field(..., description="Chunk ID")
    document_id: str = Field(..., description="Document ID")
    content: str = Field(..., description="Matching content")
    similarity_score: float = Field(..., description="Similarity score")
    document_title: str | None = Field(None, description="Document title")
    document_filename: str = Field(..., description="Document filename")
    chunk_index: int = Field(..., description="Chunk index")



class DocumentProcessingResponse(BaseModel):
    """Schema for document processing response."""

    document_id: str = Field(..., description="Document ID")
    status: DocumentStatus = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    processing_started_at: datetime | None = Field(
        None, description="Processing start time"
    )


class DocumentStatsResponse(BaseModel):
    """Schema for document statistics response."""

    total_documents: int = Field(
        ..., description="Total number of documents"
    )
    total_chunks: int = Field(..., description="Total number of chunks")
    total_size_bytes: int = Field(
        ..., description="Total size in bytes"
    )
    documents_by_status: dict[str, int] = Field(
        ..., description="Documents grouped by status"
    )
    documents_by_type: dict[str, int] = Field(
        ..., description="Documents grouped by type"
    )
    processing_stats: dict[str, Any] = Field(
        ..., description="Processing statistics"
    )


class DocumentChunksResponse(BaseModel):
    """Schema for document chunks response with pagination."""

    chunks: list[DocumentChunkResponse] = Field(
        ..., description="List of document chunks"
    )
    total_count: int = Field(..., description="Total number of chunks")
    limit: int = Field(..., description="Applied limit")
    offset: int = Field(..., description="Applied offset")
