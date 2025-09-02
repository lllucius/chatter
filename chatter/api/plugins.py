"""Plugin management endpoints."""

from fastapi import APIRouter, Depends, status

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.plugins import (
    PluginActionResponse,
    PluginDeleteResponse,
    PluginInstallRequest,
    PluginListRequest,
    PluginListResponse,
    PluginResponse,
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
    request: PluginListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    plugin_manager: PluginManager = Depends(get_plugin_manager),
) -> PluginListResponse:
    """List installed plugins with optional filtering.

    Args:
        request: List request parameters
        current_user: Current authenticated user
        plugin_manager: Plugin manager instance

    Returns:
        List of installed plugins
    """
    try:
        plugins = list(plugin_manager.plugins.values())

        # Apply filters
        if request.plugin_type is not None:
            plugins = [
                p
                for p in plugins
                if p.manifest.plugin_type == request.plugin_type
            ]

        if request.status is not None:
            plugins = [p for p in plugins if p.status == request.status]

        if request.enabled is not None:
            plugins = [
                p for p in plugins if p.enabled == request.enabled
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
            raise BadRequestProblem(
                detail="Failed to enable plugin - check plugin status and dependencies"
            )

        return PluginActionResponse(
            success=True,
            message=f"Plugin {plugin_id} enabled successfully",
            plugin_id=plugin_id,
        )

    except BadRequestProblem:
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
            raise BadRequestProblem(detail="Failed to disable plugin")

        return PluginActionResponse(
            success=True,
            message=f"Plugin {plugin_id} disabled successfully",
            plugin_id=plugin_id,
        )

    except BadRequestProblem:
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
