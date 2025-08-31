"""Dependency injection container for resolving circular imports and managing service dependencies."""

from __future__ import annotations

from typing import Any, TypeVar

from chatter.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class DependencyContainer:
    """Simple dependency injection container to manage service instances and resolve circular imports."""

    def __init__(self):
        """Initialize the dependency container."""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, callable] = {}
        self._singletons: dict[str, Any] = {}
        self._lazy_loaders: dict[str, callable] = {}

    def register_singleton(self, service_type: type[T], instance: T) -> None:
        """Register a singleton instance.

        Args:
            service_type: The service type/interface
            instance: The singleton instance
        """
        key = self._get_service_key(service_type)
        self._singletons[key] = instance
        logger.debug(f"Registered singleton: {key}")

    def register_factory(self, service_type: type[T], factory: callable[[], T]) -> None:
        """Register a factory function for creating service instances.

        Args:
            service_type: The service type/interface
            factory: Factory function that creates instances
        """
        key = self._get_service_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")

    def register_lazy_loader(self, service_name: str, loader: callable) -> None:
        """Register a lazy loader function to avoid circular imports.

        Args:
            service_name: Name of the service
            loader: Lazy loader function
        """
        self._lazy_loaders[service_name] = loader
        logger.debug(f"Registered lazy loader: {service_name}")

    def get(self, service_type: type[T]) -> T:
        """Get a service instance.

        Args:
            service_type: The service type to retrieve

        Returns:
            Service instance

        Raises:
            ValueError: If service is not registered
        """
        key = self._get_service_key(service_type)

        # Check singletons first
        if key in self._singletons:
            return self._singletons[key]

        # Check factories
        if key in self._factories:
            instance = self._factories[key]()
            # Cache as singleton for future requests
            self._singletons[key] = instance
            return instance

        raise ValueError(f"Service not registered: {key}")

    def get_lazy(self, service_name: str) -> Any:
        """Get a service instance using lazy loading.

        Args:
            service_name: Name of the service

        Returns:
            Service instance

        Raises:
            ValueError: If lazy loader is not registered
        """
        if service_name not in self._lazy_loaders:
            raise ValueError(f"Lazy loader not registered: {service_name}")

        # Cache the result after first load
        if service_name not in self._services:
            try:
                self._services[service_name] = self._lazy_loaders[service_name]()
                logger.debug(f"Lazy loaded service: {service_name}")
            except Exception as e:
                logger.error(f"Failed to lazy load service {service_name}: {e}")
                raise

        return self._services[service_name]

    def clear(self) -> None:
        """Clear all registered services and singletons."""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._lazy_loaders.clear()
        logger.debug("Dependency container cleared")

    @staticmethod
    def _get_service_key(service_type: type) -> str:
        """Get a unique key for a service type."""
        return f"{service_type.__module__}.{service_type.__name__}"


# Global dependency container instance
container = DependencyContainer()


def register_lazy_loaders() -> None:
    """Register all lazy loaders to avoid circular imports."""

    # Register lazy loaders for commonly problematic circular imports
    container.register_lazy_loader(
        "builtin_tools",
        lambda: _lazy_import_builtin_tools()
    )

    container.register_lazy_loader(
        "orchestrator",
        lambda: _lazy_import_orchestrator()
    )

    container.register_lazy_loader(
        "mcp_service",
        lambda: _lazy_import_mcp_service()
    )

    container.register_lazy_loader(
        "model_registry",
        lambda: _lazy_import_model_registry()
    )

    container.register_lazy_loader(
        "workflow_manager",
        lambda: _lazy_import_workflow_manager()
    )


def _lazy_import_builtin_tools():
    """Lazy import of BuiltInTools to avoid circular imports."""
    from chatter.services.mcp import BuiltInTools
    return BuiltInTools.create_builtin_tools()


def _lazy_import_orchestrator():
    """Lazy import of orchestrator to avoid circular imports."""
    from chatter.core.langchain import orchestrator
    return orchestrator


def _lazy_import_mcp_service():
    """Lazy import of MCP service to avoid circular imports."""
    from chatter.services.mcp import mcp_service
    return mcp_service


def _lazy_import_model_registry():
    """Lazy import of model registry to avoid circular imports."""
    from chatter.core.model_registry import ModelRegistryService
    return ModelRegistryService


def _lazy_import_workflow_manager():
    """Lazy import of workflow manager to avoid circular imports."""
    from chatter.core.langgraph import workflow_manager
    return workflow_manager


# Initialize lazy loaders on module import
register_lazy_loaders()


# Helper functions for common dependency injection patterns
def get_builtin_tools():
    """Get builtin tools with dependency injection."""
    return container.get_lazy("builtin_tools")


def get_orchestrator():
    """Get orchestrator with dependency injection."""
    return container.get_lazy("orchestrator")


def get_mcp_service():
    """Get MCP service with dependency injection."""
    return container.get_lazy("mcp_service")


def get_model_registry():
    """Get model registry with dependency injection."""
    return container.get_lazy("model_registry")


def get_workflow_manager():
    """Get workflow manager with dependency injection."""
    return container.get_lazy("workflow_manager")
