"""Unified workflow executor classes.

This module provides executor classes that use the new capability-based 
workflow system while maintaining compatibility with existing code and tests.
All executors now use the UnifiedWorkflowEngine internally.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from chatter.core.unified_workflow_engine import UnifiedWorkflowEngine
from chatter.core.workflow_capabilities import WorkflowCapabilities, WorkflowSpec
from chatter.models.conversation import Conversation, Message
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService


class BaseWorkflowExecutor:
    """Base class for workflow executors using unified engine."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        template_manager,
    ):
        """Initialize base workflow executor."""
        self._engine = UnifiedWorkflowEngine(
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
        """Execute workflow using unified engine."""
        # Convert ChatRequest to WorkflowSpec
        spec = WorkflowSpec.from_chat_request(chat_request)
        
        # Prepare input data
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        return await self._engine.execute_workflow(
            spec, conversation, input_data, user_id
        )

    async def execute_streaming(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming using unified engine."""
        # Convert ChatRequest to WorkflowSpec
        spec = WorkflowSpec.from_chat_request(chat_request)
        
        # Prepare input data
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        async for chunk in self._engine.execute_workflow_streaming(
            spec, conversation, input_data, user_id
        ):
            yield chunk


class PlainWorkflowExecutor(BaseWorkflowExecutor):
    """Plain workflow executor - simple chat without tools or retrieval."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute plain workflow with basic capabilities."""
        # Override capabilities to ensure plain workflow
        spec = WorkflowSpec(
            capabilities=WorkflowCapabilities(),  # Plain capabilities
            provider=getattr(chat_request, 'provider', 'openai'),
            model=getattr(chat_request, 'model', 'gpt-4'),
            temperature=getattr(chat_request, 'temperature', 0.7),
            max_tokens=getattr(chat_request, 'max_tokens', 1000),
            system_prompt=getattr(chat_request, 'system_prompt_override', None)
        )
        
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        return await self._engine.execute_workflow(
            spec, conversation, input_data, user_id
        )


class RAGWorkflowExecutor(BaseWorkflowExecutor):
    """RAG workflow executor - retrieval-augmented generation."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute RAG workflow with retrieval capabilities."""
        # Override capabilities to ensure RAG workflow
        spec = WorkflowSpec(
            capabilities=WorkflowCapabilities(
                enable_retrieval=True,
                max_documents=10,
                memory_window=30
            ),
            provider=getattr(chat_request, 'provider', 'openai'),
            model=getattr(chat_request, 'model', 'gpt-4'),
            temperature=getattr(chat_request, 'temperature', 0.7),
            max_tokens=getattr(chat_request, 'max_tokens', 1000),
            system_prompt=getattr(chat_request, 'system_prompt_override', None)
        )
        
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        return await self._engine.execute_workflow(
            spec, conversation, input_data, user_id
        )


class ToolsWorkflowExecutor(BaseWorkflowExecutor):
    """Tools workflow executor - function calling."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute tools workflow with tool capabilities."""
        # Override capabilities to ensure tools workflow
        spec = WorkflowSpec(
            capabilities=WorkflowCapabilities(
                enable_tools=True,
                max_tool_calls=10,
                memory_window=100
            ),
            provider=getattr(chat_request, 'provider', 'openai'),
            model=getattr(chat_request, 'model', 'gpt-4'),
            temperature=getattr(chat_request, 'temperature', 0.7),
            max_tokens=getattr(chat_request, 'max_tokens', 1000),
            system_prompt=getattr(chat_request, 'system_prompt_override', None)
        )
        
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        return await self._engine.execute_workflow(
            spec, conversation, input_data, user_id
        )


class FullWorkflowExecutor(BaseWorkflowExecutor):
    """Full workflow executor - both tools and retrieval."""

    async def execute(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        correlation_id: str,
        user_id: str | None = None,
        limits=None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute full workflow with all capabilities."""
        # Override capabilities to ensure full workflow
        spec = WorkflowSpec(
            capabilities=WorkflowCapabilities(
                enable_retrieval=True,
                enable_tools=True,
                max_tool_calls=5,
                max_documents=10,
                memory_window=50
            ),
            provider=getattr(chat_request, 'provider', 'openai'),
            model=getattr(chat_request, 'model', 'gpt-4'),
            temperature=getattr(chat_request, 'temperature', 0.7),
            max_tokens=getattr(chat_request, 'max_tokens', 1000),
            system_prompt=getattr(chat_request, 'system_prompt_override', None)
        )
        
        input_data = {
            'message': chat_request.message,
            'user_id': user_id,
            'correlation_id': correlation_id
        }
        
        return await self._engine.execute_workflow(
            spec, conversation, input_data, user_id
        )
