"""Simplified workflow execution service.

This provides a clean interface for workflow execution using a unified
executor that handles all workflow types efficiently.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.streamlined_workflow_performance import (
    performance_monitor,
    workflow_cache,
)
from chatter.core.unified_template_manager import (
    get_template_manager_with_session,
)
from chatter.core.unified_workflow_executor import (
    UnifiedWorkflowExecutor,
)
from chatter.core.workflow_limits import (
    WorkflowLimits,
    workflow_limit_manager,
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
        self.session = session
        self.template_manager = get_template_manager_with_session(
            session
        )
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
        workflow_type = chat_request.workflow_type or "simple_chat"

        # Check if workflow type is supported
        supported_types = self.executor.get_supported_types()
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
        supported_types = self.executor.get_supported_types()

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

    # New Chat Workflow Methods
    async def execute_chat_workflow(
        self,
        user_id: str,
        request: "ChatWorkflowRequest",
        streaming: bool = False,
    ) -> tuple[Conversation, Message] | AsyncGenerator[StreamingChatChunk, None]:
        """Execute chat using workflow system."""
        from chatter.schemas.chat import ChatRequest
        
        # Convert ChatWorkflowRequest to ChatRequest and get conversation
        chat_request, conversation = await self._convert_chat_workflow_request(
            user_id, request
        )
        
        # Generate correlation ID
        from chatter.utils.correlation import get_correlation_id
        correlation_id = get_correlation_id()
        
        if streaming:
            return self.execute_workflow_streaming(
                conversation, chat_request, correlation_id, user_id
            )
        else:
            # Execute workflow and return (conversation, message) tuple as expected by API
            message, usage_info = await self.execute_workflow(
                conversation, chat_request, correlation_id, user_id
            )
            return conversation, message

    async def _convert_chat_workflow_request(
        self, user_id: str, request: "ChatWorkflowRequest"
    ):
        """Convert ChatWorkflowRequest to ChatRequest and setup conversation."""
        from chatter.schemas.chat import ChatRequest
        from chatter.services.conversation import ConversationService
        from chatter.schemas.chat import ConversationCreate as ConversationCreateSchema
        
        # Setup conversation service
        conversation_service = ConversationService(self.session)
        
        # Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.conversation_id, user_id, include_messages=True
            )
        else:
            # Create new conversation
            conv_data = ConversationCreateSchema(
                title=(
                    request.message[:50] + "..."
                    if len(request.message) > 50
                    else request.message
                ),
                description=None,
                profile_id=request.profile_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                workflow_config=request.workflow_config.model_dump() if request.workflow_config else None,
                extra_metadata=None,
            )
            conversation = await conversation_service.create_conversation(
                user_id, conv_data
            )
        
        # Convert to ChatRequest based on workflow configuration
        workflow_type = self._determine_workflow_type(request)
        
        chat_request = ChatRequest(
            message=request.message,
            conversation_id=conversation.id,
            profile_id=request.profile_id,
            workflow=workflow_type,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            context_limit=request.context_limit,
            enable_retrieval=self._should_enable_retrieval(request),
            document_ids=request.document_ids,
            system_prompt_override=request.system_prompt_override,
            workflow_type=workflow_type,
        )
        
        return chat_request, conversation

    def _determine_workflow_type(self, request: "ChatWorkflowRequest") -> str:
        """Determine workflow type from ChatWorkflowRequest."""
        if request.workflow_template_name:
            # Map template names to workflow types
            template_mapping = {
                "simple_chat": "plain",
                "rag_chat": "rag", 
                "function_chat": "tools",
                "advanced_chat": "full"
            }
            return template_mapping.get(request.workflow_template_name, "plain")
        
        elif request.workflow_config:
            config = request.workflow_config
            # Determine type based on enabled features
            if config.enable_retrieval and config.enable_tools:
                return "full"
            elif config.enable_tools:
                return "tools"
            elif config.enable_retrieval:
                return "rag"
            else:
                return "plain"
        
        else:
            return "plain"

    def _should_enable_retrieval(self, request: "ChatWorkflowRequest") -> bool:
        """Determine if retrieval should be enabled."""
        if request.workflow_config:
            return request.workflow_config.enable_retrieval
        elif request.workflow_template_name in ["rag_chat", "advanced_chat"]:
            return True
        else:
            return False
