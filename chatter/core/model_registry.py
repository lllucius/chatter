"""Service layer for provider/model/embedding registry."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from sqlalchemy import create_engine, delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.config import settings
from chatter.core.dynamic_embeddings import (
    ensure_table_and_index,
    get_embedding_model,
)
from chatter.models.registry import (
    EmbeddingSpace,
    ModelDef,
    ModelType,
    Provider,
)
from chatter.schemas.model_registry import (
    EmbeddingSpaceCreate,
    EmbeddingSpaceUpdate,
    ModelDefCreate,
    ModelDefUpdate,
    ProviderCreate,
    ProviderUpdate,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


def get_sync_engine():
    """Create a synchronous engine for table creation operations."""
    # Convert async URL to sync URL
    sync_url = settings.database_url.replace("+asyncpg", "").replace(
        "+aiopg", ""
    )
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
        """Initialize the model registry service.

        Args:
            session: Database session
        """
        self.session = session
        # Import here to avoid circular imports
        from chatter.core.cache_factory import get_general_cache
        from chatter.utils.performance import get_performance_metrics

        self.cache = get_general_cache()  # Use simplified general cache
        self.metrics = get_performance_metrics()

    async def _clear_cache(self, reason: str = "data_changed") -> None:
        """Clear cache when data changes.

        Args:
            reason: Reason for cache clear (for logging)
        """
        try:
            await self.cache.clear()
            logger.debug("Cleared cache", reason=reason)
        except Exception as e:
            logger.warning(
                "Failed to clear cache", error=str(e), reason=reason
            )

    async def _invalidate_dependent_service_caches(
        self, provider_name: str | None = None
    ) -> None:
        """Invalidate caches in dependent services when providers/models change.

        Args:
            provider_name: Specific provider to invalidate, or None to invalidate all
        """
        try:
            # Import here to avoid circular imports
            from chatter.services.embeddings import EmbeddingService
            from chatter.services.llm import LLMService

            # Create temporary service instances to call invalidation
            # Note: These don't need a session for cache invalidation operations
            embedding_service = EmbeddingService()
            llm_service = LLMService()

            # Invalidate provider caches in dependent services
            await embedding_service.invalidate_provider_cache(
                provider_name
            )
            await llm_service.invalidate_provider_cache(provider_name)

            logger.debug(
                "Invalidated dependent service caches",
                provider_name=provider_name or "all",
            )
        except Exception as e:
            # Don't fail the main operation if cache invalidation fails
            logger.warning(
                "Failed to invalidate dependent service caches",
                error=str(e),
                provider_name=provider_name,
            )

    # Provider methods
    async def list_providers(
        self, params: ListParams = ListParams()
    ) -> tuple[Sequence[Provider], int]:
        """List providers with pagination."""
        # Simplified: removed complex caching, direct database query

        # Use performance metrics
        async with self.metrics.measure_query("list_providers"):
            query = select(Provider)

            if params.active_only:
                query = query.where(Provider.is_active)

            # Order by default first, then by display name
            query = query.order_by(
                Provider.is_default.desc(), Provider.display_name
            )

            # Use optimized count query
            count_query = select(func.count(Provider.id))
            if params.active_only:
                count_query = count_query.where(Provider.is_active)
            total = await self.session.scalar(count_query)

            # Apply pagination
            query = query.offset(
                (params.page - 1) * params.per_page
            ).limit(params.per_page)
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

    async def create_provider(
        self, provider_data: ProviderCreate
    ) -> Provider:
        """Create a new provider."""
        # Defensive logging to help debug field saving issues
        logger.debug(
            "Creating provider",
            name=provider_data.name,
            description=provider_data.description,
            api_key_required=provider_data.api_key_required,
            is_active=provider_data.is_active,
        )

        provider = Provider(**provider_data.model_dump())
        self.session.add(provider)
        await self.session.commit()
        await self.session.refresh(provider)

        # Invalidate list caches since a new provider is added
        await self._clear_cache("data_changed")

        # Invalidate dependent service caches
        await self._invalidate_dependent_service_caches()

        # Log the created provider to verify fields were saved
        logger.debug(
            "Provider created successfully",
            id=provider.id,
            description=provider.description,
            api_key_required=provider.api_key_required,
            is_active=provider.is_active,
        )

        return provider

    async def update_provider(
        self, provider_id: str, provider_data: ProviderUpdate
    ) -> Provider | None:
        """Update a provider."""
        provider = await self.get_provider(provider_id)
        if not provider:
            return None

        update_data = provider_data.model_dump(exclude_unset=True)

        # Defensive logging to help debug field saving issues
        logger.debug(
            "Updating provider",
            provider_id=provider_id,
            update_fields=list(update_data.keys()),
            description=update_data.get("description"),
            api_key_required=update_data.get("api_key_required"),
            is_active=update_data.get("is_active"),
        )

        # Validate that we're not trying to update critical read-only fields
        if "name" in update_data or "provider_type" in update_data:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                "Cannot update provider name or type after creation"
            )

        for field, value in update_data.items():
            setattr(provider, field, value)

        # Handle cascading status changes
        if "is_active" in update_data:
            await self._handle_provider_status_change(
                provider, update_data["is_active"]
            )

        await self.session.commit()
        await self.session.refresh(provider)

        # Invalidate provider cache and list caches after update
        await self._clear_cache("data_changed")
        await self._clear_cache("data_changed")

        # Invalidate dependent service caches for this specific provider
        await self._invalidate_dependent_service_caches(provider.name)

        # Log the updated provider to verify fields were saved
        logger.debug(
            "Provider updated successfully",
            id=provider.id,
            description=provider.description,
            api_key_required=provider.api_key_required,
            is_active=provider.is_active,
        )

        return provider

    async def _handle_provider_status_change(
        self, provider: Provider, is_active: bool
    ) -> None:
        """Handle cascading effects when provider status changes.

        Args:
            provider: The provider being updated
            is_active: New active status
        """
        if not is_active:
            # If provider is being deactivated, deactivate all its models
            logger.info(
                f"Deactivating all models for provider {provider.name} "
                f"due to provider deactivation"
            )

            await self.session.execute(
                update(ModelDef)
                .where(ModelDef.provider_id == provider.id)
                .values(is_active=False, is_default=False)
            )

            # Also deactivate all embedding spaces for these models
            await self.session.execute(
                update(EmbeddingSpace)
                .where(
                    EmbeddingSpace.model_id.in_(
                        select(ModelDef.id).where(
                            ModelDef.provider_id == provider.id
                        )
                    )
                )
                .values(is_active=False, is_default=False)
            )

            logger.info(
                f"Deactivated all models and embedding spaces for provider {provider.name}"
            )

    async def delete_provider(self, provider_id: str) -> bool:
        """Delete a provider and its dependent models and embedding spaces."""
        # Get models before deletion for cache invalidation
        models_result = await self.session.execute(
            select(ModelDef).where(ModelDef.provider_id == provider_id)
        )
        models = models_result.scalars().all()

        # Delete all embedding spaces for all models under this provider
        for model in models:
            await self.session.execute(
                delete(EmbeddingSpace).where(
                    EmbeddingSpace.model_id == model.id
                )
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

        if result.rowcount > 0:
            # Get provider name before we lose access to models data
            provider_name = None
            if models:
                # Get provider for dependent cache invalidation
                provider_result = await self.session.execute(
                    select(Provider).where(Provider.id == provider_id)
                )
                if provider_obj := provider_result.scalar_one_or_none():
                    provider_name = provider_obj.name

            # Invalidate provider cache
            await self._clear_cache("data_changed")

            # Invalidate model caches for all deleted models
            for _model in models:
                await self._clear_cache("data_changed")

            # Invalidate list caches and defaults for all model types that might be affected
            await self._clear_cache("data_changed")
            for model in models:
                if model.is_default:
                    await self._clear_cache("data_changed")

            # Invalidate dependent service caches for this specific provider
            if provider_name:
                await self._invalidate_dependent_service_caches(
                    provider_name
                )

        return result.rowcount > 0

    async def set_default_provider(
        self, provider_id: str, model_type: ModelType
    ) -> bool:
        """Set a provider as default for a model type."""
        # Verify the provider exists and supports the model type
        provider = await self.get_provider(provider_id)
        if not provider:
            return False

        # Check if provider has models of the specified type
        models_of_type = await self.session.execute(
            select(ModelDef).where(
                ModelDef.provider_id == provider_id,
                ModelDef.model_type == model_type,
                ModelDef.is_active,
            )
        )
        if not models_of_type.scalars().first():
            # Provider doesn't have models of this type, cannot be default
            return False

        # First, unset current default for this model type by finding
        # all providers that have default models of this type
        current_default_models = await self.session.execute(
            select(ModelDef.provider_id)
            .where(
                ModelDef.model_type == model_type,
                ModelDef.is_default,
                ModelDef.is_active,
            )
            .distinct()
        )
        current_provider_ids = [
            row[0] for row in current_default_models.fetchall()
        ]

        if current_provider_ids:
            await self.session.execute(
                update(Provider)
                .where(Provider.id.in_(current_provider_ids))
                .values(is_default=False)
            )

        # Set new default provider
        result = await self.session.execute(
            update(Provider)
            .where(Provider.id == provider_id)
            .values(is_default=True)
        )

        # Also set one of its models as default for this type if none exists
        default_model = await self.session.execute(
            select(ModelDef).where(
                ModelDef.provider_id == provider_id,
                ModelDef.model_type == model_type,
                ModelDef.is_default,
                ModelDef.is_active,
            )
        )
        if not default_model.scalars().first():
            # Set the first active model as default
            first_model = await self.session.execute(
                select(ModelDef)
                .where(
                    ModelDef.provider_id == provider_id,
                    ModelDef.model_type == model_type,
                    ModelDef.is_active,
                )
                .limit(1)
            )
            if first_model_obj := first_model.scalar_one_or_none():
                await self.session.execute(
                    update(ModelDef)
                    .where(ModelDef.id == first_model_obj.id)
                    .values(is_default=True)
                )

        await self.session.commit()

        # Invalidate defaults cache for this model type
        await self._clear_cache("data_changed")

        # Also invalidate list caches as provider defaults may affect lists
        await self._clear_cache("data_changed")

        # Invalidate dependent service caches
        await self._invalidate_dependent_service_caches()

        return result.rowcount > 0

    # Model definition methods
    async def list_models(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
        params: ListParams = ListParams(),
    ) -> tuple[Sequence[ModelDef], int]:
        """List model definitions with pagination."""
        query = select(ModelDef).options(
            selectinload(ModelDef.provider)
        )

        if provider_id:
            query = query.where(ModelDef.provider_id == provider_id)

        if model_type:
            query = query.where(ModelDef.model_type == model_type)

        if params.active_only:
            # Filter for active models AND active providers
            query = query.join(Provider).where(
                ModelDef.is_active, Provider.is_active
            )

        # Order by default first, then by display name
        query = query.order_by(
            ModelDef.is_default.desc(), ModelDef.display_name
        )

        # Get total count efficiently using the same filters
        count_query = select(func.count(ModelDef.id))

        if provider_id:
            count_query = count_query.where(
                ModelDef.provider_id == provider_id
            )

        if model_type:
            count_query = count_query.where(
                ModelDef.model_type == model_type
            )

        if params.active_only:
            # Filter for active models AND active providers
            count_query = count_query.join(Provider).where(
                ModelDef.is_active, Provider.is_active
            )

        total = await self.session.scalar(count_query)

        # Apply pagination
        query = query.offset((params.page - 1) * params.per_page).limit(
            params.per_page
        )
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

    async def get_model_by_name(
        self, provider_id: str, name: str
    ) -> ModelDef | None:
        """Get model definition by provider and name."""
        result = await self.session.execute(
            select(ModelDef)
            .options(selectinload(ModelDef.provider))
            .where(
                ModelDef.provider_id == provider_id,
                ModelDef.name == name,
            )
        )
        return result.scalar_one_or_none()

    async def create_model(
        self, model_data: ModelDefCreate
    ) -> ModelDef:
        """Create a new model definition."""
        # Validate that provider exists
        provider = await self.get_provider(model_data.provider_id)
        if not provider:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Provider with ID {model_data.provider_id} not found"
            )

        # Validate that provider is active
        if not provider.is_active:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Provider {provider.name} is not active"
            )

        model = ModelDef(**model_data.model_dump())

        # Validate model configuration consistency
        await self._validate_model_consistency(model)

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        # Invalidate list caches since a new model is added
        await self._clear_cache("list_changed")

        # Invalidate dependent service caches for models
        await self._invalidate_dependent_service_caches()

        return model

    async def update_model(
        self, model_id: str, model_data: ModelDefUpdate
    ) -> ModelDef | None:
        """Update a model definition."""
        model = await self.get_model(model_id)
        if not model:
            return None

        update_data = model_data.model_dump(exclude_unset=True)

        # Validate that we're not trying to update critical read-only fields
        if (
            "name" in update_data
            or "model_type" in update_data
            or "provider_id" in update_data
        ):
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                "Cannot update model name, type, or provider after creation"
            )

        # Validate dimension changes for embedding models
        if (
            "dimensions" in update_data
            and model.model_type == ModelType.EMBEDDING
        ):
            # Check if there are existing embedding spaces using this model
            existing_spaces = await self.session.execute(
                select(EmbeddingSpace).where(
                    EmbeddingSpace.model_id == model_id,
                    EmbeddingSpace.is_active,
                )
            )
            if existing_spaces.scalars().first():
                from chatter.core.exceptions import ValidationError

                raise ValidationError(
                    "Cannot change dimensions of embedding model that has active embedding spaces"
                )

        # Validate if trying to deactivate the model
        if "is_active" in update_data and not update_data["is_active"]:
            await self._validate_deactivation_allowed(model)

        for field, value in update_data.items():
            setattr(model, field, value)

        await self.session.commit()
        await self.session.refresh(model)

        # Invalidate model cache and list caches after update
        await self._clear_cache("data_changed")
        await self._clear_cache("list_changed")

        # If default status changed, invalidate defaults cache
        if "is_default" in update_data:
            await self._clear_cache("data_changed")

        # Invalidate dependent service caches for models
        await self._invalidate_dependent_service_caches()

        return model

    async def delete_model(self, model_id: str) -> bool:
        """Delete a model definition and its dependent embedding spaces."""
        # Get the model before deletion for cache invalidation
        model = await self.get_model(model_id)
        if not model:
            return False

        # First delete all embedding spaces that depend on this model
        await self.session.execute(
            delete(EmbeddingSpace).where(
                EmbeddingSpace.model_id == model_id
            )
        )

        # Then delete the model
        result = await self.session.execute(
            delete(ModelDef).where(ModelDef.id == model_id)
        )
        await self.session.commit()

        if result.rowcount > 0:
            # Invalidate model cache
            await self._clear_cache("data_changed")

            # Invalidate list caches
            await self._clear_cache("list_changed")

            # If this was a default model, invalidate defaults
            if model.is_default:
                await self._clear_cache("data_changed")

            # Invalidate dependent service caches for models
            await self._invalidate_dependent_service_caches()

        return result.rowcount > 0

    async def set_default_model(self, model_id: str) -> bool:
        """Set a model as default for its type."""
        model = await self.get_model(model_id)
        if not model:
            return False

        # First, unset current default for this model type
        await self.session.execute(
            update(ModelDef)
            .where(
                ModelDef.model_type == model.model_type,
                ModelDef.is_default,
            )
            .values(is_default=False)
        )

        # Set new default
        result = await self.session.execute(
            update(ModelDef)
            .where(ModelDef.id == model_id)
            .values(is_default=True)
        )
        await self.session.commit()

        # Invalidate defaults cache for this model type
        await self._clear_cache("data_changed")

        # Invalidate dependent service caches for models
        await self._invalidate_dependent_service_caches()

        return result.rowcount > 0

    # Embedding space methods
    async def list_embedding_spaces(
        self,
        model_id: str | None = None,
        params: ListParams = ListParams(),
    ) -> tuple[Sequence[EmbeddingSpace], int]:
        """List embedding spaces with pagination."""
        query = select(EmbeddingSpace).options(
            selectinload(EmbeddingSpace.model).selectinload(
                ModelDef.provider
            )
        )

        if model_id:
            query = query.where(EmbeddingSpace.model_id == model_id)

        if params.active_only:
            query = query.where(EmbeddingSpace.is_active)

        # Order by default first, then by display name
        query = query.order_by(
            EmbeddingSpace.is_default.desc(),
            EmbeddingSpace.display_name,
        )

        # Get total count efficiently using the same filters
        count_query = select(func.count(EmbeddingSpace.id))

        if model_id:
            count_query = count_query.where(
                EmbeddingSpace.model_id == model_id
            )

        if params.active_only:
            count_query = count_query.where(EmbeddingSpace.is_active)

        total = await self.session.scalar(count_query)

        # Apply pagination
        query = query.offset((params.page - 1) * params.per_page).limit(
            params.per_page
        )
        result = await self.session.execute(query)
        spaces = result.scalars().all()

        return spaces, total or 0

    async def _validate_model_consistency(
        self, model: ModelDef
    ) -> None:
        """Validate that model configuration is consistent."""
        # Embedding models must have dimensions
        if (
            model.model_type == ModelType.EMBEDDING
            and not model.dimensions
        ):
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                "Embedding models must specify dimensions"
            )

        # LLM models should not have dimensions
        if model.model_type == ModelType.LLM and model.dimensions:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                "LLM models should not specify dimensions"
            )

        # Validate token limits are reasonable
        if model.max_tokens and model.max_tokens <= 0:
            from chatter.core.exceptions import ValidationError

            raise ValidationError("max_tokens must be positive")

        if model.context_length and model.context_length <= 0:
            from chatter.core.exceptions import ValidationError

            raise ValidationError("context_length must be positive")

        # Validate batch settings
        if model.max_batch_size and model.max_batch_size <= 0:
            from chatter.core.exceptions import ValidationError

            raise ValidationError("max_batch_size must be positive")

        if model.max_batch_size and not model.supports_batch:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                "max_batch_size specified but supports_batch is False"
            )

    async def _validate_deactivation_allowed(
        self, model: ModelDef
    ) -> None:
        """Validate that model can be deactivated."""
        if not model.is_active:
            return  # Already inactive

        # Check if this is the only active model of its type for this provider
        active_models = await self.session.execute(
            select(func.count()).where(
                ModelDef.provider_id == model.provider_id,
                ModelDef.model_type == model.model_type,
                ModelDef.is_active,
                ModelDef.id != model.id,
            )
        )
        count = active_models.scalar() or 0

        if count == 0:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Cannot deactivate the last active {model.model_type} model for provider {model.provider.name}"
            )

    async def get_embedding_space(
        self, space_id: str
    ) -> EmbeddingSpace | None:
        """Get embedding space by ID."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(
                    ModelDef.provider
                )
            )
            .where(EmbeddingSpace.id == space_id)
        )
        return result.scalar_one_or_none()

    async def get_embedding_space_by_name(
        self, name: str
    ) -> EmbeddingSpace | None:
        """Get embedding space by name."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(
                    ModelDef.provider
                )
            )
            .where(EmbeddingSpace.name == name)
        )
        return result.scalar_one_or_none()

    async def get_embedding_space_by_table_name(
        self, table_name: str
    ) -> EmbeddingSpace | None:
        """Get embedding space by table name."""
        result = await self.session.execute(
            select(EmbeddingSpace).where(
                EmbeddingSpace.table_name == table_name
            )
        )
        return result.scalar_one_or_none()

    async def create_embedding_space(
        self, space_data: EmbeddingSpaceCreate
    ) -> EmbeddingSpace:
        """Create a new embedding space with backing table and index."""
        # Validate that model exists and is an embedding model
        model = await self.get_model(space_data.model_id)
        if not model:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Model with ID {space_data.model_id} not found"
            )

        if model.model_type != ModelType.EMBEDDING:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Model {model.name} is not an embedding model"
            )

        if not model.is_active:
            from chatter.core.exceptions import ValidationError

            raise ValidationError(f"Model {model.name} is not active")

        # Validate dimensions match
        if (
            model.dimensions
            and space_data.base_dimensions != model.dimensions
        ):
            from chatter.core.exceptions import ValidationError

            raise ValidationError(
                f"Base dimensions {space_data.base_dimensions} do not match model dimensions {model.dimensions}"
            )

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
                dimensions=space.effective_dimensions,
            )

            return space
        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to create embedding space",
                space_name=space.name,
                error=str(e),
            )
            raise

    async def _create_embedding_table(
        self, space: EmbeddingSpace
    ) -> None:
        """Create the physical embedding table and index."""
        # Get sync engine for table creation
        sync_engine = get_sync_engine()

        # Create the dynamic model and table
        model_class = get_embedding_model(
            space.table_name, space.effective_dimensions, sync_engine
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
            .where(EmbeddingSpace.is_default)
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
    async def get_default_provider(
        self, model_type: ModelType
    ) -> Provider | None:
        """Get the default provider for a model type with caching."""
        # Check cache first
        cache_key = self.cache.make_key(
            "default_provider", model_type.value
        )
        cached_provider_id = await self.cache.get(cache_key)

        if cached_provider_id:
            provider = await self.get_provider(cached_provider_id)
            if provider and provider.is_active:
                return provider
            else:
                # Cache is stale, remove it
                await self.cache.delete(cache_key)
                await self._clear_cache("data_changed")

        # Use performance metrics
        async with self.metrics.measure_query("get_default_provider"):
            # Find provider that has default models of the specified type
            # Use explicit join condition to avoid JSON comparison issues
            result = await self.session.execute(
                select(Provider)
                .join(ModelDef, Provider.id == ModelDef.provider_id)
                .where(
                    ModelDef.model_type == model_type,
                    ModelDef.is_default,
                    ModelDef.is_active,
                    Provider.is_active,
                    Provider.is_default,
                )
                .distinct(
                    Provider.id
                )  # DISTINCT on ID only to avoid JSON comparison
                .limit(1)  # We only need one result
            )
            provider = result.scalar_one_or_none()

            # Cache the result
            if provider:
                cache_key = self.cache.make_key(
                    "default_provider", model_type.value
                )
                await self.cache.set(
                    cache_key, provider.id, 1800
                )  # 30 minutes

            return provider

    async def get_default_model(
        self, model_type: ModelType
    ) -> ModelDef | None:
        """Get the default model for a type with caching."""
        # Check cache first
        cache_key = self.cache.make_key(
            "default_model", model_type.value
        )
        cached_model_id = await self.cache.get(cache_key)

        if cached_model_id:
            model = await self.get_model(cached_model_id)
            if model and model.is_active:
                return model
            else:
                # Cache is stale, remove it
                await self.cache.delete(cache_key)

        # Use performance metrics
        async with self.metrics.measure_query("get_default_model"):
            result = await self.session.execute(
                select(ModelDef)
                .options(selectinload(ModelDef.provider))
                .where(
                    ModelDef.model_type == model_type,
                    ModelDef.is_default,
                    ModelDef.is_active,
                )
            )
            model = result.scalar_one_or_none()

            # Cache the result
            if model:
                cache_key = self.cache.make_key(
                    "default_model", model_type.value
                )
                await self.cache.set(
                    cache_key, model.id, 1800
                )  # 30 minutes

            return model

    async def get_default_embedding_space(
        self,
    ) -> EmbeddingSpace | None:
        """Get the default embedding space."""
        result = await self.session.execute(
            select(EmbeddingSpace)
            .options(
                selectinload(EmbeddingSpace.model).selectinload(
                    ModelDef.provider
                )
            )
            .where(EmbeddingSpace.is_default, EmbeddingSpace.is_active)
        )
        return result.scalar_one_or_none()
