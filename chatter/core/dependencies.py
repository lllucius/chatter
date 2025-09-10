"""Dependency injection container for resolving circular imports and managing service dependencies."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any, TypeVar

from chatter.utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class DependencyContainer:
    """Simple dependency injection container to manage service instances and resolve circular imports."""

    def __init__(self):
        """Initialize the dependency container."""
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable[..., Any]] = {}
        self._singletons: dict[str, Any] = {}
        self._lazy_loaders: dict[str, Callable[..., Any]] = {}

    def register_singleton(
        self, service_type: type[T], instance: T
    ) -> None:
        """Register a singleton instance.

        Args:
            service_type: The service type/interface
            instance: The singleton instance
        """
        key = self._get_service_key(service_type)
        self._singletons[key] = instance
        logger.debug(f"Registered singleton: {key}")

    def register_factory(
        self, service_type: type[T], factory: Callable[[], T]
    ) -> None:
        """Register a factory function for creating service instances.

        Args:
            service_type: The service type/interface
            factory: Factory function that creates instances
        """
        key = self._get_service_key(service_type)
        self._factories[key] = factory
        logger.debug(f"Registered factory: {key}")

    def register_lazy_loader(
        self, service_name: str, loader: callable
    ) -> None:
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
            raise ValueError(
                f"Lazy loader not registered: {service_name}"
            )

        # Cache the result after first load
        if service_name not in self._services:
            try:
                self._services[service_name] = self._lazy_loaders[
                    service_name
                ]()
                logger.debug(f"Lazy loaded service: {service_name}")
            except Exception as e:
                logger.error(
                    f"Failed to lazy load service {service_name}: {e}"
                )
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
        "builtin_tools", lambda: _lazy_import_builtin_tools()
    )

    container.register_lazy_loader(
        "orchestrator", lambda: _lazy_import_orchestrator()
    )

    container.register_lazy_loader(
        "mcp_service", lambda: _lazy_import_mcp_service()
    )

    container.register_lazy_loader(
        "model_registry", lambda: _lazy_import_model_registry()
    )

    container.register_lazy_loader(
        "workflow_manager", lambda: _lazy_import_workflow_manager()
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


class CircularDependencyDetector:
    """Detector for circular dependencies in service registration."""

    def __init__(self):
        """Initialize the circular dependency detector."""
        self.dependency_graph: dict[str, set[str]] = {}

    def add_dependency(self, service: str, dependency: str) -> None:
        """Add a dependency relationship.

        Args:
            service: Name of the service
            dependency: Name of the dependency
        """
        if service not in self.dependency_graph:
            self.dependency_graph[service] = set()
        self.dependency_graph[service].add(dependency)

    def detect_circular_dependencies(self) -> list[list[str]]:
        """Detect circular dependencies.

        Returns:
            List of circular dependency chains
        """
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node: str, path: list[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, set()):
                if neighbor not in visited:
                    dfs(neighbor, path.copy())
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])

            rec_stack.remove(node)

        for service in self.dependency_graph:
            if service not in visited:
                dfs(service, [])

        return cycles


class LazyServiceLoader:
    """Loader for services that should be initialized lazily."""

    def __init__(self):
        """Initialize the lazy service loader."""
        self.loaders: dict[str, callable] = {}
        self.loaded_services: dict[str, Any] = {}

    def register_loader(self, name: str, loader: callable) -> None:
        """Register a lazy loader for a service.

        Args:
            name: Name of the service
            loader: Callable that returns the service instance
        """
        self.loaders[name] = loader

    def get_service(self, name: str) -> Any:
        """Get a service, loading it lazily if needed.

        Args:
            name: Name of the service

        Returns:
            Service instance
        """
        if name not in self.loaded_services:
            if name not in self.loaders:
                raise ValueError(
                    f"No loader registered for service: {name}"
                )
            self.loaded_services[name] = self.loaders[name]()
        return self.loaded_services[name]

    def is_loaded(self, name: str) -> bool:
        """Check if a service is already loaded.

        Args:
            name: Name of the service

        Returns:
            True if service is loaded
        """
        return name in self.loaded_services


class ServiceLifecycleManager:
    """Manager for service lifecycle events."""

    def __init__(self):
        """Initialize the service lifecycle manager."""
        self.services: dict[str, Any] = {}
        self.lifecycle_handlers: dict[str, dict[str, callable]] = {}

    def register_service(self, name: str, service: Any) -> None:
        """Register a service.

        Args:
            name: Name of the service
            service: Service instance
        """
        self.services[name] = service
        self._trigger_lifecycle_event(name, "created")

    def start_service(self, name: str) -> None:
        """Start a service.

        Args:
            name: Name of the service
        """
        if name in self.services:
            service = self.services[name]
            if hasattr(service, "start"):
                service.start()
            self._trigger_lifecycle_event(name, "started")

    def stop_service(self, name: str) -> None:
        """Stop a service.

        Args:
            name: Name of the service
        """
        if name in self.services:
            service = self.services[name]
            if hasattr(service, "stop"):
                service.stop()
            self._trigger_lifecycle_event(name, "stopped")

    def register_lifecycle_handler(
        self, service_name: str, event: str, handler: callable
    ) -> None:
        """Register a lifecycle event handler.

        Args:
            service_name: Name of the service
            event: Lifecycle event name
            handler: Event handler function
        """
        if service_name not in self.lifecycle_handlers:
            self.lifecycle_handlers[service_name] = {}
        self.lifecycle_handlers[service_name][event] = handler

    def _trigger_lifecycle_event(
        self, service_name: str, event: str
    ) -> None:
        """Trigger a lifecycle event.

        Args:
            service_name: Name of the service
            event: Event name
        """
        handlers = self.lifecycle_handlers.get(service_name, {})
        if event in handlers:
            handlers[event](self.services[service_name])


class ServiceRegistry:
    """Registry for managing service instances and their metadata."""

    def __init__(self):
        """Initialize the service registry."""
        self.services: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        service: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a service.

        Args:
            name: Name of the service
            service: Service instance
            metadata: Optional service metadata
        """
        self.services[name] = {
            "instance": service,
            "metadata": metadata or {},
            "registered_at": datetime.now(UTC).isoformat(),
        }

    def get(self, name: str) -> Any:
        """Get a service by name.

        Args:
            name: Name of the service

        Returns:
            Service instance

        Raises:
            KeyError: If service is not registered
        """
        if name not in self.services:
            raise KeyError(f"Service not found: {name}")
        return self.services[name]["instance"]

    def unregister(self, name: str) -> None:
        """Unregister a service.

        Args:
            name: Name of the service
        """
        if name in self.services:
            del self.services[name]

    def list_services(self) -> list[str]:
        """List all registered service names.

        Returns:
            List of service names
        """
        return list(self.services.keys())

    def get_metadata(self, name: str) -> dict[str, Any]:
        """Get metadata for a service.

        Args:
            name: Name of the service

        Returns:
            Service metadata
        """
        if name not in self.services:
            return {}
        return self.services[name]["metadata"]
