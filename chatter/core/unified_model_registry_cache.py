"""Unified model registry cache using the new cache interface."""

from typing import Any

from chatter.core.cache_factory import get_model_registry_cache
from chatter.core.cache_interface import CacheInterface
from chatter.models.registry import ModelType
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class UnifiedModelRegistryCache:
    """Unified model registry cache using the new cache interface.

    This replaces the old ModelRegistryCache with a version that uses
    the unified cache system underneath.
    """

    def __init__(self, cache: CacheInterface | None = None):
        """Initialize unified model registry cache.

        Args:
            cache: Cache implementation to use (auto-created if None)
        """
        self.cache = cache or get_model_registry_cache()

        # Cache TTL settings (in seconds) - these match the original implementation
        self.defaults_ttl = 300  # 5 minutes for defaults
        self.provider_ttl = 900  # 15 minutes for provider data
        self.model_ttl = 600  # 10 minutes for model data
        self.list_ttl = 180  # 3 minutes for list operations

        logger.debug("Unified model registry cache initialized")

    # Default provider/model caching

    async def get_default_provider(
        self, model_type: ModelType
    ) -> str | None:
        """Get cached default provider ID.

        Args:
            model_type: Model type

        Returns:
            Cached provider ID or None
        """
        key = self.cache.make_key("default_provider", model_type.value)
        return await self.cache.get(key)

    async def set_default_provider(
        self, model_type: ModelType, provider_id: str
    ) -> bool:
        """Cache default provider ID.

        Args:
            model_type: Model type
            provider_id: Provider ID

        Returns:
            True if successful
        """
        key = self.cache.make_key("default_provider", model_type.value)
        return await self.cache.set(key, provider_id, self.defaults_ttl)

    async def get_default_model(
        self, model_type: ModelType
    ) -> str | None:
        """Get cached default model ID.

        Args:
            model_type: Model type

        Returns:
            Cached model ID or None
        """
        key = self.cache.make_key("default_model", model_type.value)
        return await self.cache.get(key)

    async def set_default_model(
        self, model_type: ModelType, model_id: str
    ) -> bool:
        """Cache default model ID.

        Args:
            model_type: Model type
            model_id: Model ID

        Returns:
            True if successful
        """
        key = self.cache.make_key("default_model", model_type.value)
        return await self.cache.set(key, model_id, self.defaults_ttl)

    async def invalidate_defaults(
        self, model_type: ModelType | None = None
    ) -> bool:
        """Invalidate default caches.

        Args:
            model_type: Specific model type to invalidate, or None for all

        Returns:
            True if successful
        """
        if model_type:
            # Invalidate specific model type
            provider_key = self.cache.make_key(
                "default_provider", model_type.value
            )
            model_key = self.cache.make_key(
                "default_model", model_type.value
            )

            provider_success = await self.cache.delete(provider_key)
            model_success = await self.cache.delete(model_key)

            return provider_success or model_success
        else:
            # Invalidate all defaults
            success_count = 0
            for mt in ModelType:
                if await self.invalidate_defaults(mt):
                    success_count += 1

            return success_count > 0

    # Provider data caching

    async def get_provider(
        self, provider_id: str
    ) -> dict[str, Any] | None:
        """Get cached provider data.

        Args:
            provider_id: Provider ID

        Returns:
            Cached provider data or None
        """
        key = self.cache.make_key("provider", provider_id)
        return await self.cache.get(key)

    async def set_provider(
        self, provider_id: str, provider_data: dict[str, Any]
    ) -> bool:
        """Cache provider data.

        Args:
            provider_id: Provider ID
            provider_data: Provider data dictionary

        Returns:
            True if successful
        """
        key = self.cache.make_key("provider", provider_id)
        return await self.cache.set(
            key, provider_data, self.provider_ttl
        )

    async def invalidate_provider(self, provider_id: str) -> bool:
        """Invalidate provider cache.

        Args:
            provider_id: Provider ID to invalidate

        Returns:
            True if successful
        """
        key = self.cache.make_key("provider", provider_id)
        return await self.cache.delete(key)

    # Model data caching

    async def get_model(self, model_id: str) -> dict[str, Any] | None:
        """Get cached model data.

        Args:
            model_id: Model ID

        Returns:
            Cached model data or None
        """
        key = self.cache.make_key("model", model_id)
        return await self.cache.get(key)

    async def set_model(
        self, model_id: str, model_data: dict[str, Any]
    ) -> bool:
        """Cache model data.

        Args:
            model_id: Model ID
            model_data: Model data dictionary

        Returns:
            True if successful
        """
        key = self.cache.make_key("model", model_id)
        return await self.cache.set(key, model_data, self.model_ttl)

    async def invalidate_model(self, model_id: str) -> bool:
        """Invalidate model cache.

        Args:
            model_id: Model ID to invalidate

        Returns:
            True if successful
        """
        key = self.cache.make_key("model", model_id)
        return await self.cache.delete(key)

    # List operation caching

    async def get_provider_list(
        self,
        provider_type: str | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[dict], int] | None:
        """Get cached provider list.

        Args:
            provider_type: Provider type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page

        Returns:
            Cached (providers, total) or None
        """
        key = self.cache.make_key(
            "provider_list",
            provider_type=provider_type,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return await self.cache.get(key)

    async def set_provider_list(
        self,
        provider_type: str | None,
        active_only: bool,
        page: int,
        per_page: int,
        providers: list[dict],
        total: int,
    ) -> bool:
        """Cache provider list.

        Args:
            provider_type: Provider type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page
            providers: Provider list
            total: Total count

        Returns:
            True if successful
        """
        key = self.cache.make_key(
            "provider_list",
            provider_type=provider_type,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return await self.cache.set(
            key, (providers, total), self.list_ttl
        )

    async def get_model_list(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[dict], int] | None:
        """Get cached model list.

        Args:
            provider_id: Provider ID filter
            model_type: Model type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page

        Returns:
            Cached (models, total) or None
        """
        key = self.cache.make_key(
            "model_list",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return await self.cache.get(key)

    async def set_model_list(
        self,
        provider_id: str | None,
        model_type: ModelType | None,
        active_only: bool,
        page: int,
        per_page: int,
        models: list[dict],
        total: int,
    ) -> bool:
        """Cache model list.

        Args:
            provider_id: Provider ID filter
            model_type: Model type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page
            models: Model list
            total: Total count

        Returns:
            True if successful
        """
        key = self.cache.make_key(
            "model_list",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return await self.cache.set(key, (models, total), self.list_ttl)

    async def invalidate_list_caches(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
    ) -> bool:
        """Invalidate list caches.

        Args:
            provider_id: Provider ID that was affected
            model_type: Model type that was affected

        Returns:
            True if successful
        """
        # Get all keys matching list patterns
        provider_keys = await self.cache.keys("provider_list")
        model_keys = await self.cache.keys("model_list")

        # Delete all list caches (more efficient than pattern matching for now)
        # In a production system with Redis, you could use pattern-based deletion
        success_count = 0

        for key in provider_keys + model_keys:
            if await self.cache.delete(key):
                success_count += 1

        logger.info(
            "Invalidated list caches",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
            invalidated_count=success_count,
        )

        return success_count > 0

    async def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        stats = await self.cache.get_stats()
        return {
            "total_entries": stats.total_entries,
            "cache_hits": stats.cache_hits,
            "cache_misses": stats.cache_misses,
            "hit_rate": stats.hit_rate,
            "memory_usage": stats.memory_usage,
            "evictions": stats.evictions,
            "errors": stats.errors,
        }

    async def clear_cache(self) -> bool:
        """Clear all cached data.

        Returns:
            True if successful
        """
        return await self.cache.clear()

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on cache.

        Returns:
            Health status information
        """
        return await self.cache.health_check()


class CacheWarmer:
    """Utility to warm up cache with frequently accessed data."""

    def __init__(self, cache: UnifiedModelRegistryCache):
        """Initialize cache warmer.

        Args:
            cache: Cache instance to warm
        """
        self.cache = cache

    async def warm_defaults_cache(self, session) -> None:
        """Warm up the defaults cache.

        Args:
            session: Database session
        """
        from chatter.core.model_registry import ModelRegistryService

        service = ModelRegistryService(session)

        # Warm default providers for each model type
        for model_type in ModelType:
            try:
                provider = await service.get_default_provider(
                    model_type
                )
                if provider:
                    await self.cache.set_default_provider(
                        model_type, provider.id
                    )

                model = await service.get_default_model(model_type)
                if model:
                    await self.cache.set_default_model(
                        model_type, model.id
                    )

            except Exception as e:
                logger.warning(
                    f"Failed to warm defaults for {model_type}: {e}"
                )

    async def warm_frequent_data_cache(self, session) -> None:
        """Warm up cache with frequently accessed data.

        Args:
            session: Database session
        """
        from chatter.core.model_registry import ModelRegistryService

        service = ModelRegistryService(session)

        try:
            # Cache first page of active providers
            providers, total = await service.list_providers()
            provider_list = []
            for provider in providers:
                provider_dict = {
                    "id": provider.id,
                    "name": provider.name,
                    "display_name": provider.display_name,
                    "provider_type": provider.provider_type,
                    "is_active": provider.is_active,
                    "is_default": provider.is_default,
                }
                provider_list.append(provider_dict)
                await self.cache.set_provider(
                    provider.id, provider_dict
                )

            await self.cache.set_provider_list(
                provider_type=None,
                active_only=True,
                page=1,
                per_page=20,
                providers=provider_list,
                total=total,
            )

            # Cache first page of active models
            models, total = await service.list_models()
            model_list = []
            for model in models:
                model_dict = {
                    "id": model.id,
                    "name": model.name,
                    "display_name": model.display_name,
                    "model_type": model.model_type,
                    "provider_id": model.provider_id,
                    "is_active": model.is_active,
                    "is_default": model.is_default,
                }
                model_list.append(model_dict)
                await self.cache.set_model(model.id, model_dict)

            await self.cache.set_model_list(
                provider_id=None,
                model_type=None,
                active_only=True,
                page=1,
                per_page=20,
                models=model_list,
                total=total,
            )

        except Exception as e:
            logger.warning(f"Failed to warm frequent data cache: {e}")

    async def warm_all_caches(self, session) -> None:
        """Warm all caches.

        Args:
            session: Database session
        """
        await self.warm_defaults_cache(session)
        await self.warm_frequent_data_cache(session)


# Global cache instance
_registry_cache: UnifiedModelRegistryCache | None = None


def get_registry_cache() -> UnifiedModelRegistryCache:
    """Get the global unified model registry cache instance.

    Returns:
        UnifiedModelRegistryCache instance
    """
    global _registry_cache
    if _registry_cache is None:
        _registry_cache = UnifiedModelRegistryCache()
    return _registry_cache


def clear_registry_cache() -> None:
    """Clear the global registry cache."""
    global _registry_cache
    if _registry_cache:
        # Create new instance to fully reset
        _registry_cache = UnifiedModelRegistryCache()
