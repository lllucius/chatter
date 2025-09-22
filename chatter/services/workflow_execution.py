"""Modern workflow execution service.

This service provides the modern workflow execution system using the
new flexible architecture with support for all node types.
"""

from __future__ import annotations

import time
from typing import Any
from collections.abc import AsyncGenerator

from langchain_core.messages import BaseMessage, HumanMessage

from chatter.core.enhanced_memory_manager import EnhancedMemoryManager
from chatter.core.enhanced_tool_executor import EnhancedToolExecutor
from chatter.core.langgraph import workflow_manager
from chatter.core.workflow_graph_builder import create_simple_workflow_definition
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid
from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.services.llm import LLMService
from chatter.services.message import MessageService
from chatter.utils.logging import get_logger
from datetime import UTC

logger = get_logger(__name__)


class WorkflowExecutionService:
    """Modern workflow execution service."""

    def __init__(
        self,
        llm_service: LLMService,
        message_service: MessageService,
        session,
    ):
        """Initialize the workflow execution service."""
        self.llm_service = llm_service
        self.message_service = message_service
        self.session = session

        # Initialize enhanced components
        self.memory_manager = EnhancedMemoryManager()
        self.tool_executor = EnhancedToolExecutor()

    async def execute_chat_workflow(
        self,
        user_id: str,
        request: Any,
    ) -> tuple[Conversation, Message]:
        """Execute chat workflow - API wrapper method."""
        # Get or create conversation
        conversation = await self._get_or_create_conversation(user_id, request)

        # Convert request to ChatRequest
        chat_request = self._convert_to_chat_request(request)

        # Execute the actual workflow
        message, result = await self._execute_chat_workflow_internal(
            conversation=conversation,
            chat_request=chat_request,
            user_id=user_id,
        )

        return conversation, message

    async def _execute_chat_workflow_internal(
        self,
        conversation: Conversation,
        chat_request: ChatRequest,
        user_id: str,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a chat workflow using the modern system."""
        start_time = time.time()

        try:
            # Get LLM
            llm = await self.llm_service.get_llm(
                provider=chat_request.provider,
                model=chat_request.model,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Get tools and retriever if needed
            tools = None
            retriever = None

            if chat_request.enable_tools:
                # TODO: Get tools from tool registry
                tools = []

            if chat_request.enable_retrieval:
                # TODO: Get retriever from vector store
                retriever = None

            # Create workflow using modern system
            workflow = await workflow_manager.create_workflow(
                llm=llm,
                enable_retrieval=chat_request.enable_retrieval,
                enable_tools=chat_request.enable_tools,
                enable_memory=chat_request.enable_memory,
                system_message=chat_request.system_prompt_override,
                retriever=retriever,
                tools=tools,
                memory_window=getattr(chat_request, 'memory_window', 10),
                max_tool_calls=getattr(chat_request, 'max_tool_calls', 10),
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation history
            messages = await self._get_conversation_messages(conversation)

            # Add new user message
            messages.append(HumanMessage(content=chat_request.message))

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {
                    "provider": chat_request.provider,
                    "model": chat_request.model,
                    "temperature": chat_request.temperature,
                    "max_tokens": chat_request.max_tokens,
                },
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
            )

            # Extract AI response
            ai_message = self._extract_ai_response(result)

            # Create and save message
            message = await self._create_and_save_message(
                conversation=conversation,
                content=ai_message.content,
                role=MessageRole.ASSISTANT,
                metadata=result.get("metadata", {}),
            )

            # Calculate usage info
            execution_time_ms = int((time.time() - start_time) * 1000)
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "tool_calls": result.get("tool_call_count", 0),
                "workflow_execution": True,
                "modern_system": True,
                **result.get("metadata", {}),
            }

            return message, usage_info

        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            # Create error message
            error_message = await self._create_and_save_message(
                conversation=conversation,
                content=f"I encountered an error: {str(e)}",
                role=MessageRole.ASSISTANT,
                metadata={"error": True, "error_message": str(e)},
            )

            execution_time_ms = int((time.time() - start_time) * 1000)
            usage_info = {
                "execution_time_ms": execution_time_ms,
                "error": True,
                "error_message": str(e),
            }

            return error_message, usage_info

    async def execute_chat_workflow_streaming(
        self,
        user_id: str,
        request: Any,  # ChatWorkflowRequest
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute a chat workflow with streaming using the modern system."""
        try:
            # Get or create conversation
            conversation = await self._get_or_create_conversation(user_id, request)

            # Convert to ChatRequest for compatibility
            chat_request = self._convert_to_chat_request(request)

            # Get LLM
            llm = await self.llm_service.get_llm(
                provider=chat_request.provider,
                model=chat_request.model,
                temperature=chat_request.temperature,
                max_tokens=chat_request.max_tokens,
            )

            # Create workflow
            workflow = await workflow_manager.create_workflow(
                llm=llm,
                enable_retrieval=chat_request.enable_retrieval,
                enable_tools=chat_request.enable_tools,
                enable_memory=chat_request.enable_memory,
                enable_streaming=True,
                system_message=chat_request.system_prompt_override,
                user_id=user_id,
                conversation_id=conversation.id,
            )

            # Get conversation history and create initial state
            messages = await self._get_conversation_messages(conversation)
            messages.append(HumanMessage(content=request.message))

            initial_state: WorkflowNodeContext = {
                "messages": messages,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {},
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Stream workflow execution
            content_buffer = ""
            async for update in workflow_manager.stream_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=conversation.id,
                enable_llm_streaming=True,
            ):
                if isinstance(update, dict) and "messages" in update:
                    # Extract streaming content
                    messages = update["messages"]
                    if messages:
                        last_message = messages[-1]
                        if hasattr(last_message, "content"):
                            new_content = last_message.content[len(content_buffer):]
                            if new_content:
                                content_buffer += new_content
                                yield StreamingChatChunk(
                                    type="content",
                                    content=new_content,
                                    metadata=update.get("metadata", {}),
                                )

            # Send completion chunk
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={"streaming_complete": True},
            )

        except Exception as e:
            logger.error(f"Streaming workflow execution failed: {e}")
            yield StreamingChatChunk(
                type="error",
                content=f"Error: {str(e)}",
                metadata={"error": True},
            )

    async def execute_custom_workflow(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        message: str,
        user_id: str,
        provider: str = "anthropic",
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs,
    ) -> dict[str, Any]:
        """Execute a custom workflow definition."""
        try:
            # Get LLM
            llm = await self.llm_service.get_llm(provider=provider, model=model)

            # Create custom workflow
            workflow = await workflow_manager.create_custom_workflow(
                nodes=nodes,
                edges=edges,
                llm=llm,
                **kwargs,
            )

            # Create initial state
            initial_state: WorkflowNodeContext = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "conversation_id": generate_ulid(),
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": {},
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
            )

            return result

        except Exception as e:
            logger.error(f"Custom workflow execution failed: {e}")
            raise

    async def execute_workflow_definition(
        self,
        definition: Any,
        input_data: dict[str, Any],
        user_id: str,
    ) -> dict[str, Any]:
        """Execute a workflow from a stored definition."""
        try:
            # Get LLM from default settings for now
            llm = await self.llm_service.get_llm(
                provider="anthropic",
                model="claude-3-5-sonnet-20241022",
                temperature=0.1,
                max_tokens=2048,
            )

            # Extract message from input data
            message = input_data.get("message", "")
            if not message:
                raise ValueError("No message provided in input_data")

            # Create simple workflow definition for now
            # TODO: Parse actual definition structure when workflow definitions are implemented
            workflow_def = create_simple_workflow_definition(
                enable_memory=True,
                enable_retrieval=False,
                enable_tools=False,
            )

            # Create workflow from definition
            workflow = await workflow_manager.create_workflow_from_definition(
                definition=workflow_def,
                llm=llm,
            )

            # Create execution context
            context: WorkflowNodeContext = {
                "messages": [HumanMessage(content=message)],
                "user_id": user_id,
                "conversation_id": generate_ulid(),
                "retrieval_context": None,
                "conversation_summary": None,
                "tool_call_count": 0,
                "metadata": input_data.get("metadata", {}),
                "variables": {},
                "loop_state": {},
                "error_state": {},
                "conditional_results": {},
                "execution_history": [],
            }

            # Execute workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=context,
                thread_id=generate_ulid(),
            )

            # Extract response
            ai_message = self._extract_ai_response(result)

            return {
                "response": ai_message.content,
                "conversation_id": context["conversation_id"],
                "user_id": user_id,
                "metadata": result.get("metadata", {}),
            }

        except Exception as e:
            logger.error(f"Workflow definition execution failed: {e}")
            raise

    async def _get_conversation_messages(self, conversation: Conversation) -> list[BaseMessage]:
        """Get conversation history as LangChain messages."""
        messages = []

        # Get recent messages from conversation
        # TODO: Implement pagination and limits
        conversation_messages = []  # await self.message_service.get_messages(conversation.id)

        for msg in conversation_messages:
            if msg.role == MessageRole.USER:
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == MessageRole.ASSISTANT:
                from langchain_core.messages import AIMessage
                messages.append(AIMessage(content=msg.content))

        return messages

    def _extract_ai_response(self, workflow_result: dict[str, Any]) -> BaseMessage:
        """Extract AI response from workflow result."""
        messages = workflow_result.get("messages", [])

        # Find the last AI message
        for message in reversed(messages):
            if hasattr(message, "content") and message.content:
                return message

        # Fallback
        from langchain_core.messages import AIMessage
        return AIMessage(content="No response generated")

    async def _create_and_save_message(
        self,
        conversation: Conversation,
        content: str,
        role: MessageRole,
        metadata: dict[str, Any] | None = None,
    ) -> Message:
        """Create and save a message to the conversation."""
        from datetime import datetime

        # Get next sequence number (for now, using a simple increment)
        # TODO: Get proper sequence number from conversation message count
        message_count = getattr(conversation, 'message_count', 0)
        if message_count is None:
            message_count = 0
        sequence_number = message_count + 1

        # Create message object with all required fields
        # Note: Base class automatically sets id, created_at, updated_at, but we need to
        # ensure all the Message-specific required fields are set
        message = Message(
            id=generate_ulid(),
            conversation_id=conversation.id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            rating_count=0,  # Default value for required field
            extra_metadata=metadata or {},
        )

        # The Base class will automatically set created_at and updated_at
        # But to be safe, let's explicitly set created_at if it's not set
        if not hasattr(message, 'created_at') or message.created_at is None:
            message.created_at = datetime.now(UTC)

        # TODO: Save to database via message service
        # await self.message_service.create_message(message)

        return message

    async def _get_or_create_conversation(self, user_id: str, request: Any) -> Conversation:
        """Get existing conversation or create new one."""
        conversation_id = getattr(request, 'conversation_id', None)

        if conversation_id:
            # TODO: Get existing conversation
            # conversation = await self.conversation_service.get_conversation(conversation_id)
            pass

        # Create new conversation
        conversation = Conversation(
            id=generate_ulid(),
            user_id=user_id,
            title=getattr(request, 'title', 'New Conversation'),
            metadata={},
        )

        # TODO: Save to database
        # await self.conversation_service.create_conversation(conversation)

        return conversation

    def _convert_to_chat_request(self, request: Any) -> ChatRequest:
        """Convert workflow request to ChatRequest for compatibility."""
        return ChatRequest(
            message=request.message,
            conversation_id=getattr(request, 'conversation_id', None),
            provider=getattr(request, 'provider', 'anthropic'),
            model=getattr(request, 'model', 'claude-3-5-sonnet-20241022'),
            temperature=getattr(request, 'temperature', None),
            max_tokens=getattr(request, 'max_tokens', None),
            system_prompt_override=getattr(request, 'system_prompt_override', None),
            enable_retrieval=getattr(request, 'enable_retrieval', False),
            enable_tools=getattr(request, 'enable_tools', False),
            enable_memory=getattr(request, 'enable_memory', True),
        )


# Factory function for dependency injection
def create_workflow_execution_service(
    llm_service: LLMService,
    message_service: MessageService,
    session,
) -> WorkflowExecutionService:
    """Create modern workflow execution service."""
    return WorkflowExecutionService(
        llm_service=llm_service,
        message_service=message_service,
        session=session,
    )
