"""Execution request schemas for unified workflow execution.

This module provides Pydantic schemas for workflow execution requests,
supporting all execution types (template, definition, custom, chat).
"""

from typing import Any

from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    """Unified request for workflow execution.

    This schema supports all execution types and replaces the various
    request formats used across different execution paths.
    """

    # Execution type indicators (at least one must be provided)
    template_id: str | None = Field(
        default=None, description="ID of template to execute"
    )
    definition_id: str | None = Field(
        default=None, description="ID of definition to execute"
    )
    nodes: list[dict[str, Any]] | None = Field(
        default=None, description="Custom workflow nodes"
    )
    edges: list[dict[str, Any]] | None = Field(
        default=None, description="Custom workflow edges"
    )

    # Input data
    message: str | None = Field(
        default=None, description="User message for chat workflows"
    )
    input_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional input data"
    )

    # LLM configuration
    provider: str | None = Field(
        default=None, description="LLM provider (e.g., 'openai', 'anthropic')"
    )
    model: str | None = Field(
        default=None, description="Model name (e.g., 'gpt-4', 'claude-3')"
    )
    temperature: float | None = Field(
        default=None, ge=0.0, le=2.0, description="Sampling temperature"
    )
    max_tokens: int | None = Field(
        default=None, gt=0, description="Maximum tokens to generate"
    )
    system_prompt: str | None = Field(
        default=None, description="System prompt override"
    )

    # Feature flags
    enable_memory: bool = Field(
        default=False, description="Enable conversation memory"
    )
    enable_retrieval: bool = Field(
        default=False, description="Enable document retrieval"
    )
    enable_tools: bool = Field(
        default=False, description="Enable tool calling"
    )
    streaming: bool = Field(
        default=False, description="Enable streaming response"
    )

    # Limits
    memory_window: int = Field(
        default=10, gt=0, description="Number of messages to keep in memory"
    )
    max_tool_calls: int = Field(
        default=10, gt=0, description="Maximum tool calls allowed"
    )
    max_documents: int | None = Field(
        default=None, gt=0, description="Maximum documents to retrieve"
    )

    # Tool configuration
    allowed_tools: list[str] | None = Field(
        default=None, description="List of allowed tool names"
    )
    tool_config: dict[str, Any] | None = Field(
        default=None, description="Additional tool configuration"
    )

    # Retrieval configuration
    document_ids: list[str] | None = Field(
        default=None, description="Document IDs for retrieval"
    )

    # Conversation context
    conversation_id: str | None = Field(
        default=None, description="Conversation ID for context"
    )

    # Template parameters (for template execution)
    template_params: dict[str, Any] | None = Field(
        default=None, description="Parameters for template instantiation"
    )

    # Debug mode
    debug_mode: bool = Field(
        default=False, description="Enable debug logging"
    )

    # Workflow-specific configuration
    workflow_config: dict[str, Any] = Field(
        default_factory=dict, description="Additional workflow configuration"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "message": "What is the weather like?",
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "enable_tools": True,
                "conversation_id": "01HXX1234567890",
            }
        }
