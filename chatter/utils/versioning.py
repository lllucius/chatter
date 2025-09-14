"""API versioning strategy and management."""

import re
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.routing import APIRoute
from starlette.responses import Response

from chatter.config import settings
from chatter.schemas.utilities import (
    APIVersion,
    EndpointVersioning,
    VersionInfo,
    VersionStatus,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class APIVersionManager:
    """Manages API versioning strategy."""

    def __init__(self) -> None:
        """Initialize the API version manager."""
        self.versions: dict[APIVersion, VersionInfo] = {}
        self.endpoints: dict[str, EndpointVersioning] = {}
        self.default_version = APIVersion.V1
        self._setup_versions()

    def _setup_versions(self) -> None:
        """Setup version information."""
        self.versions[APIVersion.V1] = VersionInfo(
            version=APIVersion.V1,
            status=VersionStatus.ACTIVE,
            release_date="2024-01-01",
            documentation_url=f"{settings.api_base_url}/docs/v1",
            new_features=[
                "Core chat functionality",
                "Document management",
                "User authentication",
                "Vector store operations",
                "Basic LangGraph workflows",
            ],
        )

        self.versions[APIVersion.V2] = VersionInfo(
            version=APIVersion.V2,
            status=VersionStatus.ACTIVE,
            release_date="2024-08-01",
            documentation_url=f"{settings.api_base_url}/docs/v2",
            breaking_changes=[
                "Changed response format for chat endpoints",
                "Updated authentication token structure",
                "Modified error response schema",
                "Replaced PostgreSQL checkpointing with Redis checkpointing for LangGraph",
            ],
            new_features=[
                "AI agent management",
                "Advanced job queue system",
                "Conversation branching and forking",
                "A/B testing infrastructure",
                "Enhanced security validation",
                "Advanced vector store filtering",
                "Redis checkpointer for LangGraph",
            ],
        )

    def add_version(self, version_info: VersionInfo) -> None:
        """Add a new API version.

        Args:
            version_info: Version information
        """
        self.versions[version_info.version] = version_info
        logger.info(f"Added API version {version_info.version}")

    def get_version_info(
        self, version: APIVersion
    ) -> VersionInfo | None:
        """Get information about a specific version.

        Args:
            version: API version

        Returns:
            Version information or None if not found
        """
        return self.versions.get(version)

    def get_all_versions(self) -> list[VersionInfo]:
        """Get information about all versions.

        Returns:
            List of version information
        """
        return list(self.versions.values())

    def get_active_versions(self) -> list[VersionInfo]:
        """Get all active API versions.

        Returns:
            List of active versions
        """
        return [
            info
            for info in self.versions.values()
            if info.status == VersionStatus.ACTIVE
        ]

    def is_version_supported(self, version: APIVersion) -> bool:
        """Check if a version is supported.

        Args:
            version: API version to check

        Returns:
            True if supported, False otherwise
        """
        version_info = self.versions.get(version)
        return (
            version_info is not None
            and version_info.status != VersionStatus.SUNSET
        )

    def register_endpoint(
        self,
        path: str,
        method: str,
        introduced_in: APIVersion,
        removed_in: APIVersion | None = None,
    ) -> None:
        """Register an endpoint with versioning information.

        Args:
            path: Endpoint path
            method: HTTP method
            introduced_in: Version where endpoint was introduced
            removed_in: Version where endpoint was removed
        """
        endpoint_key = f"{method.upper()}:{path}"
        self.endpoints[endpoint_key] = EndpointVersioning(
            path=path,
            method=method.upper(),
            introduced_in=introduced_in,
            removed_in=removed_in,
        )

    def is_endpoint_available(
        self, path: str, method: str, version: APIVersion
    ) -> bool:
        """Check if an endpoint is available in a specific version.

        Args:
            path: Endpoint path
            method: HTTP method
            version: API version

        Returns:
            True if available, False otherwise
        """
        endpoint_key = f"{method.upper()}:{path}"
        endpoint = self.endpoints.get(endpoint_key)

        if not endpoint:
            return False

        # Check if introduced
        if endpoint.introduced_in.value > version.value:
            return False

        # Check if removed
        if (
            endpoint.removed_in
            and endpoint.removed_in.value <= version.value
        ):
            return False

        return True

    def get_endpoint_status(
        self, path: str, method: str, version: APIVersion
    ) -> str | None:
        """Get the status of an endpoint in a specific version.

        Args:
            path: Endpoint path
            method: HTTP method
            version: API version

        Returns:
            Endpoint status or None if not found
        """
        endpoint_key = f"{method.upper()}:{path}"
        endpoint = self.endpoints.get(endpoint_key)

        if not endpoint:
            return None

        if not self.is_endpoint_available(path, method, version):
            return "unavailable"

        return "active"


def extract_version_from_request(request: Request) -> APIVersion:
    """Extract API version from request.

    Args:
        request: FastAPI request object

    Returns:
        Extracted API version
    """
    # Check URL path for version (e.g., /api/v1/...)
    path_match = re.match(r"/api/(v\d+)/", request.url.path)
    if path_match:
        version_str = path_match.group(1)
        try:
            return APIVersion(version_str)
        except ValueError:
            pass

    # Check Accept header for version
    accept_header = request.headers.get("Accept", "")
    version_match = re.search(
        r"application/vnd\.chatter\.(v\d+)\+json", accept_header
    )
    if version_match:
        version_str = version_match.group(1)
        try:
            return APIVersion(version_str)
        except ValueError:
            pass

    # Check custom header
    api_version_header = request.headers.get("API-Version")
    if api_version_header:
        try:
            return APIVersion(api_version_header)
        except ValueError:
            pass

    # Return default version
    return version_manager.default_version


async def version_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Middleware to handle API versioning.

    Args:
        request: FastAPI request object
        call_next: Next middleware in chain

    Returns:
        Response with version headers
    """
    # Extract version from request
    version = extract_version_from_request(request)

    # Check if version is supported
    if not version_manager.is_version_supported(version):
        raise HTTPException(
            status_code=400,
            detail=f"API version {version.value} is not supported",
        )

    # Add version to request state
    request.state.api_version = version

    # Check endpoint availability
    path = request.url.path
    method = request.method

    # Remove version prefix from path for endpoint checking
    clean_path = re.sub(r"/api/v\d+", "", path)

    if not version_manager.is_endpoint_available(
        clean_path, method, version
    ):
        raise HTTPException(
            status_code=404,
            detail=f"Endpoint not available in API version {version.value}",
        )

    # Process request
    response = await call_next(request)

    # Add version headers to response
    response.headers["API-Version"] = version.value
    response.headers["API-Supported-Versions"] = ",".join(
        [v.value for v in APIVersion]
    )

    return response


def create_versioned_app() -> FastAPI:
    """Create FastAPI app with versioning support.

    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="Chatter API",
        description="Advanced AI Chatbot Backend API Platform",
        version=settings.api_version,
    )

    # Add version middleware
    app.middleware("http")(version_middleware)

    return app


def version_route(
    versions: list[APIVersion],
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator to mark routes with version information.

    Args:
        versions: List of supported versions

    Returns:
        Route decorator
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Add version metadata to function
        func._api_versions = versions  # type: ignore[attr-defined]

        # Register endpoint with version manager
        # This would be called during route registration
        # For now, just mark the function

        return func

    return decorator


class VersionedRouter:
    """Router that supports versioning."""

    def __init__(self, prefix: str = "") -> None:
        """Initialize versioned router.

        Args:
            prefix: Route prefix
        """
        self.prefix = prefix
        self.routes: dict[APIVersion, list[APIRoute]] = {}

    def add_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        methods: list[str],
        versions: list[APIVersion],
        **kwargs: Any,
    ) -> None:
        """Add a versioned route.

        Args:
            path: Route path
            endpoint: Route endpoint function
            methods: HTTP methods
            versions: Supported API versions
            **kwargs: Additional route arguments
        """
        for version in versions:
            if version not in self.routes:
                self.routes[version] = []

            versioned_path = f"/api/{version.value}{self.prefix}{path}"
            route = APIRoute(
                path=versioned_path,
                endpoint=endpoint,
                methods=methods,
                **kwargs,
            )
            self.routes[version].append(route)

    def get_routes_for_version(
        self, version: APIVersion
    ) -> list[APIRoute]:
        """Get routes for a specific version.

        Args:
            version: API version

        Returns:
            List of routes for the version
        """
        return self.routes.get(version, [])


# Global version manager
version_manager = APIVersionManager()


# Example of how to use versioning decorators
@version_route(versions=[APIVersion.V1, APIVersion.V2])
async def get_health() -> dict[str, str]:
    """Health check endpoint available in all versions."""
    return {"status": "healthy"}


@version_route(versions=[APIVersion.V2])
async def get_agents() -> dict[str, list[Any]]:
    """Agent management endpoint only in v2."""
    return {"agents": []}
