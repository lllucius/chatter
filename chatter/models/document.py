"""Document and document chunk models for knowledge base."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
)
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:
    from pgvector.sqlalchemy import Vector

    PGVECTOR_AVAILABLE = True
except ImportError:
    Vector = None
    PGVECTOR_AVAILABLE = False

from chatter.models.base import Base, Keys

if TYPE_CHECKING:
    from chatter.models.user import User


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

    __table_args__ = (
        CheckConstraint(
            "file_size > 0",
            name="check_file_size_positive",
        ),
        CheckConstraint(
            "chunk_size > 0",
            name="check_chunk_size_positive",
        ),
        CheckConstraint(
            "chunk_overlap >= 0",
            name="check_chunk_overlap_non_negative",
        ),
        CheckConstraint(
            "chunk_count >= 0",
            name="check_chunk_count_non_negative",
        ),
        CheckConstraint(
            "version > 0",
            name="check_version_positive",
        ),
        CheckConstraint(
            "view_count >= 0",
            name="check_view_count_non_negative",
        ),
        CheckConstraint(
            "search_count >= 0",
            name="check_search_count_non_negative",
        ),
        UniqueConstraint(
            "owner_id", "file_hash", name="uq_document_owner_hash"
        ),
    )

    # Foreign keys
    owner_id: Mapped[str] = mapped_column(
        String(26), ForeignKey(Keys.USERS), nullable=False, index=True
    )

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    file_path: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # SHA-256
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        SQLEnum(DocumentType), nullable=False, index=True
    )

    # Content
    title: Mapped[str | None] = mapped_column(
        String(500), nullable=True
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Processing status
    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(DocumentStatus),
        default=DocumentStatus.PENDING,
        nullable=False,
        index=True,
    )
    processing_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_error: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    # Chunking configuration
    chunk_size: Mapped[int] = mapped_column(
        Integer, default=1000, nullable=False
    )
    chunk_overlap: Mapped[int] = mapped_column(
        Integer, default=200, nullable=False
    )
    chunk_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Metadata and tags
    extra_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        "extra_metadata", JSON, nullable=True
    )
    tags: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    # Version control
    version: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    parent_document_id: Mapped[str | None] = mapped_column(
        String(26),
        ForeignKey(Keys.DOCUMENTS),
        nullable=True,
        index=True,
    )

    # Access control
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Usage statistics
    view_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    search_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    owner: Mapped[User] = relationship(
        "User", back_populates="documents"
    )
    chunks: Mapped[list[DocumentChunk]] = relationship(
        "DocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    parent_document: Mapped[Document | None] = relationship(
        "Document",
        remote_side="Document.id",
        back_populates="child_documents",
    )
    child_documents: Mapped[list[Document]] = relationship(
        "Document", back_populates="parent_document"
    )

    def __repr__(self) -> str:
        """String representation of document."""
        return f"<Document(id={self.id}, filename={self.filename}, status={self.status})>"

    @property
    def is_processed(self) -> bool:
        """Check if document is fully processed."""
        processed: bool = self.status == DocumentStatus.PROCESSED
        return processed

    @property
    def processing_duration(self) -> float | None:
        """Get processing duration in seconds."""
        if self.processing_started_at and self.processing_completed_at:
            delta = (
                self.processing_completed_at
                - self.processing_started_at
            )
            duration: float = delta.total_seconds()
            return duration
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
            "processing_started_at": (
                self.processing_started_at.isoformat()
                if self.processing_started_at
                else None
            ),
            "processing_completed_at": (
                self.processing_completed_at.isoformat()
                if self.processing_completed_at
                else None
            ),
            "processing_error": self.processing_error,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunk_count": self.chunk_count,
            "extra_metadata": self.extra_metadata,
            "tags": self.tags,
            "version": self.version,
            "parent_document_id": self.parent_document_id,
            "is_public": self.is_public,
            "view_count": self.view_count,
            "search_count": self.search_count,
            "last_accessed_at": (
                self.last_accessed_at.isoformat()
                if self.last_accessed_at
                else None
            ),
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


class DocumentChunk(Base):
    """Document chunk model for vector storage."""

    __table_args__ = (
        CheckConstraint(
            "chunk_index >= 0",
            name="check_chunk_index_non_negative",
        ),
        CheckConstraint(
            "start_char IS NULL OR start_char >= 0",
            name="check_start_char_non_negative",
        ),
        CheckConstraint(
            "end_char IS NULL OR end_char > 0",
            name="check_end_char_positive",
        ),
        CheckConstraint(
            "start_char IS NULL OR end_char IS NULL OR end_char > start_char",
            name="check_end_char_greater_than_start",
        ),
        CheckConstraint(
            "token_count IS NULL OR token_count > 0",
            name="check_token_count_positive",
        ),
        CheckConstraint(
            "content != ''", name="check_content_not_empty"
        ),
    )

    # Foreign keys
    document_id: Mapped[str] = mapped_column(
        String(26),
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

    # Hybrid vector storage for automatic column selection
    # Fixed dimension embedding for fast pgvector search (1536 dimensions)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(1536) if PGVECTOR_AVAILABLE else JSON,
        nullable=True,
        comment="Fixed 1536-dim vector embedding for fast search",
    )

    # Raw embedding storage for any dimension size
    raw_embedding: Mapped[list[float] | None] = mapped_column(
        JSON,
        nullable=True,
        comment="Raw embedding vector of any dimension",
    )

    # Computed embedding for padded/truncated vectors with full indexing
    computed_embedding: Mapped[list[float] | None] = mapped_column(
        Vector(1536) if PGVECTOR_AVAILABLE else JSON,
        nullable=True,
        comment="Computed embedding (padded/truncated to 1536) with index",
    )

    # Metadata about original embedding dimensions
    raw_dim: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
        comment="Original embedding dimension for filtering",
    )

    # Provider and model metadata
    embedding_provider: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    embedding_model: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    embedding_dimensions: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    embedding_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Embedding metadata for content chunks
    embedding_models: Mapped[list[str] | None] = mapped_column(
        "embedding_models",
        JSON,
        nullable=True,
        comment="List of embedding model names that have been applied to this chunk",
    )
    primary_embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Primary embedding model for this chunk",
    )

    # Search optimization
    content_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )

    # Relationships
    document: Mapped[Document] = relationship(
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
    def has_dynamic_embeddings(self) -> bool:
        """Check if chunk has embeddings in dynamic tables."""
        return bool(
            self.embedding_models and len(self.embedding_models) > 0
        )

    def add_embedding_model(
        self, model_name: str, set_as_primary: bool = False
    ) -> None:
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
        if (
            self.embedding_models
            and model_name in self.embedding_models
        ):
            self.embedding_models.remove(model_name)

            # Update primary if it was the removed model
            if self.primary_embedding_model == model_name:
                self.primary_embedding_model = (
                    self.embedding_models[0]
                    if self.embedding_models
                    else None
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
            "extra_metadata": self.extra_metadata,
            "token_count": self.token_count,
            "language": self.language,
            "embedding_provider": self.embedding_provider,
            "embedding_model": self.embedding_model,
            "embedding_dimensions": self.embedding_dimensions,
            "embedding_created_at": (
                self.embedding_created_at.isoformat()
                if self.embedding_created_at
                else None
            ),
            "content_hash": self.content_hash,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
        }


# Hybrid Vector Search Implementation with Event Listeners


def normalize_embedding_to_fixed_dim(
    raw_embedding: list[float], target_dim: int = 1536
) -> list[float]:
    """
    Normalize embedding to fixed dimension by padding with zeros or truncating.

    Args:
        raw_embedding: Original embedding vector
        target_dim: Target dimension size (default 1536)

    Returns:
        Normalized embedding of target dimension
    """
    if not raw_embedding:
        return [0.0] * target_dim

    if len(raw_embedding) == target_dim:
        return raw_embedding.copy()
    elif len(raw_embedding) < target_dim:
        # Pad with zeros
        result = raw_embedding.copy()
        result.extend([0.0] * (target_dim - len(raw_embedding)))
        return result
    else:
        # Truncate to target dimension
        return raw_embedding[:target_dim]


@event.listens_for(DocumentChunk.raw_embedding, 'set')
def update_computed_embedding(target, value, oldvalue, initiator):
    """
    Event listener that automatically updates computed_embedding when raw_embedding is set.
    This ensures computed_embedding is always normalized to 1536 dimensions.
    """
    if value is not None:
        # Store original dimension
        target.raw_dim = len(value)

        # Create computed embedding (normalized to 1536)
        target.computed_embedding = normalize_embedding_to_fixed_dim(
            value, 1536
        )

        # If the raw embedding is exactly 1536 dimensions, also set the main embedding
        if len(value) == 1536:
            target.embedding = value
        else:
            # Use computed embedding for the main embedding field
            target.embedding = target.computed_embedding


@event.listens_for(DocumentChunk, 'before_insert')
@event.listens_for(DocumentChunk, 'before_update')
def ensure_embedding_consistency(mapper, connection, target):
    """
    Event listener to ensure embedding consistency before database operations.
    This handles cases where embeddings are set directly.
    """
    # If raw_embedding is set but computed_embedding is not, compute it
    if target.raw_embedding and not target.computed_embedding:
        target.raw_dim = len(target.raw_embedding)
        target.computed_embedding = normalize_embedding_to_fixed_dim(
            target.raw_embedding, 1536
        )

        # Set main embedding based on dimension
        if len(target.raw_embedding) == 1536:
            target.embedding = target.raw_embedding
        else:
            target.embedding = target.computed_embedding

    # If only embedding is set, populate raw_embedding and computed_embedding
    elif target.embedding and not target.raw_embedding:
        target.raw_embedding = target.embedding
        target.raw_dim = len(target.embedding)
        target.computed_embedding = normalize_embedding_to_fixed_dim(
            target.embedding, 1536
        )


class HybridVectorSearchHelper:
    """
    Helper class for hybrid vector search that automatically chooses the correct column
    based on query vector size and search requirements.
    """

    @staticmethod
    def choose_search_column(
        query_vector: list[float], prefer_exact_match: bool = True
    ) -> str:
        """
        Choose the optimal embedding column for search based on query vector size.

        Args:
            query_vector: The query embedding vector
            prefer_exact_match: Whether to prefer exact dimension matches

        Returns:
            Column name to use for search ('embedding', 'computed_embedding', or 'raw_embedding')
        """
        query_dim = len(query_vector)

        if query_dim == 1536:
            # Perfect match - use the optimized embedding column
            return 'embedding'
        elif prefer_exact_match:
            # Look for exact dimensional match in raw_embedding with raw_dim filter
            return 'raw_embedding'
        else:
            # Use computed_embedding for consistent searches
            return 'computed_embedding'

    @staticmethod
    def prepare_query_vector(
        query_vector: list[float], target_column: str
    ) -> list[float]:
        """
        Prepare query vector for the chosen search column.

        Args:
            query_vector: Original query vector
            target_column: Target column name

        Returns:
            Prepared query vector
        """
        if (
            target_column == 'embedding'
            or target_column == 'computed_embedding'
        ):
            # Normalize to 1536 dimensions
            return normalize_embedding_to_fixed_dim(query_vector, 1536)
        else:
            # Use raw vector as-is
            return query_vector

    @staticmethod
    def build_similarity_filter(
        query_vector: list[float], exact_dim_only: bool = False
    ) -> dict[str, Any]:
        """
        Build filter conditions for hybrid search.

        Args:
            query_vector: Query embedding vector
            exact_dim_only: Whether to filter by exact dimension match

        Returns:
            Dictionary of filter conditions
        """
        filters = {}

        if exact_dim_only:
            filters['raw_dim'] = len(query_vector)

        return filters


# Additional helper methods for DocumentChunk
def _add_hybrid_search_methods():
    """Add hybrid search methods to DocumentChunk class."""

    def get_search_embedding(
        self, query_dim: int
    ) -> list[float] | None:
        """
        Get the appropriate embedding for search based on query dimension.

        Args:
            query_dim: Dimension of the query vector

        Returns:
            Best matching embedding vector or None
        """
        if query_dim == 1536 and self.embedding:
            return self.embedding
        elif query_dim == self.raw_dim and self.raw_embedding:
            return self.raw_embedding
        elif self.computed_embedding:
            return self.computed_embedding
        else:
            return self.embedding

    def has_embedding_for_dimension(self, target_dim: int) -> bool:
        """
        Check if chunk has embedding suitable for the target dimension.

        Args:
            target_dim: Target embedding dimension

        Returns:
            True if suitable embedding exists
        """
        if target_dim == 1536:
            return (
                self.embedding is not None
                or self.computed_embedding is not None
            )
        elif target_dim == self.raw_dim:
            return self.raw_embedding is not None
        else:
            return self.computed_embedding is not None

    def set_embedding_vector(
        self,
        vector: list[float],
        provider: str = None,
        model: str = None,
    ):
        """
        Set embedding vector with automatic normalization.

        Args:
            vector: Embedding vector
            provider: Embedding provider name
            model: Embedding model name
        """
        self.raw_embedding = vector
        self.embedding_provider = provider
        self.embedding_model = model
        self.embedding_dimensions = len(vector)
        self.embedding_created_at = datetime.now()

        # Event listeners will handle computed_embedding and embedding updates

    # Add methods to DocumentChunk
    DocumentChunk.get_search_embedding = get_search_embedding
    DocumentChunk.has_embedding_for_dimension = (
        has_embedding_for_dimension
    )
    DocumentChunk.set_embedding_vector = set_embedding_vector


# Initialize hybrid search methods
_add_hybrid_search_methods()
