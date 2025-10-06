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
    conditional_results: dict[
        str, bool
    ]  # For conditional evaluation results
    execution_history: list[
        dict[str, Any]
    ]  # For debugging and progress tracking
    usage_metadata: dict[str, Any]  # For token usage tracking


class WorkflowNode(ABC):
    """Abstract base class for all workflow nodes."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        self.node_id = node_id
        self.config = config or {}

    @abstractmethod
    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute the node logic and return state updates."""
        pass

    def validate_config(self) -> list[str]:
        """Validate node configuration and return any errors."""
        return []


class ConfigParser:
    """Shared configuration parsing utilities for workflow nodes."""

    @staticmethod
    def parse_model_config(config: dict[str, Any]) -> dict[str, Any]:
        """Parse and standardize model configuration."""
        return {
            "provider": config.get("provider", "openai"),
            "model": config.get("model", "gpt-4"),
            "temperature": config.get("temperature", 0.7),
            "max_tokens": config.get("max_tokens", 1000),
        }

    @staticmethod
    def parse_retry_config(config: dict[str, Any]) -> dict[str, int]:
        """Parse retry configuration."""
        return {
            "max_retries": config.get("max_retries", 3),
            "retry_delay": config.get("retry_delay", 1),
        }

    @staticmethod
    def parse_timeout_config(config: dict[str, Any]) -> int:
        """Parse timeout configuration."""
        return config.get("timeout", 30)

    @staticmethod
    def validate_enum_value(
        value: str, valid_values: list[str], field_name: str
    ) -> str | None:
        """Validate enum value and return error if invalid."""
        if value not in valid_values:
            return (
                f"{field_name} must be one of {valid_values}, got: {value}"
            )
        return None


class BaseWorkflowNode(WorkflowNode):
    """Enhanced base class with shared functionality for all workflow nodes."""

    def __init__(
        self,
        node_id: str,
        config: dict[str, Any] | None = None,
        node_type: str | None = None,
    ):
        super().__init__(node_id, config)
        self.node_type = node_type or self.__class__.__name__

    def _validate_required_fields(
        self, fields: list[str]
    ) -> list[str]:
        """Validate that required fields are present in config."""
        errors = []
        for field in fields:
            if field not in self.config:
                errors.append(
                    f"{self.node_type} requires '{field}' in config"
                )
        return errors

    def _validate_field_types(
        self, field_types: dict[str, type]
    ) -> list[str]:
        """Validate field types in config."""
        errors = []
        for field, expected_type in field_types.items():
            if field in self.config:
                value = self.config[field]
                if not isinstance(value, expected_type):
                    errors.append(
                        f"{self.node_type} field '{field}' must be {expected_type.__name__}, got {type(value).__name__}"
                    )
        return errors

    def _get_config(self, key: str, default: Any = None) -> Any:
        """Safely get config value with default."""
        return self.config.get(key, default)

    def _get_required_config(self, key: str) -> Any:
        """Get required config value, raises KeyError if not found."""
        if key not in self.config:
            raise KeyError(
                f"{self.node_type} requires '{key}' in config"
            )
        return self.config[key]

    def _create_error_result(self, error_msg: str) -> dict[str, Any]:
        """Create standardized error result."""
        return {
            "error_state": {
                "has_error": True,
                "error_message": error_msg,
                "error_node": self.node_id,
            }
        }


class MemoryNode(BaseWorkflowNode):
    """Node for memory management and conversation summarization."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "MemoryNode")
        self.memory_window = self._get_config("memory_window", 10)
        self.llm: BaseChatModel | None = None
    
    def validate_config(self) -> list[str]:
        """Validate memory node configuration."""
        errors = []
        errors.extend(self._validate_field_types({"memory_window": int}))
        return errors

    def set_llm(self, llm: BaseChatModel) -> None:
        """Set the LLM for summarization."""
        self.llm = llm

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Manage memory by summarizing older messages."""
        messages = list(context["messages"])

        if len(messages) <= self.memory_window:
            return {}

        recent_messages = messages[-self.memory_window :]
        older_messages = messages[: -self.memory_window]

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
                    },
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
                    },
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
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            summary_prompt += f"{role}: {msg.content}\n"

        summary_prompt += "\nProvide a factual summary:"

        response = await self.llm.ainvoke(
            [HumanMessage(content=summary_prompt)]
        )
        summary = getattr(response, "content", str(response)).strip()

        if not summary.lower().startswith("summary:"):
            summary = f"Summary: {summary}"

        return summary


class RetrievalNode(BaseWorkflowNode):
    """Node for document retrieval and context gathering."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "RetrievalNode")
        self.retriever = None
        self.max_documents = self._get_config("max_documents", 5)
    
    def validate_config(self) -> list[str]:
        """Validate retrieval node configuration."""
        errors = []
        errors.extend(self._validate_field_types({"max_documents": int}))
        return errors

    def set_retriever(self, retriever: Any) -> None:
        """Set the retriever for document search."""
        self.retriever = retriever
        logger.info(
            f"Retriever set on RetrievalNode {self.node_id}",
            has_retriever=retriever is not None,
        )

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Retrieve relevant documents for the current query."""
        logger.info(
            f"RetrievalNode {self.node_id} executing",
            has_retriever=self.retriever is not None,
        )

        if not self.retriever:
            logger.warning(
                f"RetrievalNode {self.node_id} has no retriever, returning empty context"
            )
            return {"retrieval_context": ""}

        messages = context["messages"]

        # Get the last human message
        last_human_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_human_message = msg
                break

        if not last_human_message:
            logger.warning(
                f"RetrievalNode {self.node_id} found no human message"
            )
            return {"retrieval_context": ""}

        logger.info(
            f"RetrievalNode {self.node_id} retrieving for query",
            query=last_human_message.content[:100],
        )

        try:
            docs = await self.retriever.ainvoke(
                last_human_message.content
            )
            limited_docs = docs[: self.max_documents] if docs else []

            logger.info(
                f"RetrievalNode {self.node_id} retrieved documents",
                doc_count=len(limited_docs),
                max_documents=self.max_documents,
            )

            context_text = "\n\n".join(
                getattr(doc, "page_content", str(doc))
                for doc in limited_docs
            )

            logger.info(
                f"RetrievalNode {self.node_id} generated context",
                context_length=len(context_text),
            )

            return {
                "retrieval_context": context_text,
                "metadata": {
                    **context.get("metadata", {}),
                    "retrieved_docs": len(limited_docs),
                    "retrieval_query": last_human_message.content,
                },
            }
        except Exception as e:
            logger.error(
                f"Retrieval failed in RetrievalNode {self.node_id}: {e}"
            )
            return {"retrieval_context": ""}


class ConditionalNode(BaseWorkflowNode):
    """Node for conditional logic and branching."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "ConditionalNode")
        self.condition = self._get_config("condition", "")

    def validate_config(self) -> list[str]:
        """Validate that condition is provided."""
        return self._validate_required_fields(["condition"])

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
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
                },
            }
        except Exception as e:
            logger.error(f"Conditional evaluation failed: {e}")
            return self._create_error_result(
                f"Conditional evaluation failed: {str(e)}"
            )

    async def _evaluate_condition(
        self, context: WorkflowNodeContext
    ) -> bool:
        """Evaluate the condition expression."""
        # Simple condition evaluation - can be extended for complex expressions
        condition = self.condition.lower().strip()

        # Check message content conditions
        if "message contains" in condition:
            _, search_term = condition.split("message contains", 1)
            search_term = search_term.strip().strip('"\'')
            last_message = (
                context["messages"][-1] if context["messages"] else None
            )
            if last_message:
                return (
                    search_term.lower() in last_message.content.lower()
                )

        # Handle capability-specific variable conditions BEFORE general tool_calls check
        if "variable" in condition:
            # Handle "variable max_tool_calls" pattern with comparison operators
            if " max_tool_calls" in condition:
                variables = context.get("variables", {})
                capabilities = variables.get("capabilities", {})
                max_calls = capabilities.get("max_tool_calls", 10)
                tool_count = context.get("tool_call_count", 0)
                if ">=" in condition:
                    return tool_count >= max_calls
                elif ">" in condition:
                    return tool_count > max_calls
                elif "<=" in condition:
                    return tool_count <= max_calls
                elif "<" in condition:
                    return tool_count < max_calls
            # Handle general variable equals conditions
            elif "equals" in condition:
                parts = condition.split()
                if len(parts) >= 3:
                    var_name = parts[1]
                    expected_value = parts[3]
                    actual_value = context.get("variables", {}).get(
                        var_name
                    )
                    return str(actual_value) == expected_value

        # Check tool call count conditions (with literal numbers)
        if "tool_calls" in condition:
            tool_count = context.get("tool_call_count", 0)
            if ">=" in condition:
                threshold = int(condition.split(">=")[1].strip())
                return tool_count >= threshold
            elif ">" in condition:
                threshold = int(condition.split(">")[1].strip())
                return tool_count > threshold
            elif "<=" in condition:
                threshold = int(condition.split("<=")[1].strip())
                return tool_count <= threshold
            elif "<" in condition:
                threshold = int(condition.split("<")[1].strip())
                return tool_count < threshold

        # Default evaluation - can be extended
        return True


class LoopNode(BaseWorkflowNode):
    """Node for loop iteration and repetitive execution."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "LoopNode")
        self.max_iterations = self._get_config("max_iterations", 10)
        self.loop_condition = self._get_config("condition", "")
    
    def validate_config(self) -> list[str]:
        """Validate loop node configuration."""
        return self._validate_field_types({"max_iterations": int})

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Manage loop state and iteration control."""
        loop_state = context.get("loop_state", {})
        current_iteration = loop_state.get(self.node_id, 0)

        # Check termination conditions
        should_continue = current_iteration < self.max_iterations

        if self.loop_condition and should_continue:
            # Evaluate loop condition (similar to conditional node)
            should_continue = await self._evaluate_loop_condition(
                context
            )

        return {
            "loop_state": {
                **loop_state,
                self.node_id: (
                    current_iteration + 1
                    if should_continue
                    else current_iteration
                ),
            },
            "metadata": {
                **context.get("metadata", {}),
                f"loop_{self.node_id}_iteration": current_iteration,
                f"loop_{self.node_id}_continue": should_continue,
            },
        }

    async def _evaluate_loop_condition(
        self, context: WorkflowNodeContext
    ) -> bool:
        """Evaluate loop continuation condition."""
        # Reuse conditional logic
        conditional_node = ConditionalNode(
            "temp", {"condition": self.loop_condition}
        )
        result = await conditional_node._evaluate_condition(context)
        return result


class VariableNode(BaseWorkflowNode):
    """Node for variable manipulation and state management."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "VariableNode")
        self.operation = self._get_config("operation", "set")
        
        # Support both snake_case and camelCase for backward compatibility
        self.variable_name = (
            self._get_config("variable_name", "") or 
            self._get_config("variableName", "") or 
            f"var_{node_id}"
        )
        self.value = self._get_config("value", None)

    def validate_config(self) -> list[str]:
        """Validate variable node configuration."""
        errors = []
        valid_operations = ["set", "get", "append", "increment", "decrement"]
        if self.operation not in valid_operations:
            errors.append(
                f"Invalid operation: {self.operation}. Must be one of {valid_operations}"
            )
        
        # Log warning if variable_name was auto-generated
        if self.variable_name.startswith(f"var_{self.node_id}"):
            logger.warning(
                f"Variable node {self.node_id} using auto-generated variable name: {self.variable_name}. "
                "Consider providing an explicit 'variable_name' in the node configuration."
            )
        return errors

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute variable operation."""
        variables = context.get("variables", {})

        try:
            if self.operation == "set":
                variables[self.variable_name] = self.value
            elif self.operation == "get":
                variables.setdefault(self.variable_name, None)
            elif self.operation == "append":
                current = variables.get(self.variable_name, [])
                if isinstance(current, list):
                    current.append(self.value)
                else:
                    variables[self.variable_name] = [current, self.value]
            elif self.operation == "increment":
                current = variables.get(self.variable_name, 0)
                variables[self.variable_name] = (
                    (current + 1) if isinstance(current, (int, float)) else 1
                )
            elif self.operation == "decrement":
                current = variables.get(self.variable_name, 0)
                variables[self.variable_name] = (
                    (current - 1) if isinstance(current, (int, float)) else -1
                )

            return {
                "variables": variables,
                "metadata": {
                    **context.get("metadata", {}),
                    f"variable_{self.operation}": f"{self.variable_name}={variables.get(self.variable_name)}",
                },
            }
        except Exception as e:
            logger.error(f"Variable operation failed: {e}")
            return self._create_error_result(f"Variable operation failed: {str(e)}")


class ErrorHandlerNode(BaseWorkflowNode):
    """Node for error handling and recovery."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "ErrorHandlerNode")
        self.retry_count = self._get_config("retry_count", 3)
        self.fallback_action = self._get_config("fallback_action", "continue")
    
    def validate_config(self) -> list[str]:
        """Validate error handler node configuration."""
        errors = []
        errors.extend(self._validate_field_types({"retry_count": int}))
        valid_actions = ["continue", "clear_errors", "stop"]
        if self.fallback_action not in valid_actions:
            errors.append(
                f"fallback_action must be one of {valid_actions}, got: {self.fallback_action}"
            )
        return errors

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Handle errors and implement recovery strategies."""
        error_state = context.get("error_state", {})
        current_retries = error_state.get(f"retries_{self.node_id}", 0)

        # Check if we have errors to handle
        has_errors = any(
            key.endswith("_error") for key in error_state.keys()
        )

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
                },
            }
        elif has_errors:
            # Max retries reached, apply fallback
            if self.fallback_action == "clear_errors":
                return {
                    "error_state": {},
                    "metadata": {
                        **context.get("metadata", {}),
                        f"error_cleared_{self.node_id}": True,
                    },
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


class ToolsNode(BaseWorkflowNode):
    """Node for executing multiple tools with enhanced tracking."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "ToolsNode")
        self.max_tool_calls = self._get_config("max_tool_calls", 10)
        self.tool_timeout_ms = self._get_config("tool_timeout_ms", 30000)
        self.tools = []
    
    def validate_config(self) -> list[str]:
        """Validate tools node configuration."""
        return self._validate_field_types({
            "max_tool_calls": int,
            "tool_timeout_ms": int
        })

    def set_tools(self, tools: list) -> None:
        """Set the available tools for execution."""
        self.tools = tools

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute tools if the last message has tool calls."""
        from chatter.core.enhanced_tool_executor import (
            EnhancedToolExecutor,
            ToolExecutionConfig,
        )

        messages = context["messages"]
        if not messages:
            return {}

        last_message = messages[-1]

        # Check if we have tool calls in the last message
        if (
            not hasattr(last_message, "tool_calls")
            or not last_message.tool_calls
        ):
            return {}

        if not self.tools:
            return {}

        # Create tool execution config
        tool_config = ToolExecutionConfig(
            max_total_calls=self.max_tool_calls,
            timeout_seconds=self.tool_timeout_ms // 1000,
        )

        # Create tool executor
        executor = EnhancedToolExecutor(tool_config)

        # Execute tools
        result = await executor.execute_tools(
            context=context,
            tools=self.tools,
            last_message=last_message,
            user_id=context.get("user_id"),
        )

        return result


class DelayNode(BaseWorkflowNode):
    """Node for introducing delays in workflow execution."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "DelayNode")
        self.delay_type = self._get_config("delay_type", "fixed")
        self.duration = self._get_config("duration", 1000)  # milliseconds
        self.max_duration = self._get_config("max_duration", None)
    
    def validate_config(self) -> list[str]:
        """Validate delay node configuration."""
        errors = []
        errors.extend(self._validate_field_types({
            "duration": int,
            "max_duration": (int, type(None))
        }))
        valid_types = ["fixed", "random", "exponential"]
        if self.delay_type not in valid_types:
            errors.append(
                f"delay_type must be one of {valid_types}, got: {self.delay_type}"
            )
        return errors

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
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
            delay_ms = self.duration * (2**retry_count)
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


class StartNode(BaseWorkflowNode):
    """Node for workflow entry point."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "StartNode")

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute start node - initialize workflow context."""
        return {
            "metadata": {
                **context.get("metadata", {}),
                f"start_node_{self.node_id}": True,
                "workflow_started": True,
            }
        }


class EndNode(BaseWorkflowNode):
    """Node for workflow exit point."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config, "EndNode")

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute end node - finalize workflow context."""
        return {
            "metadata": {
                **context.get("metadata", {}),
                f"end_node_{self.node_id}": True,
                "workflow_completed": True,
            }
        }


class ModelNode(BaseWorkflowNode):
    """Node for language model processing with LLM integration."""

    def __init__(
        self, node_id: str, config: dict[str, Any] | None = None
    ):
        super().__init__(node_id, config)
        self.llm: BaseChatModel | None = None
        self.tools: list[Any] | None = None
        self.system_message = (
            config.get("system_message") if config else None
        )
        self.temperature = config.get("temperature") if config else None
        self.max_tokens = config.get("max_tokens") if config else None

    def set_llm(self, llm: BaseChatModel) -> None:
        """Set the LLM for this node."""
        self.llm = llm

    def set_tools(self, tools: list[Any] | None) -> None:
        """Set the tools for this node."""
        self.tools = tools

    async def execute(
        self, context: WorkflowNodeContext
    ) -> dict[str, Any]:
        """Execute LLM call with context and extract usage metadata."""
        if not self.llm:
            return {
                "messages": [
                    HumanMessage(
                        content="Error: No LLM configured for model node"
                    )
                ],
                "error_state": {
                    **context.get("error_state", {}),
                    f"model_error_{self.node_id}": "No LLM configured",
                },
            }

        messages = list(context["messages"])
        try:
            # Apply configuration if provided
            llm_kwargs = {}
            if self.temperature is not None:
                llm_kwargs["temperature"] = self.temperature
            if self.max_tokens is not None:
                llm_kwargs["max_tokens"] = self.max_tokens

            # Use tools if available
            llm_to_use = (
                self.llm.bind_tools(self.tools)
                if self.tools
                else self.llm
            )
            response = await llm_to_use.ainvoke(messages, **llm_kwargs)

            # Extract usage metadata from response
            usage_metadata = {}
            if hasattr(response, 'usage_metadata'):
                usage_metadata = response.usage_metadata or {}
            elif hasattr(response, 'response_metadata'):
                usage_metadata = response.response_metadata.get(
                    'token_usage', {}
                )

            # Convert usage_metadata to dict if it's not already
            if not isinstance(usage_metadata, dict):
                usage_metadata = {
                    'input_tokens': getattr(
                        usage_metadata, 'input_tokens', None
                    ),
                    'output_tokens': getattr(
                        usage_metadata, 'output_tokens', None
                    ),
                    'total_tokens': getattr(
                        usage_metadata, 'total_tokens', None
                    ),
                }

            return {
                "messages": [response],
                "usage_metadata": usage_metadata,
            }
        except Exception as e:
            logger.error(f"Model node execution failed: {e}")
            return {
                "messages": [
                    HumanMessage(
                        content=f"I encountered an error: {str(e)}"
                    )
                ],
                "error_state": {
                    **context.get("error_state", {}),
                    f"model_error_{self.node_id}": str(e),
                },
            }


class WorkflowNodeFactory:
    """Factory for creating workflow nodes of different types."""

    _node_types = {
        # Core workflow nodes
        "memory": MemoryNode,
        "retrieval": RetrievalNode,
        "conditional": ConditionalNode,
        "loop": LoopNode,
        "variable": VariableNode,
        "error_handler": ErrorHandlerNode,
        "delay": DelayNode,
        # Tool execution nodes
        "tools": ToolsNode,
        "tool": ToolsNode,  # Alias for tools
        "execute_tools": ToolsNode,  # Alias for tools
        # Workflow control nodes
        "start": StartNode,
        "end": EndNode,
        # Language model nodes (all aliases point to ModelNode)
        "model": ModelNode,
        "llm": ModelNode,
        "call_model": ModelNode,
    }

    # Registry for custom node creators (used by WorkflowGraphBuilder)
    _custom_creators = {}

    @classmethod
    def create_node(
        cls,
        node_type: str,
        node_id: str,
        config: dict[str, Any] | None = None,
        **kwargs,
    ) -> WorkflowNode:
        """Create a node of the specified type."""
        if node_type not in cls._node_types:
            raise ValueError(f"Unknown node type: {node_type}")

        # Check if there's a custom creator registered for this node type
        if node_type in cls._custom_creators:
            return cls._custom_creators[node_type](
                node_id, config, **kwargs
            )

        # Use standard factory creation
        node_class = cls._node_types[node_type]
        node = node_class(node_id, config)

        # Validate configuration
        errors = node.validate_config()
        if errors:
            raise ValueError(
                f"Node configuration errors: {', '.join(errors)}"
            )

        return node

    @classmethod
    def register_custom_creator(cls, node_type: str, creator_func):
        """Register a custom creator function for a node type."""
        cls._custom_creators[node_type] = creator_func

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported node types."""
        return list(cls._node_types.keys())

    @classmethod
    def register_node_type(
        cls, node_type: str, node_class: type[WorkflowNode]
    ) -> None:
        """Register a new node type."""
        cls._node_types[node_type] = node_class
