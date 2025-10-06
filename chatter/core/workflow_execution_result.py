"""Execution result for unified workflow execution.

This module provides the ExecutionResult dataclass which standardizes the
result format from workflow execution, replacing multiple result dictionary
formats with a single, consistent structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from chatter.schemas.workflows import WorkflowExecutionResponse


@dataclass
class ExecutionResult:
    """Standardized execution result from workflow execution.

    This replaces the various result dictionary formats used across different
    execution paths with a single, consistent result structure.
    """

    # Response
    response: str
    messages: list[BaseMessage] = field(default_factory=list)

    # Metrics
    execution_time_ms: int = 0
    tokens_used: int = 0
    cost: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0

    # Tracking
    tool_calls: int = 0
    errors: list[str] = field(default_factory=list)

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)

    # Execution context info
    execution_id: str | None = None
    conversation_id: str | None = None
    workflow_type: str | None = None

    @classmethod
    def from_raw(
        cls,
        raw_result: dict[str, Any],
        execution_id: str | None = None,
        conversation_id: str | None = None,
        workflow_type: str | None = None,
    ) -> ExecutionResult:
        """Create ExecutionResult from raw workflow result.

        Args:
            raw_result: Raw result dictionary from workflow_manager.run_workflow()
            execution_id: Optional execution ID
            conversation_id: Optional conversation ID
            workflow_type: Optional workflow type

        Returns:
            ExecutionResult instance
        """
        # Extract messages
        messages = raw_result.get("messages", [])

        # Extract AI response from last message
        response = ""
        if messages:
            last_message = messages[-1]
            if isinstance(last_message, (AIMessage, BaseMessage)):
                response = last_message.content if hasattr(last_message, "content") else ""
            elif isinstance(last_message, dict):
                response = last_message.get("content", "")

        # Extract usage metadata
        usage_metadata = raw_result.get("usage_metadata", {})
        prompt_tokens = usage_metadata.get("input_tokens", 0) or usage_metadata.get("prompt_tokens", 0)
        completion_tokens = usage_metadata.get("output_tokens", 0) or usage_metadata.get("completion_tokens", 0)
        total_tokens = usage_metadata.get("total_tokens", 0) or (prompt_tokens + completion_tokens)

        # Extract cost
        cost = raw_result.get("cost", 0.0)

        # Extract metadata
        metadata = raw_result.get("metadata", {})

        # Extract tool call count
        tool_calls = raw_result.get("tool_call_count", 0)

        return cls(
            response=response,
            messages=messages,
            execution_time_ms=0,  # Will be set by execution engine
            tokens_used=total_tokens,
            cost=cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            tool_calls=tool_calls,
            metadata=metadata,
            execution_id=execution_id,
            conversation_id=conversation_id,
            workflow_type=workflow_type,
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "response": self.response,
            "messages": self.messages,
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "tool_calls": self.tool_calls,
            "errors": self.errors,
            "metadata": self.metadata,
            "execution_id": self.execution_id,
            "conversation_id": self.conversation_id,
            "workflow_type": self.workflow_type,
        }

    def to_api_response(self) -> WorkflowExecutionResponse:
        """Convert to API response format.

        Returns:
            WorkflowExecutionResponse for API
        """
        return WorkflowExecutionResponse(
            execution_id=self.execution_id or "",
            status="completed" if not self.errors else "failed",
            output_data={
                "response": self.response,
                "metadata": self.metadata,
            },
            execution_time_ms=self.execution_time_ms,
            tokens_used=self.tokens_used,
            cost=self.cost,
            error=self.errors[0] if self.errors else None,
        )

    def to_event_data(self) -> dict[str, Any]:
        """Convert to event data format for UnifiedEvent system."""
        return {
            "execution_id": self.execution_id,
            "conversation_id": self.conversation_id,
            "workflow_type": self.workflow_type,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "execution_time_ms": self.execution_time_ms,
            "tool_calls": self.tool_calls,
            "success": len(self.errors) == 0,
            "error_count": len(self.errors),
        }
