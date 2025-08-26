"""Updated document models to support dynamic embedding tables."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base, Keys


class DocumentStatus(str, Enum):
    """Enumeration for document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    ARCHIVED = "archived"


class DocumentType(str, Enum):
    """Enumeration for document types."""

    PDF = "pdf"
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    DOC = "doc"
    DOCX = "docx"
    RTF = "rtf"


class Document(Base):
    """Document model for knowledge base."""

    # File information
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Document metadata
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType), nullable=False, index=True
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing status
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus), nullable=False, index=True
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Chunking configuration
    chunk_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_overlap: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Metadata
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Versioning
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parent_document_id: Mapped[str | None] = mapped_column(
        String(12), nullable=True, index=True
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )

    # Analytics
    view_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    search_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        """String representation of document."""
        return f"<Document(id={self.id}, filename={self.original_filename}, status={self.status.value})>"

    @property
    def has_chunks(self) -> bool:
        """Check if document has chunks."""
        return self.chunk_count is not None and self.chunk_count > 0

    @property
    def is_processed(self) -> bool:
        """Check if document is processed."""
        return self.status == DocumentStatus.PROCESSED

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "document_type": self.document_type.value,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "processing_started_at": self.processing_started_at.isoformat()
            if self.processing_started_at
            else None,
            "processing_completed_at": (
                self.processing_completed_at.isoformat()
                if self.processing_completed_at
                else None
            ),
            "processing_error": self.processing_error,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunk_count": self.chunk_count,
            "metadata": self.extra_metadata,
            "tags": self.tags,
            "version": self.version,
            "parent_document_id": self.parent_document_id,
            "is_public": self.is_public,
            "view_count": self.view_count,
            "search_count": self.search_count,
            "last_accessed_at": self.last_accessed_at.isoformat()
            if self.last_accessed_at
            else None,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
        }


class DocumentChunk(Base):
    """Document chunk model for vector storage.
    
    Updated to support dynamic embedding models. The actual embeddings
    are now stored in separate per-model tables, while this table
    contains metadata about which embedding models have been applied.
    """

    # Foreign keys
    document_id: Mapped[str] = mapped_column(
        String(12),
        ForeignKey(Keys.DOCUMENTS),
        nullable=False,
        index=True,
    )

    # Chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False, index=True
    )
    start_char: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    end_char: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Legacy embedding field - kept for backwards compatibility during migration
    # No longer used for new embeddings, which go to dynamic tables
    embedding: Mapped[Any | None] = mapped_column(
        Text, nullable=True  # Changed from Vector to Text for compatibility
    )

    # Metadata
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )

    # Content analysis
    token_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    language: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )

    # Embedding metadata - tracks which models have been applied
    embedding_models: Mapped[list[str] | None] = mapped_column(
        "embedding_models", JSON, nullable=True, 
        comment="List of embedding model names that have been applied to this chunk"
    )
    primary_embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
        comment="Primary embedding model for this chunk"
    )
    embedding_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    embedding_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Search optimization
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document", back_populates="chunks"
    )

    def __repr__(self) -> str:
        """String representation of document chunk."""
        content_preview = (
            self.content[:50] + "..."
            if len(self.content) > 50
            else self.content
        )
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index}, content={content_preview})>"

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has any embeddings (legacy or dynamic)."""
        return (
            self.embedding is not None 
            or (self.embedding_models and len(self.embedding_models) > 0)
        )

    @property
    def has_dynamic_embeddings(self) -> bool:
        """Check if chunk has embeddings in dynamic tables."""
        return self.embedding_models and len(self.embedding_models) > 0

    def add_embedding_model(self, model_name: str, set_as_primary: bool = False) -> None:
        """Add an embedding model to the list of applied models.
        
        Args:
            model_name: Name of the embedding model
            set_as_primary: Whether to set this as the primary model
        """
        if not self.embedding_models:
            self.embedding_models = []
        
        if model_name not in self.embedding_models:
            self.embedding_models.append(model_name)
        
        if set_as_primary or not self.primary_embedding_model:
            self.primary_embedding_model = model_name

    def remove_embedding_model(self, model_name: str) -> None:
        """Remove an embedding model from the list.
        
        Args:
            model_name: Name of the embedding model to remove
        """
        if self.embedding_models and model_name in self.embedding_models:
            self.embedding_models.remove(model_name)
            
            # Update primary if it was the removed model
            if self.primary_embedding_model == model_name:
                self.primary_embedding_model = (
                    self.embedding_models[0] if self.embedding_models else None
                )

    def to_dict(self) -> dict[str, Any]:
        """Convert document chunk to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "has_embedding": self.has_embedding,
            "has_dynamic_embeddings": self.has_dynamic_embeddings,
            "embedding_models": self.embedding_models,
            "primary_embedding_model": self.primary_embedding_model,
            "embedding_provider": self.embedding_provider,
            "embedding_created_at": self.embedding_created_at.isoformat()
            if self.embedding_created_at
            else None,
            "token_count": self.token_count,
            "language": self.language,
            "content_hash": self.content_hash,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
            "updated_at": self.updated_at.isoformat()
            if self.updated_at
            else None,
        }