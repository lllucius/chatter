"""Execution context for unified workflow execution.

This module provides the ExecutionContext dataclass which serves as a single
source of truth for all workflow execution state, replacing the previous
fragmented state management across multiple containers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from langchain_core.language_models import BaseChatModel

from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid


class WorkflowType(str, Enum):
    """Type of workflow being executed."""

    TEMPLATE = "template"  # Executed from a template
    DEFINITION = "definition"  # Executed from a stored definition
    CUSTOM = "custom"  # Custom workflow from nodes/edges
    CHAT = "chat"  # Simple chat workflow


@dataclass
class ExecutionConfig:
    """Configuration for workflow execution."""

    # Input data
    input_data: dict[str, Any] = field(default_factory=dict)

    # LLM configuration
    provider: str | None = None
    model: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    system_prompt: str | None = None

    # Feature flags
    enable_memory: bool = False
    enable_retrieval: bool = False
    enable_tools: bool = False
    enable_streaming: bool = False

    # Limits
    memory_window: int = 10
    max_tool_calls: int = 10
    max_documents: int | None = None

    # Tool configuration
    allowed_tools: list[str] | None = None
    tool_config: dict[str, Any] | None = None

    # Retrieval configuration
    document_ids: list[str] | None = None

    # Workflow-specific config
    workflow_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Single source of truth for workflow execution state.

    This context replaces the previous fragmented state management where
    information was duplicated across WorkflowNodeContext, WorkflowExecution,
    PerformanceMonitor, MonitoringService, and various result dictionaries.
    """

    # Identification
    execution_id: str
    user_id: str
    conversation_id: str | None = None

    # Workflow identification
    workflow_type: WorkflowType = WorkflowType.CHAT
    source_template_id: str | None = None
    source_definition_id: str | None = None
    workflow_id: str | None = None  # For monitoring service
    execution_record_id: str | None = None  # Database execution record ID

    # Configuration
    config: ExecutionConfig = field(default_factory=ExecutionConfig)

    # Runtime State (for LangGraph)
    state: WorkflowNodeContext | None = None

    # Resources
    llm: BaseChatModel | None = None
    tools: list[Any] | None = None
    retriever: Any | None = None

    # Tracking
    correlation_id: str = field(default_factory=generate_ulid)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def thread_id(self) -> str:
        """Thread ID for LangGraph checkpointing."""
        return self.conversation_id or self.execution_id

    def to_execution_record(self) -> dict[str, Any]:
        """Convert to WorkflowExecution format for database storage."""
        return {
            "id": self.execution_id,
            "definition_id": self.source_definition_id,
            "template_id": self.source_template_id,
            "owner_id": self.user_id,
            "workflow_type": self.workflow_type.value,
            "workflow_config": {
                "provider": self.config.provider,
                "model": self.config.model,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "enable_memory": self.config.enable_memory,
                "enable_retrieval": self.config.enable_retrieval,
                "enable_tools": self.config.enable_tools,
                **self.config.workflow_config,
            },
            "input_data": self.config.input_data,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
        }

    def to_event_data(self) -> dict[str, Any]:
        """Convert to event data format for UnifiedEvent system."""
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type.value,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "correlation_id": self.correlation_id,
            "template_id": self.source_template_id,
            "definition_id": self.source_definition_id,
            "provider": self.config.provider,
            "model": self.config.model,
            "enable_tools": self.config.enable_tools,
            "enable_retrieval": self.config.enable_retrieval,
            "enable_memory": self.config.enable_memory,
        }

    def to_monitoring_config(self) -> dict[str, Any]:
        """Convert to monitoring service configuration."""
        return {
            "user_id": self.user_id,
            "conversation_id": self.conversation_id or "",
            "provider_name": self.config.provider or "",
            "model_name": self.config.model or "",
            "correlation_id": self.correlation_id,
            "workflow_config": {
                "template_id": self.source_template_id,
                "definition_id": self.source_definition_id,
                "workflow_type": self.workflow_type.value,
                "enable_tools": self.config.enable_tools,
                "enable_retrieval": self.config.enable_retrieval,
                "enable_memory": self.config.enable_memory,
            },
        }
