"""Type definitions for unified workflow execution.

This module provides the core type definitions for the refactored workflow
execution system, supporting unified execution across templates, definitions,
and dynamic workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from chatter.models.conversation import Conversation, Message
from chatter.schemas.chat import ChatResponse
from chatter.schemas.workflows import WorkflowExecutionResponse


class ExecutionMode(str, Enum):
    """Execution mode for workflows."""

    STANDARD = "standard"
    STREAMING = "streaming"


class WorkflowSourceType(str, Enum):
    """Type of workflow source."""

    TEMPLATE = "template"
    DEFINITION = "definition"
    DYNAMIC = "dynamic"


@dataclass
class WorkflowSource:
    """Source configuration for workflow execution.
    
    This defines where the workflow comes from - a template, a stored
    definition, or dynamically created.
    """

    source_type: WorkflowSourceType
    source_id: str | None = None  # Template ID or Definition ID
    template_params: dict[str, Any] | None = None


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution.
    
    This consolidates all configuration options for workflow execution,
    replacing scattered configuration across multiple methods.
    """

    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2048
    enable_tools: bool = False
    enable_retrieval: bool = False
    enable_memory: bool = True
    allowed_tools: list[str] | None = None
    document_ids: list[str] | None = None
    memory_window: int = 10
    max_tool_calls: int = 10
    system_prompt_override: str | None = None


@dataclass
class WorkflowInput:
    """Input data for workflow execution.
    
    This provides a unified input structure for all workflow execution
    methods, replacing multiple parameter lists.
    """

    message: str
    user_id: str
    config: WorkflowConfig
    conversation_id: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class WorkflowResult:
    """Unified workflow execution result.
    
    This provides a single result type for all workflow executions,
    replacing the 6 different result conversion paths.
    """

    message: Message  # SQLAlchemy Message
    conversation: Conversation  # SQLAlchemy Conversation
    execution_id: str
    execution_time_ms: int
    tokens_used: int
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cost: float = 0.0
    tool_calls: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_log: list[dict[str, Any]] | None = None

    def to_chat_response(self) -> ChatResponse:
        """Convert to ChatResponse for /execute/chat endpoint.
        
        This consolidates the chat workflow result conversion path.
        """
        from chatter.schemas.chat import (
            ConversationResponse,
            MessageResponse,
        )

        return ChatResponse(
            conversation_id=self.conversation.id,
            message=MessageResponse.model_validate(self.message),
            conversation=ConversationResponse.model_validate(
                self.conversation
            ),
        )

    def to_execution_response(self) -> WorkflowExecutionResponse:
        """Convert to WorkflowExecutionResponse for /definitions/{id}/execute.
        
        This consolidates the workflow definition execution result conversion.
        """
        return WorkflowExecutionResponse(
            execution_id=self.execution_id,
            status="completed",
            output_data={
                "response": self.message.content,
                "conversation_id": self.conversation.id,
                "metadata": self.metadata,
            },
            tokens_used=self.tokens_used,
            cost=self.cost,
            execution_time_ms=self.execution_time_ms,
        )

    def to_detailed_response(self) -> dict[str, Any]:
        """Convert to detailed response with logs.
        
        This consolidates the detailed execution response with debug logs.
        """
        return {
            "id": self.execution_id,
            "workflow_name": self.metadata.get("workflow_name", ""),
            "status": "completed",
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "cost": self.cost,
            "tool_calls": self.tool_calls,
            "execution_log": self.execution_log or [],
            "output": {"response": self.message.content},
            "metadata": self.metadata,
        }
