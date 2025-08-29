"""Service layer for provider/model/embedding registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.registry import (
    Provider,
    ModelDef,
    EmbeddingSpace,
    ProviderType,
    ModelType,
    DistanceMetric,
    ReductionStrategy,
)
from chatter.schemas.model_registry import (
    ProviderCreate,
    ProviderUpdate,
    ModelDefCreate,
    ModelDefUpdate,
    EmbeddingSpaceCreate,
    EmbeddingSpaceUpdate,
)
from chatter.core.dynamic_embeddings import ensure_table_and_index, get_embedding_model
from sqlalchemy import create_engine
from chatter.config import get_settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def get_sync_engine():
    """Create a synchronous engine for table creation operations."""
    # Convert async URL to sync URL
    sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiopg", "")
    return create_engine(sync_url)


@dataclass
class ListParams:
    """Parameters for list operations."""
    page: int = 1
    per_page: int = 20
    active_only: bool = True


class ModelRegistryService:
    """Service for managing providers, models, and embedding spaces."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # Provider methods
    async def list_providers(
        self, params: ListParams = ListParams()
    ) -> tuple[Sequence[Provider], int]:
        """List providers with pagination."""
        query = select(Provider)
        
        if params.active_only:
            query = query.where(Provider.is_active == True)
        
        # Order by default first, then by display name
        query = query.order_by(Provider.is_default.desc(), Provider.display_name)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Apply pagination
        query = query.offset((params.page - 1) * params.per_page).limit(params.per_page)
        result = await self.session.execute(query)
        providers = result.scalars().all()
        
        return providers, total or 0

    async def get_provider(self, provider_id: str) -> Provider | None:
        """Get provider by ID."""
        result = await self.session.execute(
            select(Provider).where(Provider.id == provider_id)
        )
        return result.scalar_one_or_none()

    async def get_provider_by_name(self, name: str) -> Provider | None:
        """Get provider by name."""
        result = await self.session.execute(
            select(Provider).where(Provider.name == name)
        )
        return result.scalar_one_or_none()

    async def create_provider(self, provider_data: ProviderCreate) -> Provider:
        """Create a new provider."""
        provider = Provider(**provider_data.model_dump())
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def update_provider(
        self, provider_id: str, provider_data: ProviderUpdate
    ) -> Provider | None:
        """Update a provider."""
        provider = await self.get_provider(provider_id)
        if not provider:
            return None
        
        update_data = provider_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)
        
        await self.session.commit()
        await self.session.refresh(provider)
        return provider

    async def delete_provider(self, provider_id: str) -> bool:
        """Delete a provider and its dependent models and embedding spaces."""
        # Check if provider has any models
        models_result = await self.session.execute(
            select(ModelDef).where(ModelDef.provider_id == provider_id)
        )
        models = models_result.scalars().all()
        
        # Delete all embedding spaces for all models under this provider
        for model in models:
            await self.session.execute(
                delete(EmbeddingSpace).where(EmbeddingSpace.model_id == model.id)
            )
        
        # Delete all models under this provider
        await self.session.execute(
            delete(ModelDef).where(ModelDef.provider_id == provider_id)
        )
        
        # Finally delete the provider
        result = await self.session.execute(
            delete(Provider).where(Provider.id == provider_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def set_default_provider(self, provider_id: str, model_type: ModelType) -> bool:
        """Set a provider as default for a model type."""
        # First, unset current default
        await self.session.execute(
            update(Provider).where(Provider.is_default == True).values(is_default=False)
        )
        
        # Set new default
        result = await self.session.execute(
            update(Provider)
            .where(Provider.id == provider_id)
            .values(is_default=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    # Model definition methods
    async def list_models(
        self, 
        provider_id: str | None = None,
        model_type: ModelType | None = None,
        params: ListParams = ListParams()
    ) -> tuple[Sequence[ModelDef], int]:
        """List model definitions with pagination."""
        query = select(ModelDef).options(selectinload(ModelDef.provider))
        
        if provider_id:
            query = query.where(ModelDef.provider_id == provider_id)
        
        if model_type:
            query = query.where(ModelDef.model_type == model_type)
        
        if params.active_only:
            query = query.where(ModelDef.is_active == True)
        
        # Order by default first, then by display name
        query = query.order_by(ModelDef.is_default.desc(), ModelDef.display_name)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Apply pagination
        query = query.offset((params.page - 1) * params.per_page).limit(params.per_page)
        result = await self.session.execute(query)
        models = result.scalars().all()
        
        return models, total or 0

    async def get_model(self, model_id: str) -> ModelDef | None:
        """Get model definition by ID."""
        result = await self.session.execute(
            select(ModelDef)
            .options(selectinload(ModelDef.provider))
            .where(ModelDef.id == model_id)
        )
        return result.scalar_one_or_none()

    async def get_model_by_name(self, provider_id: str, name: str) -> ModelDef | None:
        """Get model definition by provider and name."""
        result = await self.session.execute(
            select(ModelDef)
            .options(selectinload(ModelDef.provider))
            .where(ModelDef.provider_id == provider_id, ModelDef.name == name)
        )
        return result.scalar_one_or_none()

    async def create_model(self, model_data: ModelDefCreate) -> ModelDef:
        """Create a new model definition."""
        model = ModelDef(**model_data.model_dump())
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def update_model(
        self, model_id: str, model_data: ModelDefUpdate
    ) -> ModelDef | None:
        """Update a model definition."""
        model = await self.get_model(model_id)
        if not model:
            return None
        
        update_data = model_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model definition and its dependent embedding spaces."""
        # First delete all embedding spaces that depend on this model
        await self.session.execute(
            delete(EmbeddingSpace).where(EmbeddingSpace.model_id == model_id)
        )
        
        # Then delete the model
        result = await self.session.execute(
            delete(ModelDef).where(ModelDef.id == model_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def set_default_model(self, model_id: str) -> bool:
        """Set a model as default for its type."""
        model = await self.get_model(model_id)
        if not model:
            return False
        
        # First, unset current default for this model type
        await self.session.execute(
            update(ModelDef)
            .where(ModelDef.model_type == model.model_type, ModelDef.is_default == True)
            .values(is_default=False)
        )
        
        # Set new default
        result = await self.session.execute(
            update(ModelDef)
            .where(ModelDef.id == model_id)
            .values(is_default=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    # Embedding space methods
    async def list_embedding_spaces(
        self,
        model_id: str | None = None,
        params: ListParams = ListParams()
    ) -> tuple[Sequence[EmbeddingSpace], int]:
        """List embedding spaces with pagination."""
        query = select(EmbeddingSpace).options(
            selectinload(EmbeddingSpace.model).selectinload(ModelDef.provider)
        )
        
        if model_id:
            query = query.where(EmbeddingSpace.model_id == model_id)
        
        if params.active_only:
            query = query.where(EmbeddingSpace.is_active == True)
        
        # Order by default first, then by display name
        query = query.order_by(EmbeddingSpace.is_default.desc(), EmbeddingSpace.display_name)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)
        
        # Apply pagination
        query = query.offset((params.page - 1) * params.per_page).limit(params.per_page)
        result = await self.session.execute(query)
        spaces = result.scalars().all()
        
        return spaces, total or 0

    async def get_embedding_space(self, space_id: str) -> EmbeddingSpace | None:
        """Get embedding space by ID."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(ModelDef.provider)
            )
            .where(EmbeddingSpace.id == space_id)
        )
        return result.scalar_one_or_none()

    async def get_embedding_space_by_name(self, name: str) -> EmbeddingSpace | None:
        """Get embedding space by name."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(ModelDef.provider)
            )
            .where(EmbeddingSpace.name == name)
        )
        return result.scalar_one_or_none()

    async def get_embedding_space_by_table_name(self, table_name: str) -> EmbeddingSpace | None:
        """Get embedding space by table name."""
        result = await self.session.execute(
            select(EmbeddingSpace).where(EmbeddingSpace.table_name == table_name)
        )
        return result.scalar_one_or_none()

    async def create_embedding_space(self, space_data: EmbeddingSpaceCreate) -> EmbeddingSpace:
        """Create a new embedding space with backing table and index."""
        # Create the space record
        space = EmbeddingSpace(**space_data.model_dump())
        self.session.add(space)
        await self.session.flush()  # Get the ID
        
        try:
            # Create the backing table and index
            await self._create_embedding_table(space)
            
            await self.session.commit()
            await self.session.refresh(space)
            
            logger.info(
                "Created embedding space",
                space_id=space.id,
                space_name=space.name,
                table_name=space.table_name,
                dimensions=space.effective_dimensions
            )
            
            return space
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to create embedding space",
                space_name=space.name,
                error=str(e)
            )
            raise

    async def _create_embedding_table(self, space: EmbeddingSpace) -> None:
        """Create the physical embedding table and index."""
        # Get sync engine for table creation
        sync_engine = get_sync_engine()
        
        # Create the dynamic model and table
        model_class = get_embedding_model(
            space.table_name,
            space.effective_dimensions,
            sync_engine
        )
        
        # Configure index parameters
        index_config = space.index_config or {}
        
        if space.index_type == "hnsw":
            m = index_config.get("m", 16)
            ef_construction = index_config.get("ef_construction", 200)
        else:  # ivfflat
            m = 16  # not used for ivfflat
            ef_construction = index_config.get("lists", 100)
        
        # Create the index
        ensure_table_and_index(
            sync_engine,
            model_class,
            metric=space.distance_metric,
            m=m,
            ef_construction=ef_construction,
        )

    async def update_embedding_space(
        self, space_id: str, space_data: EmbeddingSpaceUpdate
    ) -> EmbeddingSpace | None:
        """Update an embedding space."""
        space = await self.get_embedding_space(space_id)
        if not space:
            return None
        
        update_data = space_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(space, field, value)
        
        await self.session.commit()
        await self.session.refresh(space)
        return space

    async def delete_embedding_space(self, space_id: str) -> bool:
        """Delete an embedding space (does not drop the table)."""
        result = await self.session.execute(
            delete(EmbeddingSpace).where(EmbeddingSpace.id == space_id)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def set_default_embedding_space(self, space_id: str) -> bool:
        """Set an embedding space as default."""
        # First, unset current default
        await self.session.execute(
            update(EmbeddingSpace)
            .where(EmbeddingSpace.is_default == True)
            .values(is_default=False)
        )
        
        # Set new default
        result = await self.session.execute(
            update(EmbeddingSpace)
            .where(EmbeddingSpace.id == space_id)
            .values(is_default=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    # Default lookups
    async def get_default_provider(self, model_type: ModelType) -> Provider | None:
        """Get the default provider for a model type."""
        result = await self.session.execute(
            select(Provider)
            .where(Provider.is_default == True, Provider.is_active == True)
        )
        return result.scalar_one_or_none()

    async def get_default_model(self, model_type: ModelType) -> ModelDef | None:
        """Get the default model for a type."""
        result = await self.session.execute(
            select(ModelDef)
            .options(selectinload(ModelDef.provider))
            .where(
                ModelDef.model_type == model_type,
                ModelDef.is_default == True,
                ModelDef.is_active == True
            )
        )
        return result.scalar_one_or_none()

    async def get_default_embedding_space(self) -> EmbeddingSpace | None:
        """Get the default embedding space."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(ModelDef.provider)
            )
            .where(
                EmbeddingSpace.is_default == True,
                EmbeddingSpace.is_active == True
            )
        )
        return result.scalar_one_or_none()