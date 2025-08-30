"""Pydantic schemas for model/embedding registry."""

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
    name: str = Field(..., description="Unique provider name")
    provider_type: ProviderType = Field(..., description="Type of provider")
    display_name: str = Field(..., description="Human-readable name")
    description: str | None = Field(None, description="Provider description")
    api_key_required: bool = Field(True, description="Whether API key is required")
    base_url: str | None = Field(None, description="Base URL for API")
    default_config: dict[str, Any] = Field(default_factory=dict, description="Default configuration")
    is_active: bool = Field(True, description="Whether provider is active")
    is_default: bool = Field(False, description="Whether this is the default provider")


class ProviderCreate(ProviderBase):
    """Schema for creating a provider."""
    pass


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""
    display_name: str | None = None
    description: str | None = None
    api_key_required: bool | None = None
    base_url: str | None = None
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
    name: str = Field(..., description="Model name")
    model_type: ModelType = Field(..., description="Type of model")
    display_name: str = Field(..., description="Human-readable name")
    description: str | None = Field(None, description="Model description")
    model_name: str = Field(..., description="Actual model name for API calls")
    max_tokens: int | None = Field(None, description="Maximum tokens")
    context_length: int | None = Field(None, description="Context length")
    dimensions: int | None = Field(None, description="Embedding dimensions")
    chunk_size: int | None = Field(None, description="Default chunk size")
    supports_batch: bool = Field(True, description="Supports batch processing")
    max_batch_size: int | None = Field(None, description="Maximum batch size")
    default_config: dict[str, Any] = Field(default_factory=dict, description="Default configuration")
    is_active: bool = Field(True, description="Whether model is active")
    is_default: bool = Field(False, description="Whether this is the default model")


class ModelDefCreate(ModelDefBase):
    """Schema for creating a model definition."""
    provider_id: str = Field(..., description="Provider ID")


class ModelDefUpdate(BaseModel):
    """Schema for updating a model definition."""
    display_name: str | None = None
    description: str | None = None
    model_name: str | None = None
    max_tokens: int | None = None
    context_length: int | None = None
    dimensions: int | None = None
    chunk_size: int | None = None
    supports_batch: bool | None = None
    max_batch_size: int | None = None
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
    name: str = Field(..., description="Unique space name")
    display_name: str = Field(..., description="Human-readable name")
    description: str | None = Field(None, description="Space description")
    base_dimensions: int = Field(..., description="Original model dimensions")
    effective_dimensions: int = Field(..., description="Effective dimensions after reduction")
    reduction_strategy: ReductionStrategy = Field(ReductionStrategy.NONE, description="Reduction strategy")
    reducer_path: str | None = Field(None, description="Path to reducer file")
    reducer_version: str | None = Field(None, description="Reducer version/hash")
    normalize_vectors: bool = Field(True, description="Whether to normalize vectors")
    distance_metric: DistanceMetric = Field(DistanceMetric.COSINE, description="Distance metric")
    table_name: str = Field(..., description="Database table name")
    index_type: str = Field("hnsw", description="Index type")
    index_config: dict[str, Any] = Field(default_factory=dict, description="Index configuration")
    is_active: bool = Field(True, description="Whether space is active")
    is_default: bool = Field(False, description="Whether this is the default space")


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
    providers: list[Provider]
    total: int
    page: int
    per_page: int


class ModelDefList(BaseModel):
    """List of model definitions with pagination."""
    models: list[ModelDefWithProvider]
    total: int
    page: int
    per_page: int


class EmbeddingSpaceList(BaseModel):
    """List of embedding spaces with pagination."""
    spaces: list[EmbeddingSpaceWithModel]
    total: int
    page: int
    per_page: int


# Default selection schemas
class DefaultProvider(BaseModel):
    """Schema for setting default provider."""
    provider_id: str
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
