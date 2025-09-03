"""Caching layer for model registry performance optimization."""

import hashlib
from datetime import datetime, timedelta
from typing import Any

from chatter.models.registry import ModelType
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class InMemoryCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 300):
        """Initialize in-memory cache.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.cache = {}
        self.timestamps = {}
        self.default_ttl = default_ttl

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired.

        Args:
            key: Cache key

        Returns:
            True if expired, False otherwise
        """
        if key not in self.timestamps:
            return True

        expiry_time = self.timestamps[key]
        return datetime.now() > expiry_time

    def get(self, key: str) -> Any:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self.cache or self._is_expired(key):
            return None

        return self.cache[key]

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        ttl = ttl or self.default_ttl
        expiry_time = datetime.now() + timedelta(seconds=ttl)

        self.cache[key] = value
        self.timestamps[key] = expiry_time

    def delete(self, key: str) -> None:
        """Delete key from cache.

        Args:
            key: Cache key to delete
        """
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self.timestamps.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        now = datetime.now()
        expired_keys = [
            key for key, expiry in self.timestamps.items()
            if now > expiry
        ]

        for key in expired_keys:
            self.delete(key)

        return len(expired_keys)


class ModelRegistryCache:
    """Specialized cache for model registry data."""

    def __init__(self, cache_impl: InMemoryCache | None = None):
        """Initialize model registry cache.

        Args:
            cache_impl: Cache implementation to use
        """
        self.cache = cache_impl or InMemoryCache()

        # Cache TTL settings (in seconds)
        self.defaults_ttl = 300      # 5 minutes for defaults
        self.provider_ttl = 900      # 15 minutes for provider data
        self.model_ttl = 600         # 10 minutes for model data
        self.list_ttl = 180          # 3 minutes for list operations

    def _make_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Create a consistent cache key.

        Args:
            prefix: Cache key prefix
            *args: Positional arguments for key
            **kwargs: Keyword arguments for key

        Returns:
            Cache key string
        """
        # Create stable key from arguments
        key_parts = [prefix]
        key_parts.extend(str(arg) for arg in args)

        # Sort kwargs for consistency
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key_string = ":".join(key_parts)

        # Hash long keys to avoid memory issues
        if len(key_string) > 100:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            key_string = f"{prefix}:{key_hash}"

        return key_string

    # Default provider/model caching
    def get_default_provider(self, model_type: ModelType) -> str | None:
        """Get cached default provider ID.

        Args:
            model_type: Model type

        Returns:
            Cached provider ID or None
        """
        key = self._make_cache_key("default_provider", model_type.value)
        return self.cache.get(key)

    def set_default_provider(self, model_type: ModelType, provider_id: str) -> None:
        """Cache default provider ID.

        Args:
            model_type: Model type
            provider_id: Provider ID
        """
        key = self._make_cache_key("default_provider", model_type.value)
        self.cache.set(key, provider_id, self.defaults_ttl)

    def get_default_model(self, model_type: ModelType) -> str | None:
        """Get cached default model ID.

        Args:
            model_type: Model type

        Returns:
            Cached model ID or None
        """
        key = self._make_cache_key("default_model", model_type.value)
        return self.cache.get(key)

    def set_default_model(self, model_type: ModelType, model_id: str) -> None:
        """Cache default model ID.

        Args:
            model_type: Model type
            model_id: Model ID
        """
        key = self._make_cache_key("default_model", model_type.value)
        self.cache.set(key, model_id, self.defaults_ttl)

    def invalidate_defaults(self, model_type: ModelType | None = None) -> None:
        """Invalidate default caches.

        Args:
            model_type: Specific model type to invalidate, or None for all
        """
        if model_type:
            self.cache.delete(self._make_cache_key("default_provider", model_type.value))
            self.cache.delete(self._make_cache_key("default_model", model_type.value))
        else:
            # Clear all defaults - this is inefficient but safe
            # In production, use a more sophisticated cache that supports pattern matching
            for mt in ModelType:
                self.cache.delete(self._make_cache_key("default_provider", mt.value))
                self.cache.delete(self._make_cache_key("default_model", mt.value))

    # Provider data caching
    def get_provider(self, provider_id: str) -> dict | None:
        """Get cached provider data.

        Args:
            provider_id: Provider ID

        Returns:
            Cached provider data or None
        """
        key = self._make_cache_key("provider", provider_id)
        return self.cache.get(key)

    def set_provider(self, provider_id: str, provider_data: dict) -> None:
        """Cache provider data.

        Args:
            provider_id: Provider ID
            provider_data: Provider data dictionary
        """
        key = self._make_cache_key("provider", provider_id)
        self.cache.set(key, provider_data, self.provider_ttl)

    def invalidate_provider(self, provider_id: str) -> None:
        """Invalidate provider cache.

        Args:
            provider_id: Provider ID to invalidate
        """
        self.cache.delete(self._make_cache_key("provider", provider_id))

    # Model data caching
    def get_model(self, model_id: str) -> dict | None:
        """Get cached model data.

        Args:
            model_id: Model ID

        Returns:
            Cached model data or None
        """
        key = self._make_cache_key("model", model_id)
        return self.cache.get(key)

    def set_model(self, model_id: str, model_data: dict) -> None:
        """Cache model data.

        Args:
            model_id: Model ID
            model_data: Model data dictionary
        """
        key = self._make_cache_key("model", model_id)
        self.cache.set(key, model_data, self.model_ttl)

    def invalidate_model(self, model_id: str) -> None:
        """Invalidate model cache.

        Args:
            model_id: Model ID to invalidate
        """
        self.cache.delete(self._make_cache_key("model", model_id))

    # List operation caching
    def get_provider_list(
        self,
        provider_type: str | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list, int] | None:
        """Get cached provider list.

        Args:
            provider_type: Provider type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page

        Returns:
            Cached (providers, total) or None
        """
        key = self._make_cache_key(
            "provider_list",
            provider_type=provider_type,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return self.cache.get(key)

    def set_provider_list(
        self,
        provider_type: str | None,
        active_only: bool,
        page: int,
        per_page: int,
        providers: list,
        total: int,
    ) -> None:
        """Cache provider list.

        Args:
            provider_type: Provider type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page
            providers: Provider list
            total: Total count
        """
        key = self._make_cache_key(
            "provider_list",
            provider_type=provider_type,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        self.cache.set(key, (providers, total), self.list_ttl)

    def get_model_list(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
        active_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list, int] | None:
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
        key = self._make_cache_key(
            "model_list",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        return self.cache.get(key)

    def set_model_list(
        self,
        provider_id: str | None,
        model_type: ModelType | None,
        active_only: bool,
        page: int,
        per_page: int,
        models: list,
        total: int,
    ) -> None:
        """Cache model list.

        Args:
            provider_id: Provider ID filter
            model_type: Model type filter
            active_only: Active filter
            page: Page number
            per_page: Items per page
            models: Model list
            total: Total count
        """
        key = self._make_cache_key(
            "model_list",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
            active_only=active_only,
            page=page,
            per_page=per_page,
        )
        self.cache.set(key, (models, total), self.list_ttl)

    def invalidate_list_caches(
        self,
        provider_id: str | None = None,
        model_type: ModelType | None = None,
    ) -> None:
        """Invalidate list caches.

        Args:
            provider_id: Provider ID that was affected
            model_type: Model type that was affected
        """
        # In a production system, you'd want a more sophisticated cache
        # that can invalidate by patterns. For now, we clear all list caches
        # when any provider or model changes.

        # This is inefficient but ensures consistency
        self.cache.clear()

        logger.info(
            "Invalidated list caches",
            provider_id=provider_id,
            model_type=model_type.value if model_type else None,
        )

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        total_entries = len(self.cache.cache)
        expired_count = self.cache.cleanup_expired()

        return {
            "total_entries": total_entries,
            "expired_cleaned": expired_count,
            "current_entries": len(self.cache.cache),
        }


# Global cache instance
_registry_cache: ModelRegistryCache | None = None


def get_registry_cache() -> ModelRegistryCache:
    """Get the global model registry cache instance.

    Returns:
        ModelRegistryCache instance
    """
    global _registry_cache
    if _registry_cache is None:
        _registry_cache = ModelRegistryCache()
    return _registry_cache


def clear_registry_cache() -> None:
    """Clear the global registry cache."""
    global _registry_cache
    if _registry_cache:
        _registry_cache.cache.clear()


class CacheWarmer:
    """Utility to warm up cache with frequently accessed data."""

    def __init__(self, cache: ModelRegistryCache):
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
                provider = await service.get_default_provider(model_type)
                if provider:
                    self.cache.set_default_provider(model_type, provider.id)

                model = await service.get_default_model(model_type)
                if model:
                    self.cache.set_default_model(model_type, model.id)

            except Exception as e:
                logger.warning(f"Failed to warm defaults for {model_type}: {e}")

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
                    'id': provider.id,
                    'name': provider.name,
                    'display_name': provider.display_name,
                    'provider_type': provider.provider_type,
                    'is_active': provider.is_active,
                    'is_default': provider.is_default,
                }
                provider_list.append(provider_dict)
                self.cache.set_provider(provider.id, provider_dict)

            self.cache.set_provider_list(
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
                    'id': model.id,
                    'name': model.name,
                    'display_name': model.display_name,
                    'model_type': model.model_type,
                    'provider_id': model.provider_id,
                    'is_active': model.is_active,
                    'is_default': model.is_default,
                }
                model_list.append(model_dict)
                self.cache.set_model(model.id, model_dict)

            self.cache.set_model_list(
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
