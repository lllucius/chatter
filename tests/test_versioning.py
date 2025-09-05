"""Tests for API versioning system."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from chatter.schemas.utilities import (
    APIVersion,
    EndpointVersioning,
    VersionInfo,
    VersionStatus,
)
from chatter.utils.versioning import APIVersionManager


class TestAPIVersion:
    """Test APIVersion enum."""

    def test_api_version_values(self):
        """Test API version enum values."""
        assert APIVersion.V1 == "v1"
        assert APIVersion.V2 == "v2"

    def test_api_version_string_representation(self):
        """Test API version string representation."""
        assert str(APIVersion.V1) == "v1"
        assert str(APIVersion.V2) == "v2"


class TestVersionStatus:
    """Test VersionStatus enum."""

    def test_version_status_values(self):
        """Test version status enum values."""
        assert VersionStatus.ACTIVE == "active"
        assert VersionStatus.DEPRECATED == "deprecated"
        assert VersionStatus.SUNSET == "sunset"

    def test_version_status_progression(self):
        """Test logical version status progression."""
        statuses = [VersionStatus.ACTIVE, VersionStatus.DEPRECATED, VersionStatus.SUNSET]
        
        # Each status should be a string
        for status in statuses:
            assert isinstance(status.value, str)


class TestVersionInfo:
    """Test VersionInfo dataclass."""

    def test_version_info_creation(self):
        """Test creating VersionInfo."""
        version_info = VersionInfo(
            version=APIVersion.V2,
            status=VersionStatus.ACTIVE,
            release_date="2024-01-01",
            documentation_url="https://api.example.com/docs/v2",
            breaking_changes=["Changed auth format"],
            new_features=["Added new endpoint"]
        )
        
        assert version_info.version == APIVersion.V2
        assert version_info.status == VersionStatus.ACTIVE
        assert version_info.release_date == "2024-01-01"
        assert version_info.documentation_url == "https://api.example.com/docs/v2"
        assert len(version_info.breaking_changes) == 1
        assert len(version_info.new_features) == 1

    def test_version_info_minimal(self):
        """Test creating VersionInfo with minimal fields."""
        version_info = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.ACTIVE,
            release_date="2023-01-01"
        )
        
        assert version_info.version == APIVersion.V1
        assert version_info.status == VersionStatus.ACTIVE
        assert version_info.documentation_url is None
        assert version_info.breaking_changes == []
        assert version_info.new_features == []


class TestEndpointVersioning:
    """Test EndpointVersioning dataclass."""

    def test_endpoint_versioning_creation(self):
        """Test creating EndpointVersioning."""
        endpoint = EndpointVersioning(
            path="/api/users",
            method="GET",
            introduced_in=APIVersion.V1,
            deprecated_in=APIVersion.V2,
            removed_in=None
        )
        
        assert endpoint.path == "/api/users"
        assert endpoint.method == "GET"
        assert endpoint.introduced_in == APIVersion.V1
        assert endpoint.deprecated_in == APIVersion.V2
        assert endpoint.removed_in is None

    def test_endpoint_versioning_lifecycle(self):
        """Test endpoint lifecycle through versions."""
        # Endpoint introduced in V1, deprecated in V2, removed in hypothetical V3
        endpoint = EndpointVersioning(
            path="/api/legacy",
            method="POST",
            introduced_in=APIVersion.V1,
            deprecated_in=APIVersion.V2,
            removed_in=APIVersion.V2  # Removed in V2 (immediately deprecated and removed)
        )
        
        assert endpoint.introduced_in == APIVersion.V1
        assert endpoint.deprecated_in == APIVersion.V2
        assert endpoint.removed_in == APIVersion.V2


class TestAPIVersionManager:
    """Test APIVersionManager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.manager = APIVersionManager()

    def test_manager_initialization(self):
        """Test APIVersionManager initialization."""
        assert isinstance(self.manager.versions, dict)
        assert isinstance(self.manager.endpoints, dict)
        assert self.manager.default_version == APIVersion.V1
        
        # Should have default versions loaded
        assert len(self.manager.versions) >= 2  # At least V1 and V2

    def test_default_versions_loaded(self):
        """Test that default versions are properly loaded."""
        # V1 should exist
        v1_info = self.manager.get_version_info(APIVersion.V1)
        assert v1_info is not None
        assert v1_info.version == APIVersion.V1
        assert v1_info.status == VersionStatus.DEPRECATED
        
        # V2 should exist
        v2_info = self.manager.get_version_info(APIVersion.V2)
        assert v2_info is not None
        assert v2_info.version == APIVersion.V2
        assert v2_info.status == VersionStatus.ACTIVE

    def test_add_version(self):
        """Test adding a new version."""
        new_version_info = VersionInfo(
            version=APIVersion.V1,  # Override existing
            status=VersionStatus.ACTIVE,
            release_date="2024-06-01",
            documentation_url="https://api.example.com/docs/v1-new",
            breaking_changes=[],
            new_features=["Updated V1"]
        )
        
        self.manager.add_version(new_version_info)
        
        retrieved_info = self.manager.get_version_info(APIVersion.V1)
        assert retrieved_info == new_version_info
        assert retrieved_info.documentation_url == "https://api.example.com/docs/v1-new"

    def test_get_version_info_existing(self):
        """Test getting info for existing version."""
        info = self.manager.get_version_info(APIVersion.V2)
        
        assert info is not None
        assert info.version == APIVersion.V2
        assert isinstance(info.breaking_changes, list)
        assert isinstance(info.new_features, list)

    def test_get_version_info_nonexistent(self):
        """Test getting info for non-existent version."""
        # Create a custom APIVersion that doesn't exist
        fake_version = "v99"  # This would need to be added to enum for real use
        
        # Since we can't dynamically create enum values, test with None
        info = self.manager.get_version_info(None)
        assert info is None

    def test_get_all_versions(self):
        """Test getting all versions."""
        all_versions = self.manager.get_all_versions()
        
        assert isinstance(all_versions, list)
        assert len(all_versions) >= 2  # At least V1 and V2
        
        version_numbers = [v.version for v in all_versions]
        assert APIVersion.V1 in version_numbers
        assert APIVersion.V2 in version_numbers

    def test_get_active_versions(self):
        """Test getting only active versions."""
        active_versions = self.manager.get_active_versions()
        
        assert isinstance(active_versions, list)
        
        for version_info in active_versions:
            assert version_info.status == VersionStatus.ACTIVE
        
        # V2 should be active by default
        active_version_numbers = [v.version for v in active_versions]
        assert APIVersion.V2 in active_version_numbers

    def test_is_version_supported_active(self):
        """Test version support check for active version."""
        # V2 should be supported (active)
        assert self.manager.is_version_supported(APIVersion.V2) is True

    def test_is_version_supported_deprecated(self):
        """Test version support check for deprecated version."""
        # V1 should be supported (deprecated but not sunset)
        assert self.manager.is_version_supported(APIVersion.V1) is True

    def test_is_version_supported_sunset(self):
        """Test version support check for sunset version."""
        # Create a sunset version
        sunset_version_info = VersionInfo(
            version=APIVersion.V1,  # Override V1 to be sunset
            status=VersionStatus.SUNSET,
            release_date="2023-01-01"
        )
        self.manager.add_version(sunset_version_info)
        
        # V1 should not be supported (sunset)
        assert self.manager.is_version_supported(APIVersion.V1) is False

    def test_is_version_supported_nonexistent(self):
        """Test version support check for non-existent version."""
        # Clear all versions
        self.manager.versions.clear()
        
        # Non-existent version should not be supported
        assert self.manager.is_version_supported(APIVersion.V1) is False

    def test_register_endpoint(self):
        """Test registering an endpoint with versioning info."""
        path = "/api/test"
        method = "GET"
        introduced_in = APIVersion.V1
        removed_in = APIVersion.V2
        
        self.manager.register_endpoint(
            path=path,
            method=method,
            introduced_in=introduced_in,
            removed_in=removed_in
        )
        
        endpoint_key = f"{method.upper()}:{path}"
        assert endpoint_key in self.manager.endpoints
        
        endpoint_info = self.manager.endpoints[endpoint_key]
        assert endpoint_info.path == path
        assert endpoint_info.method == method.upper()
        assert endpoint_info.introduced_in == introduced_in
        assert endpoint_info.removed_in == removed_in

    def test_register_endpoint_method_normalization(self):
        """Test that HTTP methods are normalized to uppercase."""
        self.manager.register_endpoint(
            path="/api/test",
            method="post",  # lowercase
            introduced_in=APIVersion.V1
        )
        
        endpoint_key = "POST:/api/test"  # Should be uppercase
        assert endpoint_key in self.manager.endpoints
        
        endpoint_info = self.manager.endpoints[endpoint_key]
        assert endpoint_info.method == "POST"

    def test_is_endpoint_available_current_version(self):
        """Test endpoint availability check for current version."""
        # Register endpoint available in V2
        self.manager.register_endpoint(
            path="/api/v2-feature",
            method="GET",
            introduced_in=APIVersion.V2
        )
        
        # Should be available in V2
        is_available = self.manager.is_endpoint_available(
            "/api/v2-feature", "GET", APIVersion.V2
        )
        assert is_available is True

    def test_is_endpoint_available_future_version(self):
        """Test endpoint availability for version before introduction."""
        # Register endpoint introduced in V2
        self.manager.register_endpoint(
            path="/api/future-feature",
            method="GET",
            introduced_in=APIVersion.V2
        )
        
        # Should not be available in V1 (before introduction)
        is_available = self.manager.is_endpoint_available(
            "/api/future-feature", "GET", APIVersion.V1
        )
        assert is_available is False

    def test_is_endpoint_available_after_removal(self):
        """Test endpoint availability after removal."""
        # Register endpoint that was removed in V2
        self.manager.register_endpoint(
            path="/api/legacy-feature",
            method="GET",
            introduced_in=APIVersion.V1,
            removed_in=APIVersion.V2
        )
        
        # Should be available in V1
        is_available_v1 = self.manager.is_endpoint_available(
            "/api/legacy-feature", "GET", APIVersion.V1
        )
        assert is_available_v1 is True
        
        # Should not be available in V2 (removed)
        is_available_v2 = self.manager.is_endpoint_available(
            "/api/legacy-feature", "GET", APIVersion.V2
        )
        assert is_available_v2 is False

    def test_is_endpoint_available_unregistered(self):
        """Test endpoint availability for unregistered endpoint."""
        is_available = self.manager.is_endpoint_available(
            "/api/nonexistent", "GET", APIVersion.V1
        )
        # Unregistered endpoints should be considered available
        assert is_available is True

    def test_deprecate_endpoint(self):
        """Test deprecating an endpoint."""
        # Register endpoint
        self.manager.register_endpoint(
            path="/api/to-deprecate",
            method="GET",
            introduced_in=APIVersion.V1
        )
        
        # Deprecate endpoint
        self.manager.deprecate_endpoint(
            "/api/to-deprecate", "GET", APIVersion.V2
        )
        
        endpoint_key = "GET:/api/to-deprecate"
        endpoint_info = self.manager.endpoints[endpoint_key]
        assert endpoint_info.deprecated_in == APIVersion.V2

    def test_deprecate_nonexistent_endpoint(self):
        """Test deprecating a non-existent endpoint."""
        # Should not raise error
        self.manager.deprecate_endpoint(
            "/api/nonexistent", "GET", APIVersion.V2
        )
        
        # Endpoint should not be created by deprecation
        endpoint_key = "GET:/api/nonexistent"
        assert endpoint_key not in self.manager.endpoints

    def test_get_endpoint_info(self):
        """Test getting endpoint information."""
        # Register endpoint
        self.manager.register_endpoint(
            path="/api/info-test",
            method="POST",
            introduced_in=APIVersion.V1,
            removed_in=APIVersion.V2
        )
        
        endpoint_info = self.manager.get_endpoint_info(
            "/api/info-test", "POST"
        )
        
        assert endpoint_info is not None
        assert endpoint_info.path == "/api/info-test"
        assert endpoint_info.method == "POST"
        assert endpoint_info.introduced_in == APIVersion.V1
        assert endpoint_info.removed_in == APIVersion.V2

    def test_get_endpoint_info_nonexistent(self):
        """Test getting info for non-existent endpoint."""
        endpoint_info = self.manager.get_endpoint_info(
            "/api/nonexistent", "GET"
        )
        
        assert endpoint_info is None

    def test_get_endpoints_for_version(self):
        """Test getting all endpoints available for a version."""
        # Register multiple endpoints
        endpoints_to_register = [
            ("/api/v1-only", "GET", APIVersion.V1, APIVersion.V2),
            ("/api/v1-v2", "GET", APIVersion.V1, None),
            ("/api/v2-only", "GET", APIVersion.V2, None),
        ]
        
        for path, method, introduced, removed in endpoints_to_register:
            self.manager.register_endpoint(
                path=path,
                method=method,
                introduced_in=introduced,
                removed_in=removed
            )
        
        # Get endpoints for V1
        v1_endpoints = self.manager.get_endpoints_for_version(APIVersion.V1)
        v1_paths = [ep.path for ep in v1_endpoints]
        
        assert "/api/v1-only" in v1_paths
        assert "/api/v1-v2" in v1_paths
        assert "/api/v2-only" not in v1_paths
        
        # Get endpoints for V2
        v2_endpoints = self.manager.get_endpoints_for_version(APIVersion.V2)
        v2_paths = [ep.path for ep in v2_endpoints]
        
        assert "/api/v1-only" not in v2_paths  # Removed in V2
        assert "/api/v1-v2" in v2_paths
        assert "/api/v2-only" in v2_paths

    def test_version_middleware_integration(self):
        """Test integration with versioning middleware."""
        app = FastAPI()
        
        @app.get("/api/test")
        async def test_endpoint():
            return {"message": "test"}
        
        # Add versioning middleware
        @app.middleware("http")
        async def version_middleware(request: Request, call_next):
            # Extract version from header
            api_version = request.headers.get("API-Version", "v1")
            
            # Validate version
            version_enum = APIVersion.V1 if api_version == "v1" else APIVersion.V2
            
            if not self.manager.is_version_supported(version_enum):
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=400,
                    detail=f"API version {api_version} is not supported"
                )
            
            response = await call_next(request)
            response.headers["API-Version"] = api_version
            return response
        
        client = TestClient(app)
        
        # Test with supported version
        response = client.get("/api/test", headers={"API-Version": "v2"})
        assert response.status_code == 200
        assert response.headers["API-Version"] == "v2"
        
        # Test with unsupported version (after making V1 sunset)
        sunset_v1 = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.SUNSET,
            release_date="2023-01-01"
        )
        self.manager.add_version(sunset_v1)
        
        response = client.get("/api/test", headers={"API-Version": "v1"})
        assert response.status_code == 400


@pytest.mark.integration
class TestVersioningIntegration:
    """Integration tests for versioning system."""

    def setup_method(self):
        """Set up test environment."""
        self.manager = APIVersionManager()

    def test_complete_version_lifecycle(self):
        """Test complete version lifecycle management."""
        # 1. Add a new version
        v3_info = VersionInfo(
            version=APIVersion.V2,  # Override V2 for testing
            status=VersionStatus.ACTIVE,
            release_date="2024-12-01",
            documentation_url="https://api.example.com/docs/v3",
            breaking_changes=["Restructured response format"],
            new_features=["Real-time streaming", "Enhanced security"]
        )
        self.manager.add_version(v3_info)
        
        # 2. Register endpoints for different versions
        self.manager.register_endpoint("/api/legacy", "GET", APIVersion.V1, APIVersion.V2)
        self.manager.register_endpoint("/api/stable", "GET", APIVersion.V1)
        self.manager.register_endpoint("/api/new", "GET", APIVersion.V2)
        
        # 3. Deprecate an endpoint
        self.manager.deprecate_endpoint("/api/stable", "GET", APIVersion.V2)
        
        # 4. Verify version information
        assert self.manager.is_version_supported(APIVersion.V2)
        assert len(self.manager.get_active_versions()) >= 1
        
        # 5. Check endpoint availability across versions
        assert self.manager.is_endpoint_available("/api/legacy", "GET", APIVersion.V1)
        assert not self.manager.is_endpoint_available("/api/legacy", "GET", APIVersion.V2)
        assert self.manager.is_endpoint_available("/api/stable", "GET", APIVersion.V1)
        assert self.manager.is_endpoint_available("/api/stable", "GET", APIVersion.V2)  # Deprecated but still available
        assert not self.manager.is_endpoint_available("/api/new", "GET", APIVersion.V1)
        assert self.manager.is_endpoint_available("/api/new", "GET", APIVersion.V2)

    def test_version_migration_scenario(self):
        """Test a realistic version migration scenario."""
        # Scenario: Migrating from V1 to V2 with gradual deprecation
        
        # 1. Start with V1 as active, V2 as new
        v1_info = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.ACTIVE,
            release_date="2023-01-01",
            documentation_url="https://api.example.com/docs/v1"
        )
        self.manager.add_version(v1_info)
        
        # 2. Register endpoints that exist in V1
        legacy_endpoints = [
            "/api/users",
            "/api/posts",
            "/api/comments"
        ]
        
        for endpoint in legacy_endpoints:
            self.manager.register_endpoint(endpoint, "GET", APIVersion.V1)
            self.manager.register_endpoint(endpoint, "POST", APIVersion.V1)
        
        # 3. Add V2 with some endpoints deprecated/changed
        v2_info = VersionInfo(
            version=APIVersion.V2,
            status=VersionStatus.ACTIVE,
            release_date="2024-06-01",
            documentation_url="https://api.example.com/docs/v2",
            breaking_changes=[
                "Removed /api/comments endpoint",
                "Changed /api/posts response format"
            ],
            new_features=[
                "Added /api/threads endpoint",
                "Enhanced /api/users with filtering"
            ]
        )
        self.manager.add_version(v2_info)
        
        # 4. Register V2 changes
        self.manager.register_endpoint("/api/comments", "GET", APIVersion.V1, APIVersion.V2)  # Removed in V2
        self.manager.register_endpoint("/api/threads", "GET", APIVersion.V2)  # New in V2
        self.manager.deprecate_endpoint("/api/posts", "POST", APIVersion.V2)  # Deprecated in V2
        
        # 5. Verify migration state
        # V1 endpoints
        v1_endpoints = self.manager.get_endpoints_for_version(APIVersion.V1)
        v1_paths = [ep.path for ep in v1_endpoints]
        assert "/api/users" in v1_paths
        assert "/api/posts" in v1_paths
        assert "/api/comments" in v1_paths
        assert "/api/threads" not in v1_paths
        
        # V2 endpoints
        v2_endpoints = self.manager.get_endpoints_for_version(APIVersion.V2)
        v2_paths = [ep.path for ep in v2_endpoints]
        assert "/api/users" in v2_paths
        assert "/api/posts" in v2_paths
        assert "/api/comments" not in v2_paths  # Removed
        assert "/api/threads" in v2_paths  # New
        
        # 6. Later: Sunset V1
        v1_sunset = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.SUNSET,
            release_date="2023-01-01",
            documentation_url="https://api.example.com/docs/v1"
        )
        self.manager.add_version(v1_sunset)
        
        assert not self.manager.is_version_supported(APIVersion.V1)
        assert self.manager.is_version_supported(APIVersion.V2)

    def test_backwards_compatibility_checking(self):
        """Test backwards compatibility validation."""
        # Register endpoints in V1
        self.manager.register_endpoint("/api/stable", "GET", APIVersion.V1)
        self.manager.register_endpoint("/api/changing", "GET", APIVersion.V1, APIVersion.V2)
        
        # Get compatibility report
        v1_endpoints = self.manager.get_endpoints_for_version(APIVersion.V1)
        v2_endpoints = self.manager.get_endpoints_for_version(APIVersion.V2)
        
        # Find breaking changes
        v1_paths = set(ep.path for ep in v1_endpoints)
        v2_paths = set(ep.path for ep in v2_endpoints)
        
        removed_in_v2 = v1_paths - v2_paths
        added_in_v2 = v2_paths - v1_paths
        
        # Verify our test scenario
        assert "/api/changing" in removed_in_v2
        assert "/api/stable" not in removed_in_v2