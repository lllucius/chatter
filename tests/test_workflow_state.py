"""Tests for workflow state utilities."""

import pytest
from unittest.mock import MagicMock

from langchain_core.messages import HumanMessage, AIMessage

from chatter.services.workflow_state import (
    create_workflow_state,
    update_workflow_state,
    extract_state_metadata,
)
from chatter.services.workflow_types import WorkflowConfig


@pytest.fixture
def sample_config():
    """Sample workflow configuration."""
    return WorkflowConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.7,
        max_tokens=2000,
    )


@pytest.fixture
def sample_messages():
    """Sample conversation messages."""
    return [
        HumanMessage(content="Hello"),
        AIMessage(content="Hi there!"),
    ]


def test_create_workflow_state_minimal(sample_messages, sample_config):
    """Test creating workflow state with minimal parameters."""
    state = create_workflow_state(
        messages=sample_messages,
        user_id="user_123",
        conversation_id="conv_456",
        config=sample_config,
    )
    
    # Check core fields
    assert state["messages"] == sample_messages
    assert state["user_id"] == "user_123"
    assert state["conversation_id"] == "conv_456"
    
    # Check metadata
    assert state["metadata"]["provider"] == "openai"
    assert state["metadata"]["model"] == "gpt-4"
    assert state["metadata"]["temperature"] == 0.7
    assert state["metadata"]["max_tokens"] == 2000
    
    # Check optional fields have defaults
    assert state["retrieval_context"] is None
    assert state["conversation_summary"] is None
    assert state["tool_call_count"] == 0
    assert state["variables"] == {}
    assert state["loop_state"] == {}
    assert state["error_state"] == {}
    assert state["conditional_results"] == {}
    assert state["execution_history"] == []
    assert state["usage_metadata"] == {}


def test_create_workflow_state_with_source(sample_messages, sample_config):
    """Test creating workflow state with source information."""
    state = create_workflow_state(
        messages=sample_messages,
        user_id="user_123",
        conversation_id="conv_456",
        config=sample_config,
        source_type="template",
        source_id="template_789",
    )
    
    assert state["metadata"]["source_type"] == "template"
    assert state["metadata"]["source_id"] == "template_789"


def test_create_workflow_state_with_optional_fields(sample_messages, sample_config):
    """Test creating workflow state with optional fields."""
    state = create_workflow_state(
        messages=sample_messages,
        user_id="user_123",
        conversation_id="conv_456",
        config=sample_config,
        tool_call_count=5,
        variables={"key": "value"},
        retrieval_context="Some context",
    )
    
    assert state["tool_call_count"] == 5
    assert state["variables"] == {"key": "value"}
    assert state["retrieval_context"] == "Some context"


def test_update_workflow_state():
    """Test updating workflow state."""
    initial_state = {
        "messages": [],
        "user_id": "user_123",
        "metadata": {"provider": "openai"},
        "variables": {"old": "value"},
    }
    
    updated_state = update_workflow_state(
        initial_state,
        user_id="user_456",  # Replace
        metadata={"model": "gpt-4"},  # Merge
        variables={"new": "value"},  # Merge
        custom_field="custom",  # Add
    )
    
    # Original state unchanged
    assert initial_state["user_id"] == "user_123"
    
    # Updated state has changes
    assert updated_state["user_id"] == "user_456"
    assert updated_state["metadata"]["provider"] == "openai"
    assert updated_state["metadata"]["model"] == "gpt-4"
    assert updated_state["variables"]["old"] == "value"
    assert updated_state["variables"]["new"] == "value"
    assert updated_state["custom_field"] == "custom"


def test_update_workflow_state_list_extend():
    """Test updating workflow state with list extension."""
    initial_state = {
        "execution_history": ["step1"],
    }
    
    updated_state = update_workflow_state(
        initial_state,
        execution_history=["step2", "step3"],
    )
    
    assert updated_state["execution_history"] == ["step1", "step2", "step3"]


def test_extract_state_metadata(sample_messages, sample_config):
    """Test extracting metadata from workflow state."""
    state = create_workflow_state(
        messages=sample_messages,
        user_id="user_123",
        conversation_id="conv_456",
        config=sample_config,
        source_type="template",
        source_id="template_789",
        retrieval_context="Some context",
        tool_call_count=3,
    )
    
    metadata = extract_state_metadata(state)
    
    assert metadata["user_id"] == "user_123"
    assert metadata["conversation_id"] == "conv_456"
    assert metadata["tool_call_count"] == 3
    assert metadata["provider"] == "openai"
    assert metadata["model"] == "gpt-4"
    assert metadata["temperature"] == 0.7
    assert metadata["max_tokens"] == 2000
    assert metadata["source_type"] == "template"
    assert metadata["source_id"] == "template_789"
    assert metadata["has_retrieval"] is True
    assert metadata["has_summary"] is False


def test_extract_state_metadata_minimal():
    """Test extracting metadata from minimal state."""
    state = {
        "user_id": "user_123",
        "conversation_id": "conv_456",
    }
    
    metadata = extract_state_metadata(state)
    
    assert metadata["user_id"] == "user_123"
    assert metadata["conversation_id"] == "conv_456"
    assert metadata["tool_call_count"] == 0
    assert metadata["provider"] is None
    assert metadata["has_retrieval"] is False
