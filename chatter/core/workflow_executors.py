"""Individual workflow executor classes for backward compatibility.

This module provides the individual executor classes that tests expect,
while delegating to the UnifiedWorkflowExecutor internally.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from chatter.core.unified_workflow_executor import (
    UnifiedWorkflowExecutor,
)
from chatter.models.conversation import Conversation, Message
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService


class BaseWorkflowExecutor:
    """Base class for workflow executors."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        template_manager,
    ):
        """Initialize base workflow executor."""
        self._unified_executor = UnifiedWorkflowExecutor(
            llm_service, message_service, template_manager
        )

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute workflow."""
        return await self._unified_executor.execute(
            conversation, chat_request, correlation_id, user_id, limits
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming."""
        async for chunk in self._unified_executor.execute_streaming(
            conversation, chat_request, correlation_id, user_id, limits
        ):
            yield chunk


class PlainWorkflowExecutor(BaseWorkflowExecutor):
    """Plain workflow executor for simple chat without tools or retrieval."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute plain workflow."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "plain"
        request_copy.workflow_type = "plain"
        return await super().execute(
            conversation, request_copy, correlation_id, user_id, limits
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute plain workflow with streaming."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "plain"
        request_copy.workflow_type = "plain"
        async for chunk in super().execute_streaming(
            conversation, request_copy, correlation_id, user_id, limits
        ):
            yield chunk


class RAGWorkflowExecutor(BaseWorkflowExecutor):
    """RAG workflow executor for retrieval-augmented generation."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute RAG workflow."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "rag"
        request_copy.workflow_type = "rag"
        return await super().execute(
            conversation, request_copy, correlation_id, user_id, limits
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute RAG workflow with streaming."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "rag"
        request_copy.workflow_type = "rag"
        async for chunk in super().execute_streaming(
            conversation, request_copy, correlation_id, user_id, limits
        ):
            yield chunk


class ToolsWorkflowExecutor(BaseWorkflowExecutor):
    """Tools workflow executor for function calling."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute tools workflow."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "tools"
        request_copy.workflow_type = "tools"
        return await super().execute(
            conversation, request_copy, correlation_id, user_id, limits
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute tools workflow with streaming."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "tools"
        request_copy.workflow_type = "tools"
        async for chunk in super().execute_streaming(
            conversation, request_copy, correlation_id, user_id, limits
        ):
            yield chunk


class FullWorkflowExecutor(BaseWorkflowExecutor):
    """Full workflow executor with both tools and retrieval."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute full workflow."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "full"
        request_copy.workflow_type = "full"
        return await super().execute(
            conversation, request_copy, correlation_id, user_id, limits
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute full workflow with streaming."""
        # Create a copy of the request to avoid mutating the original
        from copy import copy

        request_copy = copy(chat_request)
        request_copy.workflow = "full"
        request_copy.workflow_type = "full"
        async for chunk in super().execute_streaming(
            conversation, request_copy, correlation_id, user_id, limits
        ):
            yield chunk
