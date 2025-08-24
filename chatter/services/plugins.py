"""Plugin architecture for custom tools and extensibility."""

import asyncio
import importlib
import importlib.util
import inspect
import json
import sys
import uuid
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from chatter.config import settings
from chatter.services.job_queue import job_queue
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class PluginType(str, Enum):
    """Types of plugins."""
    TOOL = "tool"
    WORKFLOW = "workflow"
    INTEGRATION = "integration"
    MIDDLEWARE = "middleware"
    HANDLER = "handler"
    EXTENSION = "extension"


class PluginStatus(str, Enum):
    """Plugin status."""
    INSTALLED = "installed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"


class PluginCapability(BaseModel):
    """Plugin capability definition."""
    name: str
    description: str
    required_permissions: List[str] = Field(default_factory=list)
    optional_permissions: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    api_endpoints: List[str] = Field(default_factory=list)


class PluginManifest(BaseModel):
    """Plugin manifest file structure."""
    name: str
    version: str
    description: str
    author: str
    license: str
    plugin_type: PluginType
    entry_point: str
    capabilities: List[PluginCapability] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    python_version: str = ">=3.11"
    chatter_version: str = ">=0.1.0"
    configuration_schema: Dict[str, Any] = Field(default_factory=dict)
    permissions: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PluginInstance(BaseModel):
    """Plugin instance information."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manifest: PluginManifest
    status: PluginStatus = PluginStatus.INSTALLED
    installation_path: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    enabled_capabilities: List[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    installed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    usage_stats: Dict[str, Any] = Field(default_factory=dict)


class BasePlugin(ABC):
    """Base class for all plugins."""

    def __init__(self, config: Dict[str, Any] = None):
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
    def get_capabilities(self) -> List[PluginCapability]:
        """Get plugin capabilities.
        
        Returns:
            List of plugin capabilities
        """
        pass

    async def health_check(self) -> Dict[str, Any]:
        """Perform plugin health check.
        
        Returns:
            Health check result
        """
        return {
            "healthy": True,
            "status": "active",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def get_configuration_schema(self) -> Dict[str, Any]:
        """Get configuration schema for the plugin.
        
        Returns:
            JSON schema for configuration
        """
        return {}

    async def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        return True


class ToolPlugin(BasePlugin):
    """Base class for tool plugins."""

    @abstractmethod
    def get_tools(self) -> List[BaseTool]:
        """Get tools provided by this plugin.
        
        Returns:
            List of LangChain tools
        """
        pass


class WorkflowPlugin(BasePlugin):
    """Base class for workflow plugins."""

    @abstractmethod
    async def create_workflow(self, config: Dict[str, Any]) -> Any:
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
        self.plugins: Dict[str, PluginInstance] = {}
        self.loaded_plugins: Dict[str, BasePlugin] = {}
        self.plugin_registry: Dict[str, Type[BasePlugin]] = {}
        self.plugins_directory = Path(settings.document_storage_path) / "plugins"
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure plugin directories exist."""
        self.plugins_directory.mkdir(parents=True, exist_ok=True)

    async def install_plugin(
        self,
        plugin_path: Union[str, Path],
        enable_on_install: bool = True,
    ) -> str:
        """Install a plugin from a directory or archive.
        
        Args:
            plugin_path: Path to plugin directory or archive
            enable_on_install: Whether to enable plugin after installation
            
        Returns:
            Plugin ID
            
        Raises:
            ValueError: If plugin installation fails
        """
        plugin_path = Path(plugin_path)
        
        if not plugin_path.exists():
            raise ValueError(f"Plugin path does not exist: {plugin_path}")

        # Load plugin manifest
        manifest_path = plugin_path / "manifest.json"
        if not manifest_path.exists():
            raise ValueError(f"Plugin manifest not found: {manifest_path}")

        try:
            with open(manifest_path, 'r') as f:
                manifest_data = json.load(f)
            
            manifest = PluginManifest(**manifest_data)
        except Exception as e:
            raise ValueError(f"Invalid plugin manifest: {str(e)}")

        # Check if plugin already installed
        for plugin_instance in self.plugins.values():
            if plugin_instance.manifest.name == manifest.name:
                raise ValueError(f"Plugin '{manifest.name}' is already installed")

        # Validate plugin
        await self._validate_plugin(plugin_path, manifest)

        # Copy plugin to plugins directory
        plugin_install_path = self.plugins_directory / manifest.name
        if plugin_install_path.exists():
            import shutil
            shutil.rmtree(plugin_install_path)

        import shutil
        shutil.copytree(plugin_path, plugin_install_path)

        # Create plugin instance
        plugin_instance = PluginInstance(
            manifest=manifest,
            installation_path=str(plugin_install_path),
        )

        self.plugins[plugin_instance.id] = plugin_instance

        logger.info(
            f"Installed plugin",
            plugin_id=plugin_instance.id,
            name=manifest.name,
            version=manifest.version,
        )

        # Enable plugin if requested
        if enable_on_install:
            await self.enable_plugin(plugin_instance.id)

        return plugin_instance.id

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
            f"Uninstalled plugin",
            plugin_id=plugin_id,
            name=plugin_instance.manifest.name,
        )

        return True

    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if enabled successfully, False otherwise
        """
        plugin_instance = self.plugins.get(plugin_id)
        if not plugin_instance:
            return False

        if plugin_instance.status == PluginStatus.ACTIVE:
            return True

        try:
            # Load plugin module
            plugin_class = await self._load_plugin_class(plugin_instance)
            
            # Create plugin instance
            plugin = plugin_class(plugin_instance.configuration)
            
            # Initialize plugin
            if not await plugin.initialize():
                raise RuntimeError("Plugin initialization failed")

            # Store loaded plugin
            self.loaded_plugins[plugin_id] = plugin
            
            # Update status
            plugin_instance.status = PluginStatus.ACTIVE
            plugin_instance.last_updated = datetime.now(UTC)
            plugin_instance.error_message = None

            logger.info(
                f"Enabled plugin",
                plugin_id=plugin_id,
                name=plugin_instance.manifest.name,
            )

            return True

        except Exception as e:
            plugin_instance.status = PluginStatus.ERROR
            plugin_instance.error_message = str(e)
            
            logger.error(
                f"Failed to enable plugin",
                plugin_id=plugin_id,
                name=plugin_instance.manifest.name,
                error=str(e),
            )

            return False

    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            True if disabled successfully, False otherwise
        """
        plugin_instance = self.plugins.get(plugin_id)
        if not plugin_instance:
            return False

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
                f"Disabled plugin",
                plugin_id=plugin_id,
                name=plugin_instance.manifest.name,
            )

            return True

        except Exception as e:
            logger.error(
                f"Error disabling plugin",
                plugin_id=plugin_id,
                error=str(e),
            )
            return False

    async def list_plugins(
        self,
        plugin_type: Optional[PluginType] = None,
        status: Optional[PluginStatus] = None,
    ) -> List[PluginInstance]:
        """List installed plugins.
        
        Args:
            plugin_type: Filter by plugin type
            status: Filter by status
            
        Returns:
            List of plugin instances
        """
        plugins = list(self.plugins.values())

        if plugin_type:
            plugins = [p for p in plugins if p.manifest.plugin_type == plugin_type]

        if status:
            plugins = [p for p in plugins if p.status == status]

        # Sort by name
        plugins.sort(key=lambda x: x.manifest.name)

        return plugins

    async def get_plugin(self, plugin_id: str) -> Optional[PluginInstance]:
        """Get plugin instance.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_id)

    async def get_loaded_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get loaded plugin instance.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Loaded plugin or None if not found
        """
        return self.loaded_plugins.get(plugin_id)

    async def get_tools_from_plugins(self) -> Dict[str, List[BaseTool]]:
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
                        f"Error getting tools from plugin",
                        plugin_id=plugin_id,
                        error=str(e),
                    )

        return tools

    async def configure_plugin(
        self, plugin_id: str, configuration: Dict[str, Any]
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
            if not await loaded_plugin.validate_configuration(configuration):
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

    async def health_check_plugins(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all active plugins.
        
        Returns:
            Health check results for each plugin
        """
        results = {}

        for plugin_id, plugin in self.loaded_plugins.items():
            try:
                health = await plugin.health_check()
                results[plugin_id] = health
            except Exception as e:
                results[plugin_id] = {
                    "healthy": False,
                    "error": str(e),
                    "timestamp": datetime.now(UTC).isoformat(),
                }

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
        # Check entry point exists
        entry_point_path = plugin_path / manifest.entry_point
        if not entry_point_path.exists():
            raise ValueError(f"Entry point not found: {manifest.entry_point}")

        # Validate Python version requirement
        # This is a simplified check - in production you'd use packaging.version
        if not manifest.python_version.startswith(">=3.11"):
            logger.warning(f"Plugin requires {manifest.python_version}")

        # Check for required capabilities
        for capability in manifest.capabilities:
            for permission in capability.required_permissions:
                # Check if system supports this permission
                pass  # Placeholder for permission validation

    async def _load_plugin_class(self, plugin_instance: PluginInstance) -> Type[BasePlugin]:
        """Load plugin class from file.
        
        Args:
            plugin_instance: Plugin instance
            
        Returns:
            Plugin class
            
        Raises:
            ImportError: If plugin cannot be loaded
        """
        manifest = plugin_instance.manifest
        installation_path = Path(plugin_instance.installation_path)
        entry_point_path = installation_path / manifest.entry_point

        # Load module dynamically
        spec = importlib.util.spec_from_file_location(
            f"plugin_{manifest.name}",
            entry_point_path
        )
        
        if not spec or not spec.loader:
            raise ImportError(f"Cannot load plugin module: {manifest.entry_point}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find plugin class
        plugin_class = None
        for name, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, BasePlugin) and 
                obj != BasePlugin):
                plugin_class = obj
                break

        if not plugin_class:
            raise ImportError(f"No plugin class found in {manifest.entry_point}")

        return plugin_class

    async def discover_plugins(self, search_paths: Optional[List[str]] = None) -> List[str]:
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

    async def get_plugin_stats(self) -> Dict[str, Any]:
        """Get plugin system statistics.
        
        Returns:
            Plugin statistics
        """
        total_plugins = len(self.plugins)
        active_plugins = sum(
            1 for p in self.plugins.values()
            if p.status == PluginStatus.ACTIVE
        )

        plugin_types = {}
        for plugin in self.plugins.values():
            plugin_type = plugin.manifest.plugin_type.value
            plugin_types[plugin_type] = plugin_types.get(plugin_type, 0) + 1

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

    def get_capabilities(self) -> List[PluginCapability]:
        """Get plugin capabilities."""
        return [
            PluginCapability(
                name="example_tools",
                description="Provides example tools",
                required_permissions=["tool_execution"],
            )
        ]

    def get_tools(self) -> List[BaseTool]:
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

    def get_capabilities(self) -> List[PluginCapability]:
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
plugin_manager.plugin_registry["example_integration"] = ExampleIntegrationPlugin


# Job handlers for plugin operations
async def plugin_health_check_job() -> Dict[str, Any]:
    """Job handler for plugin health checks."""
    results = await plugin_manager.health_check_plugins()
    
    # Report any unhealthy plugins
    unhealthy_plugins = [
        plugin_id for plugin_id, health in results.items()
        if not health.get("healthy", False)
    ]
    
    if unhealthy_plugins:
        logger.warning(
            f"Unhealthy plugins detected",
            unhealthy_plugins=unhealthy_plugins,
        )
    
    return {
        "total_plugins": len(results),
        "healthy_plugins": len(results) - len(unhealthy_plugins),
        "unhealthy_plugins": len(unhealthy_plugins),
        "results": results,
    }


# Register plugin job handlers
job_queue.register_handler("plugin_health_check", plugin_health_check_job)


# Helper functions for plugin management
async def create_example_plugin_manifest() -> Dict[str, Any]:
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