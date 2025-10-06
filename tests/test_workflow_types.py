"""Tests for workflow type definitions."""

import pytest

from chatter.services.workflow_types import (
    ExecutionMode,
    WorkflowConfig,
    WorkflowInput,
    WorkflowSource,
    WorkflowSourceType,
)


def test_execution_mode_enum():
    """Test ExecutionMode enum values."""
    assert ExecutionMode.STANDARD == "standard"
    assert ExecutionMode.STREAMING == "streaming"


def test_workflow_source_type_enum():
    """Test WorkflowSourceType enum values."""
    assert WorkflowSourceType.TEMPLATE == "template"
    assert WorkflowSourceType.DEFINITION == "definition"
    assert WorkflowSourceType.DYNAMIC == "dynamic"


def test_workflow_source_creation():
    """Test WorkflowSource creation."""
    # Template source
    source = WorkflowSource(
        source_type=WorkflowSourceType.TEMPLATE,
        source_id="universal_chat",
    )
    assert source.source_type == WorkflowSourceType.TEMPLATE
    assert source.source_id == "universal_chat"
    assert source.template_params is None

    # Definition source
    source = WorkflowSource(
        source_type=WorkflowSourceType.DEFINITION,
        source_id="def_123",
    )
    assert source.source_type == WorkflowSourceType.DEFINITION
    assert source.source_id == "def_123"

    # Dynamic source
    source = WorkflowSource(source_type=WorkflowSourceType.DYNAMIC)
    assert source.source_type == WorkflowSourceType.DYNAMIC
    assert source.source_id is None


def test_workflow_config_defaults():
    """Test WorkflowConfig default values."""
    config = WorkflowConfig()
    assert config.provider is None
    assert config.model is None
    assert config.temperature == 0.7
    assert config.max_tokens == 2048
    assert config.enable_tools is False
    assert config.enable_retrieval is False
    assert config.enable_memory is True
    assert config.memory_window == 10
    assert config.max_tool_calls == 10


def test_workflow_config_custom():
    """Test WorkflowConfig with custom values."""
    config = WorkflowConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.5,
        max_tokens=4096,
        enable_tools=True,
        enable_retrieval=True,
        allowed_tools=["calculator", "search"],
        document_ids=["doc1", "doc2"],
        memory_window=20,
    )
    assert config.provider == "openai"
    assert config.model == "gpt-4"
    assert config.temperature == 0.5
    assert config.max_tokens == 4096
    assert config.enable_tools is True
    assert config.enable_retrieval is True
    assert config.allowed_tools == ["calculator", "search"]
    assert config.document_ids == ["doc1", "doc2"]
    assert config.memory_window == 20


def test_workflow_input_creation():
    """Test WorkflowInput creation."""
    config = WorkflowConfig(provider="openai", model="gpt-4")
    
    workflow_input = WorkflowInput(
        message="Hello, world!",
        user_id="user_123",
        config=config,
        conversation_id="conv_456",
        metadata={"key": "value"},
    )
    
    assert workflow_input.message == "Hello, world!"
    assert workflow_input.user_id == "user_123"
    assert workflow_input.config == config
    assert workflow_input.conversation_id == "conv_456"
    assert workflow_input.metadata == {"key": "value"}


def test_workflow_input_minimal():
    """Test WorkflowInput with minimal parameters."""
    config = WorkflowConfig()
    
    workflow_input = WorkflowInput(
        message="Test message",
        user_id="user_123",
        config=config,
    )
    
    assert workflow_input.message == "Test message"
    assert workflow_input.user_id == "user_123"
    assert workflow_input.conversation_id is None
    assert workflow_input.metadata is None
