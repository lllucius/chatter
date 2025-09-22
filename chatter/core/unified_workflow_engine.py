"""Simplified workflow engine that delegates to LangGraph.

DEPRECATED: This engine now serves as a compatibility wrapper around the
LangGraphWorkflowManager. New code should use LangGraphWorkflowManager directly.
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from typing import Any

from chatter.core.langgraph import workflow_manager
from chatter.core.workflow_capabilities import WorkflowSpec
from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionError(Exception):
    """Base exception for workflow execution errors."""
    pass


class UnifiedWorkflowEngine:
    """Simplified workflow engine that delegates to LangGraph."""

    def __init__(self, llm_service, message_service):
        """Initialize engine with required services."""
        self.llm_service = llm_service
        self.message_service = message_service

    async def execute_workflow(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        input_data: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a workflow by delegating to LangGraphWorkflowManager."""
        start_time = time.time()
        
        try:
            # Convert WorkflowSpec to ChatRequest for compatibility
            chat_request = self._spec_to_chat_request(spec, input_data)
            
            # Use the unified workflow executor
            from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
            
            executor = UnifiedWorkflowExecutor(
                self.llm_service, 
                self.message_service, 
                None  # template_manager not needed
            )
            
            # Generate correlation ID
            from chatter.utils.correlation import get_correlation_id
            correlation_id = get_correlation_id()
            
            # Execute through the modern system
            message, usage_info = await executor.execute(
                conversation, chat_request, correlation_id, user_id
            )
            
            # Add execution time
            usage_info['execution_time_ms'] = int((time.time() - start_time) * 1000)
            
            return message, usage_info
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            raise WorkflowExecutionError(f"Workflow execution failed: {str(e)}") from e

    def _spec_to_chat_request(self, spec: WorkflowSpec, input_data: dict[str, Any] | None) -> ChatRequest:
        """Convert WorkflowSpec to ChatRequest for compatibility."""
        message = input_data.get('message', '') if input_data else ''
        
        return ChatRequest(
            message=message,
            conversation_id='',  # Will be set by executor
            provider=spec.provider,
            model=spec.model,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
            system_prompt_override=spec.system_prompt,
            enable_retrieval=spec.capabilities.enable_retrieval,
            enable_tools=spec.capabilities.enable_tools,
            enable_memory=spec.capabilities.enable_memory,
        )

    async def execute_workflow_streaming(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        input_data: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming by delegating to LangGraphWorkflowManager."""
        try:
            # Convert WorkflowSpec to ChatRequest for compatibility
            chat_request = self._spec_to_chat_request(spec, input_data)
            
            # Use the unified workflow executor
            from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
            
            executor = UnifiedWorkflowExecutor(
                self.llm_service, 
                self.message_service, 
                None  # template_manager not needed
            )
            
            # Generate correlation ID
            from chatter.utils.correlation import get_correlation_id
            correlation_id = get_correlation_id()
            
            # Stream through the modern system
            async for chunk in executor.execute_streaming(
                conversation, chat_request, correlation_id, user_id
            ):
                yield chunk
                
        except Exception as e:
            logger.error(f"Workflow streaming failed: {e}", exc_info=True)
            raise WorkflowExecutionError(f"Workflow streaming failed: {str(e)}") from e
