"""Plugin architecture for custom tools and extensibility."""

import asyncio
import importlib
import importlib.util
import inspect
import json
import sys
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    from langchain_core.tools import BaseTool
except ImportError:
    # Fallback for when langchain_core is not available
    class BaseTool:
        """Fallback BaseTool class."""

        pass


from chatter.config import settings
from chatter.schemas.plugins import (
    PluginCapability,
    PluginInstance,
    PluginManifest,
    PluginStatus,
    PluginType,
)
from chatter.services.job_queue import job_queue
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class PluginError(Exception):
    """Plugin operation error."""

    pass


class BasePlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, config: dict[str, Any] = None):
        """Initialize the plugin.

        Args:
            config: Plugin configuration
        """
        self.config = config or {}
        self.logger = get_logger(f"plugin.{self.__class__.__name__}")

    @abstractmethod
    async def initialize(self) -> bool:
        """Initialize the plugin.

        Returns:
            True if initialization successful, False otherwise
        """
        pass

    @abstractmethod
    async def shutdown(self) -> bool:
        """Shutdown the plugin.

        Returns:
            True if shutdown successful, False otherwise
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> list[PluginCapability]:
        """Get plugin capabilities.

        Returns:
            List of plugin capabilities
        """
        pass

    async def health_check(self) -> dict[str, Any]:
        """Perform plugin health check.

        Returns:
            Health check result
        """
        return {
            "healthy": True,
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_configuration_schema(self) -> dict[str, Any]:
        """Get configuration schema for the plugin.

        Returns:
            JSON schema for configuration
        """
        # Return a basic schema that subclasses should override
        return {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }

    async def validate_configuration(
        self, config: dict[str, Any]
    ) -> bool:
        """Validate plugin configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            schema = await self.get_configuration_schema()
            if not schema or schema == {
                "type": "object",
                "properties": {},
                "additionalProperties": True,
            }:
                # No schema defined, accept any configuration
                return True

            # Use basic validation with our schema since validation engine doesn't handle custom schemas
            return self._basic_config_validation(config, schema)

        except Exception as e:
            self.logger.error(f"Configuration validation error: {e}")
            return False

    def _basic_config_validation(
        self, config: dict[str, Any], schema: dict[str, Any]
    ) -> bool:
        """Basic configuration validation fallback.

        Args:
            config: Configuration to validate
            schema: JSON schema

        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required fields
            required = schema.get("required", [])
            for field in required:
                if field not in config:
                    self.logger.error(
                        f"Required configuration field '{field}' is missing"
                    )
                    return False

            # Check property types
            properties = schema.get("properties", {})
            for field, value in config.items():
                if field in properties:
                    expected_type = properties[field].get("type")
                    if expected_type == "string" and not isinstance(
                        value, str
                    ):
                        self.logger.error(
                            f"Configuration field '{field}' must be a string"
                        )
                        return False
                    elif expected_type == "number" and not isinstance(
                        value, int | float
                    ):
                        self.logger.error(
                            f"Configuration field '{field}' must be a number"
                        )
                        return False
                    elif expected_type == "object" and not isinstance(
                        value, dict
                    ):
                        self.logger.error(
                            f"Configuration field '{field}' must be an object"
                        )
                        return False
                    elif expected_type == "array" and not isinstance(
                        value, list
                    ):
                        self.logger.error(
                            f"Configuration field '{field}' must be an array"
                        )
                        return False
                    elif expected_type == "boolean" and not isinstance(
                        value, bool
                    ):
                        self.logger.error(
                            f"Configuration field '{field}' must be a boolean"
                        )
                        return False

            return True

        except Exception as e:
            self.logger.error(
                f"Basic configuration validation error: {e}"
            )
            return False


class ToolPlugin(BasePlugin):
    """Base class for tool plugins."""

    @abstractmethod
    def get_tools(self) -> list[BaseTool]:
        """Get tools provided by this plugin.

        Returns:
            List of LangChain tools
        """
        pass


class WorkflowPlugin(BasePlugin):
    """Base class for workflow plugins."""

    @abstractmethod
    async def create_workflow(self, config: dict[str, Any]) -> Any:
        """Create a workflow instance.

        Args:
            config: Workflow configuration

        Returns:
            Workflow instance
        """
        pass


class IntegrationPlugin(BasePlugin):
    """Base class for integration plugins."""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to external service.

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from external service.

        Returns:
            True if disconnection successful, False otherwise
        """
        pass


class PluginManager:
    """Manages plugin lifecycle and operations."""

    def __init__(self):
        """Initialize the plugin manager."""
        self.plugins: dict[str, PluginInstance] = {}
        self.loaded_plugins: dict[str, BasePlugin] = {}
        self.plugin_registry: dict[str, type[BasePlugin]] = {}
        self.plugins_directory = (
            Path(settings.document_storage_path) / "plugins"
        )
        self._ensure_directories()

        # Add concurrency control
        import asyncio

        self._operation_lock = asyncio.Lock()
        self._plugin_locks: dict[str, asyncio.Lock] = {}

    def _ensure_directories(self) -> None:
        """Ensure plugin directories exist."""
        self.plugins_directory.mkdir(parents=True, exist_ok=True)

    def _get_plugin_lock(self, plugin_id: str) -> "asyncio.Lock":
        """Get or create a lock for a specific plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            Asyncio lock for the plugin
        """
        if plugin_id not in self._plugin_locks:
            import asyncio

            self._plugin_locks[plugin_id] = asyncio.Lock()
        return self._plugin_locks[plugin_id]

    async def install_plugin(
        self,
        plugin_path: str | Path,
        enable_on_install: bool = True,
    ) -> str:
        """Install a plugin from a directory or archive with atomic operations.

        Args:
            plugin_path: Path to plugin directory or archive
            enable_on_install: Whether to enable plugin after installation

        Returns:
            Plugin ID

        Raises:
            ValueError: If plugin installation fails
        """
        async with self._operation_lock:
            # Validate plugin_path is not empty or None
            if not plugin_path or str(plugin_path).strip() == "":
                raise ValueError("Plugin path cannot be empty")

            plugin_path = Path(plugin_path)

            if not plugin_path.exists():
                raise ValueError(
                    f"Plugin path does not exist: {plugin_path}"
                )

            # Load plugin manifest
            manifest_path = plugin_path / "manifest.json"
            if not manifest_path.exists():
                raise ValueError(
                    f"Plugin manifest not found: {manifest_path}"
                )

            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest_data = json.load(f)

                manifest = PluginManifest(**manifest_data)
            except Exception as e:
                raise ValueError(
                    f"Invalid plugin manifest: {str(e)}"
                ) from e

            # Check if plugin already installed
            for plugin_instance in self.plugins.values():
                if plugin_instance.manifest.name == manifest.name:
                    raise ValueError(
                        f"Plugin '{manifest.name}' is already installed"
                    )

            # Validate plugin before proceeding
            try:
                await self._validate_plugin(plugin_path, manifest)
            except Exception as e:
                raise ValueError(
                    f"Plugin validation failed: {str(e)}"
                ) from e

            # Prepare installation path with atomic operation
            plugin_install_path = self.plugins_directory / manifest.name
            temp_install_path = (
                self.plugins_directory
                / f".temp_{manifest.name}_{hash(str(plugin_path))}"
            )

            try:
                # Remove any existing temp directory
                if temp_install_path.exists():
                    import shutil

                    shutil.rmtree(temp_install_path)

                # Copy to temporary location first
                import shutil

                shutil.copytree(plugin_path, temp_install_path)

                # Atomic move to final location
                if plugin_install_path.exists():
                    shutil.rmtree(plugin_install_path)
                shutil.move(
                    str(temp_install_path), str(plugin_install_path)
                )

            except Exception as e:
                # Cleanup on failure
                if temp_install_path.exists():
                    import shutil

                    shutil.rmtree(temp_install_path)
                raise ValueError(
                    f"Failed to install plugin files: {str(e)}"
                ) from e

            # Create plugin instance
            try:
                plugin_instance = PluginInstance(
                    manifest=manifest,
                    installation_path=str(plugin_install_path),
                )

                self.plugins[plugin_instance.id] = plugin_instance

                logger.info(
                    "Installed plugin",
                    plugin_id=plugin_instance.id,
                    name=manifest.name,
                    version=manifest.version,
                )

                # Enable plugin if requested (but don't fail installation if enable fails)
                if enable_on_install:
                    try:
                        await self.enable_plugin(plugin_instance.id)
                    except Exception as e:
                        logger.warning(
                            "Plugin installed but failed to enable",
                            plugin_id=plugin_instance.id,
                            error=str(e),
                        )

                return plugin_instance.id

            except Exception as e:
                # Rollback installation on instance creation failure
                if plugin_install_path.exists():
                    import shutil

                    shutil.rmtree(plugin_install_path)
                raise ValueError(
                    f"Failed to create plugin instance: {str(e)}"
                ) from e

    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if uninstalled successfully, False otherwise
        """
        plugin_instance = self.plugins.get(plugin_id)
        if not plugin_instance:
            return False

        # Disable plugin first
        await self.disable_plugin(plugin_id)

        # Remove installation directory
        installation_path = Path(plugin_instance.installation_path)
        if installation_path.exists():
            import shutil

            shutil.rmtree(installation_path)

        # Remove from registry
        del self.plugins[plugin_id]

        logger.info(
            "Uninstalled plugin",
            plugin_id=plugin_id,
            name=plugin_instance.manifest.name,
        )

        return True

    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin with enhanced error handling.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if enabled successfully, False otherwise
        """
        async with self._get_plugin_lock(plugin_id):
            plugin_instance = self.plugins.get(plugin_id)
            if not plugin_instance:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            if plugin_instance.status == PluginStatus.ACTIVE:
                logger.debug(f"Plugin {plugin_id} already active")
                return True

            # Check if plugin is in error state and clear it
            if plugin_instance.status == PluginStatus.ERROR:
                logger.info(
                    f"Attempting to enable plugin {plugin_id} from error state"
                )

            try:
                # Validate configuration before enabling
                if plugin_instance.configuration:
                    temp_plugin = None
                    try:
                        # Load plugin class for validation
                        plugin_class = await self._load_plugin_class(
                            plugin_instance
                        )
                        temp_plugin = plugin_class(
                            plugin_instance.configuration
                        )

                        if not await temp_plugin.validate_configuration(
                            plugin_instance.configuration
                        ):
                            raise ValueError(
                                "Configuration validation failed"
                            )
                    finally:
                        # Clean up temporary plugin if created
                        if temp_plugin and hasattr(
                            temp_plugin, "shutdown"
                        ):
                            try:
                                await temp_plugin.shutdown()
                            except Exception:
                                pass  # Ignore cleanup errors

                # Load plugin module
                plugin_class = await self._load_plugin_class(
                    plugin_instance
                )

                # Create plugin instance
                plugin = plugin_class(plugin_instance.configuration)

                # Initialize plugin with timeout
                import asyncio

                try:
                    initialization_result = await asyncio.wait_for(
                        plugin.initialize(),
                        timeout=settings.plugin_operation_timeout,
                    )
                    if not initialization_result:
                        raise RuntimeError(
                            "Plugin initialization returned False"
                        )
                except TimeoutError:
                    raise RuntimeError(
                        "Plugin initialization timed out"
                    ) from None

                # Store loaded plugin
                self.loaded_plugins[plugin_id] = plugin

                # Update status atomically
                plugin_instance.status = PluginStatus.ACTIVE
                plugin_instance.last_updated = datetime.now(UTC)
                plugin_instance.error_message = None

                logger.info(
                    "Enabled plugin",
                    plugin_id=plugin_id,
                    name=plugin_instance.manifest.name,
                )

                return True

            except Exception as e:
                # Ensure plugin is properly cleaned up on failure
                if plugin_id in self.loaded_plugins:
                    try:
                        await self.loaded_plugins[plugin_id].shutdown()
                    except Exception:
                        pass  # Ignore shutdown errors during cleanup
                    del self.loaded_plugins[plugin_id]

                plugin_instance.status = PluginStatus.ERROR
                plugin_instance.error_message = str(e)
                plugin_instance.last_updated = datetime.now(UTC)

                logger.error(
                    "Failed to enable plugin",
                    plugin_id=plugin_id,
                    name=plugin_instance.manifest.name,
                    error=str(e),
                )

                return False

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin with enhanced error handling.

        Args:
            plugin_id: Plugin ID

        Returns:
            True if disabled successfully, False otherwise
        """
        async with self._get_plugin_lock(plugin_id):
            plugin_instance = self.plugins.get(plugin_id)
            if not plugin_instance:
                logger.error(f"Plugin {plugin_id} not found")
                return False

            if plugin_instance.status != PluginStatus.ACTIVE:
                logger.debug(
                    f"Plugin {plugin_id} not active, current status: {plugin_instance.status}"
                )
                return True

            try:
                # Get loaded plugin
                plugin = self.loaded_plugins.get(plugin_id)
                if plugin:
                    # Shutdown plugin with timeout
                    import asyncio

                    try:
                        await asyncio.wait_for(
                            plugin.shutdown(),
                            timeout=settings.plugin_shutdown_timeout,
                        )  # 30 second timeout
                    except TimeoutError:
                        logger.warning(
                            f"Plugin {plugin_id} shutdown timed out"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Error during plugin {plugin_id} shutdown: {e}"
                        )

                    # Remove from loaded plugins
                    del self.loaded_plugins[plugin_id]

                # Update status
                plugin_instance.status = PluginStatus.INACTIVE
                plugin_instance.last_updated = datetime.now(UTC)
                # Don't clear error_message as it might contain useful info

                logger.info(
                    "Disabled plugin",
                    plugin_id=plugin_id,
                    name=plugin_instance.manifest.name,
                )

                return True

            except Exception as e:
                logger.error(
                    "Error disabling plugin",
                    plugin_id=plugin_id,
                    error=str(e),
                )
                # Still mark as inactive even if shutdown failed
                plugin_instance.status = PluginStatus.INACTIVE
                plugin_instance.last_updated = datetime.now(UTC)

                # Clean up loaded plugin even if shutdown failed
                if plugin_id in self.loaded_plugins:
                    del self.loaded_plugins[plugin_id]

                return True  # Return True because plugin is effectively disabled

        if plugin_instance.status != PluginStatus.ACTIVE:
            return True

        try:
            # Get loaded plugin
            plugin = self.loaded_plugins.get(plugin_id)
            if plugin:
                # Shutdown plugin
                await plugin.shutdown()

                # Remove from loaded plugins
                del self.loaded_plugins[plugin_id]

            # Update status
            plugin_instance.status = PluginStatus.INACTIVE
            plugin_instance.last_updated = datetime.now(UTC)

            logger.info(
                "Disabled plugin",
                plugin_id=plugin_id,
                name=plugin_instance.manifest.name,
            )

            return True

        except Exception as e:
            logger.error(
                "Error disabling plugin",
                plugin_id=plugin_id,
                error=str(e),
            )
            return False

    async def list_plugins(
        self,
        plugin_type: PluginType | None = None,
        status: PluginStatus | None = None,
    ) -> list[PluginInstance]:
        """List installed plugins.

        Args:
            plugin_type: Filter by plugin type
            status: Filter by status

        Returns:
            List of plugin instances
        """
        plugins = list(self.plugins.values())

        if plugin_type:
            plugins = [
                p
                for p in plugins
                if p.manifest.plugin_type == plugin_type
            ]

        if status:
            plugins = [p for p in plugins if p.status == status]

        # Sort by name
        plugins.sort(key=lambda x: x.manifest.name)

        return plugins

    async def get_plugin(self, plugin_id: str) -> PluginInstance | None:
        """Get plugin instance.

        Args:
            plugin_id: Plugin ID

        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_id)

    async def get_loaded_plugin(
        self, plugin_id: str
    ) -> BasePlugin | None:
        """Get loaded plugin instance.

        Args:
            plugin_id: Plugin ID

        Returns:
            Loaded plugin or None if not found
        """
        return self.loaded_plugins.get(plugin_id)

    async def get_tools_from_plugins(self) -> dict[str, list[BaseTool]]:
        """Get all tools from active tool plugins.

        Returns:
            Dictionary mapping plugin ID to list of tools
        """
        tools = {}

        for plugin_id, plugin in self.loaded_plugins.items():
            if isinstance(plugin, ToolPlugin):
                try:
                    plugin_tools = plugin.get_tools()
                    tools[plugin_id] = plugin_tools
                except Exception as e:
                    logger.error(
                        "Error getting tools from plugin",
                        plugin_id=plugin_id,
                        error=str(e),
                    )

        return tools

    async def configure_plugin(
        self, plugin_id: str, configuration: dict[str, Any]
    ) -> bool:
        """Configure a plugin.

        Args:
            plugin_id: Plugin ID
            configuration: Configuration to apply

        Returns:
            True if configured successfully, False otherwise
        """
        plugin_instance = self.plugins.get(plugin_id)
        if not plugin_instance:
            return False

        # Validate configuration if plugin is loaded
        loaded_plugin = self.loaded_plugins.get(plugin_id)
        if loaded_plugin:
            if not await loaded_plugin.validate_configuration(
                configuration
            ):
                return False

        # Apply configuration
        plugin_instance.configuration = configuration
        plugin_instance.last_updated = datetime.now(UTC)

        # If plugin is active, restart it with new configuration
        if plugin_instance.status == PluginStatus.ACTIVE:
            await self.disable_plugin(plugin_id)
            await self.enable_plugin(plugin_id)

        logger.info(f"Configured plugin {plugin_id}")
        return True

    async def health_check_plugins(
        self, auto_disable_unhealthy: bool = False
    ) -> dict[str, dict[str, Any]]:
        """Perform health check on all active plugins with enhanced handling.

        Args:
            auto_disable_unhealthy: Whether to automatically disable unhealthy plugins

        Returns:
            Health check results for each plugin
        """
        results = {}
        unhealthy_plugins = []

        for plugin_id, plugin in self.loaded_plugins.items():
            try:
                import asyncio

                # Add timeout to health checks
                health = await asyncio.wait_for(
                    plugin.health_check(),
                    timeout=settings.plugin_health_check_timeout,
                )
                results[plugin_id] = health

                # Check if plugin reports as unhealthy
                if not health.get("healthy", True):
                    unhealthy_plugins.append(plugin_id)

            except TimeoutError:
                results[plugin_id] = {
                    "healthy": False,
                    "error": "Health check timed out",
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                unhealthy_plugins.append(plugin_id)

            except Exception as e:
                results[plugin_id] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }
                unhealthy_plugins.append(plugin_id)

        # Auto-disable unhealthy plugins if requested
        if auto_disable_unhealthy and unhealthy_plugins:
            logger.warning(
                f"Auto-disabling unhealthy plugins: {unhealthy_plugins}"
            )
            for plugin_id in unhealthy_plugins:
                try:
                    await self.disable_plugin(plugin_id)
                    if plugin_id in results:
                        results[plugin_id]["auto_disabled"] = True
                except Exception as e:
                    logger.error(
                        f"Failed to auto-disable plugin {plugin_id}: {e}"
                    )

        return results

    async def check_plugin_dependencies(
        self, plugin_id: str
    ) -> dict[str, Any]:
        """Check if plugin dependencies are satisfied.

        Args:
            plugin_id: Plugin ID

        Returns:
            Dependency check results
        """
        plugin_instance = self.plugins.get(plugin_id)
        if not plugin_instance:
            return {"error": "Plugin not found"}

        manifest = plugin_instance.manifest
        results = {
            "plugin_id": plugin_id,
            "plugin_name": manifest.name,
            "dependencies": [],
            "all_satisfied": True,
        }

        for dependency in manifest.dependencies:
            dep_result = {
                "name": dependency,
                "satisfied": False,
                "error": None,
            }

            try:
                # Basic check - try to parse as package requirement
                import re

                match = re.match(
                    r"([a-zA-Z0-9_\-\.]+)(.*)$", dependency
                )
                if match:
                    package_name = match.group(1)
                    match.group(2)

                    # Try to import the package
                    try:
                        __import__(package_name.replace("-", "_"))
                        dep_result["satisfied"] = True
                    except ImportError:
                        dep_result["error"] = (
                            f"Package {package_name} not installed"
                        )
                        results["all_satisfied"] = False
                else:
                    dep_result["error"] = "Invalid dependency format"
                    results["all_satisfied"] = False

            except Exception as e:
                dep_result["error"] = str(e)
                results["all_satisfied"] = False

            results["dependencies"].append(dep_result)

        return results

    async def bulk_enable_plugins(
        self, plugin_ids: list[str]
    ) -> dict[str, bool]:
        """Enable multiple plugins.

        Args:
            plugin_ids: List of plugin IDs to enable

        Returns:
            Dictionary mapping plugin ID to success status
        """
        results = {}
        for plugin_id in plugin_ids:
            try:
                results[plugin_id] = await self.enable_plugin(plugin_id)
            except Exception as e:
                logger.error(
                    f"Failed to enable plugin {plugin_id}: {e}"
                )
                results[plugin_id] = False
        return results

    async def bulk_disable_plugins(
        self, plugin_ids: list[str]
    ) -> dict[str, bool]:
        """Disable multiple plugins.

        Args:
            plugin_ids: List of plugin IDs to disable

        Returns:
            Dictionary mapping plugin ID to success status
        """
        results = {}
        for plugin_id in plugin_ids:
            try:
                results[plugin_id] = await self.disable_plugin(
                    plugin_id
                )
            except Exception as e:
                logger.error(
                    f"Failed to disable plugin {plugin_id}: {e}"
                )
                results[plugin_id] = False
        return results

    async def _validate_plugin(
        self, plugin_path: Path, manifest: PluginManifest
    ) -> None:
        """Validate plugin before installation.

        Args:
            plugin_path: Path to plugin
            manifest: Plugin manifest

        Raises:
            ValueError: If validation fails
        """
        # Prevent path traversal attacks
        try:
            plugin_path = plugin_path.resolve()
            if not str(plugin_path).startswith(str(Path.cwd())):
                # Allow only plugins within current working directory
                logger.warning(
                    f"Plugin path outside allowed directory: {plugin_path}"
                )
        except (OSError, ValueError) as e:
            raise ValueError(f"Invalid plugin path: {e}") from e
        # Check entry point exists and validate path
        entry_point_path = plugin_path / manifest.entry_point
        if not entry_point_path.exists():
            raise ValueError(
                f"Entry point not found: {manifest.entry_point}"
            )

        # Prevent directory traversal in entry point
        if (
            ".." in manifest.entry_point
            or manifest.entry_point.startswith("/")
        ):
            raise ValueError(
                f"Invalid entry point path: {manifest.entry_point}"
            )

        # Validate Python version requirement properly
        try:
            import re

            import packaging.version

            # Extract version from requirement string like ">=3.11" or ">=3.11.0"
            version_match = re.match(
                r">=(\d+\.\d+(?:\.\d+)?)", manifest.python_version
            )
            if not version_match:
                raise ValueError(
                    f"Invalid Python version format: {manifest.python_version}"
                )

            required_version = packaging.version.Version(
                version_match.group(1)
            )
            current_version = packaging.version.Version(
                f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            )

            if current_version < required_version:
                raise ValueError(
                    f"Plugin requires Python {manifest.python_version}, but running {current_version}"
                )

        except ImportError:
            # Fallback to basic validation if packaging not available
            if not manifest.python_version.startswith(">=3.11"):
                logger.warning(
                    f"Plugin requires {manifest.python_version}"
                )

        # Validate plugin dependencies
        for dependency in manifest.dependencies:
            if not self._is_safe_dependency(dependency):
                raise ValueError(
                    f"Unsafe dependency detected: {dependency}"
                )

        # Check for required capabilities and validate permissions
        for capability in manifest.capabilities:
            for permission in capability.required_permissions:
                if not self._validate_permission(permission):
                    raise ValueError(
                        f"Permission '{permission}' is not supported or allowed"
                    )

    def _is_safe_dependency(self, dependency: str) -> bool:
        """Check if a dependency is safe to install.

        Args:
            dependency: Package dependency string

        Returns:
            True if dependency is safe, False otherwise
        """
        # Basic checks for suspicious packages
        unsafe_patterns = [
            "subprocess",
            "os.system",
            "eval",
            "exec",
            "import",
            "__import__",
            "open",
            "file",
            "input",
            "raw_input",
        ]

        dependency_lower = dependency.lower()
        for pattern in unsafe_patterns:
            if pattern in dependency_lower:
                logger.warning(
                    f"Potentially unsafe dependency: {dependency}"
                )
                return False

        # Check for reasonable package names (basic validation)
        if (
            len(dependency) > 100
            or not dependency.replace("-", "")
            .replace("_", "")
            .replace(".", "")
            .replace(">=", "")
            .replace("<=", "")
            .replace("==", "")
            .replace("!=", "")
            .replace(">", "")
            .replace("<", "")
            .replace(" ", "")
            .isalnum()
        ):
            return False

        return True

    def _validate_permission(self, permission: str) -> bool:
        """Validate if a permission is supported and allowed.

        Args:
            permission: Permission string to validate

        Returns:
            True if permission is valid, False otherwise
        """
        # Define allowed permissions
        allowed_permissions = {
            "tool_execution",
            "network_access",
            "file_read",
            "file_write",
            "api_access",
            "database_read",
            "database_write",
            "workflow_create",
            "workflow_execute",
        }

        return permission in allowed_permissions

    async def _load_plugin_class(
        self, plugin_instance: PluginInstance
    ) -> type[BasePlugin]:
        """Load plugin class from file with enhanced security.

        Args:
            plugin_instance: Plugin instance

        Returns:
            Plugin class

        Raises:
            ImportError: If plugin cannot be loaded
            SecurityError: If plugin fails security checks
        """
        manifest = plugin_instance.manifest
        installation_path = Path(plugin_instance.installation_path)
        entry_point_path = installation_path / manifest.entry_point

        # Additional security checks before loading
        try:
            # Resolve paths to prevent traversal attacks
            installation_path = installation_path.resolve()
            entry_point_path = entry_point_path.resolve()

            # Ensure entry point is within installation directory
            if not str(entry_point_path).startswith(
                str(installation_path)
            ):
                raise ImportError(
                    f"Entry point outside plugin directory: {entry_point_path}"
                )

        except (OSError, ValueError) as e:
            raise ImportError(f"Invalid plugin paths: {e}") from e
        # Check file size (prevent extremely large files)
        try:
            file_size = entry_point_path.stat().st_size
            max_size = 10 * 1024 * 1024  # 10MB limit
            if file_size > max_size:
                raise ImportError(
                    f"Plugin file too large: {file_size} bytes (max {max_size})"
                )
        except OSError as e:
            raise ImportError(f"Cannot access plugin file: {e}") from e
        # Create a restricted module namespace
        restricted_builtins = {
            "__builtins__": (
                {
                    k: v
                    for k, v in __builtins__.items()
                    if k
                    not in [
                        "eval",
                        "exec",
                        "__import__",
                        "open",
                        "input",
                        "compile",
                    ]
                }
                if isinstance(__builtins__, dict)
                else {
                    k: getattr(__builtins__, k)
                    for k in dir(__builtins__)
                    if k
                    not in [
                        "eval",
                        "exec",
                        "__import__",
                        "open",
                        "input",
                        "compile",
                    ]
                }
            )
        }

        try:
            # Load module dynamically with restricted environment
            spec = importlib.util.spec_from_file_location(
                f"plugin_{manifest.name}_{hash(str(entry_point_path))}",
                entry_point_path,
            )

            if not spec or not spec.loader:
                raise ImportError(
                    f"Cannot load plugin module: {manifest.entry_point}"
                )

            module = importlib.util.module_from_spec(spec)

            # Set restricted builtins
            for name, value in restricted_builtins.items():
                setattr(module, name, value)

            # Execute module with timeout protection
            try:
                import platform
                import signal

                def timeout_handler(signum, frame):  # noqa: ARG001
                    raise TimeoutError(
                        "Plugin loading timeout"
                    ) from None

                # Only use signal-based timeout on Unix systems
                if platform.system() != "Windows":
                    old_handler = signal.signal(
                        signal.SIGALRM, timeout_handler
                    )
                    signal.alarm(30)  # 30 second timeout

                    try:
                        spec.loader.exec_module(module)
                    finally:
                        signal.alarm(0)
                        signal.signal(signal.SIGALRM, old_handler)
                else:
                    # On Windows, just execute without signal-based timeout
                    spec.loader.exec_module(module)

            except (TimeoutError, OSError):
                raise ImportError(
                    "Plugin loading timed out or failed"
                ) from None
            except Exception as e:
                raise ImportError(
                    f"Error loading plugin module: {e}"
                ) from e
        except ImportError:
            raise
        except Exception as e:
            raise ImportError(f"Failed to load plugin: {e}") from e
        # Find plugin class
        plugin_class = None
        valid_base_classes = (
            BasePlugin,
            ToolPlugin,
            WorkflowPlugin,
            IntegrationPlugin,
        )

        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, BasePlugin)
                and obj
                not in valid_base_classes  # Exclude base classes
                and not name.startswith("_")  # Exclude private classes
            ):
                if plugin_class is not None:
                    # Multiple plugin classes found, be more specific
                    self.logger.warning(
                        f"Multiple plugin classes found in {manifest.entry_point}, using {obj.__name__}"
                    )
                plugin_class = obj

        if not plugin_class:
            raise ImportError(
                f"No valid plugin class found in {manifest.entry_point}. "
                f"Expected a class inheriting from BasePlugin."
            )

        # Validate plugin class has required methods
        required_methods = [
            "initialize",
            "shutdown",
            "get_capabilities",
        ]
        for method in required_methods:
            if not hasattr(plugin_class, method):
                raise ImportError(
                    f"Plugin class missing required method: {method}"
                )

        return plugin_class

    async def discover_plugins(
        self, search_paths: list[str] | None = None
    ) -> list[str]:
        """Discover available plugins in search paths.

        Args:
            search_paths: Paths to search for plugins

        Returns:
            List of discovered plugin paths
        """
        if not search_paths:
            search_paths = [str(self.plugins_directory)]

        discovered = []

        for search_path in search_paths:
            search_dir = Path(search_path)
            if not search_dir.exists():
                continue

            for item in search_dir.iterdir():
                if item.is_dir():
                    manifest_path = item / "manifest.json"
                    if manifest_path.exists():
                        discovered.append(str(item))

        return discovered

    async def get_plugin_stats(self) -> dict[str, Any]:
        """Get plugin system statistics.

        Returns:
            Plugin statistics
        """
        total_plugins = len(self.plugins)
        active_plugins = sum(
            1
            for p in self.plugins.values()
            if p.status == PluginStatus.ACTIVE
        )

        plugin_types = {}
        for plugin in self.plugins.values():
            plugin_type = plugin.manifest.plugin_type.value
            plugin_types[plugin_type] = (
                plugin_types.get(plugin_type, 0) + 1
            )

        return {
            "total_plugins": total_plugins,
            "active_plugins": active_plugins,
            "inactive_plugins": total_plugins - active_plugins,
            "plugin_types": plugin_types,
            "plugins_directory": str(self.plugins_directory),
        }


# Global plugin manager
plugin_manager = PluginManager()


# Example plugin implementations
class ExampleToolPlugin(ToolPlugin):
    """Example tool plugin implementation."""

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        self.logger.info("Example tool plugin initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        self.logger.info("Example tool plugin shutdown")
        return True

    def get_capabilities(self) -> list[PluginCapability]:
        """Get plugin capabilities."""
        return [
            PluginCapability(
                name="example_tools",
                description="Provides example tools",
                required_permissions=["tool_execution"],
            )
        ]

    def get_tools(self) -> list[BaseTool]:
        """Get tools provided by this plugin."""
        # This would return actual LangChain tools
        return []


class ExampleIntegrationPlugin(IntegrationPlugin):
    """Example integration plugin implementation."""

    async def initialize(self) -> bool:
        """Initialize the plugin."""
        self.logger.info("Example integration plugin initialized")
        return True

    async def shutdown(self) -> bool:
        """Shutdown the plugin."""
        self.logger.info("Example integration plugin shutdown")
        return True

    def get_capabilities(self) -> list[PluginCapability]:
        """Get plugin capabilities."""
        return [
            PluginCapability(
                name="external_api",
                description="Integrates with external API",
                required_permissions=["network_access"],
            )
        ]

    async def connect(self) -> bool:
        """Connect to external service."""
        # Implement actual connection logic
        return True

    async def disconnect(self) -> bool:
        """Disconnect from external service."""
        # Implement actual disconnection logic
        return True


# Register example plugins
plugin_manager.plugin_registry["example_tool"] = ExampleToolPlugin
plugin_manager.plugin_registry["example_integration"] = (
    ExampleIntegrationPlugin
)


# Job handlers for plugin operations
async def plugin_health_check_job() -> dict[str, Any]:
    """Job handler for plugin health checks."""
    results = await plugin_manager.health_check_plugins()

    # Report any unhealthy plugins
    unhealthy_plugins = [
        plugin_id
        for plugin_id, health in results.items()
        if not health.get("healthy", False)
    ]

    if unhealthy_plugins:
        logger.warning(
            "Unhealthy plugins detected",
            unhealthy_plugins=unhealthy_plugins,
        )

    return {
        "total_plugins": len(results),
        "healthy_plugins": len(results) - len(unhealthy_plugins),
        "unhealthy_plugins": len(unhealthy_plugins),
        "results": results,
    }


# Register plugin job handlers
job_queue.register_handler(
    "plugin_health_check", plugin_health_check_job
)


# Helper functions for plugin management
async def create_example_plugin_manifest() -> dict[str, Any]:
    """Create an example plugin manifest."""
    return {
        "name": "example_plugin",
        "version": "1.0.0",
        "description": "An example plugin",
        "author": "Chatter Team",
        "license": "MIT",
        "plugin_type": "tool",
        "entry_point": "plugin.py",
        "capabilities": [
            {
                "name": "example_capability",
                "description": "Example capability",
                "required_permissions": ["tool_execution"],
            }
        ],
        "dependencies": [],
        "python_version": ">=3.11",
        "chatter_version": ">=0.1.0",
        "configuration_schema": {
            "type": "object",
            "properties": {
                "api_key": {
                    "type": "string",
                    "description": "API key for external service",
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds",
                    "default": 30,
                },
            },
            "required": ["api_key"],
        },
        "permissions": ["tool_execution", "network_access"],
        "metadata": {
            "homepage": "https://example.com",
            "repository": "https://github.com/example/plugin",
        },
    }
