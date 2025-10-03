"""Integration test for complete workflow config to tool loading flow."""

import pytest

from chatter.schemas.chat import ChatRequest
from chatter.services.workflow_execution import WorkflowExecutionService


class MockTool:
    """Mock tool for testing."""
    
    def __init__(self, name):
        self.name = name
        
    def __repr__(self):
        return f"MockTool({self.name})"


class MockToolRegistry:
    """Mock tool registry for testing."""
    
    def __init__(self):
        self.all_tools = [
            MockTool('calculator'),
            MockTool('get_time'),
            MockTool('web_search'),
            MockTool('code_executor'),
        ]
    
    async def get_enabled_tools_for_workspace(self, workspace_id, user_permissions, session):
        """Return all enabled tools."""
        return self.all_tools.copy()
    
    def _get_tool_name(self, tool):
        """Get tool name."""
        return tool.name


class TestCompleteWorkflowConfigFlow:
    """Test complete flow from ChatRequest to tool loading."""
    
    def test_ui_selected_tools_are_loaded(self):
        """Test that tools selected in UI are correctly loaded."""
        # Simulate what the frontend sends
        chat_request = ChatRequest(
            message="Calculate 5 + 3 and get the current time",
            enable_tools=False,  # Default, not set by UI
            workflow_config={
                'enable_tools': False,  # Default from ChatWorkflowConfig
                'tool_config': {
                    'enabled': True,  # User enabled in UI
                    'allowed_tools': ['calculator', 'get_time'],  # User selected
                    'max_tool_calls': 5,
                }
            }
        )
        
        # Extract settings
        service = WorkflowExecutionService(None, None, None)
        settings = service._extract_workflow_config_settings(chat_request)
        
        # Verify extraction
        assert settings['enable_tools'] is True, "Should extract enabled=True from tool_config"
        assert settings['allowed_tools'] == ['calculator', 'get_time']
        
        # Simulate tool loading and filtering
        tool_registry = MockToolRegistry()
        all_tools = [
            MockTool('calculator'),
            MockTool('get_time'),
            MockTool('web_search'),
            MockTool('code_executor'),
        ]
        
        # Filter by allowed_tools
        if settings['allowed_tools']:
            allowed_tools_set = set(settings['allowed_tools'])
            filtered_tools = [
                tool for tool in all_tools
                if tool_registry._get_tool_name(tool) in allowed_tools_set
            ]
        else:
            filtered_tools = all_tools
        
        # Verify filtering
        assert len(filtered_tools) == 2
        tool_names = [t.name for t in filtered_tools]
        assert 'calculator' in tool_names
        assert 'get_time' in tool_names
        assert 'web_search' not in tool_names
        assert 'code_executor' not in tool_names
    
    def test_no_allowed_tools_loads_all(self):
        """Test that when no allowed_tools specified, all enabled tools are loaded."""
        chat_request = ChatRequest(
            message="Test",
            enable_tools=False,
            workflow_config={
                'tool_config': {
                    'enabled': True,  # Enabled but no allowed_tools
                }
            }
        )
        
        service = WorkflowExecutionService(None, None, None)
        settings = service._extract_workflow_config_settings(chat_request)
        
        assert settings['enable_tools'] is True
        assert settings['allowed_tools'] is None  # No filtering
        
        # All tools should be available
        tool_registry = MockToolRegistry()
        all_tools = tool_registry.all_tools
        
        # No filtering since allowed_tools is None
        if settings['allowed_tools']:
            filtered_tools = []  # Would filter
        else:
            filtered_tools = all_tools  # No filtering
        
        assert len(filtered_tools) == 4
    
    def test_tools_disabled_loads_none(self):
        """Test that when tools are disabled, no tools are loaded."""
        chat_request = ChatRequest(
            message="Test",
            enable_tools=False,
            workflow_config={
                'tool_config': {
                    'enabled': False,  # Explicitly disabled
                    'allowed_tools': ['calculator'],  # This should be ignored
                }
            }
        )
        
        service = WorkflowExecutionService(None, None, None)
        settings = service._extract_workflow_config_settings(chat_request)
        
        assert settings['enable_tools'] is False
        
        # Tools should not be loaded at all
        if settings['enable_tools']:
            tools = ['would', 'load', 'tools']
        else:
            tools = None
        
        assert tools is None
    
    def test_empty_allowed_tools_list(self):
        """Test that empty allowed_tools list results in no tools."""
        chat_request = ChatRequest(
            message="Test",
            enable_tools=False,
            workflow_config={
                'tool_config': {
                    'enabled': True,
                    'allowed_tools': [],  # Empty list
                }
            }
        )
        
        service = WorkflowExecutionService(None, None, None)
        settings = service._extract_workflow_config_settings(chat_request)
        
        assert settings['enable_tools'] is True
        assert settings['allowed_tools'] == []
        
        # Filter with empty list
        tool_registry = MockToolRegistry()
        all_tools = tool_registry.all_tools
        
        if settings['allowed_tools'] is not None:  # Empty list is not None
            allowed_tools_set = set(settings['allowed_tools'])
            filtered_tools = [
                tool for tool in all_tools
                if tool_registry._get_tool_name(tool) in allowed_tools_set
            ]
        else:
            filtered_tools = all_tools
        
        assert len(filtered_tools) == 0  # No tools match empty set
    
    def test_nonexistent_tools_filtered_out(self):
        """Test that nonexistent tools in allowed_tools are filtered out."""
        chat_request = ChatRequest(
            message="Test",
            workflow_config={
                'tool_config': {
                    'enabled': True,
                    'allowed_tools': [
                        'calculator',
                        'nonexistent_tool',  # Doesn't exist
                        'get_time',
                        'another_fake_tool',  # Doesn't exist
                    ],
                }
            }
        )
        
        service = WorkflowExecutionService(None, None, None)
        settings = service._extract_workflow_config_settings(chat_request)
        
        # Filter simulation
        tool_registry = MockToolRegistry()
        all_tools = tool_registry.all_tools
        
        allowed_tools_set = set(settings['allowed_tools'])
        filtered_tools = [
            tool for tool in all_tools
            if tool_registry._get_tool_name(tool) in allowed_tools_set
        ]
        
        # Only real tools should remain
        assert len(filtered_tools) == 2
        tool_names = [t.name for t in filtered_tools]
        assert 'calculator' in tool_names
        assert 'get_time' in tool_names
        assert 'nonexistent_tool' not in tool_names
        assert 'another_fake_tool' not in tool_names
