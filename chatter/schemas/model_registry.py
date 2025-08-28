"""Pydantic schemas for model/embedding registry."""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from chatter.models.registry import DistanceMetric, ModelType, ProviderType, ReductionStrategy


# Provider Schemas
class ProviderBase(BaseModel):
    """Base provider schema."""
    name: str = Field(..., description="Unique provider name")
    provider_type: ProviderType = Field(..., description="Type of provider")
    display_name: str = Field(..., description="Human-readable name")
    description: Optional[str] = Field(None, description="Provider description")
    api_key_required: bool = Field(True, description="Whether API key is required")
    base_url: Optional[str] = Field(None, description="Base URL for API")
    default_config: dict[str, Any] = Field(default_factory=dict, description="Default configuration")
    is_active: bool = Field(True, description="Whether provider is active")
    is_default: bool = Field(False, description="Whether this is the default provider")


class ProviderCreate(ProviderBase):
    """Schema for creating a provider."""
    pass


class ProviderUpdate(BaseModel):
    """Schema for updating a provider."""
    display_name: Optional[str] = None
    description: Optional[str] = None
    api_key_required: Optional[bool] = None
    base_url: Optional[str] = None
    default_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


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
    description: Optional[str] = Field(None, description="Model description")
    model_name: str = Field(..., description="Actual model name for API calls")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens")
    context_length: Optional[int] = Field(None, description="Context length")
    dimensions: Optional[int] = Field(None, description="Embedding dimensions")
    chunk_size: Optional[int] = Field(None, description="Default chunk size")
    supports_batch: bool = Field(True, description="Supports batch processing")
    max_batch_size: Optional[int] = Field(None, description="Maximum batch size")
    default_config: dict[str, Any] = Field(default_factory=dict, description="Default configuration")
    is_active: bool = Field(True, description="Whether model is active")
    is_default: bool = Field(False, description="Whether this is the default model")


class ModelDefCreate(ModelDefBase):
    """Schema for creating a model definition."""
    provider_id: str = Field(..., description="Provider ID")


class ModelDefUpdate(BaseModel):
    """Schema for updating a model definition."""
    display_name: Optional[str] = None
    description: Optional[str] = None
    model_name: Optional[str] = None
    max_tokens: Optional[int] = None
    context_length: Optional[int] = None
    dimensions: Optional[int] = None
    chunk_size: Optional[int] = None
    supports_batch: Optional[bool] = None
    max_batch_size: Optional[int] = None
    default_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


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
    description: Optional[str] = Field(None, description="Space description")
    base_dimensions: int = Field(..., description="Original model dimensions")
    effective_dimensions: int = Field(..., description="Effective dimensions after reduction")
    reduction_strategy: ReductionStrategy = Field(ReductionStrategy.NONE, description="Reduction strategy")
    reducer_path: Optional[str] = Field(None, description="Path to reducer file")
    reducer_version: Optional[str] = Field(None, description="Reducer version/hash")
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
    display_name: Optional[str] = None
    description: Optional[str] = None
    reduction_strategy: Optional[ReductionStrategy] = None
    reducer_path: Optional[str] = None
    reducer_version: Optional[str] = None
    normalize_vectors: Optional[bool] = None
    distance_metric: Optional[DistanceMetric] = None
    index_type: Optional[str] = None
    index_config: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


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