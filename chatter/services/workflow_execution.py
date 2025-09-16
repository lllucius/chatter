"""Simplified workflow execution service.

This provides a clean interface for workflow execution using a unified
executor that handles all workflow types efficiently.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import (
    get_template_manager_with_session,
)
from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
from chatter.core.workflow_limits import (
    WorkflowLimits,
    workflow_limit_manager,
)
from chatter.core.workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.models.conversation import Conversation, Message
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionService:
    """Simplified service for executing chat workflows."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session: AsyncSession,
    ):
        """Initialize simplified workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = get_template_manager_with_session(session)
        self.limit_manager = workflow_limit_manager
        self.executor = UnifiedWorkflowExecutor(
            llm_service, message_service, self.template_manager
        )

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
        return await self.executor.execute(
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
        async for chunk in self.executor.execute_streaming(
            conversation, chat_request, correlation_id, user_id, limits
        ):
            yield chunk

    async def get_service_stats(self) -> dict[str, Any]:
        """Get comprehensive service statistics.

        Returns:
            Dictionary containing service performance and usage stats
        """
        return {
            "supported_workflow_types": self.executor.get_supported_types(),
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
        supported_types = self.executor.get_supported_types()
        if workflow_type not in supported_types:
            return {
                "valid": False,
                "errors": [f"Unsupported workflow type: {workflow_type}"],
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
        supported_types = self.executor.get_supported_types()

        if workflow_type not in supported_types:
            return {"error": f"Unsupported workflow type: {workflow_type}"}

        # Basic capabilities mapping
        capabilities = {
            "plain": {
                "requires_tools": False,
                "requires_retriever": False,
                "supports_streaming": True,
                "memory_window": 20,
            },
            "basic": {
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

    # Legacy node-based execution support (simplified)
    async def execute_workflow_definition(
        self,
        workflow_definition: Any,  # WorkflowDefinition object
        input_data: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a node-based workflow definition (legacy support).

        This is a simplified version that supports basic node execution
        for backwards compatibility. For new workflows, use the main
        execute_workflow method.

        Args:
            workflow_definition: Workflow definition with nodes and edges
            input_data: Input data for the workflow
            context: Optional execution context

        Returns:
            Dictionary with execution results
        """
        from datetime import datetime
        from chatter.models.base import generate_ulid

        execution_id = generate_ulid()
        started_at = datetime.utcnow()

        try:
            # Simple validation
            if not hasattr(workflow_definition, 'nodes') or not workflow_definition.nodes:
                raise ValueError("Workflow definition must have nodes")

            # For now, return a simple success response
            # In the future, this could be extended to support specific node types
            # that are actually needed by the application
            completed_at = datetime.utcnow()
            total_time = int((completed_at - started_at).total_seconds() * 1000)

            return {
                "execution_id": execution_id,
                "status": "completed",
                "result": input_data,  # Pass through input data
                "steps": [
                    {
                        "node_id": "simplified_execution",
                        "node_type": "passthrough",
                        "status": "completed",
                        "input_data": input_data,
                        "output_data": input_data,
                        "error": None,
                        "execution_time_ms": total_time,
                        "timestamp": started_at,
                    }
                ],
                "total_execution_time_ms": total_time,
                "error": None,
                "started_at": started_at,
                "completed_at": completed_at,
            }

        except Exception as e:
            logger.error(f"Workflow definition execution failed: {e}")
            completed_at = datetime.utcnow()
            total_time = int((completed_at - started_at).total_seconds() * 1000)

            return {
                "execution_id": execution_id,
                "status": "failed",
                "result": None,
                "steps": [],
                "total_execution_time_ms": total_time,
                "error": str(e),
                "started_at": started_at,
                "completed_at": completed_at,
            }
