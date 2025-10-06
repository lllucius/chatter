"""Unified workflow execution service - consolidates 9 execution methods into 3.

This module provides the modernized, unified workflow execution system that
replaces the previous fragmented implementation with 9 separate methods.

Architecture:
- Single execute_workflow() method for standard execution
- Single execute_workflow_streaming() method for streaming execution  
- Single execute_workflow_definition() method for stored definitions
- Uses WorkflowPreparationService for workflow setup
- Uses WorkflowResultProcessor for result handling
- Uses WorkflowTypes for unified type definitions
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from langchain_core.messages import BaseMessage, HumanMessage

from chatter.core.events import EventCategory, EventPriority, UnifiedEvent
from chatter.core.langgraph import workflow_manager
from chatter.core.monitoring import get_monitoring_service
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.core.workflow_performance import PerformanceMonitor
from chatter.models.base import generate_ulid
from chatter.models.conversation import Conversation, Message
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.services.workflow_preparation import (
    PreparedWorkflow,
    WorkflowPreparationService,
)
from chatter.services.workflow_result_processor import (
    WorkflowResultProcessor,
)
from chatter.services.workflow_types import (
    ExecutionMode,
    WorkflowConfig,
    WorkflowInput,
    WorkflowResult,
    WorkflowSource,
    WorkflowSourceType,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Global event emitter (will be initialized on first use)
_event_emitter = None


async def _emit_event(event: UnifiedEvent) -> None:
    """Emit an event to the unified event system."""
    global _event_emitter
    if _event_emitter is None:
        try:
            from chatter.core.events import get_event_emitter

            _event_emitter = await get_event_emitter()
        except Exception as e:
            logger.warning(f"Could not initialize event emitter: {e}")
            return

    try:
        await _event_emitter.emit(event)
    except Exception as e:
        logger.warning(f"Could not emit event: {e}")


class UnifiedWorkflowExecutionService:
    """Unified workflow execution service.
    
    Consolidates 9 previous execution methods into 3:
    - execute_workflow(): Standard execution
    - execute_workflow_streaming(): Streaming execution
    - execute_workflow_definition(): Execute stored workflow definition
    """

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session,
    ):
        """Initialize the unified workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.session = session
        self.preparation_service = WorkflowPreparationService(
            llm_service, session
        )
        self.result_processor = WorkflowResultProcessor(session)

    async def execute_workflow(
        self,
        workflow_input: WorkflowInput,
        workflow_source: WorkflowSource,
        workflow_config: WorkflowConfig,
        user_id: str,
    ) -> WorkflowResult:
        """Execute a workflow with unified interface.
        
        This replaces:
        - execute_chat_workflow()
        - _execute_chat_workflow_internal()
        - _execute_with_universal_template()
        - _execute_with_dynamic_workflow()
        - execute_custom_workflow()
        
        Args:
            workflow_input: Input data (conversation, message, etc.)
            workflow_source: Source of workflow (template/definition/dynamic)
            workflow_config: Execution configuration
            user_id: User ID
            
        Returns:
            WorkflowResult with execution results
        """
        start_time = time.time()
        performance_monitor = PerformanceMonitor(
            execution_id=generate_ulid(),
            debug_mode=workflow_config.debug_mode,
        )

        try:
            # Get or create conversation
            conversation = workflow_input.conversation
            if conversation is None:
                conversation = await self._get_or_create_conversation(
                    user_id, workflow_input.conversation_id
                )

            # Emit workflow start event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    priority=EventPriority.INFO,
                    message="Workflow execution started",
                    data={
                        "user_id": user_id,
                        "conversation_id": conversation.id,
                        "source_type": workflow_source.source_type.value,
                    },
                )
            )

            # Prepare workflow (consolidates template/definition/dynamic logic)
            prepared_workflow = await self.preparation_service.prepare_workflow(
                workflow_source=workflow_source,
                workflow_config=workflow_config,
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation messages
            messages = await self._get_conversation_messages(conversation)
            
            # Add new user message
            if workflow_input.message:
                messages.append(HumanMessage(content=workflow_input.message))

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {
                    "provider": workflow_config.provider,
                    "model": workflow_config.model,
                    "temperature": workflow_config.temperature,
                    "max_tokens": workflow_config.max_tokens,
                    "source_type": workflow_source.source_type.value,
                    "source_id": workflow_source.source_id,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
                "usage_metadata": {},
            }

            # Execute workflow
            performance_monitor.log_debug("Starting workflow execution")
            result = await workflow_manager.run_workflow(
                workflow=prepared_workflow.workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            )
            performance_monitor.log_debug("Workflow execution completed")

            # Process result (consolidates message creation, AI response extraction)
            workflow_result = await self.result_processor.process_result(
                result=result,
                conversation=conversation,
                user_message=workflow_input.message,
                user_id=user_id,
                execution_time_ms=int((time.time() - start_time) * 1000),
                performance_monitor=performance_monitor,
            )

            # Emit workflow completion event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    priority=EventPriority.INFO,
                    message="Workflow execution completed",
                    data={
                        "user_id": user_id,
                        "conversation_id": conversation.id,
                        "execution_time_ms": workflow_result.execution_time_ms,
                    },
                )
            )

            return workflow_result

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}", exc_info=True)
            
            # Emit workflow error event
            await _emit_event(
                UnifiedEvent(
                    category=EventCategory.WORKFLOW,
                    priority=EventPriority.ERROR,
                    message=f"Workflow execution failed: {str(e)}",
                    data={
                        "user_id": user_id,
                        "error": str(e),
                    },
                )
            )
            
            raise

    async def execute_workflow_streaming(
        self,
        workflow_input: WorkflowInput,
        workflow_source: WorkflowSource,
        workflow_config: WorkflowConfig,
        user_id: str,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a workflow with streaming response.
        
        This replaces:
        - execute_chat_workflow_streaming()
        - _execute_streaming_with_universal_template()
        - _execute_streaming_with_dynamic_workflow()
        
        Args:
            workflow_input: Input data (conversation, message, etc.)
            workflow_source: Source of workflow (template/definition/dynamic)
            workflow_config: Execution configuration
            user_id: User ID
            
        Yields:
            StreamingChatChunk with partial responses
        """
        start_time = time.time()
        content_buffer = ""
        
        try:
            # Get or create conversation
            conversation = workflow_input.conversation
            if conversation is None:
                conversation = await self._get_or_create_conversation(
                    user_id, workflow_input.conversation_id
                )

            # Prepare workflow
            prepared_workflow = await self.preparation_service.prepare_workflow(
                workflow_source=workflow_source,
                workflow_config=workflow_config,
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation messages
            messages = await self._get_conversation_messages(conversation)
            
            # Add new user message
            if workflow_input.message:
                messages.append(HumanMessage(content=workflow_input.message))

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {
                    "provider": workflow_config.provider,
                    "model": workflow_config.model,
                    "temperature": workflow_config.temperature,
                    "max_tokens": workflow_config.max_tokens,
                    "source_type": workflow_source.source_type.value,
                    "source_id": workflow_source.source_id,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
                "usage_metadata": {},
            }

            # Stream workflow execution
            async for event in workflow_manager.stream_workflow(
                workflow=prepared_workflow.workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            ):
                # Extract content from event
                if "messages" in event and event["messages"]:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, "content"):
                        content = str(last_message.content)
                        
                        # Send incremental content
                        if content and content != content_buffer:
                            new_content = content[len(content_buffer):]
                            content_buffer = content
                            
                            yield StreamingChatChunk(
                                type="content",
                                content=new_content,
                                metadata={},
                            )

            # Create and save final message
            if content_buffer:
                await self.message_service.create_message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=content_buffer,
                )

            # Send done marker
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={
                    "execution_time_ms": int((time.time() - start_time) * 1000),
                },
            )

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {e}", exc_info=True)
            
            # Send error chunk
            yield StreamingChatChunk(
                type="error",
                content="",
                metadata={"error": str(e)},
            )

    async def execute_workflow_definition(
        self,
        definition: Any,
        input_data: dict[str, Any],
        user_id: str,
        debug_mode: bool = False,
    ) -> dict[str, Any]:
        """Execute a stored workflow definition.
        
        This replaces the original execute_workflow_definition() method.
        
        Args:
            definition: Workflow definition model
            input_data: Input data for execution
            user_id: User ID
            debug_mode: Enable debug mode
            
        Returns:
            Execution result dictionary
        """
        start_time = time.time()
        
        # Create workflow source from definition
        workflow_source = WorkflowSource(
            source_type=WorkflowSourceType.DEFINITION,
            source_id=definition.id,
            definition=definition,
        )
        
        # Create workflow config
        workflow_config = WorkflowConfig(
            provider=input_data.get("provider", "openai"),
            model=input_data.get("model", "gpt-4"),
            temperature=input_data.get("temperature", 0.7),
            max_tokens=input_data.get("max_tokens", 2000),
            debug_mode=debug_mode,
        )
        
        # Create workflow input
        workflow_input = WorkflowInput(
            message=input_data.get("message", ""),
            conversation_id=input_data.get("conversation_id"),
            input_data=input_data,
        )
        
        # Execute workflow
        result = await self.execute_workflow(
            workflow_input=workflow_input,
            workflow_source=workflow_source,
            workflow_config=workflow_config,
            user_id=user_id,
        )
        
        # Convert to execution response format
        return result.to_execution_response()

    async def _get_conversation_messages(
        self, conversation: Conversation
    ) -> list[BaseMessage]:
        """Get messages from a conversation."""
        db_messages = await self.message_service.get_messages(
            conversation_id=conversation.id
        )
        
        messages = []
        for msg in db_messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg.content))
        
        return messages

    async def _get_or_create_conversation(
        self, user_id: str, conversation_id: str | None = None
    ) -> Conversation:
        """Get existing or create new conversation."""
        if conversation_id:
            # Try to get existing conversation
            from chatter.services.conversation import ConversationService
            conv_service = ConversationService(self.session)
            conversation = await conv_service.get_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            if conversation:
                return conversation
        
        # Create new conversation
        from chatter.services.conversation import ConversationService
        conv_service = ConversationService(self.session)
        conversation = await conv_service.create_conversation(
            user_id=user_id,
            title="New Conversation",
        )
        return conversation
