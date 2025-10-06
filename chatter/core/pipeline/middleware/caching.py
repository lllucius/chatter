"""Caching middleware for workflow pipeline.

This middleware provides result caching to avoid redundant workflow executions.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

from chatter.core.pipeline.base import ExecutionContext, ExecutionResult, Middleware
from chatter.utils.logging import get_logger

if TYPE_CHECKING:
    from collections.abc import Callable
    from chatter.core.workflow_node_factory import Workflow

logger = get_logger(__name__)


class CachingMiddleware(Middleware):
    """Middleware for workflow result caching.
    
    This middleware:
    - Generates cache keys from workflow + context
    - Checks cache before execution
    - Stores results in cache after execution
    - Supports TTL and cache invalidation
    """

    def __init__(
        self,
        cache_backend: CacheBackend | None = None,
        ttl_seconds: int = 3600,
        enabled: bool = True,
    ):
        """Initialize caching middleware.
        
        Args:
            cache_backend: Cache backend to use (defaults to in-memory)
            ttl_seconds: Time-to-live for cache entries in seconds
            enabled: Whether caching is enabled
        """
        self.cache_backend = cache_backend or InMemoryCacheBackend()
        self.ttl_seconds = ttl_seconds
        self.enabled = enabled

    async def __call__(
        self,
        workflow: Workflow,
        context: ExecutionContext,
        next: Callable,
    ) -> ExecutionResult:
        """Execute with caching.
        
        Args:
            workflow: Workflow to execute
            context: Execution context
            next: Next middleware in chain
            
        Returns:
            Execution result (from cache or fresh execution)
        """
        if not self.enabled:
            return await next(workflow, context)
        
        # Generate cache key
        cache_key = self._generate_cache_key(workflow, context)
        
        # Check cache
        cached_result = await self.cache_backend.get(cache_key)
        if cached_result is not None:
            logger.info(
                f"Cache hit for execution {context.metadata.get('execution_id')}",
                cache_key=cache_key,
            )
            # Reconstruct ExecutionResult from cached data
            return ExecutionResult.from_dict(cached_result)
        
        logger.debug(
            f"Cache miss for execution {context.metadata.get('execution_id')}",
            cache_key=cache_key,
        )
        
        # Execute workflow
        result = await next(workflow, context)
        
        # Store in cache
        await self.cache_backend.set(
            cache_key,
            result.to_dict(),
            ttl=self.ttl_seconds,
        )
        
        return result
    
    def _generate_cache_key(
        self,
        workflow: Workflow,
        context: ExecutionContext,
    ) -> str:
        """Generate cache key from workflow and context.
        
        Args:
            workflow: Workflow
            context: Execution context
            
        Returns:
            Cache key (hash)
        """
        # Create deterministic representation
        key_data = {
            "workflow_type": workflow.__class__.__name__,
            "workflow_id": getattr(workflow, "id", None),
            "initial_state": self._serialize_state(context.initial_state),
            "user_id": context.user_id,
            # Include relevant metadata for cache key
            "provider": context.metadata.get("provider"),
            "model": context.metadata.get("model"),
            "temperature": context.metadata.get("temperature"),
        }
        
        # Generate hash
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _serialize_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Serialize state for cache key generation.
        
        Args:
            state: Initial state
            
        Returns:
            Serializable state
        """
        # Extract key parts of state for cache key
        return {
            "messages": str(state.get("messages", [])),
            "variables": state.get("variables", {}),
        }


class CacheBackend:
    """Base class for cache backends."""
    
    async def get(self, key: str) -> dict[str, Any] | None:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        raise NotImplementedError
    
    async def set(self, key: str, value: dict[str, Any], ttl: int):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        raise NotImplementedError
    
    async def delete(self, key: str):
        """Delete value from cache.
        
        Args:
            key: Cache key
        """
        raise NotImplementedError
    
    async def clear(self):
        """Clear all cache entries."""
        raise NotImplementedError


class InMemoryCacheBackend(CacheBackend):
    """Simple in-memory cache backend (for development/testing)."""
    
    def __init__(self):
        """Initialize in-memory cache."""
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
    
    async def get(self, key: str) -> dict[str, Any] | None:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        import time
        
        if key in self._cache:
            value, expires_at = self._cache[key]
            if time.time() < expires_at:
                return value
            else:
                # Expired, remove it
                del self._cache[key]
        
        return None
    
    async def set(self, key: str, value: dict[str, Any], ttl: int):
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        import time
        
        expires_at = time.time() + ttl
        self._cache[key] = (value, expires_at)
    
    async def delete(self, key: str):
        """Delete value from cache.
        
        Args:
            key: Cache key
        """
        if key in self._cache:
            del self._cache[key]
    
    async def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
