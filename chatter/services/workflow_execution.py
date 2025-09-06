"""Workflow execution service using strategy pattern.

This replaces the monolithic WorkflowExecutionService with a clean 
orchestration layer that delegates to focused executor classes.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import get_template_manager_with_session
from chatter.core.workflow_executors import (
    WorkflowExecutorFactory,
    WorkflowExecutionError,
)
from chatter.core.workflow_limits import (
    WorkflowLimitManager,
    WorkflowLimits,
    workflow_limit_manager,
)
from chatter.core.workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.models.conversation import (
    Conversation,
    Message,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService

import logging
logger = logging.getLogger(__name__)


class WorkflowExecutionService:
    """Service for executing chat workflows using strategy pattern."""

    def __init__(
        self, 
        llm_service: LLMService, 
        message_service: MessageService,
        session: AsyncSession
    ):
        """Initialize simplified workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = get_template_manager_with_session(session)
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
        workflow_type = chat_request.workflow or "plain"
        
        # Get appropriate executor
        executor = self.executor_factory.create_executor(
            workflow_type, self.llm_service, self.message_service, self.template_manager
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
        workflow_type = chat_request.workflow or "plain"
        
        # Get appropriate executor
        executor = self.executor_factory.create_executor(
            workflow_type, self.llm_service, self.message_service, self.template_manager
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
                if hasattr(workflow_cache, 'get_stats')
                else {}
            ),
            "template_stats": self.template_manager.get_stats(),
            "limit_manager_stats": (
                self.limit_manager.get_stats()
                if hasattr(self.limit_manager, 'get_stats')
                else {}
            ),
        }

    async def validate_workflow_request(
        self, 
        chat_request: ChatRequest
    ) -> dict[str, Any]:
        """Validate a workflow request.

        Args:
            chat_request: Chat request to validate

        Returns:
            Dictionary with validation results
        """
        workflow_type = chat_request.workflow or "plain"
        
        # Check if workflow type is supported
        supported_types = self.executor_factory.get_supported_types()
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
        self, 
        workflow_type: str
    ) -> dict[str, Any]:
        """Get capabilities for a specific workflow type.

        Args:
            workflow_type: Type of workflow to check

        Returns:
            Dictionary with workflow capabilities
        """
        supported_types = self.executor_factory.get_supported_types()
        
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
