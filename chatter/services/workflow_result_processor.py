"""Workflow result processing service.

This service consolidates result processing logic previously duplicated across
multiple execution methods in workflow_execution.py.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy import func, select

from chatter.models.base import generate_ulid
from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.models.workflow import WorkflowExecution
from chatter.services.workflow_types import ExecutionMode, WorkflowResult
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowResultProcessor:
    """Service for processing workflow execution results.
    
    This consolidates result processing logic that was previously
    duplicated across 9 execution methods.
    """

    def __init__(self, session):
        """Initialize the result processor."""
        self.session = session

    async def process_result(
        self,
        raw_result: dict[str, Any],
        execution: WorkflowExecution,
        conversation: Conversation,
        mode: ExecutionMode,
        start_time: float,
        provider: str | None = None,
    ) -> WorkflowResult:
        """Process workflow result and save message.
        
        This method consolidates result processing from:
        - _execute_with_universal_template()
        - _execute_with_dynamic_workflow()
        - _execute_streaming_with_universal_template()
        - _execute_streaming_with_dynamic_workflow()
        - execute_workflow_definition()
        
        Args:
            raw_result: Raw workflow execution result
            execution: Workflow execution record
            conversation: Conversation for the workflow
            mode: Execution mode (standard or streaming)
            start_time: Execution start timestamp
            provider: LLM provider used
            
        Returns:
            WorkflowResult with processed data and saved message
        """
        # Extract AI response from workflow result
        ai_message = self._extract_ai_response(raw_result)

        # Calculate execution time
        execution_time_ms = int((time.time() - start_time) * 1000)

        # Create and save message
        message = await self._create_and_save_message(
            conversation=conversation,
            content=ai_message.content,
            role=MessageRole.ASSISTANT,
            metadata=raw_result.get("metadata", {}),
            prompt_tokens=raw_result.get("prompt_tokens"),
            completion_tokens=raw_result.get("completion_tokens"),
            cost=raw_result.get("cost"),
            provider_used=provider,
            response_time_ms=execution_time_ms,
        )

        # Update conversation aggregates
        await self._update_conversation_aggregates(
            conversation=conversation,
            user_id=execution.owner_id,
            tokens_delta=raw_result.get("tokens_used", 0),
            cost_delta=raw_result.get("cost", 0.0),
        )

        # Build unified result
        return WorkflowResult(
            message=message,
            conversation=conversation,
            execution_id=execution.id,
            execution_time_ms=execution_time_ms,
            tokens_used=raw_result.get("tokens_used", 0),
            prompt_tokens=raw_result.get("prompt_tokens"),
            completion_tokens=raw_result.get("completion_tokens"),
            cost=raw_result.get("cost", 0.0),
            tool_calls=raw_result.get("tool_call_count", 0),
            metadata=raw_result.get("metadata", {}),
        )

    def _extract_ai_response(
        self, workflow_result: dict[str, Any]
    ) -> BaseMessage:
        """Extract AI response from workflow result.
        
        Consolidates extraction logic from multiple methods.
        """
        messages = workflow_result.get("messages", [])

        # Find the last AI message
        for message in reversed(messages):
            if hasattr(message, "content") and message.content:
                return message

        # Fallback if no message found
        return AIMessage(content="No response generated")

    async def _create_and_save_message(
        self,
        conversation: Conversation,
        content: str,
        role: MessageRole,
        metadata: dict[str, Any] | None = None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
        cost: float | None = None,
        provider_used: str | None = None,
        response_time_ms: int | None = None,
    ) -> Message:
        """Create and save a message to the conversation.
        
        Consolidates message creation logic from multiple methods.
        """
        # Get proper sequence number from conversation message count
        query = select(func.count(Message.id)).where(
            Message.conversation_id == conversation.id
        )
        result = await self.session.execute(query)
        message_count = result.scalar() or 0
        sequence_number = message_count + 1

        # Calculate total tokens
        total_tokens = None
        if prompt_tokens is not None or completion_tokens is not None:
            total_tokens = (prompt_tokens or 0) + (completion_tokens or 0)

        # Create message object with all fields including token statistics
        message = Message(
            id=generate_ulid(),
            conversation_id=conversation.id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            rating_count=0,
            extra_metadata=metadata or {},
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost=cost,
            provider_used=provider_used,
            response_time_ms=response_time_ms,
        )

        # Set created_at if not already set
        if not hasattr(message, 'created_at') or message.created_at is None:
            message.created_at = datetime.now(UTC)

        # Save to database
        try:
            self.session.add(message)
            await self.session.commit()
            logger.debug(
                f"Saved message {message.id} with {total_tokens} tokens"
            )
        except Exception as e:
            logger.error(f"Failed to save message: {e}")
            await self.session.rollback()

        return message

    async def _update_conversation_aggregates(
        self,
        conversation: Conversation,
        user_id: str,
        tokens_delta: int,
        cost_delta: float,
    ):
        """Update conversation aggregates.
        
        Consolidates aggregate update logic from multiple methods.
        """
        from chatter.services.conversation import ConversationService

        conversation_service = ConversationService(self.session)
        await conversation_service.update_conversation_aggregates(
            conversation_id=conversation.id,
            user_id=user_id,
            tokens_delta=tokens_delta,
            cost_delta=cost_delta,
            message_count_delta=1,  # One new assistant message
        )
        
        logger.debug(
            f"Updated conversation {conversation.id} aggregates: "
            f"+{tokens_delta} tokens, +${cost_delta:.4f} cost"
        )
