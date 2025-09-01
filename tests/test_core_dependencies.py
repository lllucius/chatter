"""Tests for dependency injection container and service management."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Protocol

from chatter.core.dependencies import (
    DependencyContainer,
    ServiceRegistry,
    LazyServiceLoader,
    CircularDependencyDetector,
    ServiceLifecycleManager
)
from chatter.core.exceptions import (
    DependencyError,
    CircularDependencyError,
    ServiceNotFoundError
)


# Test interfaces and implementations
class ITestService(Protocol):
    """Test service interface."""
    def get_value(self) -> str: ...


class TestService:
    """Test service implementation."""
    
    def __init__(self, value: str = "test"):
        self.value = value
    
    def get_value(self) -> str:
        return self.value


class DependentService:
    """Service that depends on TestService."""
    
    def __init__(self, test_service: ITestService):
        self.test_service = test_service
    
    def get_dependent_value(self) -> str:
        return f"dependent_{self.test_service.get_value()}"


class ComplexService:
    """Service with multiple dependencies."""
    
    def __init__(self, service1: TestService, service2: DependentService, config: dict):
        self.service1 = service1
        self.service2 = service2
        self.config = config
    
    def get_complex_value(self) -> str:
        return f"complex_{self.service1.get_value()}_{self.service2.get_dependent_value()}"


@pytest.mark.unit
class TestDependencyContainer:
    """Test DependencyContainer functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.container = DependencyContainer()

    def test_container_initialization(self):
        """Test DependencyContainer initialization."""
        # Assert
        assert len(self.container._services) == 0
        assert len(self.container._factories) == 0
        assert len(self.container._singletons) == 0
        assert len(self.container._lazy_loaders) == 0

    def test_register_singleton(self):
        """Test registering a singleton instance."""
        # Arrange
        test_instance = TestService("singleton_value")
        
        # Act
        self.container.register_singleton(ITestService, test_instance)
        
        # Assert
        service_key = self.container._get_service_key(ITestService)
        assert service_key in self.container._singletons
        assert self.container._singletons[service_key] == test_instance

    def test_register_factory(self):
        """Test registering a factory function."""
        # Arrange
        def test_factory() -> TestService:
            return TestService("factory_value")
        
        # Act
        self.container.register_factory(TestService, test_factory)
        
        # Assert
        service_key = self.container._get_service_key(TestService)
        assert service_key in self.container._factories
        assert self.container._factories[service_key] == test_factory

    def test_register_lazy_loader(self):
        """Test registering a lazy loader."""
        # Arrange
        def lazy_loader():
            return TestService("lazy_value")
        
        # Act
        self.container.register_lazy_loader("test_service", lazy_loader)
        
        # Assert
        assert "test_service" in self.container._lazy_loaders
        assert self.container._lazy_loaders["test_service"] == lazy_loader

    def test_resolve_singleton(self):
        """Test resolving a singleton service."""
        # Arrange
        test_instance = TestService("singleton_test")
        self.container.register_singleton(TestService, test_instance)
        
        # Act
        resolved = self.container.resolve(TestService)
        
        # Assert
        assert resolved == test_instance
        
        # Resolving again should return the same instance
        resolved_again = self.container.resolve(TestService)
        assert resolved_again is resolved

    def test_resolve_factory(self):
        """Test resolving a service from factory."""
        # Arrange
        def test_factory() -> TestService:
            return TestService("factory_test")
        
        self.container.register_factory(TestService, test_factory)
        
        # Act
        resolved1 = self.container.resolve(TestService)
        resolved2 = self.container.resolve(TestService)
        
        # Assert
        assert isinstance(resolved1, TestService)
        assert resolved1.get_value() == "factory_test"
        # Factory should create new instances each time
        assert resolved1 is not resolved2

    def test_resolve_lazy_loader(self):
        """Test resolving a service from lazy loader."""
        # Arrange
        def lazy_loader():
            return TestService("lazy_test")
        
        self.container.register_lazy_loader("test_service", lazy_loader)
        
        # Act
        resolved = self.container.resolve_lazy("test_service")
        
        # Assert
        assert isinstance(resolved, TestService)
        assert resolved.get_value() == "lazy_test"

    def test_resolve_unregistered_service(self):
        """Test resolving an unregistered service raises error."""
        # Act & Assert
        with pytest.raises(ServiceNotFoundError) as exc_info:
            self.container.resolve(TestService)
        
        assert "not registered" in str(exc_info.value)

    def test_resolve_with_dependencies(self):
        """Test resolving service with dependencies."""
        # Arrange
        test_service = TestService("dependency_test")
        self.container.register_singleton(TestService, test_service)
        
        def dependent_factory() -> DependentService:
            test_service = self.container.resolve(TestService)
            return DependentService(test_service)
        
        self.container.register_factory(DependentService, dependent_factory)
        
        # Act
        resolved = self.container.resolve(DependentService)
        
        # Assert
        assert isinstance(resolved, DependentService)
        assert resolved.get_dependent_value() == "dependent_dependency_test"

    def test_get_service_key_generation(self):
        """Test service key generation for different types."""
        # Act
        key1 = self.container._get_service_key(TestService)
        key2 = self.container._get_service_key(ITestService)
        key3 = self.container._get_service_key(str)
        
        # Assert
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        assert isinstance(key3, str)
        assert key1 != key2
        assert key2 != key3

    def test_container_clear(self):
        """Test clearing the container."""
        # Arrange
        self.container.register_singleton(TestService, TestService())
        self.container.register_factory(DependentService, lambda: DependentService(TestService()))
        
        # Act
        self.container.clear()
        
        # Assert
        assert len(self.container._services) == 0
        assert len(self.container._factories) == 0
        assert len(self.container._singletons) == 0
        assert len(self.container._lazy_loaders) == 0

    def test_list_registered_services(self):
        """Test listing registered services."""
        # Arrange
        self.container.register_singleton(TestService, TestService())
        self.container.register_factory(DependentService, lambda: DependentService(TestService()))
        
        # Act
        services = self.container.list_registered_services()
        
        # Assert
        assert len(services) == 2
        assert any("TestService" in service for service in services)
        assert any("DependentService" in service for service in services)

    def test_service_exists_check(self):
        """Test checking if service is registered."""
        # Arrange
        self.container.register_singleton(TestService, TestService())
        
        # Act & Assert
        assert self.container.is_registered(TestService) is True
        assert self.container.is_registered(DependentService) is False


@pytest.mark.unit
class TestServiceRegistry:
    """Test ServiceRegistry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = ServiceRegistry()

    def test_service_registry_initialization(self):
        """Test ServiceRegistry initialization."""
        # Assert
        assert len(self.registry.services) == 0
        assert len(self.registry.dependencies) == 0

    def test_register_service_metadata(self):
        """Test registering service metadata."""
        # Arrange
        service_info = {
            "name": "test_service",
            "type": TestService,
            "lifecycle": "singleton",
            "dependencies": [],
            "description": "Test service for unit testing"
        }
        
        # Act
        self.registry.register_service(service_info)
        
        # Assert
        assert "test_service" in self.registry.services
        assert self.registry.services["test_service"]["type"] == TestService
        assert self.registry.services["test_service"]["lifecycle"] == "singleton"

    def test_register_service_with_dependencies(self):
        """Test registering service with dependencies."""
        # Arrange
        service_info = {
            "name": "dependent_service",
            "type": DependentService,
            "lifecycle": "transient",
            "dependencies": ["test_service"]
        }
        
        # Act
        self.registry.register_service(service_info)
        
        # Assert
        assert "dependent_service" in self.registry.services
        assert "test_service" in self.registry.services["dependent_service"]["dependencies"]

    def test_get_service_info(self):
        """Test getting service information."""
        # Arrange
        service_info = {
            "name": "test_service",
            "type": TestService,
            "lifecycle": "singleton"
        }
        self.registry.register_service(service_info)
        
        # Act
        retrieved_info = self.registry.get_service_info("test_service")
        
        # Assert
        assert retrieved_info["name"] == "test_service"
        assert retrieved_info["type"] == TestService

    def test_get_service_dependencies(self):
        """Test getting service dependencies."""
        # Arrange
        self.registry.register_service({
            "name": "service_a", 
            "type": TestService,
            "dependencies": []
        })
        self.registry.register_service({
            "name": "service_b",
            "type": DependentService, 
            "dependencies": ["service_a"]
        })
        
        # Act
        deps = self.registry.get_service_dependencies("service_b")
        
        # Assert
        assert "service_a" in deps

    def test_build_dependency_graph(self):
        """Test building dependency graph."""
        # Arrange
        services = [
            {"name": "service_a", "type": TestService, "dependencies": []},
            {"name": "service_b", "type": DependentService, "dependencies": ["service_a"]},
            {"name": "service_c", "type": ComplexService, "dependencies": ["service_a", "service_b"]}
        ]
        
        for service in services:
            self.registry.register_service(service)
        
        # Act
        graph = self.registry.build_dependency_graph()
        
        # Assert
        assert "service_a" in graph
        assert "service_b" in graph
        assert "service_c" in graph
        assert len(graph["service_c"]) == 2  # service_c depends on service_a and service_b


@pytest.mark.unit
class TestLazyServiceLoader:
    """Test LazyServiceLoader functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.loader = LazyServiceLoader()

    def test_lazy_loader_initialization(self):
        """Test LazyServiceLoader initialization."""
        # Assert
        assert len(self.loader.loaded_modules) == 0
        assert len(self.loader.service_loaders) == 0

    def test_register_lazy_service(self):
        """Test registering a lazy service loader."""
        # Arrange
        def service_loader():
            return TestService("lazy_loaded")
        
        # Act
        self.loader.register_lazy_service("test_service", service_loader)
        
        # Assert
        assert "test_service" in self.loader.service_loaders

    def test_load_service_on_demand(self):
        """Test loading service only when requested."""
        # Arrange
        load_count = 0
        
        def service_loader():
            nonlocal load_count
            load_count += 1
            return TestService(f"loaded_{load_count}")
        
        self.loader.register_lazy_service("test_service", service_loader)
        
        # Act
        service1 = self.loader.load_service("test_service")
        service2 = self.loader.load_service("test_service")
        
        # Assert
        assert load_count == 1  # Should only load once
        assert service1 is service2  # Should return cached instance
        assert service1.get_value() == "loaded_1"

    def test_load_unregistered_service(self):
        """Test loading unregistered service raises error."""
        # Act & Assert
        with pytest.raises(ServiceNotFoundError):
            self.loader.load_service("unregistered_service")

    def test_register_module_loader(self):
        """Test registering module-based service loader."""
        # Arrange
        module_path = "chatter.services.test_service"
        
        # Act
        self.loader.register_module_loader("test_service", module_path, "TestService")
        
        # Assert
        assert "test_service" in self.loader.service_loaders

    def test_lazy_loading_with_dependencies(self):
        """Test lazy loading with service dependencies."""
        # Arrange
        def base_service_loader():
            return TestService("base")
        
        def dependent_service_loader():
            base_service = self.loader.load_service("base_service")
            return DependentService(base_service)
        
        self.loader.register_lazy_service("base_service", base_service_loader)
        self.loader.register_lazy_service("dependent_service", dependent_service_loader)
        
        # Act
        dependent_service = self.loader.load_service("dependent_service")
        
        # Assert
        assert isinstance(dependent_service, DependentService)
        assert dependent_service.get_dependent_value() == "dependent_base"


@pytest.mark.unit
class TestCircularDependencyDetector:
    """Test CircularDependencyDetector functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = CircularDependencyDetector()

    def test_no_circular_dependencies(self):
        """Test detection with no circular dependencies."""
        # Arrange
        dependencies = {
            "service_a": [],
            "service_b": ["service_a"],
            "service_c": ["service_a", "service_b"]
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert result.has_cycles is False
        assert len(result.cycles) == 0

    def test_simple_circular_dependency(self):
        """Test detection of simple circular dependency."""
        # Arrange
        dependencies = {
            "service_a": ["service_b"],
            "service_b": ["service_a"]
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert result.has_cycles is True
        assert len(result.cycles) > 0

    def test_complex_circular_dependency(self):
        """Test detection of complex circular dependency."""
        # Arrange
        dependencies = {
            "service_a": ["service_b"],
            "service_b": ["service_c"],
            "service_c": ["service_d"],
            "service_d": ["service_a"]  # Creates cycle a->b->c->d->a
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert result.has_cycles is True
        assert len(result.cycles) > 0

    def test_multiple_cycles(self):
        """Test detection of multiple independent cycles."""
        # Arrange
        dependencies = {
            "service_a": ["service_b"],
            "service_b": ["service_a"],  # Cycle 1: a->b->a
            "service_c": ["service_d"],
            "service_d": ["service_c"],  # Cycle 2: c->d->c
            "service_e": []  # Independent service
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert result.has_cycles is True
        assert len(result.cycles) >= 2

    def test_self_dependency(self):
        """Test detection of self-dependency."""
        # Arrange
        dependencies = {
            "service_a": ["service_a"]  # Self-dependency
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert result.has_cycles is True
        assert len(result.cycles) > 0

    def test_suggest_resolution(self):
        """Test suggesting resolution for circular dependencies."""
        # Arrange
        dependencies = {
            "service_a": ["service_b"],
            "service_b": ["service_c"],
            "service_c": ["service_a"]
        }
        
        # Act
        result = self.detector.detect_circular_dependencies(dependencies)
        suggestions = self.detector.suggest_resolution(result.cycles[0])
        
        # Assert
        assert len(suggestions) > 0
        assert any("interface" in suggestion.lower() for suggestion in suggestions)


@pytest.mark.unit
class TestServiceLifecycleManager:
    """Test ServiceLifecycleManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.lifecycle_manager = ServiceLifecycleManager()

    def test_lifecycle_manager_initialization(self):
        """Test ServiceLifecycleManager initialization."""
        # Assert
        assert len(self.lifecycle_manager.services) == 0
        assert len(self.lifecycle_manager.startup_order) == 0

    def test_register_service_lifecycle(self):
        """Test registering service lifecycle."""
        # Arrange
        mock_service = MagicMock()
        lifecycle_config = {
            "startup_priority": 1,
            "shutdown_priority": 1,
            "health_check": lambda: True,
            "dependencies": []
        }
        
        # Act
        self.lifecycle_manager.register_service("test_service", mock_service, lifecycle_config)
        
        # Assert
        assert "test_service" in self.lifecycle_manager.services
        assert self.lifecycle_manager.services["test_service"]["instance"] == mock_service

    @pytest.mark.asyncio
    async def test_startup_sequence(self):
        """Test service startup sequence."""
        # Arrange
        service1 = MagicMock()
        service2 = MagicMock()
        service1.startup = AsyncMock()
        service2.startup = AsyncMock()
        
        self.lifecycle_manager.register_service("service1", service1, {"startup_priority": 1})
        self.lifecycle_manager.register_service("service2", service2, {"startup_priority": 2})
        
        # Act
        await self.lifecycle_manager.startup_services()
        
        # Assert
        service1.startup.assert_called_once()
        service2.startup.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_sequence(self):
        """Test service shutdown sequence."""
        # Arrange
        service1 = MagicMock()
        service2 = MagicMock()
        service1.shutdown = AsyncMock()
        service2.shutdown = AsyncMock()
        
        self.lifecycle_manager.register_service("service1", service1, {"shutdown_priority": 1})
        self.lifecycle_manager.register_service("service2", service2, {"shutdown_priority": 2})
        
        # Act
        await self.lifecycle_manager.shutdown_services()
        
        # Assert
        service1.shutdown.assert_called_once()
        service2.shutdown.assert_called_once()

    def test_health_check_all_services(self):
        """Test health check for all services."""
        # Arrange
        healthy_service = MagicMock()
        unhealthy_service = MagicMock()
        
        self.lifecycle_manager.register_service(
            "healthy_service", 
            healthy_service, 
            {"health_check": lambda: True}
        )
        self.lifecycle_manager.register_service(
            "unhealthy_service",
            unhealthy_service,
            {"health_check": lambda: False}
        )
        
        # Act
        health_status = self.lifecycle_manager.check_all_services_health()
        
        # Assert
        assert health_status["healthy_service"] is True
        assert health_status["unhealthy_service"] is False

    def test_calculate_startup_order(self):
        """Test calculating service startup order based on dependencies."""
        # Arrange
        services = [
            ("service_a", {}, {"dependencies": []}),
            ("service_b", {}, {"dependencies": ["service_a"]}),
            ("service_c", {}, {"dependencies": ["service_a", "service_b"]})
        ]
        
        for service_name, service_instance, config in services:
            self.lifecycle_manager.register_service(service_name, service_instance, config)
        
        # Act
        startup_order = self.lifecycle_manager._calculate_startup_order()
        
        # Assert
        assert len(startup_order) == 3
        # service_a should come before service_b and service_c
        a_index = startup_order.index("service_a")
        b_index = startup_order.index("service_b")
        c_index = startup_order.index("service_c")
        assert a_index < b_index
        assert a_index < c_index
        assert b_index < c_index


@pytest.mark.integration
class TestDependencyIntegration:
    """Integration tests for dependency injection system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.container = DependencyContainer()
        self.registry = ServiceRegistry()
        self.lifecycle_manager = ServiceLifecycleManager()

    def test_complete_dependency_workflow(self):
        """Test complete dependency injection workflow."""
        # Arrange
        # Register services in registry
        base_service_info = {
            "name": "base_service",
            "type": TestService,
            "lifecycle": "singleton",
            "dependencies": []
        }
        dependent_service_info = {
            "name": "dependent_service", 
            "type": DependentService,
            "lifecycle": "transient",
            "dependencies": ["base_service"]
        }
        
        self.registry.register_service(base_service_info)
        self.registry.register_service(dependent_service_info)
        
        # Register in container
        base_instance = TestService("integration_test")
        self.container.register_singleton(TestService, base_instance)
        
        def dependent_factory():
            base = self.container.resolve(TestService)
            return DependentService(base)
        
        self.container.register_factory(DependentService, dependent_factory)
        
        # Act
        resolved_dependent = self.container.resolve(DependentService)
        
        # Assert
        assert isinstance(resolved_dependent, DependentService)
        assert resolved_dependent.get_dependent_value() == "dependent_integration_test"

    def test_service_lifecycle_with_dependencies(self):
        """Test service lifecycle management with dependencies."""
        # Arrange
        base_service = TestService("lifecycle_test")
        dependent_service = DependentService(base_service)
        
        # Register with lifecycle manager
        self.lifecycle_manager.register_service(
            "base_service",
            base_service,
            {"startup_priority": 1, "dependencies": []}
        )
        self.lifecycle_manager.register_service(
            "dependent_service",
            dependent_service,
            {"startup_priority": 2, "dependencies": ["base_service"]}
        )
        
        # Act
        startup_order = self.lifecycle_manager._calculate_startup_order()
        health_status = self.lifecycle_manager.check_all_services_health()
        
        # Assert
        assert startup_order.index("base_service") < startup_order.index("dependent_service")
        assert health_status["base_service"] is True
        assert health_status["dependent_service"] is True

    def test_circular_dependency_detection_and_resolution(self):
        """Test detecting and resolving circular dependencies."""
        # Arrange
        detector = CircularDependencyDetector()
        
        # Create circular dependency scenario
        dependencies = {
            "service_a": ["service_b"],
            "service_b": ["service_c"],
            "service_c": ["service_a"]
        }
        
        # Act
        detection_result = detector.detect_circular_dependencies(dependencies)
        
        # Assert
        assert detection_result.has_cycles is True
        
        # Test resolution suggestion
        if detection_result.cycles:
            suggestions = detector.suggest_resolution(detection_result.cycles[0])
            assert len(suggestions) > 0

    def test_lazy_loading_with_container_integration(self):
        """Test lazy loading integration with dependency container."""
        # Arrange
        lazy_loader = LazyServiceLoader()
        
        def lazy_service_factory():
            return TestService("lazy_integration")
        
        lazy_loader.register_lazy_service("lazy_test_service", lazy_service_factory)
        
        # Act
        loaded_service = lazy_loader.load_service("lazy_test_service")
        
        # Assert
        assert isinstance(loaded_service, TestService)
        assert loaded_service.get_value() == "lazy_integration"

    @pytest.mark.asyncio
    async def test_full_application_startup_shutdown(self):
        """Test complete application startup and shutdown sequence."""
        # Arrange
        services = []
        
        # Create mock services with startup/shutdown methods
        for i in range(3):
            service = MagicMock()
            service.startup = AsyncMock()
            service.shutdown = AsyncMock()
            services.append(service)
            
            self.lifecycle_manager.register_service(
                f"service_{i}",
                service,
                {
                    "startup_priority": i + 1,
                    "shutdown_priority": 3 - i,  # Reverse order for shutdown
                    "health_check": lambda: True
                }
            )
        
        # Act
        await self.lifecycle_manager.startup_services()
        
        # Verify all services started
        for service in services:
            service.startup.assert_called_once()
        
        # Shutdown
        await self.lifecycle_manager.shutdown_services()
        
        # Assert
        for service in services:
            service.shutdown.assert_called_once()