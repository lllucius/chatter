"""Improved tool calling system with configurable recursion detection.

This module provides enhanced tool execution capabilities with better
recursion detection, progress tracking, and per-tool type limits.
"""

from __future__ import annotations

import time
from collections import Counter, defaultdict
from typing import Any

from langchain_core.messages import AIMessage, ToolMessage

from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ToolExecutionConfig:
    """Configuration for tool execution behavior."""

    def __init__(
        self,
        max_total_calls: int = 10,
        max_calls_per_tool: dict[str, int] | None = None,
        max_consecutive_calls: int = 3,
        progress_window: int = 5,
        enable_recursion_detection: bool = True,
        recursion_strategy: str = "adaptive",  # "strict", "adaptive", "lenient"
        timeout_seconds: int = 30,
    ):
        self.max_total_calls = max_total_calls
        self.max_calls_per_tool = max_calls_per_tool or {}
        self.max_consecutive_calls = max_consecutive_calls
        self.progress_window = progress_window
        self.enable_recursion_detection = enable_recursion_detection
        self.recursion_strategy = recursion_strategy
        self.timeout_seconds = timeout_seconds


class ToolExecutionTracker:
    """Tracks tool execution history and detects patterns."""

    def __init__(self, config: ToolExecutionConfig):
        self.config = config
        self.execution_history: list[dict[str, Any]] = []
        self.tool_call_counts: Counter = Counter()
        self.consecutive_calls: dict[str, int] = defaultdict(int)
        self.last_tool_called: str | None = None

    def record_tool_call(
        self,
        tool_name: str,
        args: dict[str, Any],
        result: str,
        execution_time_ms: int,
        success: bool = True,
    ) -> None:
        """Record a tool execution."""
        execution_record = {
            "tool_name": tool_name,
            "args": args,
            "result": result,
            "execution_time_ms": execution_time_ms,
            "success": success,
            "timestamp": time.time(),
        }

        self.execution_history.append(execution_record)
        self.tool_call_counts[tool_name] += 1

        # Track consecutive calls
        if tool_name == self.last_tool_called:
            self.consecutive_calls[tool_name] += 1
        else:
            self.consecutive_calls.clear()
            self.consecutive_calls[tool_name] = 1

        self.last_tool_called = tool_name

    def should_continue_execution(self) -> tuple[bool, str]:
        """Determine if tool execution should continue."""
        # Check total call limit
        total_calls = sum(self.tool_call_counts.values())
        if total_calls >= self.config.max_total_calls:
            return (
                False,
                f"Maximum total tool calls ({self.config.max_total_calls}) reached",
            )

        # Check per-tool limits
        for tool_name, count in self.tool_call_counts.items():
            max_for_tool = self.config.max_calls_per_tool.get(
                tool_name, self.config.max_total_calls
            )
            if count >= max_for_tool:
                return (
                    False,
                    f"Maximum calls for tool '{tool_name}' ({max_for_tool}) reached",
                )

        # Check consecutive call limits
        for tool_name, count in self.consecutive_calls.items():
            if count >= self.config.max_consecutive_calls:
                return (
                    False,
                    f"Too many consecutive calls to '{tool_name}' ({count})",
                )

        # Check for recursion patterns if enabled
        if self.config.enable_recursion_detection:
            is_recursing, reason = self._detect_recursion()
            if is_recursing:
                return False, f"Recursion detected: {reason}"

        return True, "Continue execution"

    def _detect_recursion(self) -> tuple[bool, str]:
        """Detect recursion patterns in tool execution."""
        if len(self.execution_history) < 3:
            return False, "Insufficient history"

        recent_executions = self.execution_history[
            -self.config.progress_window :
        ]

        if self.config.recursion_strategy == "strict":
            return self._detect_strict_recursion(recent_executions)
        elif self.config.recursion_strategy == "adaptive":
            return self._detect_adaptive_recursion(recent_executions)
        elif self.config.recursion_strategy == "lenient":
            return self._detect_lenient_recursion(recent_executions)
        else:
            return False, "Unknown recursion strategy"

    def _detect_strict_recursion(
        self, executions: list[dict[str, Any]]
    ) -> tuple[bool, str]:
        """Strict recursion detection - any repeated tool with same args."""
        tool_arg_combinations = set()

        for execution in executions:
            tool_name = execution["tool_name"]
            args_str = str(sorted(execution["args"].items()))
            combination = f"{tool_name}:{args_str}"

            if combination in tool_arg_combinations:
                return (
                    True,
                    f"Repeated call to {tool_name} with same arguments",
                )

            tool_arg_combinations.add(combination)

        return False, "No strict recursion detected"

    def _detect_adaptive_recursion(
        self, executions: list[dict[str, Any]]
    ) -> tuple[bool, str]:
        """Adaptive recursion detection - considers progress and patterns."""
        if len(executions) < 3:
            return False, "Insufficient history for adaptive detection"

        # Check for lack of progress (same tool, same results)
        recent_tools = [e["tool_name"] for e in executions[-3:]]
        recent_results = [e["result"] for e in executions[-3:]]

        # If same tool called multiple times with same result
        if (
            len(set(recent_tools)) == 1
            and len(set(recent_results)) == 1
        ):
            return (
                True,
                f"No progress: {recent_tools[0]} returning same result repeatedly",
            )

        # Check for alternating patterns (A -> B -> A -> B)
        if len(executions) >= 4:
            last_4_tools = [e["tool_name"] for e in executions[-4:]]
            if (
                last_4_tools[0] == last_4_tools[2]
                and last_4_tools[1] == last_4_tools[3]
            ):
                return (
                    True,
                    f"Alternating pattern detected: {last_4_tools[0]} <-> {last_4_tools[1]}",
                )

        # Check for error loops
        recent_errors = [e for e in executions[-3:] if not e["success"]]
        if len(recent_errors) >= 2:
            error_tools = [e["tool_name"] for e in recent_errors]
            if len(set(error_tools)) == 1:
                return (
                    True,
                    f"Error loop detected for tool: {error_tools[0]}",
                )

        return False, "No adaptive recursion detected"

    def _detect_lenient_recursion(
        self, executions: list[dict[str, Any]]
    ) -> tuple[bool, str]:
        """Lenient recursion detection - only obvious infinite loops."""
        if len(executions) < 5:
            return False, "Insufficient history for lenient detection"

        # Only flag if same tool called 5+ times in a row with no variation
        recent_tools = [e["tool_name"] for e in executions[-5:]]
        recent_results = [e["result"] for e in executions[-5:]]

        if (
            len(set(recent_tools)) == 1
            and len(set(recent_results)) <= 2  # Allow slight variation
            and all(not e["success"] for e in executions[-3:])
        ):  # All recent calls failed
            return (
                True,
                f"Clear infinite loop: {recent_tools[0]} failing repeatedly",
            )

        return False, "No lenient recursion detected"

    def get_execution_summary(self) -> dict[str, Any]:
        """Get a summary of tool execution history."""
        total_calls = sum(self.tool_call_counts.values())
        successful_calls = sum(
            1 for e in self.execution_history if e["success"]
        )
        failed_calls = total_calls - successful_calls

        avg_execution_time = 0
        if self.execution_history:
            avg_execution_time = sum(
                e["execution_time_ms"] for e in self.execution_history
            ) / len(self.execution_history)

        return {
            "total_calls": total_calls,
            "successful_calls": successful_calls,
            "failed_calls": failed_calls,
            "unique_tools_used": len(self.tool_call_counts),
            "tool_call_counts": dict(self.tool_call_counts),
            "avg_execution_time_ms": round(avg_execution_time, 2),
            "execution_history_length": len(self.execution_history),
        }


class EnhancedToolExecutor:
    """Enhanced tool executor with improved recursion detection and progress tracking."""

    def __init__(self, config: ToolExecutionConfig | None = None):
        self.config = config or ToolExecutionConfig()

    async def execute_tools(
        self,
        context: WorkflowNodeContext,
        tools: list[Any],
        last_message: AIMessage,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute tools with enhanced tracking and recursion detection."""
        if (
            not tools
            or not hasattr(last_message, "tool_calls")
            or not last_message.tool_calls
        ):
            return {}

        # Get or create tracker from context
        tracker = self._get_or_create_tracker(context)

        # Check if we should continue execution
        should_continue, reason = tracker.should_continue_execution()
        if not should_continue:
            logger.warning(f"Tool execution stopped: {reason}")
            return self._create_finalization_response(
                context, tracker, reason
            )

        tool_messages = []
        execution_results = []

        for tool_call in last_message.tool_calls:
            try:
                result = await self._execute_single_tool(
                    tool_call, tools, tracker, user_id
                )
                tool_messages.append(result["message"])
                execution_results.append(result["execution_info"])

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                error_message = ToolMessage(
                    content=f"Error executing tool: {str(e)}",
                    tool_call_id=tool_call.get("id", ""),
                )
                tool_messages.append(error_message)

                # Record the error
                tracker.record_tool_call(
                    tool_name=tool_call.get("name", "unknown"),
                    args=tool_call.get("args", {}),
                    result=f"Error: {str(e)}",
                    execution_time_ms=0,
                    success=False,
                )

        # Update context with tracker and execution info
        updated_metadata = {
            **context.get("metadata", {}),
            "tool_execution_summary": tracker.get_execution_summary(),
            "recent_tool_results": [
                r["result"] for r in execution_results[-3:]
            ],
        }

        return {
            "messages": tool_messages,
            "tool_call_count": tracker.get_execution_summary()[
                "total_calls"
            ],
            "metadata": updated_metadata,
            "_tool_tracker": tracker,  # Store for next iteration
        }

    async def _execute_single_tool(
        self,
        tool_call: dict[str, Any],
        tools: list[Any],
        tracker: ToolExecutionTracker,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a single tool call with timing and tracking."""
        tool_name = tool_call.get("name", "")
        tool_args = tool_call.get("args", {})
        tool_id = tool_call.get("id", "")

        # Find the tool
        tool_obj = self._find_tool(tool_name, tools)
        if not tool_obj:
            error_msg = f"Tool '{tool_name}' not found"
            tracker.record_tool_call(
                tool_name, tool_args, error_msg, 0, False
            )
            return {
                "message": ToolMessage(
                    content=error_msg, tool_call_id=tool_id
                ),
                "execution_info": {
                    "tool_name": tool_name,
                    "result": error_msg,
                    "success": False,
                },
            }

        # Execute with timing
        start_time = time.time()
        try:
            # Add timeout if configured
            if self.config.timeout_seconds > 0:
                import asyncio

                result = await asyncio.wait_for(
                    self._invoke_tool(tool_obj, tool_args),
                    timeout=self.config.timeout_seconds,
                )
            else:
                result = await self._invoke_tool(tool_obj, tool_args)

            execution_time_ms = int((time.time() - start_time) * 1000)
            result_str = (
                str(result)
                if result is not None
                else f"Tool {tool_name} completed"
            )

            # Record successful execution
            tracker.record_tool_call(
                tool_name,
                tool_args,
                result_str,
                execution_time_ms,
                True,
            )

            return {
                "message": ToolMessage(
                    content=result_str, tool_call_id=tool_id
                ),
                "execution_info": {
                    "tool_name": tool_name,
                    "result": result_str,
                    "execution_time_ms": execution_time_ms,
                    "success": True,
                },
            }

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            error_msg = f"Tool execution failed: {str(e)}"

            # Record failed execution
            tracker.record_tool_call(
                tool_name,
                tool_args,
                error_msg,
                execution_time_ms,
                False,
            )

            return {
                "message": ToolMessage(
                    content=error_msg, tool_call_id=tool_id
                ),
                "execution_info": {
                    "tool_name": tool_name,
                    "result": error_msg,
                    "execution_time_ms": execution_time_ms,
                    "success": False,
                },
            }

    async def _invoke_tool(
        self, tool_obj: Any, tool_args: dict[str, Any]
    ) -> Any:
        """Invoke tool with proper async handling."""
        if hasattr(tool_obj, "ainvoke"):
            return await tool_obj.ainvoke(tool_args)
        elif hasattr(tool_obj, "invoke"):
            return tool_obj.invoke(tool_args)
        elif callable(tool_obj):
            return tool_obj(tool_args)
        else:
            raise RuntimeError("Tool is not callable")

    def _find_tool(
        self, tool_name: str, tools: list[Any]
    ) -> Any | None:
        """Find a tool by name in the tools list."""
        for tool in tools:
            t_name = (
                getattr(tool, "name", None)
                or getattr(tool, "name_", None)
                or getattr(tool, "__name__", None)
            )
            if t_name == tool_name:
                return tool
        return None

    def _get_or_create_tracker(
        self, context: WorkflowNodeContext
    ) -> ToolExecutionTracker:
        """Get existing tracker from context or create a new one."""
        existing_tracker = context.get("metadata", {}).get(
            "_tool_tracker"
        )
        if existing_tracker and isinstance(
            existing_tracker, ToolExecutionTracker
        ):
            return existing_tracker
        return ToolExecutionTracker(self.config)

    def _create_finalization_response(
        self,
        context: WorkflowNodeContext,
        tracker: ToolExecutionTracker,
        reason: str,
    ) -> dict[str, Any]:
        """Create a finalization response when tool execution should stop."""
        summary = tracker.get_execution_summary()

        finalization_content = (
            f"I've completed my tool usage ({summary['total_calls']} tool calls) "
            f"and have gathered the information needed to help with your request. "
            f"Reason for completion: {reason}"
        )

        return {
            "messages": [AIMessage(content=finalization_content)],
            "tool_call_count": summary["total_calls"],
            "metadata": {
                **context.get("metadata", {}),
                "tool_execution_finalized": True,
                "finalization_reason": reason,
                "tool_execution_summary": summary,
            },
        }
