"""Workflow execution service using strategy pattern.

This replaces the monolithic WorkflowExecutionService with a clean
orchestration layer that delegates to focused executor classes.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import (
    get_template_manager_with_session,
)
from chatter.core.workflow_executors import WorkflowExecutorFactory
from chatter.core.workflow_limits import (
    WorkflowLimits,
    workflow_limit_manager,
)
from chatter.core.workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.models.conversation import Conversation, Message
from chatter.models.base import generate_ulid
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionService:
    """Service for executing chat workflows using strategy pattern."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session: AsyncSession,
    ):
        """Initialize simplified workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = get_template_manager_with_session(
            session
        )
        self.limit_manager = workflow_limit_manager
        self.executor_factory = WorkflowExecutorFactory()

    async def execute_workflow(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a workflow for a chat request.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID
            user_id: User ID for resource tracking
            limits: Custom workflow limits (uses defaults if None)

        Returns:
            Tuple of (response_message, usage_info)

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        workflow_type = chat_request.workflow_type or chat_request.workflow or "plain"

        # Get appropriate executor
        executor = self.executor_factory.create_executor(
            workflow_type,
            self.llm_service,
            self.message_service,
            self.template_manager,
        )

        # Execute workflow
        return await executor.execute(
            conversation, chat_request, correlation_id, user_id, limits
        )

    async def execute_workflow_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits: WorkflowLimits | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a workflow with streaming for a chat request.

        Args:
            conversation: Conversation context
            chat_request: Chat request
            correlation_id: Request correlation ID
            user_id: User ID for resource tracking
            limits: Custom workflow limits (uses defaults if None)

        Yields:
            StreamingChatChunk: Streaming response chunks

        Raises:
            WorkflowExecutionError: If workflow execution fails
        """
        workflow_type = chat_request.workflow_type or chat_request.workflow or "plain"

        # Get appropriate executor
        executor = self.executor_factory.create_executor(
            workflow_type,
            self.llm_service,
            self.message_service,
            self.template_manager,
        )

        # Execute workflow with streaming
        async for chunk in executor.execute_streaming(
            conversation, chat_request, correlation_id, user_id, limits
        ):
            yield chunk

    async def get_service_stats(self) -> dict[str, Any]:
        """Get comprehensive service statistics.

        Returns:
            Dictionary containing service performance and usage stats
        """
        return {
            "supported_workflow_types": self.executor_factory.get_supported_types(),
            "performance_monitor": performance_monitor.get_performance_stats(),
            "cache_stats": (
                await workflow_cache.get_stats()
                if hasattr(workflow_cache, "get_stats")
                else {}
            ),
            "template_stats": self.template_manager.get_stats(),
            "limit_manager_stats": (
                self.limit_manager.get_stats()
                if hasattr(self.limit_manager, "get_stats")
                else {}
            ),
        }

    async def validate_workflow_request(
        self, chat_request: ChatRequest
    ) -> dict[str, Any]:
        """Validate a workflow request.

        Args:
            chat_request: Chat request to validate

        Returns:
            Dictionary with validation results
        """
        workflow_type = chat_request.workflow_type or chat_request.workflow or "plain"

        # Check if workflow type is supported
        supported_types = self.executor_factory.get_supported_types()
        if workflow_type not in supported_types:
            return {
                "valid": False,
                "errors": [
                    f"Unsupported workflow type: {workflow_type}"
                ],
                "supported_types": supported_types,
            }

        return {
            "valid": True,
            "workflow_type": workflow_type,
            "supported_types": supported_types,
        }

    async def get_workflow_capabilities(
        self, workflow_type: str
    ) -> dict[str, Any]:
        """Get capabilities for a specific workflow type.

        Args:
            workflow_type: Type of workflow to check

        Returns:
            Dictionary with workflow capabilities
        """
        supported_types = self.executor_factory.get_supported_types()

        if workflow_type not in supported_types:
            return {
                "error": f"Unsupported workflow type: {workflow_type}"
            }

        # Basic capabilities mapping
        capabilities = {
            "plain": {
                "requires_tools": False,
                "requires_retriever": False,
                "supports_streaming": True,
                "memory_window": 20,
            },
            "rag": {
                "requires_tools": False,
                "requires_retriever": True,
                "supports_streaming": True,
                "memory_window": 30,
                "max_documents": 10,
            },
            "tools": {
                "requires_tools": True,
                "requires_retriever": False,
                "supports_streaming": True,
                "memory_window": 100,
                "max_tool_calls": 10,
            },
            "full": {
                "requires_tools": True,
                "requires_retriever": True,
                "supports_streaming": True,
                "memory_window": 50,
                "max_tool_calls": 5,
                "max_documents": 10,
            },
        }

        return capabilities.get(workflow_type, {})

    async def execute_workflow_definition(
        self,
        workflow_definition: Any,  # WorkflowDefinition object
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a node-based workflow definition.

        Args:
            workflow_definition: Workflow definition with nodes and edges
            input_data: Input data for the workflow
            context: Optional execution context

        Returns:
            Dictionary with execution results
        """
        execution_id = generate_ulid()
        started_at = datetime.utcnow()
        steps: list[dict[str, Any]] = []
        workflow_context = context or {}
        workflow_variables = {}

        try:
            # Build execution graph
            nodes = {
                node["id"]: node for node in workflow_definition.nodes
            }
            edges_by_source = {}
            for edge in workflow_definition.edges:
                source = edge["source"]
                if source not in edges_by_source:
                    edges_by_source[source] = []
                edges_by_source[source].append(edge)

            # Find start node
            start_nodes = [
                node
                for node in workflow_definition.nodes
                if node.get("data", {}).get("nodeType") == "start"
            ]

            if not start_nodes:
                raise ValueError("No start node found in workflow")

            # Execute workflow
            current_data = input_data.copy()

            for start_node in start_nodes:
                result = await self._execute_node_graph(
                    start_node["id"],
                    nodes,
                    edges_by_source,
                    current_data,
                    workflow_context,
                    workflow_variables,
                    steps,
                )
                current_data.update(result)

            completed_at = datetime.utcnow()
            total_time = int(
                (completed_at - started_at).total_seconds() * 1000
            )

            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": current_data,
                "steps": steps,
                "total_execution_time_ms": total_time,
                "error": None,
                "started_at": started_at,
                "completed_at": completed_at,
            }

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            completed_at = datetime.utcnow()
            total_time = int(
                (completed_at - started_at).total_seconds() * 1000
            )

            return {
                "execution_id": execution_id,
                "status": "failed",
                "result": None,
                "steps": steps,
                "total_execution_time_ms": total_time,
                "error": str(e),
                "started_at": started_at,
                "completed_at": completed_at,
            }

    async def _execute_node_graph(
        self,
        node_id: str,
        nodes: dict[str, dict[str, Any]],
        edges_by_source: dict[str, list[dict[str, Any]]],
        data: dict[str, Any],
        context: dict[str, Any],
        variables: dict[str, Any],
        steps: list[dict[str, Any]],
        visited: set | None = None,
    ) -> dict[str, Any]:
        """Execute a node and its connected nodes."""
        if visited is None:
            visited = set()

        if node_id in visited:
            return data  # Avoid infinite loops

        visited.add(node_id)
        node = nodes.get(node_id)

        if not node:
            return data

        # Execute current node
        step_start = datetime.utcnow()

        try:
            node_result = await self._execute_single_node(
                node, data, context, variables
            )
            step_status = "completed"
            step_error = None

            # Update data with node result
            if isinstance(node_result, dict):
                data.update(node_result)

        except Exception as e:
            logger.error(f"Node {node_id} execution failed: {e}")
            node_result = {}
            step_status = "failed"
            step_error = str(e)

        step_end = datetime.utcnow()
        step_time = int((step_end - step_start).total_seconds() * 1000)

        # Record execution step
        steps.append(
            {
                "node_id": node_id,
                "node_type": node.get("data", {}).get(
                    "nodeType", "unknown"
                ),
                "status": step_status,
                "input_data": data.copy(),
                "output_data": (
                    node_result if step_status == "completed" else None
                ),
                "error": step_error,
                "execution_time_ms": step_time,
                "timestamp": step_start,
            }
        )

        # Continue to next nodes if execution succeeded
        if step_status == "completed":
            next_edges = edges_by_source.get(node_id, [])

            for edge in next_edges:
                # Check edge conditions if any
                if await self._should_follow_edge(
                    edge, data, context, variables
                ):
                    await self._execute_node_graph(
                        edge["target"],
                        nodes,
                        edges_by_source,
                        data,
                        context,
                        variables,
                        steps,
                        visited.copy(),
                    )

        return data

    async def _execute_single_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        context: dict[str, Any],
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single workflow node."""
        node_type = node.get("data", {}).get("nodeType")
        config = node.get("data", {}).get("config", {})

        if node_type == "start":
            return await self._execute_start_node(node, data, config)
        elif node_type == "model":
            return await self._execute_model_node(node, data, config)
        elif node_type == "tool":
            return await self._execute_tool_node(node, data, config)
        elif node_type == "memory":
            return await self._execute_memory_node(
                node, data, config, context
            )
        elif node_type == "retrieval":
            return await self._execute_retrieval_node(
                node, data, config
            )
        elif node_type == "conditional":
            return await self._execute_conditional_node(
                node, data, config
            )
        elif node_type == "loop":
            return await self._execute_loop_node(
                node, data, config, context, variables
            )
        elif node_type == "variable":
            return await self._execute_variable_node(
                node, data, config, variables
            )
        elif node_type == "error_handler":
            return await self._execute_error_handler_node(
                node, data, config
            )
        elif node_type == "delay":
            return await self._execute_delay_node(node, data, config)
        else:
            logger.warning(f"Unknown node type: {node_type}")
            return {}

    async def _execute_start_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute start node - just pass through data."""
        return {"workflow_started": True}

    async def _execute_model_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute model node - make LLM call."""
        try:
            model = config.get("model", "gpt-3.5-turbo")
            system_message = config.get("systemMessage", "")
            temperature = config.get("temperature", 0.7)
            max_tokens = config.get("maxTokens")

            # Build prompt from current data
            user_content = data.get("content", data.get("query", ""))
            if not user_content:
                user_content = str(
                    data
                )  # Fallback to data representation

            messages = []
            if system_message:
                messages.append(
                    {"role": "system", "content": system_message}
                )
            messages.append({"role": "user", "content": user_content})

            # Make LLM call - use None provider to get default
            response = await self.llm_service.generate(
                messages=messages,
                provider=None,  # Use default provider
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return {
                "model_response": response.get("content", ""),
                "model_used": model,
                "tokens_used": response.get("usage", {}).get(
                    "total_tokens", 0
                ),
            }

        except Exception as e:
            logger.error(f"Model node execution failed: {e}")
            raise

    async def _execute_tool_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute tool node - call external tool."""
        try:
            tool_name = config.get("toolName", "")
            parameters = config.get("parameters", {})

            if not tool_name:
                raise ValueError("Tool name not specified")

            # Tool execution would happen here
            # For now, just return a placeholder
            return {
                "tool_result": f"Tool {tool_name} executed with params: {parameters}",
                "tool_used": tool_name,
            }

        except Exception as e:
            logger.error(f"Tool node execution failed: {e}")
            raise

    async def _execute_memory_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute memory node - store/retrieve from memory."""
        try:
            operation = config.get("operation", "store")
            key = config.get("key", "")

            if not key:
                raise ValueError("Memory key not specified")

            memory = context.setdefault("memory", {})

            if operation == "store":
                value = data.get("content", data)
                memory[key] = value
                return {"memory_stored": True, "key": key}
            elif operation == "retrieve":
                value = memory.get(key, None)
                return {"memory_value": value, "key": key}
            else:
                raise ValueError(
                    f"Unknown memory operation: {operation}"
                )

        except Exception as e:
            logger.error(f"Memory node execution failed: {e}")
            raise

    async def _execute_retrieval_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute retrieval node - search documents."""
        try:
            query = config.get("query", data.get("query", ""))
            limit = config.get("limit", 5)

            if not query:
                raise ValueError("Retrieval query not specified")

            # Document retrieval would happen here
            # For now, just return a placeholder
            return {
                "retrieval_results": f"Found documents for query: {query}",
                "result_count": limit,
            }

        except Exception as e:
            logger.error(f"Retrieval node execution failed: {e}")
            raise

    async def _execute_conditional_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute conditional node - evaluate condition."""
        try:
            condition = config.get("condition", "true")

            # Safe condition evaluation - only allow basic boolean conditions
            try:
                # For security, only allow literal boolean values or simple comparisons
                if condition.lower() in ("true", "1", "yes"):
                    result = True
                elif condition.lower() in ("false", "0", "no"):
                    result = False
                else:
                    # For complex conditions, would need a proper expression parser
                    # For now, default to True for security
                    logger.warning(
                        f"Complex condition not supported for security: {condition}"
                    )
                    result = True
            except Exception:
                result = True

            return {"condition_result": result, "condition": condition}

        except Exception as e:
            logger.error(f"Conditional node execution failed: {e}")
            raise

    async def _execute_loop_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
        context: dict[str, Any],
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute loop node - handle iteration."""
        try:
            max_iterations = config.get("maxIterations", 10)
            condition = config.get("condition", "")

            loop_state = context.setdefault("loops", {})
            loop_id = node["id"]
            current_iteration = loop_state.get(loop_id, 0)

            should_continue = current_iteration < max_iterations
            if condition:
                # Safe condition evaluation - only allow basic boolean conditions
                try:
                    if condition.lower() in ("true", "1", "yes"):
                        condition_result = True
                    elif condition.lower() in ("false", "0", "no"):
                        condition_result = False
                    else:
                        # For complex conditions, would need a proper expression parser
                        logger.warning(
                            f"Complex condition not supported for security: {condition}"
                        )
                        condition_result = True
                    should_continue = (
                        should_continue and condition_result
                    )
                except Exception:
                    should_continue = should_continue and True

            if should_continue:
                loop_state[loop_id] = current_iteration + 1
                return {
                    "loop_continue": True,
                    "iteration": current_iteration + 1,
                    "max_iterations": max_iterations,
                }
            else:
                loop_state.pop(loop_id, None)
                return {
                    "loop_exit": True,
                    "final_iteration": current_iteration,
                }

        except Exception as e:
            logger.error(f"Loop node execution failed: {e}")
            raise

    async def _execute_variable_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
        variables: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute variable node - manipulate variables."""
        try:
            operation = config.get("operation", "set")
            variable_name = config.get("variableName", "")
            value = config.get("value", data.get("content", ""))

            if not variable_name:
                raise ValueError("Variable name not specified")

            if operation == "set":
                variables[variable_name] = value
                return {
                    "variable_set": True,
                    "name": variable_name,
                    "value": value,
                }
            elif operation == "get":
                current_value = variables.get(variable_name, None)
                return {
                    "variable_value": current_value,
                    "name": variable_name,
                }
            elif operation == "append":
                if variable_name not in variables:
                    variables[variable_name] = []
                if isinstance(variables[variable_name], list):
                    variables[variable_name].append(value)
                return {
                    "variable_appended": True,
                    "name": variable_name,
                }
            elif operation == "increment":
                current = variables.get(variable_name, 0)
                variables[variable_name] = current + (
                    value if isinstance(value, int | float) else 1
                )
                return {
                    "variable_incremented": True,
                    "name": variable_name,
                    "value": variables[variable_name],
                }
            elif operation == "decrement":
                current = variables.get(variable_name, 0)
                variables[variable_name] = current - (
                    value if isinstance(value, int | float) else 1
                )
                return {
                    "variable_decremented": True,
                    "name": variable_name,
                    "value": variables[variable_name],
                }
            else:
                raise ValueError(
                    f"Unknown variable operation: {operation}"
                )

        except Exception as e:
            logger.error(f"Variable node execution failed: {e}")
            raise

    async def _execute_error_handler_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute error handler node - handle errors."""
        try:
            retry_count = config.get("retryCount", 3)
            fallback_action = config.get("fallbackAction", "continue")

            # Error handling logic would be more sophisticated
            return {
                "error_handled": True,
                "retry_count": retry_count,
                "fallback_action": fallback_action,
            }

        except Exception as e:
            logger.error(f"Error handler node execution failed: {e}")
            raise

    async def _execute_delay_node(
        self,
        node: dict[str, Any],
        data: dict[str, Any],
        config: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute delay node - introduce time delays."""
        import asyncio
        import random

        try:
            delay_type = config.get("delayType", "fixed")
            duration = config.get("duration", 1000)  # milliseconds
            max_duration = config.get("maxDuration", duration * 2)

            actual_delay = duration

            if delay_type == "random":
                actual_delay = random.randint(duration, max_duration)
            elif delay_type == "exponential":
                # Simple exponential backoff
                actual_delay = min(duration * 2, max_duration)
            elif delay_type == "dynamic":
                # Could be based on system load, etc.
                actual_delay = random.randint(duration, max_duration)

            # Convert to seconds and wait
            await asyncio.sleep(actual_delay / 1000.0)

            return {
                "delay_completed": True,
                "delay_type": delay_type,
                "actual_delay_ms": actual_delay,
            }

        except Exception as e:
            logger.error(f"Delay node execution failed: {e}")
            raise

    async def _should_follow_edge(
        self,
        edge: dict[str, Any],
        data: dict[str, Any],
        context: dict[str, Any],
        variables: dict[str, Any],
    ) -> bool:
        """Determine if an edge should be followed based on conditions."""
        edge_data = edge.get("data", {})
        condition = edge_data.get("condition", "")

        if not condition:
            return True  # No condition means always follow

        try:
            # Safe condition evaluation - only allow basic boolean conditions
            if condition.lower() in ("true", "1", "yes"):
                return True
            elif condition.lower() in ("false", "0", "no"):
                return False
            else:
                # For complex conditions, would need a proper expression parser
                logger.warning(
                    f"Complex edge condition not supported for security: {condition}"
                )
                return True  # Default to following the edge
        except Exception as e:
            logger.warning(f"Edge condition evaluation failed: {e}")
            return True  # Default to following edge on error
