"""Test workflow config extraction from ChatRequest."""

import pytest

from chatter.schemas.chat import ChatRequest
from chatter.services.unified_workflow_execution import UnifiedUnifiedWorkflowExecutionService


class TestWorkflowConfigExtraction:
    """Test extraction of workflow configuration from ChatRequest."""

    def test_extract_basic_settings_from_top_level(self):
        """Test extraction when settings are at top level."""
        chat_request = ChatRequest(
            message="Test message",
            enable_tools=True,
            enable_retrieval=False,
            enable_memory=True,
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        assert settings['enable_tools'] is True
        assert settings['enable_retrieval'] is False
        assert settings['enable_memory'] is True
        assert settings['allowed_tools'] is None

    def test_extract_tool_config_from_workflow_config(self):
        """Test extraction when tool_config is in workflow_config."""
        chat_request = ChatRequest(
            message="Test message",
            enable_tools=False,  # Top-level is False
            workflow_config={
                'tool_config': {
                    'enabled': True,  # But workflow_config says True
                    'allowed_tools': ['calculator', 'get_time'],
                    'max_tool_calls': 5,
                }
            },
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        # workflow_config.tool_config.enabled should override top-level
        assert settings['enable_tools'] is True
        assert settings['allowed_tools'] == ['calculator', 'get_time']
        assert settings['tool_config'] is not None
        assert settings['tool_config']['max_tool_calls'] == 5

    def test_extract_retrieval_from_workflow_config(self):
        """Test extraction when retrieval config is in workflow_config."""
        chat_request = ChatRequest(
            message="Test message",
            enable_retrieval=False,  # Top-level is False
            workflow_config={
                'enable_retrieval': True,  # But workflow_config says True
                'retrieval_config': {'max_documents': 10},
            },
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        # workflow_config.enable_retrieval should override top-level
        assert settings['enable_retrieval'] is True

    def test_extract_memory_from_workflow_config(self):
        """Test extraction when memory config is in workflow_config."""
        chat_request = ChatRequest(
            message="Test message",
            enable_memory=True,  # Top-level is True
            workflow_config={
                'enable_memory': False,  # But workflow_config says False
            },
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        # workflow_config.enable_memory should override top-level
        assert settings['enable_memory'] is False

    def test_extract_with_no_workflow_config(self):
        """Test extraction when workflow_config is None."""
        chat_request = ChatRequest(
            message="Test message",
            enable_tools=True,
            enable_retrieval=True,
            enable_memory=False,
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        assert settings['enable_tools'] is True
        assert settings['enable_retrieval'] is True
        assert settings['enable_memory'] is False
        assert settings['allowed_tools'] is None
        assert settings['tool_config'] is None

    def test_extract_with_empty_workflow_config(self):
        """Test extraction when workflow_config is empty dict."""
        chat_request = ChatRequest(
            message="Test message",
            enable_tools=True,
            workflow_config={},
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        # Should fall back to top-level settings
        assert settings['enable_tools'] is True
        assert settings['allowed_tools'] is None

    def test_extract_allowed_tools_without_enabled(self):
        """Test extraction when allowed_tools is set but enabled is not."""
        chat_request = ChatRequest(
            message="Test message",
            enable_tools=True,
            workflow_config={
                'tool_config': {
                    'allowed_tools': ['calculator'],
                }
            },
        )

        service = UnifiedWorkflowExecutionService(
            llm_service=None, message_service=None, session=None
        )
        settings = service._extract_workflow_config_settings(chat_request)

        # Should use top-level enable_tools since tool_config.enabled not set
        assert settings['enable_tools'] is True
        assert settings['allowed_tools'] == ['calculator']
