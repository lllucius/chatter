"""Flexible node factory system for workflow graph construction.

This module provides a modern, extensible system for creating workflow nodes
that supports all defined node types including conditional, loop, variable,
and error handler nodes.
"""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
)

from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowNodeContext(TypedDict):
    """Extended context for workflow execution with support for all node types."""

    # Core fields from ConversationState
    messages: Sequence[BaseMessage]
    user_id: str
    conversation_id: str
    retrieval_context: str | None
    conversation_summary: str | None
    tool_call_count: int
    metadata: dict[str, Any]

    # Extended fields for advanced workflow features
    variables: dict[str, Any]  # For variable nodes
    loop_state: dict[str, Any]  # For loop iteration tracking
    error_state: dict[str, Any]  # For error handling state
    conditional_results: dict[str, bool]  # For conditional evaluation results
    execution_history: list[dict[str, Any]]  # For debugging and progress tracking


class WorkflowNode(ABC):
    """Abstract base class for all workflow nodes."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        self.node_id = node_id
        self.config = config or {}

    @abstractmethod
    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute the node logic and return state updates."""
        pass

    def validate_config(self) -> list[str]:
        """Validate node configuration and return any errors."""
        return []


class MemoryNode(WorkflowNode):
    """Node for memory management and conversation summarization."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.memory_window = config.get("memory_window", 10) if config else 10
        self.llm: BaseChatModel | None = None

    def set_llm(self, llm: BaseChatModel) -> None:
        """Set the LLM for summarization."""
        self.llm = llm

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Manage memory by summarizing older messages."""
        messages = list(context["messages"])

        if len(messages) <= self.memory_window:
            return {}

        recent_messages = messages[-self.memory_window:]
        older_messages = messages[:-self.memory_window]

        if not context.get("conversation_summary") and self.llm:
            try:
                summary = await self._create_summary(older_messages)
                return {
                    "messages": recent_messages,
                    "conversation_summary": summary,
                    "metadata": {
                        **context.get("metadata", {}),
                        "memory_processed": True,
                        "summarized_messages": len(older_messages),
                    }
                }
            except Exception as e:
                logger.error(f"Memory summarization failed: {e}")
                # Fallback to truncation
                return {
                    "messages": recent_messages,
                    "metadata": {
                        **context.get("metadata", {}),
                        "memory_fallback": "truncation",
                        "truncated_messages": len(older_messages),
                    }
                }

        return {"messages": recent_messages}

    async def _create_summary(self, messages: list[BaseMessage]) -> str:
        """Create a summary of older messages."""
        if not self.llm:
            return "Previous conversation context (summarization unavailable)"

        summary_prompt = (
            "Create a concise summary of this conversation. "
            "Focus on key facts, decisions, and context that would be useful for continuing the conversation. "
            "Format: 'Summary: [key points]'\n\n"
        )

        for msg in messages:
            role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
            summary_prompt += f"{role}: {msg.content}\n"

        summary_prompt += "\nProvide a factual summary:"

        response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
        summary = getattr(response, "content", str(response)).strip()

        if not summary.lower().startswith("summary:"):
            summary = f"Summary: {summary}"

        return summary


class RetrievalNode(WorkflowNode):
    """Node for document retrieval and context gathering."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.retriever = None
        self.max_documents = config.get("max_documents", 5) if config else 5

    def set_retriever(self, retriever: Any) -> None:
        """Set the retriever for document search."""
        self.retriever = retriever

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Retrieve relevant documents for the current query."""
        if not self.retriever:
            return {"retrieval_context": ""}

        messages = context["messages"]

        # Get the last human message
        last_human_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_human_message = msg
                break

        if not last_human_message:
            return {"retrieval_context": ""}

        try:
            docs = await self.retriever.ainvoke(last_human_message.content)
            limited_docs = docs[:self.max_documents] if docs else []

            context_text = "\n\n".join(
                getattr(doc, "page_content", str(doc))
                for doc in limited_docs
            )

            return {
                "retrieval_context": context_text,
                "metadata": {
                    **context.get("metadata", {}),
                    "retrieved_docs": len(limited_docs),
                    "retrieval_query": last_human_message.content,
                }
            }
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return {"retrieval_context": ""}


class ConditionalNode(WorkflowNode):
    """Node for conditional logic and branching."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.condition = config.get("condition", "") if config else ""

    def validate_config(self) -> list[str]:
        """Validate that condition is provided."""
        errors = []
        if not self.condition:
            errors.append("Conditional node must have a condition defined")
        return errors

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Evaluate the conditional expression."""
        try:
            result = await self._evaluate_condition(context)
            return {
                "conditional_results": {
                    **context.get("conditional_results", {}),
                    self.node_id: result,
                },
                "metadata": {
                    **context.get("metadata", {}),
                    f"conditional_{self.node_id}": result,
                }
            }
        except Exception as e:
            logger.error(f"Conditional evaluation failed: {e}")
            return {
                "conditional_results": {
                    **context.get("conditional_results", {}),
                    self.node_id: False,
                },
                "error_state": {
                    **context.get("error_state", {}),
                    f"conditional_error_{self.node_id}": str(e),
                }
            }

    async def _evaluate_condition(self, context: WorkflowNodeContext) -> bool:
        """Evaluate the condition expression."""
        # Simple condition evaluation - can be extended for complex expressions
        condition = self.condition.lower().strip()

        # Check message content conditions
        if "message contains" in condition:
            _, search_term = condition.split("message contains", 1)
            search_term = search_term.strip().strip('"\'')
            last_message = context["messages"][-1] if context["messages"] else None
            if last_message:
                return search_term.lower() in last_message.content.lower()

        # Check variable conditions
        if "variable" in condition and "equals" in condition:
            parts = condition.split()
            if len(parts) >= 3:
                var_name = parts[1]
                expected_value = parts[3]
                actual_value = context.get("variables", {}).get(var_name)
                return str(actual_value) == expected_value

        # Check tool call count conditions
        if "tool_calls" in condition:
            tool_count = context.get("tool_call_count", 0)
            if ">" in condition:
                threshold = int(condition.split(">")[1].strip())
                return tool_count > threshold
            elif "<" in condition:
                threshold = int(condition.split("<")[1].strip())
                return tool_count < threshold

        # Default evaluation - can be extended
        return True


class LoopNode(WorkflowNode):
    """Node for loop iteration and repetitive execution."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.max_iterations = config.get("max_iterations", 10) if config else 10
        self.loop_condition = config.get("condition", "") if config else ""

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Manage loop state and iteration control."""
        loop_state = context.get("loop_state", {})
        current_iteration = loop_state.get(self.node_id, 0)

        # Check termination conditions
        should_continue = current_iteration < self.max_iterations

        if self.loop_condition and should_continue:
            # Evaluate loop condition (similar to conditional node)
            should_continue = await self._evaluate_loop_condition(context)

        return {
            "loop_state": {
                **loop_state,
                self.node_id: current_iteration + 1 if should_continue else current_iteration,
            },
            "metadata": {
                **context.get("metadata", {}),
                f"loop_{self.node_id}_iteration": current_iteration,
                f"loop_{self.node_id}_continue": should_continue,
            }
        }

    async def _evaluate_loop_condition(self, context: WorkflowNodeContext) -> bool:
        """Evaluate loop continuation condition."""
        # Reuse conditional logic
        conditional_node = ConditionalNode("temp", {"condition": self.loop_condition})
        result = await conditional_node._evaluate_condition(context)
        return result


class VariableNode(WorkflowNode):
    """Node for variable manipulation and state management."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.operation = config.get("operation", "set") if config else "set"
        self.variable_name = config.get("variable_name", "") if config else ""
        self.value = config.get("value") if config else None

    def validate_config(self) -> list[str]:
        """Validate variable node configuration."""
        errors = []
        if not self.variable_name:
            errors.append("Variable node must have a variable_name defined")
        if self.operation not in ["set", "get", "append", "increment", "decrement"]:
            errors.append(f"Invalid operation: {self.operation}")
        return errors

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute variable operation."""
        variables = context.get("variables", {})

        try:
            if self.operation == "set":
                variables[self.variable_name] = self.value
            elif self.operation == "get":
                # Get operation just ensures variable exists
                variables.setdefault(self.variable_name, None)
            elif self.operation == "append":
                current = variables.get(self.variable_name, [])
                if isinstance(current, list):
                    current.append(self.value)
                else:
                    variables[self.variable_name] = [current, self.value]
            elif self.operation == "increment":
                current = variables.get(self.variable_name, 0)
                variables[self.variable_name] = (current + 1) if isinstance(current, (int, float)) else 1
            elif self.operation == "decrement":
                current = variables.get(self.variable_name, 0)
                variables[self.variable_name] = (current - 1) if isinstance(current, (int, float)) else -1

            return {
                "variables": variables,
                "metadata": {
                    **context.get("metadata", {}),
                    f"variable_{self.operation}": f"{self.variable_name}={variables.get(self.variable_name)}",
                }
            }
        except Exception as e:
            logger.error(f"Variable operation failed: {e}")
            return {
                "error_state": {
                    **context.get("error_state", {}),
                    f"variable_error_{self.node_id}": str(e),
                }
            }


class ErrorHandlerNode(WorkflowNode):
    """Node for error handling and recovery."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.retry_count = config.get("retry_count", 3) if config else 3
        self.fallback_action = config.get("fallback_action", "continue") if config else "continue"

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Handle errors and implement recovery strategies."""
        error_state = context.get("error_state", {})
        current_retries = error_state.get(f"retries_{self.node_id}", 0)

        # Check if we have errors to handle
        has_errors = any(key.endswith("_error") for key in error_state.keys())

        if has_errors and current_retries < self.retry_count:
            # Increment retry count and continue
            return {
                "error_state": {
                    **error_state,
                    f"retries_{self.node_id}": current_retries + 1,
                },
                "metadata": {
                    **context.get("metadata", {}),
                    f"error_retry_{self.node_id}": current_retries + 1,
                }
            }
        elif has_errors:
            # Max retries reached, apply fallback
            if self.fallback_action == "clear_errors":
                return {
                    "error_state": {},
                    "metadata": {
                        **context.get("metadata", {}),
                        f"error_cleared_{self.node_id}": True,
                    }
                }
            elif self.fallback_action == "stop":
                return {
                    "metadata": {
                        **context.get("metadata", {}),
                        f"error_stop_{self.node_id}": True,
                        "workflow_should_stop": True,
                    }
                }

        # No errors or successful recovery
        return {
            "metadata": {
                **context.get("metadata", {}),
                f"error_handler_{self.node_id}": "no_errors",
            }
        }


class ToolsNode(WorkflowNode):
    """Node for executing multiple tools with enhanced tracking."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.max_tool_calls = config.get("max_tool_calls", 10) if config else 10
        self.tool_timeout_ms = config.get("tool_timeout_ms", 30000) if config else 30000
        self.tools = []

    def set_tools(self, tools: list) -> None:
        """Set the available tools for execution."""
        self.tools = tools

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute tools if the last message has tool calls."""
        from chatter.core.enhanced_tool_executor import EnhancedToolExecutor, ToolExecutionConfig

        messages = context["messages"]
        if not messages:
            return {}

        last_message = messages[-1]

        # Check if we have tool calls in the last message
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return {}

        if not self.tools:
            return {}

        # Create tool execution config
        tool_config = ToolExecutionConfig(
            max_total_calls=self.max_tool_calls,
            timeout_seconds=self.tool_timeout_ms // 1000
        )

        # Create tool executor
        executor = EnhancedToolExecutor(tool_config)

        # Execute tools
        result = await executor.execute_tools(
            context=context,
            tools=self.tools,
            last_message=last_message,
            user_id=context.get("user_id")
        )

        return result


class DelayNode(WorkflowNode):
    """Node for introducing delays in workflow execution."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)
        self.delay_type = config.get("delay_type", "fixed") if config else "fixed"
        self.duration = config.get("duration", 1000) if config else 1000  # milliseconds
        self.max_duration = config.get("max_duration") if config else None

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute delay based on configuration."""
        import random

        if self.delay_type == "fixed":
            delay_ms = self.duration
        elif self.delay_type == "random":
            max_delay = self.max_duration or self.duration * 2
            delay_ms = random.randint(self.duration, max_delay)
        elif self.delay_type == "exponential":
            # Exponential backoff based on retry count
            error_state = context.get("error_state", {})
            retry_count = error_state.get(f"retries_{self.node_id}", 0)
            delay_ms = self.duration * (2 ** retry_count)
            if self.max_duration:
                delay_ms = min(delay_ms, self.max_duration)
        else:
            delay_ms = self.duration

        # Convert to seconds for asyncio.sleep
        delay_seconds = delay_ms / 1000.0

        start_time = time.time()
        await asyncio.sleep(delay_seconds)
        actual_delay = int((time.time() - start_time) * 1000)

        return {
            "metadata": {
                **context.get("metadata", {}),
                f"delay_{self.node_id}": actual_delay,
                "last_delay_ms": actual_delay,
            }
        }


class StartNode(WorkflowNode):
    """Node for workflow entry point."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute start node - initialize workflow context."""
        return {
            "metadata": {
                **context.get("metadata", {}),
                f"start_node_{self.node_id}": True,
                "workflow_started": True,
            }
        }


class EndNode(WorkflowNode):
    """Node for workflow exit point."""

    def __init__(self, node_id: str, config: dict[str, Any] | None = None):
        super().__init__(node_id, config)

    async def execute(self, context: WorkflowNodeContext) -> dict[str, Any]:
        """Execute end node - finalize workflow context."""
        return {
            "metadata": {
                **context.get("metadata", {}),
                f"end_node_{self.node_id}": True,
                "workflow_completed": True,
            }
        }


class WorkflowNodeFactory:
    """Factory for creating workflow nodes of different types."""

    _node_types = {
        "memory": MemoryNode,
        "retrieval": RetrievalNode,
        "conditional": ConditionalNode,
        "loop": LoopNode,
        "variable": VariableNode,
        "error_handler": ErrorHandlerNode,
        "delay": DelayNode,
        "tools": ToolsNode,
        "tool": ToolsNode,  # Alias for tools
        "start": StartNode,
        "end": EndNode,
    }

    @classmethod
    def create_node(cls, node_type: str, node_id: str, config: dict[str, Any] | None = None) -> WorkflowNode:
        """Create a node of the specified type."""
        if node_type not in cls._node_types:
            raise ValueError(f"Unknown node type: {node_type}")

        node_class = cls._node_types[node_type]
        node = node_class(node_id, config)

        # Validate configuration
        errors = node.validate_config()
        if errors:
            raise ValueError(f"Node configuration errors: {', '.join(errors)}")

        return node

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported node types."""
        return list(cls._node_types.keys())

    @classmethod
    def register_node_type(cls, node_type: str, node_class: type[WorkflowNode]) -> None:
        """Register a new node type."""
        cls._node_types[node_type] = node_class
