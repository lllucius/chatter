"""Workflow state management utilities.

This module provides utilities for creating and managing workflow state,
consolidating state initialization logic that was previously duplicated
across multiple execution methods.
"""

from __future__ import annotations

from typing import Any

from langchain_core.messages import BaseMessage

from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.services.workflow_types import WorkflowConfig


def create_workflow_state(
    messages: list[BaseMessage],
    user_id: str,
    conversation_id: str,
    config: WorkflowConfig,
    source_type: str | None = None,
    source_id: str | None = None,
    **optional_fields,
) -> WorkflowNodeContext:
    """Create workflow state with lazy initialization.
    
    This consolidates state creation from multiple locations, reducing
    duplication and providing a single source of truth for state structure.
    
    Args:
        messages: Conversation messages
        user_id: User ID
        conversation_id: Conversation ID
        config: Workflow configuration
        source_type: Workflow source type (template/definition/dynamic)
        source_id: Source identifier
        **optional_fields: Additional optional fields
        
    Returns:
        Initialized WorkflowNodeContext
    """
    # Core fields (always initialized)
    state: WorkflowNodeContext = {
        "messages": messages,
        "user_id": user_id,
        "conversation_id": conversation_id,
        "metadata": {
            "provider": config.provider,
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        },
    }

    # Add source info to metadata if provided
    if source_type:
        state["metadata"]["source_type"] = source_type
    if source_id:
        state["metadata"]["source_id"] = source_id

    # Optional fields (only if provided or needed)
    # These have default None or 0 values
    state["retrieval_context"] = optional_fields.get("retrieval_context")
    state["conversation_summary"] = optional_fields.get(
        "conversation_summary"
    )
    state["tool_call_count"] = optional_fields.get("tool_call_count", 0)

    # Rarely-used fields (lazy initialization with empty defaults)
    # These are only populated when actually needed
    state["variables"] = optional_fields.get("variables", {})
    state["loop_state"] = optional_fields.get("loop_state", {})
    state["error_state"] = optional_fields.get("error_state", {})
    state["conditional_results"] = optional_fields.get(
        "conditional_results", {}
    )
    state["execution_history"] = optional_fields.get(
        "execution_history", []
    )
    state["usage_metadata"] = optional_fields.get("usage_metadata", {})

    return state


def update_workflow_state(
    state: WorkflowNodeContext,
    **updates,
) -> WorkflowNodeContext:
    """Update workflow state with new values.
    
    This provides a safe way to update state without modifying the original.
    
    Args:
        state: Existing state to update
        **updates: Fields to update
        
    Returns:
        Updated state
    """
    updated_state = state.copy()
    
    for key, value in updates.items():
        if key in updated_state:
            if isinstance(updated_state[key], dict) and isinstance(value, dict):
                # Merge dictionaries
                updated_state[key] = {**updated_state[key], **value}
            elif isinstance(updated_state[key], list) and isinstance(value, list):
                # Extend lists
                updated_state[key] = updated_state[key] + value
            else:
                # Replace value
                updated_state[key] = value
        else:
            # Add new field
            updated_state[key] = value
    
    return updated_state


def extract_state_metadata(state: WorkflowNodeContext) -> dict[str, Any]:
    """Extract metadata from workflow state.
    
    This is useful for logging, monitoring, and result processing.
    
    Args:
        state: Workflow state
        
    Returns:
        Dictionary of metadata
    """
    return {
        "user_id": state.get("user_id"),
        "conversation_id": state.get("conversation_id"),
        "tool_call_count": state.get("tool_call_count", 0),
        "provider": state.get("metadata", {}).get("provider"),
        "model": state.get("metadata", {}).get("model"),
        "temperature": state.get("metadata", {}).get("temperature"),
        "max_tokens": state.get("metadata", {}).get("max_tokens"),
        "source_type": state.get("metadata", {}).get("source_type"),
        "source_id": state.get("metadata", {}).get("source_id"),
        "has_retrieval": state.get("retrieval_context") is not None,
        "has_summary": state.get("conversation_summary") is not None,
    }
