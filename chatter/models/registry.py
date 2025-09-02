"""Registry models for LLM providers, models, and embedding spaces."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chatter.models.base import Base


class ProviderType(str, Enum):
    """Types of AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"


class ModelType(str, Enum):
    """Types of AI models."""

    LLM = "llm"
    EMBEDDING = "embedding"


class DistanceMetric(str, Enum):
    """Distance metrics for vector similarity."""

    COSINE = "cosine"
    L2 = "l2"
    IP = "ip"  # inner product


class ReductionStrategy(str, Enum):
    """Dimensionality reduction strategies."""

    NONE = "none"
    TRUNCATE = "truncate"
    REDUCER = "reducer"  # PCA/SVD


class Provider(Base):
    """AI provider registry."""

    __tablename__ = "providers"  # type: ignore[assignment]

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    provider_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    display_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)

    # Configuration
    api_key_required: Mapped[bool] = mapped_column(
        Boolean, default=True
    )
    base_url: Mapped[str | None] = mapped_column(String(500))
    default_config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    models = relationship(
        "ModelDef",
        back_populates="provider",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Provider(name='{self.name}', type='{self.provider_type}')>"


class ModelDef(Base):
    """AI model definition registry."""

    __tablename__ = "model_defs"  # type: ignore[assignment]

    provider_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("providers.id"), nullable=False
    )

    # Model identification
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # llm, embedding
    display_name: Mapped[str] = mapped_column(
        String(300), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)

    # Model configuration
    model_name: Mapped[str] = mapped_column(
        String(200), nullable=False
    )  # actual model name for API calls
    max_tokens: Mapped[int | None] = mapped_column(Integer)
    context_length: Mapped[int | None] = mapped_column(Integer)
    dimensions: Mapped[int | None] = mapped_column(
        Integer
    )  # for embedding models

    # Embedding-specific settings
    chunk_size: Mapped[int | None] = mapped_column(Integer)
    supports_batch: Mapped[bool] = mapped_column(Boolean, default=True)
    max_batch_size: Mapped[int | None] = mapped_column(Integer)

    # Configuration
    default_config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    provider = relationship("Provider", back_populates="models")
    embedding_spaces = relationship(
        "EmbeddingSpace",
        back_populates="model",
        cascade="all, delete-orphan",
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint(
            'provider_id', 'name', name='uq_provider_model_name'
        ),
    )

    def __repr__(self) -> str:
        return f"<ModelDef(name='{self.name}', type='{self.model_type}', dimensions={self.dimensions})>"


class EmbeddingSpace(Base):
    """Embedding space definition with dimensional reduction support."""

    __tablename__ = "embedding_spaces"  # type: ignore[assignment]

    model_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("model_defs.id"), nullable=False
    )

    # Space identification
    name: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True, index=True
    )
    display_name: Mapped[str] = mapped_column(
        String(300), nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)

    # Dimensional configuration
    base_dimensions: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # original model dimensions
    effective_dimensions: Mapped[int] = mapped_column(
        Integer, nullable=False
    )  # after reduction
    reduction_strategy: Mapped[str] = mapped_column(
        String(50), default=ReductionStrategy.NONE
    )

    # Reduction configuration
    reducer_path: Mapped[str | None] = mapped_column(
        String(500)
    )  # path to joblib reducer file
    reducer_version: Mapped[str | None] = mapped_column(
        String(100)
    )  # version/hash of reducer
    normalize_vectors: Mapped[bool] = mapped_column(
        Boolean, default=True
    )

    # Vector store configuration
    distance_metric: Mapped[str] = mapped_column(
        String(50), default=DistanceMetric.COSINE
    )
    table_name: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True
    )
    index_type: Mapped[str] = mapped_column(
        String(50), default="hnsw"
    )  # hnsw, ivfflat
    index_config: Mapped[dict] = mapped_column(
        JSON, default=dict
    )  # index-specific parameters

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    model = relationship("ModelDef", back_populates="embedding_spaces")

    def __repr__(self) -> str:
        return f"<EmbeddingSpace(name='{self.name}', base_dims={self.base_dimensions}, effective_dims={self.effective_dimensions})>"
