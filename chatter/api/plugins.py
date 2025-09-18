"""Plugin management endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, Query, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.plugins import (
    PluginActionResponse,
    PluginDeleteResponse,
    PluginHealthCheckResponse,
    PluginInstallRequest,
    PluginListRequest,
    PluginListResponse,
    PluginResponse,
    PluginStatsResponse,
    PluginStatus,
    PluginType,
    PluginUpdateRequest,
)
from chatter.services.plugins import PluginManager
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_plugin_manager() -> PluginManager:
    """Get plugin manager instance.

    Returns:
        PluginManager instance
    """
    from chatter.services.plugins import plugin_manager

    return plugin_manager


@router.post(
    "/install",
    response_model=PluginResponse,
    status_code=status.HTTP_201_CREATED,
)
async def install_plugin(
    install_data: PluginInstallRequest,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginResponse:
    """Install a new plugin.

    Args:
        install_data: Plugin installation data
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Installed plugin data
    """
    try:
        plugin_id = await plugin_manager.install_plugin(
            plugin_path=install_data.plugin_path,
            enable_on_install=install_data.enable_on_install,
        )

        plugin_instance = plugin_manager.plugins.get(plugin_id)
        if not plugin_instance:
            raise InternalServerProblem(
                detail="Failed to retrieve installed plugin"
            )

        return PluginResponse(
            id=plugin_instance.id,
            name=plugin_instance.manifest.name,
            version=plugin_instance.manifest.version,
            description=plugin_instance.manifest.description,
            author=plugin_instance.manifest.author,
            plugin_type=plugin_instance.manifest.plugin_type,
            status=plugin_instance.status,
            entry_point=plugin_instance.manifest.entry_point,
            capabilities=[
                cap.model_dump()
                for cap in plugin_instance.manifest.capabilities
            ],
            dependencies=plugin_instance.manifest.dependencies,
            permissions=plugin_instance.manifest.permissions,
            enabled=plugin_instance.enabled,
            error_message=plugin_instance.error_message,
            installed_at=plugin_instance.installed_at,
            updated_at=plugin_instance.updated_at,
            metadata=plugin_instance.metadata,
        )

    except Exception as e:
        logger.error("Failed to install plugin", error=str(e))
        raise InternalServerProblem(
            detail="Failed to install plugin"
        ) from e


@router.get("/", response_model=PluginListResponse)
async def list_plugins(
    plugin_type: PluginType | None = Query(
        None, description="Filter by plugin type"
    ),
    status: PluginStatus | None = Query(
        None, description="Filter by status"
    ),
    enabled: bool | None = Query(
        None, description="Filter by enabled status"
    ),
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginListResponse:
    """List installed plugins with optional filtering.

    Args:
        plugin_type: Filter by plugin type
        status: Filter by status
        enabled: Filter by enabled status
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins
    """
    try:
        plugins = list(plugin_manager.plugins.values())

        # Apply filters
        if plugin_type is not None:
            plugins = [
                p
                for p in plugins
                if p.manifest.plugin_type == plugin_type
            ]

        if status is not None:
            plugins = [p for p in plugins if p.status == status]

        if enabled is not None:
            plugins = [
                p for p in plugins if p.enabled == enabled
            ]

        plugin_responses = []
        for plugin in plugins:
            plugin_responses.append(
                PluginResponse(
                    id=plugin.id,
                    name=plugin.manifest.name,
                    version=plugin.manifest.version,
                    description=plugin.manifest.description,
                    author=plugin.manifest.author,
                    plugin_type=plugin.manifest.plugin_type,
                    status=plugin.status,
                    entry_point=plugin.manifest.entry_point,
                    capabilities=[
                        cap.model_dump()
                        for cap in plugin.manifest.capabilities
                    ],
                    dependencies=plugin.manifest.dependencies,
                    permissions=plugin.manifest.permissions,
                    enabled=plugin.enabled,
                    error_message=plugin.error_message,
                    installed_at=plugin.installed_at,
                    updated_at=plugin.updated_at,
                    metadata=plugin.metadata,
                )
            )

        return PluginListResponse(
            plugins=plugin_responses, total=len(plugin_responses)
        )

    except Exception as e:
        logger.error("Failed to list plugins", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list plugins"
        ) from e


@router.get("/{plugin_id}", response_model=PluginResponse)
async def get_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginResponse:
    """Get plugin by ID.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Plugin data
    """
    try:
        plugin = plugin_manager.plugins.get(plugin_id)
        if not plugin:
            raise NotFoundProblem(
                detail=f"Plugin {plugin_id} not found"
            )

        return PluginResponse(
            id=plugin.id,
            name=plugin.manifest.name,
            version=plugin.manifest.version,
            description=plugin.manifest.description,
            author=plugin.manifest.author,
            plugin_type=plugin.manifest.plugin_type,
            status=plugin.status,
            entry_point=plugin.manifest.entry_point,
            capabilities=[
                cap.model_dump() for cap in plugin.manifest.capabilities
            ],
            dependencies=plugin.manifest.dependencies,
            permissions=plugin.manifest.permissions,
            enabled=plugin.enabled,
            error_message=plugin.error_message,
            installed_at=plugin.installed_at,
            updated_at=plugin.updated_at,
            metadata=plugin.metadata,
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to get plugin", plugin_id=plugin_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to get plugin"
        ) from e


@router.put("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: str,
    update_data: PluginUpdateRequest,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginResponse:
    """Update a plugin.

    Args:
        plugin_id: Plugin ID
        update_data: Plugin update data
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Updated plugin data
    """
    try:
        plugin = plugin_manager.plugins.get(plugin_id)
        if not plugin:
            raise NotFoundProblem(
                detail=f"Plugin {plugin_id} not found"
            )

        # Update plugin configuration
        if update_data.configuration is not None:
            plugin.configuration.update(update_data.configuration)

        # Handle enable/disable
        if (
            update_data.enabled is not None
            and update_data.enabled != plugin.enabled
        ):
            if update_data.enabled:
                await plugin_manager.enable_plugin(plugin_id)
            else:
                await plugin_manager.disable_plugin(plugin_id)

        # Update timestamp
        from datetime import UTC, datetime

        plugin.updated_at = datetime.now(UTC)

        return PluginResponse(
            id=plugin.id,
            name=plugin.manifest.name,
            version=plugin.manifest.version,
            description=plugin.manifest.description,
            author=plugin.manifest.author,
            plugin_type=plugin.manifest.plugin_type,
            status=plugin.status,
            entry_point=plugin.manifest.entry_point,
            capabilities=[
                cap.model_dump() for cap in plugin.manifest.capabilities
            ],
            dependencies=plugin.manifest.dependencies,
            permissions=plugin.manifest.permissions,
            enabled=plugin.enabled,
            error_message=plugin.error_message,
            installed_at=plugin.installed_at,
            updated_at=plugin.updated_at,
            metadata=plugin.metadata,
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to update plugin", plugin_id=plugin_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to update plugin"
        ) from e


@router.delete("/{plugin_id}", response_model=PluginDeleteResponse)
async def uninstall_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginDeleteResponse:
    """Uninstall a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Uninstall result
    """
    try:
        success = await plugin_manager.uninstall_plugin(plugin_id)

        if not success:
            raise NotFoundProblem(
                detail=f"Plugin {plugin_id} not found"
            )

        return PluginDeleteResponse(
            success=True,
            message=f"Plugin {plugin_id} uninstalled successfully",
        )

    except NotFoundProblem:
        raise
    except Exception as e:
        logger.error(
            "Failed to uninstall plugin",
            plugin_id=plugin_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to uninstall plugin"
        ) from e


@router.post("/{plugin_id}/enable", response_model=PluginActionResponse)
async def enable_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginActionResponse:
    """Enable a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Action result
    """
    try:
        success = await plugin_manager.enable_plugin(plugin_id)

        if not success:
            # Get plugin instance to provide more detailed error information
            plugin_instance = await plugin_manager.get_plugin(plugin_id)
            if not plugin_instance:
                raise NotFoundProblem(
                    detail=f"Plugin {plugin_id} not found"
                )

            error_detail = "Failed to enable plugin"
            if plugin_instance.error_message:
                error_detail += f": {plugin_instance.error_message}"

            raise BadRequestProblem(detail=error_detail)

        return PluginActionResponse(
            success=True,
            message=f"Plugin {plugin_id} enabled successfully",
            plugin_id=plugin_id,
        )

    except (BadRequestProblem, NotFoundProblem):
        raise
    except Exception as e:
        logger.error(
            "Failed to enable plugin", plugin_id=plugin_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to enable plugin"
        ) from e


@router.post(
    "/{plugin_id}/disable", response_model=PluginActionResponse
)
async def disable_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginActionResponse:
    """Disable a plugin.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Action result
    """
    try:
        success = await plugin_manager.disable_plugin(plugin_id)

        if not success:
            # Get plugin instance to provide more detailed error information
            plugin_instance = await plugin_manager.get_plugin(plugin_id)
            if not plugin_instance:
                raise NotFoundProblem(
                    detail=f"Plugin {plugin_id} not found"
                )

            raise BadRequestProblem(detail="Failed to disable plugin")

        return PluginActionResponse(
            success=True,
            message=f"Plugin {plugin_id} disabled successfully",
            plugin_id=plugin_id,
        )

    except (BadRequestProblem, NotFoundProblem):
        raise
    except Exception as e:
        logger.error(
            "Failed to disable plugin",
            plugin_id=plugin_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to disable plugin"
        ) from e


@router.get("/health", response_model=PluginHealthCheckResponse)
async def health_check_plugins(
    auto_disable_unhealthy: bool = False,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginHealthCheckResponse:
    """Perform health check on all plugins.

    Args:
        auto_disable_unhealthy: Whether to automatically disable unhealthy plugins
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Health check results
    """
    try:
        results = await plugin_manager.health_check_plugins(
            auto_disable_unhealthy
        )

        # Summarize results
        total_plugins = len(results)
        healthy_plugins = sum(
            1 for r in results.values() if r.get("healthy", False)
        )
        unhealthy_plugins = total_plugins - healthy_plugins

        return PluginHealthCheckResponse(
            summary={
                "total_plugins": total_plugins,
                "healthy_plugins": healthy_plugins,
                "unhealthy_plugins": unhealthy_plugins,
                "auto_disable_enabled": auto_disable_unhealthy,
            },
            results=results,
        )

    except Exception as e:
        logger.error("Failed to perform health check", error=str(e))
        raise InternalServerProblem(
            detail="Failed to perform health check"
        ) from e


@router.get("/stats", response_model=PluginStatsResponse)
async def get_plugin_stats(
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginStatsResponse:
    """Get plugin system statistics.

    Args:
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Plugin system statistics
    """
    try:
        stats = await plugin_manager.get_plugin_stats()
        return PluginStatsResponse(**stats)

    except Exception as e:
        logger.error("Failed to get plugin stats", error=str(e))
        raise InternalServerProblem(
            detail="Failed to get plugin stats"
        ) from e


@router.get("/{plugin_id}/dependencies", response_model=dict)
async def check_plugin_dependencies(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> dict[str, Any]:
    """Check plugin dependencies.

    Args:
        plugin_id: Plugin ID
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Dependency check results
    """
    try:
        results = await plugin_manager.check_plugin_dependencies(
            plugin_id
        )
        return results

    except Exception as e:
        logger.error(
            "Failed to check plugin dependencies",
            plugin_id=plugin_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to check plugin dependencies"
        ) from e


@router.post("/bulk/enable", response_model=dict)
async def bulk_enable_plugins(
    plugin_ids: list[str],
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> dict[str, Any]:
    """Enable multiple plugins.

    Args:
        plugin_ids: List of plugin IDs to enable
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Bulk operation results
    """
    try:
        results = await plugin_manager.bulk_enable_plugins(plugin_ids)

        success_count = sum(
            1 for success in results.values() if success
        )
        total_count = len(plugin_ids)

        return {
            "success_count": success_count,
            "total_count": total_count,
            "results": results,
        }

    except Exception as e:
        logger.error("Failed to bulk enable plugins", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk enable plugins"
        ) from e


@router.post("/bulk/disable", response_model=dict)
async def bulk_disable_plugins(
    plugin_ids: list[str],
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> dict[str, Any]:
    """Disable multiple plugins.

    Args:
        plugin_ids: List of plugin IDs to disable
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        Bulk operation results
    """
    try:
        results = await plugin_manager.bulk_disable_plugins(plugin_ids)

        success_count = sum(
            1 for success in results.values() if success
        )
        total_count = len(plugin_ids)

        return {
            "success_count": success_count,
            "total_count": total_count,
            "results": results,
        }

    except Exception as e:
        logger.error("Failed to bulk disable plugins", error=str(e))
        raise InternalServerProblem(
            detail="Failed to bulk disable plugins"
        ) from e
