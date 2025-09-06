"""Pydantic schemas for model/embedding registry."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from chatter.models.registry import (
    DistanceMetric,
    ModelType,
    ProviderType,
    ReductionStrategy,
)


# Provider Schemas
class ProviderBase(BaseModel):
    """Base provider schema."""

    name: str = Field(
        ...,
        description="Unique provider name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    provider_type: ProviderType = Field(
        ..., description="Type of provider"
    )
    display_name: str = Field(
        ...,
        description="Human-readable name",
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        None, description="Provider description", max_length=1000
    )
    api_key_required: bool = Field(
        True, description="Whether API key is required"
    )
    base_url: str | None = Field(
        None, description="Base URL for API", max_length=500
    )
    default_config: dict[str, Any] = Field(
        default_factory=dict, description="Default configuration"
    )
    is_active: bool = Field(
        True, description="Whether provider is active"
    )
    is_default: bool = Field(
        False, description="Whether this is the default provider"
    )


class ProviderCreate(ProviderBase):
    """Schema for creating a provider."""

    pass


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""

    display_name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    api_key_required: bool | None = None
    base_url: str | None = Field(None, max_length=500)
    default_config: dict[str, Any] | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class Provider(ProviderBase):
    """Full provider schema."""

    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Model Definition Schemas
class ModelDefBase(BaseModel):
    """Base model definition schema."""

    name: str = Field(
        ...,
        description="Model name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    model_type: ModelType = Field(..., description="Type of model")
    display_name: str = Field(
        ...,
        description="Human-readable name",
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        None, description="Model description", max_length=1000
    )
    model_name: str = Field(
        ...,
        description="Actual model name for API calls",
        min_length=1,
        max_length=200,
    )
    max_tokens: int | None = Field(
        None, description="Maximum tokens", gt=0, le=1000000
    )
    context_length: int | None = Field(
        None, description="Context length", gt=0, le=10000000
    )
    dimensions: int | None = Field(
        None, description="Embedding dimensions", gt=0, le=10000
    )
    chunk_size: int | None = Field(
        None, description="Default chunk size", gt=0, le=100000
    )
    supports_batch: bool = Field(
        False, description="Whether model supports batch operations"
    )
    max_batch_size: int | None = Field(
        None, description="Maximum batch size", gt=0, le=10000
    )
    default_config: dict[str, Any] = Field(
        default_factory=dict, description="Default configuration"
    )
    is_active: bool = Field(True, description="Whether model is active")
    is_default: bool = Field(
        False, description="Whether this is the default model"
    )


class ModelDefCreate(ModelDefBase):
    """Schema for creating a model definition."""

    provider_id: str = Field(..., description="Provider ID")


class ModelDefUpdate(BaseModel):
    """Schema for updating a model definition."""

    display_name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    model_name: str | None = Field(None, min_length=1, max_length=200)
    max_tokens: int | None = Field(None, gt=0, le=1000000)
    context_length: int | None = Field(None, gt=0, le=10000000)
    dimensions: int | None = Field(None, gt=0, le=10000)
    chunk_size: int | None = Field(None, gt=0, le=100000)
    supports_batch: bool | None = None
    max_batch_size: int | None = Field(None, gt=0, le=10000)
    default_config: dict[str, Any] | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class ModelDef(ModelDefBase):
    """Full model definition schema."""

    id: str
    provider_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ModelDefWithProvider(ModelDef):
    """Model definition with provider information."""

    provider: Provider


# Embedding Space Schemas
class EmbeddingSpaceBase(BaseModel):
    """Base embedding space schema."""

    name: str = Field(
        ...,
        description="Unique space name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_-]+$",
    )
    display_name: str = Field(
        ...,
        description="Human-readable name",
        min_length=1,
        max_length=200,
    )
    description: str | None = Field(
        None, description="Space description", max_length=1000
    )
    base_dimensions: int = Field(
        ..., description="Original model dimensions", gt=0, le=10000
    )
    effective_dimensions: int = Field(
        ...,
        description="Effective dimensions after reduction",
        gt=0,
        le=10000,
    )
    reduction_strategy: ReductionStrategy = Field(
        ReductionStrategy.NONE, description="Reduction strategy"
    )
    reducer_path: str | None = Field(
        None, description="Path to reducer file", max_length=500
    )
    reducer_version: str | None = Field(
        None, description="Reducer version/hash", max_length=100
    )
    normalize_vectors: bool = Field(
        True, description="Whether to normalize vectors"
    )
    distance_metric: DistanceMetric = Field(
        DistanceMetric.COSINE, description="Distance metric"
    )
    table_name: str = Field(
        ...,
        description="Database table name",
        min_length=1,
        max_length=100,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    index_type: str = Field(
        "hnsw", description="Index type", max_length=50
    )
    index_config: dict[str, Any] = Field(
        default_factory=dict, description="Index configuration"
    )
    is_active: bool = Field(True, description="Whether space is active")
    is_default: bool = Field(
        False, description="Whether this is the default space"
    )


class EmbeddingSpaceCreate(EmbeddingSpaceBase):
    """Schema for creating an embedding space."""

    model_id: str = Field(..., description="Model ID")


class EmbeddingSpaceUpdate(BaseModel):
    """Schema for updating an embedding space."""

    display_name: str | None = None
    description: str | None = None
    reduction_strategy: ReductionStrategy | None = None
    reducer_path: str | None = None
    reducer_version: str | None = None
    normalize_vectors: bool | None = None
    distance_metric: DistanceMetric | None = None
    index_type: str | None = None
    index_config: dict[str, Any] | None = None
    is_active: bool | None = None
    is_default: bool | None = None


class EmbeddingSpace(EmbeddingSpaceBase):
    """Full embedding space schema."""

    id: str
    model_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmbeddingSpaceWithModel(EmbeddingSpace):
    """Embedding space with model and provider information."""

    model: ModelDefWithProvider


# Query and list schemas
class ProviderList(BaseModel):
    """List of providers with pagination."""

    providers: Sequence[Provider]
    total: int
    page: int
    per_page: int


class ModelDefList(BaseModel):
    """List of model definitions with pagination."""

    models: Sequence[ModelDefWithProvider]
    total: int
    page: int
    per_page: int


class EmbeddingSpaceList(BaseModel):
    """List of embedding spaces with pagination."""

    spaces: Sequence[EmbeddingSpaceWithModel]
    total: int
    page: int
    per_page: int


# Default selection schemas
class DefaultProvider(BaseModel):
    """Schema for setting default provider."""

    model_type: ModelType


class DefaultModel(BaseModel):
    """Schema for setting default model."""

    model_id: str


class DefaultEmbeddingSpace(BaseModel):
    """Schema for setting default embedding space."""

    space_id: str


# Response schemas
class ProviderDeleteResponse(BaseModel):
    """Response schema for provider deletion."""

    message: str = Field(..., description="Deletion result message")


class ProviderDefaultResponse(BaseModel):
    """Response schema for setting default provider."""

    message: str = Field(..., description="Operation result message")


class ModelDeleteResponse(BaseModel):
    """Response schema for model deletion."""

    message: str = Field(..., description="Deletion result message")


class ModelDefaultResponse(BaseModel):
    """Response schema for setting default model."""

    message: str = Field(..., description="Operation result message")


class EmbeddingSpaceDeleteResponse(BaseModel):
    """Response schema for embedding space deletion."""

    message: str = Field(..., description="Deletion result message")


class EmbeddingSpaceDefaultResponse(BaseModel):
    """Response schema for setting default embedding space."""

    message: str = Field(..., description="Operation result message")
