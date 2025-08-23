"""Document and document chunk models for knowledge base."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from pgvector.sqlalchemy import Vector

    PGVECTOR_AVAILABLE = True
except ImportError:
    # Fallback for non-PostgreSQL environments
    Vector = Text
    PGVECTOR_AVAILABLE = False

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
    ODT = "odt"
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    OTHER = "other"


class Document(Base):
    """Document model for knowledge base files."""

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(String(12), ForeignKey(Keys.USERS), nullable=False, index=True)

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SHA-256
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(SQLEnum(DocumentType), nullable=False, index=True)

    # Content
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing status
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False, index=True
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processing_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Chunking configuration
    chunk_size: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    chunk_overlap: Mapped[int] = mapped_column(Integer, default=200, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Metadata and tags
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column("extra_metadata", JSON, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_document_id: Mapped[str | None] = mapped_column(
        String(12), ForeignKey(Keys.DOCUMENTS), nullable=True, index=True
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Usage statistics
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    search_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_accessed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="documents")
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        "DocumentChunk", back_populates="document", cascade="all, delete-orphan"
    )
    parent_document: Mapped[Optional["Document"]] = relationship(
        "Document", remote_side="Document.id", back_populates="child_documents"
    )
    child_documents: Mapped[list["Document"]] = relationship("Document", back_populates="parent_document")

    def __repr__(self) -> str:
        """String representation of document."""
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"

    @property
    def is_processed(self) -> bool:
        """Check if document is fully processed."""
        return self.status == DocumentStatus.PROCESSED

    @property
    def processing_duration(self) -> float | None:
        """Get processing duration in seconds."""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return delta.total_seconds()
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert document to dictionary."""
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_size": self.file_size,
            "file_hash": self.file_hash,
            "mime_type": self.mime_type,
            "document_type": self.document_type.value,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "processing_started_at": self.processing_started_at.isoformat() if self.processing_started_at else None,
            "processing_completed_at": (
                self.processing_completed_at.isoformat() if self.processing_completed_at else None
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
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DocumentChunk(Base):
    """Document chunk model for vector storage."""

    # Foreign keys
    document_id: Mapped[str] = mapped_column(String(12), ForeignKey(Keys.DOCUMENTS), nullable=False, index=True)

    # Chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    start_char: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_char: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Vector embedding (conditional on pgvector availability)
    # Use Any type to handle both Vector and Text types
    embedding: Mapped[Any | None] = mapped_column(Vector(1536) if PGVECTOR_AVAILABLE else Text, nullable=True)

    # Metadata
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column("extra_metadata", JSON, nullable=True)

    # Content analysis
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Embedding metadata
    embedding_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    embedding_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    embedding_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Search optimization
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        """String representation of document chunk."""
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<DocumentChunk(id={self.id}, document_id={self.document_id}, index={self.chunk_index}, content={content_preview})>"

    @property
    def has_embedding(self) -> bool:
        """Check if chunk has an embedding."""
        return self.embedding is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert document chunk to dictionary."""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "metadata": self.extra_metadata,
            "token_count": self.token_count,
            "language": self.language,
            "embedding_model": self.embedding_model,
            "embedding_provider": self.embedding_provider,
            "embedding_created_at": self.embedding_created_at.isoformat() if self.embedding_created_at else None,
            "content_hash": self.content_hash,
            "has_embedding": self.has_embedding,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
