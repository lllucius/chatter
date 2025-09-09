"""Tests for plugin system."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chatter.schemas.plugins import (
    PluginInstance,
    PluginStatus,
    PluginType,
)
from chatter.services.plugins import (
    BasePlugin,
    PluginError,
    PluginManager,
    ToolPlugin,
    WorkflowPlugin,
)


# Mock BaseTool for testing
class MockBaseTool:
    """Mock BaseTool class for testing."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class TestBasePlugin:
    """Test BasePlugin functionality."""

    def test_base_plugin_initialization(self):
        """Test BasePlugin initialization."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

        config = {"param1": "value1", "param2": 123}
        plugin = TestPlugin(config)

        assert plugin.config == config
        assert hasattr(plugin, 'logger')
        assert plugin.logger is not None

    def test_base_plugin_default_config(self):
        """Test BasePlugin with default empty config."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

        plugin = TestPlugin()

        assert plugin.config == {}
        # Remove reference to nonexistent 'enabled' attribute
        assert hasattr(plugin, 'logger')
        assert plugin.logger is not None

    @pytest.mark.asyncio
    async def test_base_plugin_get_configuration_schema(self):
        """Test default configuration schema."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

        plugin = TestPlugin()
        schema = await plugin.get_configuration_schema()

        expected_schema = {
            "type": "object",
            "properties": {},
            "additionalProperties": True,
        }
        assert schema == expected_schema

    @pytest.mark.asyncio
    async def test_validate_configuration_no_schema(self):
        """Test configuration validation with no schema."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

        plugin = TestPlugin()
        config = {"any": "value", "is": "accepted"}

        is_valid = await plugin.validate_configuration(config)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_configuration_with_schema(self):
        """Test configuration validation with custom schema."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

            async def get_configuration_schema(self):
                return {
                    "type": "object",
                    "properties": {
                        "required_param": {"type": "string"},
                        "optional_param": {"type": "number"},
                    },
                    "required": ["required_param"],
                }

        plugin = TestPlugin()

        # Valid configuration
        valid_config = {"required_param": "test", "optional_param": 123}
        is_valid = await plugin.validate_configuration(valid_config)
        assert is_valid is True

        # Missing required parameter
        invalid_config = {"optional_param": 123}
        is_valid = await plugin.validate_configuration(invalid_config)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_configuration_type_checking(self):
        """Test configuration validation with type checking."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

            async def get_configuration_schema(self):
                return {
                    "type": "object",
                    "properties": {
                        "string_param": {"type": "string"},
                        "number_param": {"type": "number"},
                        "boolean_param": {"type": "boolean"},
                        "object_param": {"type": "object"},
                        "array_param": {"type": "array"},
                    },
                }

        plugin = TestPlugin()

        # Valid types
        valid_config = {
            "string_param": "test",
            "number_param": 123,
            "boolean_param": True,
            "object_param": {"key": "value"},
            "array_param": [1, 2, 3],
        }
        is_valid = await plugin.validate_configuration(valid_config)
        assert is_valid is True

        # Invalid string type
        invalid_config = {"string_param": 123}
        is_valid = await plugin.validate_configuration(invalid_config)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_configuration_error_handling(self):
        """Test configuration validation error handling."""

        class TestPlugin(BasePlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                return True

            def get_capabilities(self):
                return []

            async def health_check(self):
                return {"status": "healthy"}

            async def get_configuration_schema(self):
                raise Exception("Schema generation error")

        plugin = TestPlugin()

        is_valid = await plugin.validate_configuration(
            {"test": "config"}
        )
        assert is_valid is False


class TestToolPlugin:
    """Test ToolPlugin functionality."""

    def test_tool_plugin_inheritance(self):
        """Test ToolPlugin inherits from BasePlugin."""

        class TestToolPlugin(ToolPlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                pass

            async def health_check(self):
                return {"status": "healthy"}

            def get_tools(self):
                return [
                    MockBaseTool("test_tool", "Test tool description")
                ]

        plugin = TestToolPlugin()
        assert isinstance(plugin, BasePlugin)

    def test_get_tools_abstract_method(self):
        """Test that get_tools is abstract and must be implemented."""

        # This should raise TypeError because get_tools is not implemented
        with pytest.raises(TypeError):

            class IncompleteToolPlugin(ToolPlugin):
                async def initialize(self):
                    pass

                async def shutdown(self):
                    pass

                async def health_check(self):
                    return {"status": "healthy"}

            IncompleteToolPlugin()

    def test_get_tools_implementation(self):
        """Test get_tools implementation."""

        class TestToolPlugin(ToolPlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                pass

            async def health_check(self):
                return {"status": "healthy"}

            def get_tools(self):
                return [
                    MockBaseTool("tool1", "First tool"),
                    MockBaseTool("tool2", "Second tool"),
                ]

        plugin = TestToolPlugin()
        tools = plugin.get_tools()

        assert len(tools) == 2
        assert tools[0].name == "tool1"
        assert tools[1].name == "tool2"


class TestWorkflowPlugin:
    """Test WorkflowPlugin functionality."""

    def test_workflow_plugin_inheritance(self):
        """Test WorkflowPlugin inherits from BasePlugin."""

        class TestWorkflowPlugin(WorkflowPlugin):
            async def initialize(self):
                pass

            async def shutdown(self):
                pass

            async def health_check(self):
                return {"status": "healthy"}

            async def execute_workflow(
                self, workflow_id: str, params: dict
            ):
                return {"result": "workflow executed"}

        plugin = TestWorkflowPlugin()
        assert isinstance(plugin, BasePlugin)

    def test_execute_workflow_abstract_method(self):
        """Test that execute_workflow is abstract and must be implemented."""

        # This should raise TypeError because execute_workflow is not implemented
        with pytest.raises(TypeError):

            class IncompleteWorkflowPlugin(WorkflowPlugin):
                async def initialize(self):
                    pass

                async def shutdown(self):
                    pass

                async def health_check(self):
                    return {"status": "healthy"}

            IncompleteWorkflowPlugin()


class TestPluginManager:
    """Test PluginManager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.plugin_manager = PluginManager()

    def test_plugin_manager_initialization(self):
        """Test PluginManager initialization."""
        assert isinstance(self.plugin_manager.plugins, dict)
        assert isinstance(self.plugin_manager.plugin_instances, dict)
        assert self.plugin_manager.plugins_dir is not None

    def test_get_plugin_directory_default(self):
        """Test getting default plugin directory."""
        plugins_dir = self.plugin_manager._get_plugin_directory()
        assert plugins_dir.name == "plugins"

    def test_get_plugin_directory_custom(self):
        """Test getting custom plugin directory."""
        with patch(
            'chatter.services.plugins.settings'
        ) as mock_settings:
            mock_settings.plugins_directory = "/custom/plugins"

            plugins_dir = self.plugin_manager._get_plugin_directory()
            assert str(plugins_dir) == "/custom/plugins"

    @pytest.mark.asyncio
    async def test_load_plugin_from_file_success(self):
        """Test successfully loading plugin from file."""

        # Create a temporary plugin file
        plugin_code = '''
from chatter.services.plugins import ToolPlugin

class TestFilePlugin(ToolPlugin):
    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def health_check(self):
        return {"status": "healthy"}

    def get_tools(self):
        from tests.test_plugins import MockBaseTool
        return [MockBaseTool("file_tool", "Tool from file")]

# Plugin entry point
plugin_class = TestFilePlugin
'''

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(plugin_code)
            plugin_file = Path(f.name)

        try:
            plugin_instance = (
                await self.plugin_manager.load_plugin_from_file(
                    plugin_file, "test_file_plugin", {}
                )
            )

            assert plugin_instance is not None
            assert plugin_instance.plugin_id == "test_file_plugin"
            assert plugin_instance.status == PluginStatus.LOADED

        finally:
            plugin_file.unlink()

    @pytest.mark.asyncio
    async def test_load_plugin_from_file_missing_file(self):
        """Test loading plugin from non-existent file."""
        non_existent_file = Path("/non/existent/plugin.py")

        with pytest.raises(PluginError, match="Plugin file not found"):
            await self.plugin_manager.load_plugin_from_file(
                non_existent_file, "missing_plugin", {}
            )

    @pytest.mark.asyncio
    async def test_load_plugin_from_file_syntax_error(self):
        """Test loading plugin with syntax error."""

        # Create plugin file with syntax error
        plugin_code = '''
from chatter.services.plugins import ToolPlugin

class TestFilePlugin(ToolPlugin):
    async def initialize(self)
        # Missing colon - syntax error
        pass
'''

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(plugin_code)
            plugin_file = Path(f.name)

        try:
            with pytest.raises(
                PluginError, match="Failed to load plugin"
            ):
                await self.plugin_manager.load_plugin_from_file(
                    plugin_file, "syntax_error_plugin", {}
                )
        finally:
            plugin_file.unlink()

    @pytest.mark.asyncio
    async def test_unload_plugin_success(self):
        """Test successfully unloading a plugin."""

        # Create a mock plugin instance
        mock_plugin = MagicMock()
        mock_plugin.cleanup = AsyncMock()

        plugin_instance = PluginInstance(
            plugin_id="test_plugin",
            name="Test Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["test_plugin"] = (
            plugin_instance
        )

        result = await self.plugin_manager.unload_plugin("test_plugin")

        assert result is True
        assert "test_plugin" not in self.plugin_manager.plugin_instances
        mock_plugin.cleanup.assert_called_once()

    @pytest.mark.asyncio
    async def test_unload_plugin_not_found(self):
        """Test unloading non-existent plugin."""
        result = await self.plugin_manager.unload_plugin(
            "non_existent_plugin"
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_unload_plugin_cleanup_error(self):
        """Test unloading plugin when cleanup fails."""

        mock_plugin = MagicMock()
        mock_plugin.cleanup = AsyncMock(
            side_effect=Exception("Cleanup failed")
        )

        plugin_instance = PluginInstance(
            plugin_id="test_plugin",
            name="Test Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["test_plugin"] = (
            plugin_instance
        )

        # Should still succeed even if cleanup fails
        result = await self.plugin_manager.unload_plugin("test_plugin")

        assert result is True
        assert "test_plugin" not in self.plugin_manager.plugin_instances

    def test_list_plugins(self):
        """Test listing plugins."""

        # Add some mock plugin instances
        plugin1 = PluginInstance(
            plugin_id="plugin1",
            name="Plugin 1",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        plugin2 = PluginInstance(
            plugin_id="plugin2",
            name="Plugin 2",
            plugin_type=PluginType.WORKFLOW,
            status=PluginStatus.ERROR,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["plugin1"] = plugin1
        self.plugin_manager.plugin_instances["plugin2"] = plugin2

        plugins = self.plugin_manager.list_plugins()

        assert len(plugins) == 2
        assert plugins["plugin1"] == plugin1
        assert plugins["plugin2"] == plugin2

    def test_list_plugins_by_type(self):
        """Test listing plugins filtered by type."""

        tool_plugin = PluginInstance(
            plugin_id="tool_plugin",
            name="Tool Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        workflow_plugin = PluginInstance(
            plugin_id="workflow_plugin",
            name="Workflow Plugin",
            plugin_type=PluginType.WORKFLOW,
            status=PluginStatus.ACTIVE,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["tool_plugin"] = (
            tool_plugin
        )
        self.plugin_manager.plugin_instances["workflow_plugin"] = (
            workflow_plugin
        )

        tool_plugins = self.plugin_manager.list_plugins(
            plugin_type=PluginType.TOOL
        )

        assert len(tool_plugins) == 1
        assert "tool_plugin" in tool_plugins
        assert "workflow_plugin" not in tool_plugins

    def test_list_plugins_by_status(self):
        """Test listing plugins filtered by status."""

        active_plugin = PluginInstance(
            plugin_id="active_plugin",
            name="Active Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        error_plugin = PluginInstance(
            plugin_id="error_plugin",
            name="Error Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ERROR,
            plugin_object=MagicMock(),
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["active_plugin"] = (
            active_plugin
        )
        self.plugin_manager.plugin_instances["error_plugin"] = (
            error_plugin
        )

        active_plugins = self.plugin_manager.list_plugins(
            status=PluginStatus.ACTIVE
        )

        assert len(active_plugins) == 1
        assert "active_plugin" in active_plugins
        assert "error_plugin" not in active_plugins

    def test_get_plugin_info_found(self):
        """Test getting plugin info for existing plugin."""

        plugin = PluginInstance(
            plugin_id="test_plugin",
            name="Test Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=MagicMock(),
            config={"param": "value"},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T01:00:00Z",
        )

        self.plugin_manager.plugin_instances["test_plugin"] = plugin

        info = self.plugin_manager.get_plugin_info("test_plugin")

        assert info == plugin

    def test_get_plugin_info_not_found(self):
        """Test getting plugin info for non-existent plugin."""
        info = self.plugin_manager.get_plugin_info("non_existent")

        assert info is None

    def test_get_tools_from_plugins(self):
        """Test getting tools from tool plugins."""

        # Create mock tool plugin
        mock_tool_plugin = MagicMock()
        mock_tool_plugin.get_tools.return_value = [
            MockBaseTool("tool1", "Tool 1"),
            MockBaseTool("tool2", "Tool 2"),
        ]

        tool_plugin = PluginInstance(
            plugin_id="tool_plugin",
            name="Tool Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_tool_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        # Create mock workflow plugin (should be ignored)
        mock_workflow_plugin = MagicMock()
        workflow_plugin = PluginInstance(
            plugin_id="workflow_plugin",
            name="Workflow Plugin",
            plugin_type=PluginType.WORKFLOW,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_workflow_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["tool_plugin"] = (
            tool_plugin
        )
        self.plugin_manager.plugin_instances["workflow_plugin"] = (
            workflow_plugin
        )

        tools = self.plugin_manager.get_tools_from_plugins()

        assert len(tools) == 2
        assert tools[0].name == "tool1"
        assert tools[1].name == "tool2"
        mock_tool_plugin.get_tools.assert_called_once()

    def test_get_tools_from_plugins_inactive_ignored(self):
        """Test that inactive plugins are ignored when getting tools."""

        # Create inactive tool plugin
        mock_tool_plugin = MagicMock()
        mock_tool_plugin.get_tools.return_value = [
            MockBaseTool("tool1", "Tool 1")
        ]

        inactive_plugin = PluginInstance(
            plugin_id="inactive_plugin",
            name="Inactive Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ERROR,  # Inactive status
            plugin_object=mock_tool_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["inactive_plugin"] = (
            inactive_plugin
        )

        tools = self.plugin_manager.get_tools_from_plugins()

        assert len(tools) == 0
        mock_tool_plugin.get_tools.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_all_plugins(self):
        """Test health check for all plugins."""

        # Create mock plugins with health checks
        mock_plugin1 = MagicMock()
        mock_plugin1.health_check = AsyncMock(
            return_value={"status": "healthy"}
        )

        mock_plugin2 = MagicMock()
        mock_plugin2.health_check = AsyncMock(
            return_value={
                "status": "degraded",
                "issues": ["slow response"],
            }
        )

        plugin1 = PluginInstance(
            plugin_id="plugin1",
            name="Plugin 1",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_plugin1,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        plugin2 = PluginInstance(
            plugin_id="plugin2",
            name="Plugin 2",
            plugin_type=PluginType.WORKFLOW,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_plugin2,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["plugin1"] = plugin1
        self.plugin_manager.plugin_instances["plugin2"] = plugin2

        health_results = (
            await self.plugin_manager.health_check_all_plugins()
        )

        assert len(health_results) == 2
        assert "plugin1" in health_results
        assert "plugin2" in health_results
        assert health_results["plugin1"]["status"] == "healthy"
        assert health_results["plugin2"]["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_health_check_plugin_error(self):
        """Test health check when plugin health check fails."""

        mock_plugin = MagicMock()
        mock_plugin.health_check = AsyncMock(
            side_effect=Exception("Health check failed")
        )

        plugin = PluginInstance(
            plugin_id="error_plugin",
            name="Error Plugin",
            plugin_type=PluginType.TOOL,
            status=PluginStatus.ACTIVE,
            plugin_object=mock_plugin,
            config={},
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )

        self.plugin_manager.plugin_instances["error_plugin"] = plugin

        health_results = (
            await self.plugin_manager.health_check_all_plugins()
        )

        assert len(health_results) == 1
        assert health_results["error_plugin"]["status"] == "error"
        assert (
            "Health check failed"
            in health_results["error_plugin"]["error"]
        )


@pytest.mark.integration
class TestPluginIntegration:
    """Integration tests for plugin system."""

    def setup_method(self):
        """Set up test environment."""
        self.plugin_manager = PluginManager()

    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self):
        """Test complete plugin lifecycle: load, activate, health check, unload."""

        # Create a temporary plugin file
        plugin_code = '''
from chatter.services.plugins import ToolPlugin

class LifecycleTestPlugin(ToolPlugin):
    def __init__(self, config=None):
        super().__init__(config)
        self.initialized = False
        self.cleaned_up = False

    async def initialize(self):
        self.initialized = True

    async def shutdown(self):
        self.cleaned_up = True

    async def health_check(self):
        return {
            "status": "healthy" if self.initialized and not self.cleaned_up else "error",
            "initialized": self.initialized,
            "cleaned_up": self.cleaned_up
        }

    def get_tools(self):
        from tests.test_plugins import MockBaseTool
        return [MockBaseTool("lifecycle_tool", "Test tool for lifecycle")]

plugin_class = LifecycleTestPlugin
'''

        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        ) as f:
            f.write(plugin_code)
            plugin_file = Path(f.name)

        try:
            # Load plugin
            plugin_instance = (
                await self.plugin_manager.load_plugin_from_file(
                    plugin_file, "lifecycle_plugin", {}
                )
            )

            assert plugin_instance is not None
            assert plugin_instance.status == PluginStatus.LOADED

            # Initialize plugin
            await plugin_instance.plugin_object.initialize()
            plugin_instance.status = PluginStatus.ACTIVE

            # Health check
            health = await plugin_instance.plugin_object.health_check()
            assert health["status"] == "healthy"
            assert health["initialized"] is True

            # Get tools
            tools = plugin_instance.plugin_object.get_tools()
            assert len(tools) == 1
            assert tools[0].name == "lifecycle_tool"

            # Unload plugin
            result = await self.plugin_manager.unload_plugin(
                "lifecycle_plugin"
            )
            assert result is True

            # Verify cleanup was called
            assert plugin_instance.plugin_object.cleaned_up is True

        finally:
            plugin_file.unlink()

    @pytest.mark.asyncio
    async def test_multiple_plugins_management(self):
        """Test managing multiple plugins simultaneously."""

        # Create multiple plugin files
        plugin_codes = {
            "plugin1": '''
from chatter.services.plugins import ToolPlugin

class Plugin1(ToolPlugin):
    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def health_check(self):
        return {"status": "healthy", "plugin": "plugin1"}

    def get_tools(self):
        from tests.test_plugins import MockBaseTool
        return [MockBaseTool("plugin1_tool", "Tool from plugin 1")]

plugin_class = Plugin1
''',
            "plugin2": '''
from chatter.services.plugins import ToolPlugin

class Plugin2(ToolPlugin):
    async def initialize(self):
        pass

    async def shutdown(self):
        pass

    async def health_check(self):
        return {"status": "healthy", "plugin": "plugin2"}

    def get_tools(self):
        from tests.test_plugins import MockBaseTool
        return [MockBaseTool("plugin2_tool", "Tool from plugin 2")]

plugin_class = Plugin2
''',
        }

        plugin_files = []
        try:
            # Create and load plugins
            for plugin_name, plugin_code in plugin_codes.items():
                with tempfile.NamedTemporaryFile(
                    mode='w', suffix='.py', delete=False
                ) as f:
                    f.write(plugin_code)
                    plugin_file = Path(f.name)
                    plugin_files.append(plugin_file)

                plugin_instance = (
                    await self.plugin_manager.load_plugin_from_file(
                        plugin_file, plugin_name, {}
                    )
                )
                plugin_instance.status = PluginStatus.ACTIVE

            # List all plugins
            plugins = self.plugin_manager.list_plugins()
            assert len(plugins) == 2
            assert "plugin1" in plugins
            assert "plugin2" in plugins

            # Health check all plugins
            health_results = (
                await self.plugin_manager.health_check_all_plugins()
            )
            assert len(health_results) == 2
            assert health_results["plugin1"]["plugin"] == "plugin1"
            assert health_results["plugin2"]["plugin"] == "plugin2"

            # Get tools from all plugins
            all_tools = self.plugin_manager.get_tools_from_plugins()
            assert len(all_tools) == 2
            tool_names = [tool.name for tool in all_tools]
            assert "plugin1_tool" in tool_names
            assert "plugin2_tool" in tool_names

            # Unload one plugin
            result = await self.plugin_manager.unload_plugin("plugin1")
            assert result is True

            # Verify only one plugin remains
            remaining_plugins = self.plugin_manager.list_plugins()
            assert len(remaining_plugins) == 1
            assert "plugin2" in remaining_plugins

        finally:
            # Clean up plugin files
            for plugin_file in plugin_files:
                if plugin_file.exists():
                    plugin_file.unlink()


class TestPluginError:
    """Test PluginError exception."""

    def test_plugin_error_creation(self):
        """Test creating PluginError."""
        error = PluginError("Test plugin error")
        assert str(error) == "Test plugin error"
        assert isinstance(error, Exception)

    def test_plugin_error_with_cause(self):
        """Test PluginError with underlying cause."""
        original_error = ImportError("Module not found")
        try:
            raise PluginError("Plugin load failed") from original_error
        except PluginError as plugin_error:
            assert str(plugin_error) == "Plugin load failed"
            assert plugin_error.__cause__ == original_error


class TestPluginInstallValidation:
    """Test plugin installation validation."""

    def setup_method(self):
        """Set up test environment."""
        self.plugin_manager = PluginManager()

    @pytest.mark.asyncio
    async def test_install_plugin_empty_path(self):
        """Test that install_plugin rejects empty plugin paths."""
        
        # Test empty string
        with pytest.raises(ValueError, match="Plugin path cannot be empty"):
            await self.plugin_manager.install_plugin("")
            
        # Test None
        with pytest.raises(ValueError, match="Plugin path cannot be empty"):
            await self.plugin_manager.install_plugin(None)
            
        # Test whitespace only
        with pytest.raises(ValueError, match="Plugin path cannot be empty"):
            await self.plugin_manager.install_plugin("   ")

    @pytest.mark.asyncio
    async def test_install_plugin_nonexistent_path(self):
        """Test that install_plugin rejects non-existent paths."""
        
        with pytest.raises(ValueError, match="Plugin path does not exist"):
            await self.plugin_manager.install_plugin("/nonexistent/path")
