"""Unified workflow execution service.

This provides a unified interface for executing all types of workflows:
- Chat workflows with dynamic configuration
- Predefined workflow definitions with node/edge graphs
- Template-based workflows

Uses the new capability-based system instead of hardcoded workflow types.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import (
    get_template_manager_with_session,
)
from chatter.core.unified_workflow_engine import UnifiedWorkflowEngine
from chatter.core.workflow_capabilities import WorkflowSpec
from chatter.core.workflow_limits import workflow_limit_manager
from chatter.models.conversation import Conversation, Message
from chatter.models.workflow import WorkflowDefinition
from chatter.schemas.chat import StreamingChatChunk
from chatter.schemas.workflows import ChatWorkflowRequest
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionService:
    """Unified service for executing all types of workflows."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session: AsyncSession,
    ):
        """Initialize unified workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.session = session
        self.template_manager = get_template_manager_with_session(
            session
        )
        self.limit_manager = workflow_limit_manager
        self.engine = UnifiedWorkflowEngine(
            llm_service, message_service, self.template_manager
        )

    # Chat Workflow Methods
    async def execute_chat_workflow(
        self,
        user_id: str,
        request: ChatWorkflowRequest,
    ) -> tuple[Conversation, Message]:
        """Execute chat using workflow system (non-streaming)."""
        # Convert ChatWorkflowRequest to WorkflowSpec and get conversation
        spec, conversation = await self._convert_chat_workflow_request(
            user_id, request
        )

        # Prepare input data
        input_data = {'message': request.message, 'user_id': user_id}

        # Execute workflow using unified engine
        message, usage_info = await self.engine.execute_workflow(
            spec=spec,
            conversation=conversation,
            input_data=input_data,
            user_id=user_id,
        )

        # Save the message to database so it has all required fields for MessageResponse
        saved_message = (
            await self.message_service.add_message_to_conversation(
                conversation_id=conversation.id,
                user_id=user_id,
                role=message.role,
                content=message.content,
                metadata=message.extra_metadata,
                input_tokens=usage_info.get("prompt_tokens"),
                output_tokens=usage_info.get("completion_tokens"),
                cost=usage_info.get("cost"),
                provider=usage_info.get("provider_used"),
            )
        )

        return conversation, saved_message

    async def execute_chat_workflow_streaming(
        self,
        user_id: str,
        request: ChatWorkflowRequest,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute chat using workflow system (streaming)."""
        # Convert ChatWorkflowRequest to WorkflowSpec and get conversation
        spec, conversation = await self._convert_chat_workflow_request(
            user_id, request
        )

        # Prepare input data
        input_data = {'message': request.message, 'user_id': user_id}

        # Use unified engine for streaming execution
        async for chunk in self.engine.execute_workflow_streaming(
            spec=spec,
            conversation=conversation,
            input_data=input_data,
            user_id=user_id,
        ):
            yield chunk

    async def execute_workflow_definition(
        self,
        definition: WorkflowDefinition,
        input_data: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any]:
        """Execute a workflow definition with provided input data.

        Args:
            definition: The workflow definition to execute
            input_data: Input data for the workflow
            user_id: User ID for tracking

        Returns:
            Dictionary containing execution results
        """
        try:
            from chatter.schemas.chat import (
                ConversationCreate,
            )
            from chatter.services.conversation import (
                ConversationService,
            )

            # Setup conversation service
            conversation_service = ConversationService(self.session)

            # Create or get conversation for this execution
            conversation_id = input_data.get('conversation_id')
            if conversation_id:
                conversation = (
                    await conversation_service.get_conversation(
                        conversation_id, user_id, include_messages=True
                    )
                )
            else:
                # Create new conversation for this workflow execution
                conv_data = ConversationCreate(
                    title=f"Workflow: {definition.name}",
                    description=f"Execution of workflow definition {definition.id}",
                    workflow_config=None,
                    extra_metadata={
                        'workflow_definition_id': definition.id,
                        'execution_type': 'workflow_definition',
                    },
                )
                conversation = (
                    await conversation_service.create_conversation(
                        user_id, conv_data
                    )
                )

            # Create workflow specification from definition
            spec = WorkflowSpec.from_workflow_definition(definition)

            # Add input data configuration
            if 'message' in input_data:
                input_data_with_message = dict(input_data)
            else:
                # Use a default message if none provided
                input_data_with_message = {
                    **input_data,
                    'message': input_data.get(
                        'prompt', 'Execute this workflow.'
                    ),
                }

            # Execute workflow using unified engine
            message, usage_info = await self.engine.execute_workflow(
                spec=spec,
                conversation=conversation,
                input_data=input_data_with_message,
                user_id=user_id,
            )

            # Save the message to database
            saved_message = (
                await self.message_service.add_message_to_conversation(
                    conversation_id=conversation.id,
                    user_id=user_id,
                    role=message.role,
                    content=message.content,
                    metadata=message.extra_metadata,
                    input_tokens=usage_info.get("prompt_tokens"),
                    output_tokens=usage_info.get("completion_tokens"),
                    cost=usage_info.get("cost"),
                    provider=usage_info.get("provider_used"),
                )
            )

            # Generate correlation ID for tracking
            from chatter.utils.correlation import get_correlation_id

            correlation_id = get_correlation_id()

            # Return execution result
            result = {
                "id": correlation_id,
                "definition_id": definition.id,
                "owner_id": user_id,
                "status": "completed",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "input_data": input_data,
                "output_data": {
                    "message": message.content,
                    "conversation_id": conversation.id,
                    "message_id": saved_message.id,
                    "capabilities_used": spec.capabilities.__dict__,
                },
                "metadata": {
                    "execution_time_ms": usage_info.get(
                        "execution_time_ms", 0
                    ),
                    "nodes_executed": usage_info.get(
                        "nodes_executed", 0
                    ),
                    "workflow_spec": spec.__dict__,
                    "usage_info": usage_info,
                },
            }

            logger.info(
                f"Successfully executed workflow definition {definition.id}"
            )
            return result

        except Exception as e:
            logger.error(
                f"Failed to execute workflow definition {definition.id}: {e}",
                exc_info=True,
            )

            # Generate correlation ID for failed execution
            from chatter.utils.correlation import get_correlation_id

            correlation_id = get_correlation_id()

            # Return error result
            return {
                "id": correlation_id,
                "definition_id": definition.id,
                "owner_id": user_id,
                "status": "failed",
                "started_at": datetime.utcnow().isoformat(),
                "completed_at": datetime.utcnow().isoformat(),
                "input_data": input_data,
                "output_data": {
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                "metadata": {
                    "execution_time_ms": 0,
                    "nodes_executed": 0,
                    "error_details": str(e),
                },
            }

    async def _convert_chat_workflow_request(
        self, user_id: str, request: ChatWorkflowRequest
    ) -> tuple[WorkflowSpec, Conversation]:
        """Convert ChatWorkflowRequest to WorkflowSpec and get conversation."""
        from chatter.schemas.chat import (
            ConversationCreate,
        )
        from chatter.services.conversation import ConversationService

        # Setup conversation service
        conversation_service = ConversationService(self.session)

        # Get or create conversation
        if request.conversation_id:
            conversation = await conversation_service.get_conversation(
                request.conversation_id, user_id, include_messages=True
            )
        else:
            # Create new conversation
            conv_data = ConversationCreate(
                title=(
                    request.message[:50] + "..."
                    if len(request.message) > 50
                    else request.message
                ),
                description=None,
                profile_id=request.profile_id,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                workflow_config=(
                    request.workflow_config.model_dump()
                    if request.workflow_config
                    else None
                ),
                extra_metadata=None,
            )
            conversation = (
                await conversation_service.create_conversation(
                    user_id, conv_data
                )
            )

        # Create WorkflowSpec based on request type
        if request.workflow_definition_id:
            # Get workflow definition and create spec from it
            from chatter.services.workflow_management import (
                WorkflowManagementService,
            )

            workflow_service = WorkflowManagementService(self.session)
            definition = await workflow_service.get_workflow_definition(
                request.workflow_definition_id, user_id
            )
            spec = WorkflowSpec.from_workflow_definition(definition)
        elif request.workflow_template_name:
            # Get template and create spec from it
            template = await self.template_manager.get_template(
                request.workflow_template_name, user_id
            )
            # Convert template to spec (simplified for now)
            from chatter.core.workflow_capabilities import (
                WorkflowCapabilities,
            )

            capabilities = WorkflowCapabilities.from_workflow_type(
                template.workflow_type or "simple_chat"
            )
            spec = WorkflowSpec(
                capabilities=capabilities,
                provider=request.provider or "openai",
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1000,
                system_prompt=request.system_prompt_override,
                name=template.name,
                description=template.description,
            )
        elif request.workflow_config:
            # Create spec from chat workflow config
            spec = WorkflowSpec.from_chat_workflow_config(
                request.workflow_config
            )
            # Apply request overrides
            if request.provider:
                spec.provider = request.provider
            if request.temperature is not None:
                spec.temperature = request.temperature
            if request.max_tokens:
                spec.max_tokens = request.max_tokens
            if request.system_prompt_override:
                spec.system_prompt = request.system_prompt_override
        else:
            # Default to plain workflow
            from chatter.core.workflow_capabilities import (
                WorkflowCapabilities,
            )

            spec = WorkflowSpec(
                capabilities=WorkflowCapabilities(),
                provider=request.provider or "openai",
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1000,
                system_prompt=request.system_prompt_override,
            )

        return spec, conversation
