"""Tests for API versioning utilities."""

import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException, Request

from chatter.utils.versioning import (
    APIVersionManager,
    extract_version_from_request,
    version_middleware,
    version_route,
    VersionedRouter,
    version_manager,
)
from chatter.schemas.utilities import APIVersion, VersionInfo, VersionStatus, EndpointVersioning


@pytest.mark.unit
class TestAPIVersionManager:
    """Test API version manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = APIVersionManager()

    def test_initialization(self):
        """Test manager initialization."""
        # Assert
        assert self.manager.default_version == APIVersion.V1
        assert len(self.manager.versions) >= 2
        assert APIVersion.V1 in self.manager.versions
        assert APIVersion.V2 in self.manager.versions

    def test_get_version_info(self):
        """Test getting version information."""
        # Act
        v1_info = self.manager.get_version_info(APIVersion.V1)
        v2_info = self.manager.get_version_info(APIVersion.V2)
        unknown_info = self.manager.get_version_info("v999")

        # Assert
        assert v1_info is not None
        assert v1_info.version == APIVersion.V1
        assert v1_info.status == VersionStatus.ACTIVE
        assert "Core chat functionality" in v1_info.new_features

        assert v2_info is not None
        assert v2_info.version == APIVersion.V2
        assert v2_info.status == VersionStatus.ACTIVE
        assert len(v2_info.breaking_changes) > 0

        assert unknown_info is None

    def test_get_all_versions(self):
        """Test getting all versions."""
        # Act
        all_versions = self.manager.get_all_versions()

        # Assert
        assert len(all_versions) >= 2
        version_values = [v.version for v in all_versions]
        assert APIVersion.V1 in version_values
        assert APIVersion.V2 in version_values

    def test_get_active_versions(self):
        """Test getting active versions."""
        # Act
        active_versions = self.manager.get_active_versions()

        # Assert
        assert len(active_versions) >= 2
        for version_info in active_versions:
            assert version_info.status == VersionStatus.ACTIVE

    def test_is_version_supported(self):
        """Test version support checking."""
        # Act & Assert
        assert self.manager.is_version_supported(APIVersion.V1) is True
        assert self.manager.is_version_supported(APIVersion.V2) is True

    def test_add_version(self):
        """Test adding a new version."""
        # Arrange
        new_version = VersionInfo(
            version=APIVersion.V3,
            status=VersionStatus.ACTIVE,
            release_date="2024-12-01",
            documentation_url="https://api.example.com/docs/v3",
            new_features=["Feature 1", "Feature 2"]
        )

        # Act
        self.manager.add_version(new_version)

        # Assert
        assert APIVersion.V3 in self.manager.versions
        retrieved = self.manager.get_version_info(APIVersion.V3)
        assert retrieved == new_version

    def test_register_endpoint(self):
        """Test endpoint registration."""
        # Act
        self.manager.register_endpoint(
            path="/test",
            method="GET",
            introduced_in=APIVersion.V1
        )

        # Assert
        assert "GET:/test" in self.manager.endpoints
        endpoint = self.manager.endpoints["GET:/test"]
        assert endpoint.path == "/test"
        assert endpoint.method == "GET"
        assert endpoint.introduced_in == APIVersion.V1

    def test_is_endpoint_available(self):
        """Test endpoint availability checking."""
        # Arrange
        self.manager.register_endpoint(
            path="/available",
            method="GET",
            introduced_in=APIVersion.V1
        )
        
        self.manager.register_endpoint(
            path="/removed",
            method="POST",
            introduced_in=APIVersion.V1,
            removed_in=APIVersion.V2
        )

        # Act & Assert
        # Available endpoint
        assert self.manager.is_endpoint_available("/available", "GET", APIVersion.V1) is True
        assert self.manager.is_endpoint_available("/available", "GET", APIVersion.V2) is True

        # Removed endpoint
        assert self.manager.is_endpoint_available("/removed", "POST", APIVersion.V1) is True
        assert self.manager.is_endpoint_available("/removed", "POST", APIVersion.V2) is False

        # Non-existent endpoint
        assert self.manager.is_endpoint_available("/nonexistent", "GET", APIVersion.V1) is False

    def test_get_endpoint_status(self):
        """Test getting endpoint status."""
        # Arrange
        self.manager.register_endpoint(
            path="/status-test",
            method="GET",
            introduced_in=APIVersion.V1
        )

        # Act & Assert
        assert self.manager.get_endpoint_status("/status-test", "GET", APIVersion.V1) == "active"
        assert self.manager.get_endpoint_status("/nonexistent", "GET", APIVersion.V1) is None


@pytest.mark.unit
class TestVersionExtraction:
    """Test version extraction from requests."""

    def test_extract_version_from_path(self):
        """Test extracting version from URL path."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v2/chat"
        request.headers = {}

        # Act
        version = extract_version_from_request(request)

        # Assert
        assert version == APIVersion.V2

    def test_extract_version_from_accept_header(self):
        """Test extracting version from Accept header."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/chat"
        request.headers = {
            "Accept": "application/vnd.chatter.v1+json"
        }

        # Act
        version = extract_version_from_request(request)

        # Assert
        assert version == APIVersion.V1

    def test_extract_version_from_api_version_header(self):
        """Test extracting version from API-Version header."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/chat"
        request.headers = {
            "API-Version": "v2"
        }

        # Act
        version = extract_version_from_request(request)

        # Assert
        assert version == APIVersion.V2

    def test_extract_version_default(self):
        """Test default version when no version specified."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/chat"
        request.headers = {}

        # Act
        version = extract_version_from_request(request)

        # Assert
        assert version == version_manager.default_version

    def test_extract_version_invalid(self):
        """Test handling invalid version strings."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v999/chat"
        request.headers = {}

        # Act
        version = extract_version_from_request(request)

        # Assert
        assert version == version_manager.default_version


@pytest.mark.asyncio
class TestVersionMiddleware:
    """Test version middleware functionality."""

    async def test_version_middleware_supported_version(self):
        """Test middleware with supported version."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v1/health"
        request.method = "GET"
        request.state = Mock()
        request.headers = {}

        call_next = Mock()
        response = Mock()
        response.headers = {}
        call_next.return_value = response

        # Act
        result = await version_middleware(request, call_next)

        # Assert
        assert result == response
        assert request.state.api_version == APIVersion.V1
        assert "API-Version" in response.headers
        assert "API-Supported-Versions" in response.headers

    async def test_version_middleware_unsupported_version(self):
        """Test middleware with unsupported version."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v999/health"
        request.method = "GET"
        request.headers = {}

        call_next = Mock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await version_middleware(request, call_next)
        
        assert exc_info.value.status_code == 400
        assert "not supported" in exc_info.value.detail

    async def test_version_middleware_unavailable_endpoint(self):
        """Test middleware with unavailable endpoint."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v1/nonexistent"
        request.method = "GET"
        request.headers = {}

        call_next = Mock()

        # Mock endpoint as unavailable
        with patch.object(version_manager, 'is_endpoint_available', return_value=False):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await version_middleware(request, call_next)
            
            assert exc_info.value.status_code == 404
            assert "not available" in exc_info.value.detail


@pytest.mark.unit
class TestVersionDecorators:
    """Test version decorators and utilities."""

    def test_version_route_decorator(self):
        """Test version route decorator."""
        # Arrange & Act
        @version_route(versions=[APIVersion.V1, APIVersion.V2])
        def test_endpoint():
            return {"test": "data"}

        # Assert
        assert hasattr(test_endpoint, '_api_versions')
        assert test_endpoint._api_versions == [APIVersion.V1, APIVersion.V2]

    def test_versioned_router_initialization(self):
        """Test versioned router initialization."""
        # Act
        router = VersionedRouter(prefix="/test")

        # Assert
        assert router.prefix == "/test"
        assert len(router.routes) == 0

    def test_versioned_router_add_route(self):
        """Test adding routes to versioned router."""
        # Arrange
        router = VersionedRouter(prefix="/test")
        
        def test_endpoint():
            return {"test": "data"}

        # Act
        router.add_route(
            path="/endpoint",
            endpoint=test_endpoint,
            methods=["GET"],
            versions=[APIVersion.V1, APIVersion.V2]
        )

        # Assert
        assert APIVersion.V1 in router.routes
        assert APIVersion.V2 in router.routes
        assert len(router.routes[APIVersion.V1]) == 1
        assert len(router.routes[APIVersion.V2]) == 1

        route_v1 = router.routes[APIVersion.V1][0]
        assert route_v1.path == "/api/v1/test/endpoint"

    def test_versioned_router_get_routes_for_version(self):
        """Test getting routes for specific version."""
        # Arrange
        router = VersionedRouter()
        
        def endpoint1():
            return {"endpoint": "1"}
        
        def endpoint2():
            return {"endpoint": "2"}

        router.add_route("/ep1", endpoint1, ["GET"], [APIVersion.V1])
        router.add_route("/ep2", endpoint2, ["GET"], [APIVersion.V1, APIVersion.V2])

        # Act
        v1_routes = router.get_routes_for_version(APIVersion.V1)
        v2_routes = router.get_routes_for_version(APIVersion.V2)
        v3_routes = router.get_routes_for_version(APIVersion.V3)

        # Assert
        assert len(v1_routes) == 2
        assert len(v2_routes) == 1
        assert len(v3_routes) == 0


@pytest.mark.integration
class TestVersioningIntegration:
    """Integration tests for versioning system."""

    def test_full_version_workflow(self):
        """Test complete versioning workflow."""
        # Arrange
        manager = APIVersionManager()
        
        # Register endpoints
        manager.register_endpoint("/health", "GET", APIVersion.V1)
        manager.register_endpoint("/agents", "GET", APIVersion.V2)

        # Act & Assert
        # V1 version checks
        assert manager.is_version_supported(APIVersion.V1) is True
        assert manager.is_endpoint_available("/health", "GET", APIVersion.V1) is True
        assert manager.is_endpoint_available("/agents", "GET", APIVersion.V1) is False

        # V2 version checks
        assert manager.is_version_supported(APIVersion.V2) is True
        assert manager.is_endpoint_available("/health", "GET", APIVersion.V2) is True
        assert manager.is_endpoint_available("/agents", "GET", APIVersion.V2) is True

    def test_version_manager_singleton(self):
        """Test that version manager is a singleton."""
        # Act
        manager1 = version_manager
        manager2 = version_manager

        # Assert
        assert manager1 is manager2
        assert id(manager1) == id(manager2)

    async def test_request_processing_workflow(self):
        """Test complete request processing workflow."""
        # Arrange
        request = Mock(spec=Request)
        request.url.path = "/api/v1/health"
        request.method = "GET"
        request.state = Mock()
        request.headers = {}

        call_next = Mock()
        response = Mock()
        response.headers = {}
        call_next.return_value = response

        # Register the endpoint
        version_manager.register_endpoint("/health", "GET", APIVersion.V1)

        # Act
        result = await version_middleware(request, call_next)

        # Assert
        assert result == response
        assert request.state.api_version == APIVersion.V1
        call_next.assert_called_once_with(request)