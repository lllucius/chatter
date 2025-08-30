"""Core chat service orchestrating conversations, messages, and workflows."""

from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.langgraph import ConversationState, workflow_manager
from chatter.core.workflow_performance import (
    lazy_tool_loader,
    performance_monitor,
    workflow_cache,
)
from chatter.core.workflow_templates import WorkflowTemplateManager
from chatter.core.workflow_validation import WorkflowValidator
from chatter.models.conversation import (
    Conversation,
    ConversationStatus,
    Message,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.schemas.chat import (
    ConversationCreate as ConversationCreateSchema,
)
from chatter.schemas.chat import (
    ConversationUpdate as ConversationUpdateSchema,
)
from chatter.services.llm import LLMProviderError, LLMService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ChatError(Exception):
    """Chat error for invalid operations or failed processing."""


class ConversationNotFoundError(Exception):
    """Raised when a conversation is not found or inaccessible."""


class ChatService:
    """Service layer to manage conversations, messages, and chat interactions."""

    def __init__(self, session: AsyncSession, llm_service: LLMService) -> None:
        self.session = session
        self.llm_service = llm_service

    # ------------
    # Conversation CRUD
    # ------------

    async def create_conversation(
        self, user_id: str, data: ConversationCreateSchema
    ) -> Conversation:
        """Create a new conversation for a user."""
        conv = Conversation(
            user_id=user_id,
            title=data.title,
            description=data.description,
            status=ConversationStatus.ACTIVE,
            profile_id=data.profile_id,
            system_prompt=data.system_prompt,
            enable_retrieval=bool(data.enable_retrieval),
        )
        self.session.add(conv)
        await self.session.flush()
        await self.session.refresh(conv)
        return conv

    async def list_conversations(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> tuple[list[Conversation], int]:
        """List conversations for a user with pagination."""
        from sqlalchemy import func, select

        q = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        total_q = select(func.count()).select_from(
            select(Conversation.id)
            .where(Conversation.user_id == user_id)
            .subquery()
        )

        result = await self.session.execute(q.limit(limit).offset(offset))
        conversations: list[Conversation] = list(result.scalars().all())

        total_result = await self.session.execute(total_q)
        total = int(total_result.scalar() or 0)

        return conversations, total

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = False,
    ) -> Conversation | None:
        """Get a conversation by ID if it belongs to the user."""
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload

        q = select(Conversation).where(
            Conversation.id == conversation_id, Conversation.user_id == user_id
        )
        if include_messages:
            q = q.options(selectinload(Conversation.messages))

        res = await self.session.execute(q)
        conv = res.scalars().first()
        return conv

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update: ConversationUpdateSchema,
    ) -> Conversation:
        """Update conversation metadata."""
        conv = await self.get_conversation(conversation_id, user_id)
        if not conv:
            raise ConversationNotFoundError()

        if update.title is not None:
            conv.title = update.title
        if update.description is not None:
            conv.description = update.description
        if update.status is not None:
            conv.status = update.status

        await self.session.flush()
        await self.session.refresh(conv)
        return conv

    async def delete_conversation(self, conversation_id: str, user_id: str) -> None:
        """Delete a conversation and its messages."""
        conv = await self.get_conversation(conversation_id, user_id)
        if not conv:
            raise ConversationNotFoundError()
        await self.session.delete(conv)
        await self.session.flush()

    async def get_conversation_messages(
        self, conversation_id: str, user_id: str
    ) -> list[Message]:
        """Return messages ordered by sequence number."""
        conv = await self.get_conversation(conversation_id, user_id, include_messages=True)
        if not conv:
            raise ConversationNotFoundError()

        # Ensure ordered by sequence_number
        return sorted(conv.messages, key=lambda m: m.sequence_number)

    # ------------
    # Message CRUD
    # ------------

    async def add_message_to_conversation(
        self, conversation_id: str, user_id: str, content: str, role: str = "user"
    ) -> Message:
        """Append a message to the conversation."""
        from sqlalchemy import text

        conv = await self.get_conversation(conversation_id, user_id)
        if not conv:
            raise ConversationNotFoundError()

        # Use database-level sequence number generation to avoid race conditions
        # This query gets the next sequence number for the conversation
        # Note: The unique constraint on (conversation_id, sequence_number) handles race conditions
        result = await self.session.execute(
            text("""
                SELECT COALESCE(MAX(sequence_number), 0) + 1 as next_seq
                FROM messages
                WHERE conversation_id = :conversation_id
            """),
            {"conversation_id": conv.id}
        )
        seq = result.scalar()

        msg = Message(
            conversation_id=conv.id,
            role=role,
            content=content,
            sequence_number=seq,
        )
        self.session.add(msg)

        # Update aggregates (basic: message_count)
        conv.message_count = (conv.message_count or 0) + 1

        await self.session.flush()
        await self.session.refresh(msg)
        return msg

    async def delete_message(self, conversation_id: str, message_id: str, user_id: str) -> None:
        """Delete a message if it belongs to the user and conversation."""
        from sqlalchemy import select

        conv = await self.get_conversation(conversation_id, user_id)
        if not conv:
            raise ConversationNotFoundError()

        q = select(Message).where(Message.id == message_id, Message.conversation_id == conv.id)
        res = await self.session.execute(q)
        msg = res.scalars().first()
        if not msg:
            raise ConversationNotFoundError()

        await self.session.delete(msg)
        await self.session.flush()

    # ------------
    # Plain chat (legacy/basic)
    # ------------

    async def chat(self, user_id: str, chat_request: ChatRequest) -> tuple[Conversation, Message]:
        """Basic chat without workflows."""
        # Ensure conversation
        conversation = None
        if chat_request.conversation_id:
            conversation = await self.get_conversation(chat_request.conversation_id, user_id, include_messages=True)
        if not conversation:
            # Create a default conversation
            conversation = await self.create_conversation(
                user_id,
                ConversationCreateSchema(
                    title="New Conversation",
                    description=None,
                    profile_id=chat_request.profile_id,
                    system_prompt=chat_request.system_prompt_override,
                    enable_retrieval=bool(chat_request.enable_retrieval),
                ),
            )

        # User message
        user_msg = await self.add_message_to_conversation(conversation.id, user_id, chat_request.message, role="user")

        # Prepare messages for LLM
        msgs: list[BaseMessage] = self.llm_service.convert_conversation_to_messages(
            conversation, [*conversation.messages, user_msg]
        )

        # Provider
        try:
            provider = (
                await self.llm_service.get_provider(chat_request.provider)
                if chat_request.provider
                else await self.llm_service.get_default_provider()
            )
        except LLMProviderError as e:
            raise ChatError(str(e)) from e

        # Overrides
        kwargs: dict[str, Any] = {}
        if chat_request.temperature is not None:
            kwargs["temperature"] = chat_request.temperature
        if chat_request.max_tokens is not None:
            kwargs["max_tokens"] = chat_request.max_tokens

        content, usage = await self.llm_service.generate_response(msgs, provider=provider, **kwargs)

        # Persist assistant message
        assistant_msg = await self.add_message_to_conversation(conversation.id, user_id, content, role="assistant")

        # Store usage metrics when available
        self._apply_usage_to_message(assistant_msg, usage, provider)

        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation, assistant_msg

    async def chat_streaming(self, user_id: str, chat_request: ChatRequest) -> AsyncGenerator[dict[str, Any], None]:
        """Basic streaming without workflows (token-level from provider)."""
        # Ensure conversation
        conversation = None
        if chat_request.conversation_id:
            conversation = await self.get_conversation(chat_request.conversation_id, user_id, include_messages=True)
        if not conversation:
            conversation = await self.create_conversation(
                user_id,
                ConversationCreateSchema(
                    title="New Conversation",
                    description=None,
                    profile_id=chat_request.profile_id,
                    system_prompt=chat_request.system_prompt_override,
                    enable_retrieval=bool(chat_request.enable_retrieval),
                ),
            )

        # Persist user message first
        user_msg = await self.add_message_to_conversation(conversation.id, user_id, chat_request.message, role="user")

        # Prepare messages for LLM (include the just-added user_msg explicitly)
        msgs: list[BaseMessage] = self.llm_service.convert_conversation_to_messages(
            conversation, [*conversation.messages, user_msg]
        )

        # Provider
        try:
            provider = (
                await self.llm_service.get_provider(chat_request.provider)
                if chat_request.provider
                else await self.llm_service.get_default_provider()
            )
        except LLMProviderError as e:
            yield {"type": "error", "error": str(e)}
            return

        # Overrides
        kwargs: dict[str, Any] = {}
        if chat_request.temperature is not None:
            kwargs["temperature"] = chat_request.temperature
        if chat_request.max_tokens is not None:
            kwargs["max_tokens"] = chat_request.max_tokens

        # Buffer for final assistant content (for persistence)
        full_content = ""

        async for chunk in self.llm_service.generate_streaming_response(
            msgs, provider=provider, **kwargs
        ):
            if chunk.get("type") == "token" and chunk.get("content"):
                full_content += chunk["content"]
            yield chunk

        # Persist the assistant message if any content accumulated
        if full_content:
            await self.add_message_to_conversation(conversation.id, user_id, full_content, role="assistant")
            await self.session.flush()

    async def chat_with_template(
        self, user_id: str, chat_request: ChatRequest, template_name: str
    ) -> tuple[Conversation, Message]:
        """Run a chat using a pre-configured workflow template."""
        try:
            # Get template configuration
            template = WorkflowTemplateManager.get_template(template_name)

            # Ensure conversation
            conversation = None
            if chat_request.conversation_id:
                conversation = await self.get_conversation(chat_request.conversation_id, user_id, include_messages=True)
            if not conversation:
                conversation = await self.create_conversation(
                    user_id,
                    ConversationCreateSchema(
                        title=f"New {template.description}",
                        description=f"Using template: {template_name}",
                        profile_id=chat_request.profile_id,
                        system_prompt=template.default_params.get("system_message"),
                        enable_retrieval=template.workflow_type in ["rag", "full"],
                    ),
                )

            # Resolve provider
            provider_name = await self._resolve_provider_name(conversation, chat_request)

            # Get required resources
            retriever = None
            tools = None

            if template.required_retrievers:
                retriever = await self._maybe_get_retriever(conversation, chat_request)
                if not retriever:
                    logger.warning(
                        "Template requires retriever but none available",
                        template=template_name,
                        required_retrievers=template.required_retrievers
                    )

            if template.required_tools:
                # Load only required tools for efficiency
                tools = await lazy_tool_loader.get_tools(template.required_tools)
                missing_tools = [
                    tool for tool in template.required_tools
                    if not any(getattr(t, 'name', '') == tool for t in tools)
                ]
                if missing_tools:
                    logger.warning(
                        "Some required tools not available",
                        template=template_name,
                        missing_tools=missing_tools
                    )

            # Create workflow from template
            workflow = await WorkflowTemplateManager.create_workflow_from_template(
                template_name=template_name,
                llm_service=self.llm_service,
                provider_name=provider_name,
                overrides=getattr(chat_request, 'template_overrides', None),
                retriever=retriever,
                tools=tools
            )

            # Persist user message
            user_msg = await self.add_message_to_conversation(conversation.id, user_id, chat_request.message, role="user")

            # Prepare messages
            history_msgs: list[BaseMessage] = self.llm_service.convert_conversation_to_messages(
                conversation, conversation.messages + [user_msg]
            )

            # Initial state
            initial_state: ConversationState = {
                "messages": history_msgs,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "tool_calls": [],
                "metadata": {"template_used": template_name},
                "conversation_summary": None,
                "parent_conversation_id": None,
                "branch_id": None,
                "memory_context": {},
                "workflow_template": template_name,
                "a_b_test_group": None,
            }

            # Run workflow
            result = await workflow_manager.run_workflow(
                workflow=workflow, initial_state=initial_state, thread_id=conversation.id
            )

            # Extract response
            ai_message = self._extract_last_ai_message(result.get("messages", []))
            content = ai_message.content if isinstance(ai_message, AIMessage) else (str(ai_message) if ai_message else "")

            # Persist assistant message
            assistant = await self.add_message_to_conversation(conversation.id, user_id, content, role="assistant")

            await self.session.flush()
            await self.session.refresh(conversation)

            return conversation, assistant

        except Exception as e:
            logger.error(
                "Template workflow execution failed",
                template=template_name,
                error=str(e),
                user_id=user_id
            )
            raise

    def get_available_templates(self) -> dict[str, Any]:
        """Get information about available workflow templates."""
        return WorkflowTemplateManager.get_template_info()

    def get_performance_stats(self) -> dict[str, Any]:
        """Get workflow performance statistics."""
        return performance_monitor.get_performance_stats()

    # ------------
    # Unified workflow chat
    # ------------

    async def chat_with_workflow(
        self, user_id: str, chat_request: ChatRequest, workflow_type: str = "basic"
    ) -> tuple[Conversation, Message]:
        """Run a chat using LangGraph workflows: basic/plain, rag, tools, full."""
        # Generate unique ID for performance tracking
        workflow_id = str(uuid.uuid4())
        performance_monitor.start_workflow(workflow_id, workflow_type)

        try:
            # Normalize workflow_type
            mode = self._normalize_workflow(workflow_type)

            # Ensure conversation
            conversation = None
            if chat_request.conversation_id:
                conversation = await self.get_conversation(chat_request.conversation_id, user_id, include_messages=True)
            if not conversation:
                conversation = await self.create_conversation(
                    user_id,
                    ConversationCreateSchema(
                        title="New Conversation",
                        description=None,
                        profile_id=chat_request.profile_id,
                        system_prompt=chat_request.system_prompt_override,
                        enable_retrieval=bool(chat_request.enable_retrieval),
                    ),
                )

            # Persist user message
            user_msg = await self.add_message_to_conversation(conversation.id, user_id, chat_request.message, role="user")

            # Prepare lc messages
            history_msgs: list[BaseMessage] = self.llm_service.convert_conversation_to_messages(
                conversation, conversation.messages + [user_msg]
            )

            # Resolve provider name (string) for workflow factory
            provider_name = await self._resolve_provider_name(conversation, chat_request)

            # Resolve retriever/tools as needed
            retriever = await self._maybe_get_retriever(conversation, chat_request) if mode in ("rag", "full") else None
            tools = await self._maybe_get_tools(conversation, chat_request) if mode in ("tools", "full") else None

            # Validate workflow configuration
            try:
                WorkflowValidator.validate_workflow_request(
                    workflow_type=self._to_public_mode(mode),
                    retriever=retriever,
                    tools=tools,
                    system_message=chat_request.system_prompt_override,
                    enable_memory=False  # Conversations handle memory differently
                )
            except Exception as validation_error:
                logger.warning(
                    "Workflow validation failed",
                    workflow_type=workflow_type,
                    error=str(validation_error)
                )
                # Continue execution but log the validation issue

            # Check workflow cache for performance optimization
            workflow_config = {
                "system_message": chat_request.system_prompt_override or getattr(conversation, "system_prompt", None),
                "enable_memory": False,
                "retriever_available": retriever is not None,
                "tools_count": len(tools) if tools else 0
            }

            cached_workflow = workflow_cache.get(
                provider_name=provider_name,
                workflow_type=self._to_public_mode(mode),
                config=workflow_config
            )

            if cached_workflow:
                workflow = cached_workflow
                logger.debug("Using cached workflow", workflow_id=workflow_id)
            else:
                # Build workflow
                workflow = await self.llm_service.create_langgraph_workflow(
                    provider_name=provider_name,
                    workflow_type=self._to_public_mode(mode),  # plain|rag|tools|full
                    system_message=chat_request.system_prompt_override or getattr(conversation, "system_prompt", None),
                    retriever=retriever,
                    tools=tools,
                    enable_memory=False,
                )

                # Cache the workflow for future use
                workflow_cache.put(
                    provider_name=provider_name,
                    workflow_type=self._to_public_mode(mode),
                    config=workflow_config,
                    workflow=workflow
                )
                logger.debug("Workflow compiled and cached", workflow_id=workflow_id)

            # Initial state
            initial_state: ConversationState = {
                "messages": history_msgs,
                "user_id": user_id,
                "conversation_id": conversation.id,
                "retrieval_context": None,
                "tool_calls": [],
                "metadata": {},
                "conversation_summary": None,
                "parent_conversation_id": None,
                "branch_id": None,
                "memory_context": {},
                "workflow_template": None,
                "a_b_test_group": None,
            }

            # Run the graph
            result = await workflow_manager.run_workflow(
                workflow=workflow, initial_state=initial_state, thread_id=conversation.id
            )

            # Get the last AI message from result state
            ai_message = self._extract_last_ai_message(result.get("messages", []))
            content = ai_message.content if isinstance(ai_message, AIMessage) else (str(ai_message) if ai_message else "")

            # Persist assistant message
            assistant = await self.add_message_to_conversation(conversation.id, user_id, content, role="assistant")

            await self.session.flush()
            await self.session.refresh(conversation)

            # Track successful completion
            performance_monitor.end_workflow(workflow_id, success=True)

            return conversation, assistant

        except Exception as e:
            # Track failed execution
            error_type = type(e).__name__
            performance_monitor.end_workflow(workflow_id, success=False, error_type=error_type)

            logger.error(
                "Workflow execution failed",
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                error=str(e),
                user_id=user_id
            )
            raise

    async def chat_workflow_streaming(
        self, user_id: str, chat_request: ChatRequest, workflow_type: str = "basic"
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Stream workflow execution (coarse-grained, node-level, not token-level)."""
        mode = self._normalize_workflow(workflow_type)

        # Ensure conversation
        conversation = None
        if chat_request.conversation_id:
            conversation = await self.get_conversation(chat_request.conversation_id, user_id, include_messages=True)
        if not conversation:
            conversation = await self.create_conversation(
                user_id,
                ConversationCreateSchema(
                    title="New Conversation",
                    description=None,
                    profile_id=chat_request.profile_id,
                    system_prompt=chat_request.system_prompt_override,
                    enable_retrieval=bool(chat_request.enable_retrieval),
                ),
            )

        # Persist user message
        user_msg = await self.add_message_to_conversation(conversation.id, user_id, chat_request.message, role="user")

        # Prepare lc messages
        history_msgs: list[BaseMessage] = self.llm_service.convert_conversation_to_messages(
            conversation, conversation.messages + [user_msg]
        )

        # Provider for workflow construction
        provider_name = await self._resolve_provider_name(conversation, chat_request)

        # Resolve retriever/tools
        retriever = await self._maybe_get_retriever(conversation, chat_request) if mode in ("rag", "full") else None
        tools = await self._maybe_get_tools(conversation, chat_request) if mode in ("tools", "full") else None

        # Build workflow
        workflow = await self.llm_service.create_langgraph_workflow(
            provider_name=provider_name,
            workflow_type=self._to_public_mode(mode),
            system_message=chat_request.system_prompt_override or getattr(conversation, "system_prompt", None),
            retriever=retriever,
            tools=tools,
            enable_memory=False,
        )

        # Initial state
        initial_state: ConversationState = {
            "messages": history_msgs,
            "user_id": user_id,
            "conversation_id": conversation.id,
            "retrieval_context": None,
            "tool_calls": [],
            "metadata": {},
            "conversation_summary": None,
            "parent_conversation_id": None,
            "branch_id": None,
            "memory_context": {},
            "workflow_template": None,
            "a_b_test_group": None,
        }

        # Stream the graph. This yields graph events rather than token chunks.
        full_content = ""
        node_outputs = []
        workflow_start_time = None

        try:
            workflow_start_time = __import__('time').time()

            async for event in workflow_manager.stream_workflow(
                workflow=workflow, initial_state=initial_state, thread_id=conversation.id
            ):
                # Extract node information for better debugging
                if isinstance(event, dict):
                    for node_name, _node_data in event.items():
                        if node_name != "__end__":  # Skip end marker
                            # Emit node start event
                            yield {
                                "type": "node_start",
                                "node": node_name,
                                "conversation_id": conversation.id,
                            }

                # Try to extract any AIMessage appended in this event
                values = event.get("values") or event.get("state") or {}
                msgs = values.get("messages") if isinstance(values, dict) else None
                if msgs:
                    last_ai = self._extract_last_ai_message(msgs)
                    if last_ai and isinstance(last_ai, AIMessage) and last_ai.content:
                        # Emit content as token chunks for better streaming experience
                        content = last_ai.content
                        if content != full_content:  # Only emit new content
                            new_content = content[len(full_content):] if full_content else content
                            full_content = content

                            # Emit as token chunk
                            yield {
                                "type": "token",
                                "content": new_content,
                                "conversation_id": conversation.id,
                            }

                            node_outputs.append({
                                "node": list(event.keys())[0] if isinstance(event, dict) else "unknown",
                                "content": new_content,
                                "timestamp": __import__('time').time()
                            })

                # Emit node completion event if we have node data
                if isinstance(event, dict):
                    for node_name, _node_data in event.items():
                        if node_name != "__end__":
                            yield {
                                "type": "node_complete",
                                "node": node_name,
                                "conversation_id": conversation.id,
                            }

            # Calculate timing
            workflow_end_time = __import__('time').time()
            response_time_ms = int((workflow_end_time - workflow_start_time) * 1000) if workflow_start_time else None

            # Emit enhanced usage summary
            yield {
                "type": "usage",
                "usage": {
                    "response_time_ms": response_time_ms,
                    "workflow_type": workflow_type,
                    "nodes_executed": len(node_outputs),
                    "total_content_length": len(full_content),
                    "conversation_id": conversation.id,
                }
            }

        except Exception as e:
            logger.error("Workflow streaming failed", error=str(e), conversation_id=conversation.id)

            # Create proper workflow error
            if "timeout" in str(e).lower():
                error_msg = f"Workflow execution timed out: {str(e)}"
            elif "validation" in str(e).lower():
                error_msg = f"Workflow validation failed: {str(e)}"
            else:
                error_msg = f"Workflow execution failed: {str(e)}"

            yield {
                "type": "error",
                "error": error_msg,
                "error_code": "WORKFLOW_EXECUTION_ERROR",
                "conversation_id": conversation.id,
            }
            return

        # Persist final assistant message
        if full_content:
            await self.add_message_to_conversation(conversation.id, user_id, full_content, role="assistant")
            await self.session.flush()

    # ------------
    # Helpers
    # ------------

    def _apply_usage_to_message(self, message: Message, usage: dict[str, Any], provider: Any) -> None:
        """Attach usage fields to message when available."""
        try:
            if not usage:
                return
            message.model_used = usage.get("model")
            message.provider_used = usage.get("provider")
            message.response_time_ms = usage.get("response_time_ms")
            message.prompt_tokens = usage.get("prompt_tokens")
            message.completion_tokens = usage.get("completion_tokens")
            message.total_tokens = usage.get("total_tokens")
        except Exception:
            # Best effort; don't fail chat on usage persistence
            pass

    async def _resolve_provider_name(self, conversation: Conversation, chat_request: ChatRequest) -> str:
        """Decide which provider name string to use to build the workflow ('openai', 'anthropic', ...)."""
        # Prefer explicit request override
        if chat_request.provider:
            return chat_request.provider

        # Then conversation setting if available
        if getattr(conversation, "llm_provider", None):
            return conversation.llm_provider  # type: ignore[return-value]

        # Fall back to configured default or first available
        available = self.llm_service.list_available_providers()
        from chatter.config import settings as _settings

        if getattr(_settings, "default_llm_provider", None) in available:
            return _settings.default_llm_provider  # type: ignore[return-value]

        if available:
            return available[0]

        # No providers configured
        raise ChatError("No LLM providers available")

    async def _maybe_get_retriever(self, conversation: Conversation, chat_request: ChatRequest) -> Any | None:
        """Resolve a retriever instance, if any. Placeholder for integration."""
        # Integrate your vector store / retriever wiring here.
        # For now, return None to allow the workflow to proceed without context.
        return None

    async def _maybe_get_tools(self, conversation: Conversation, chat_request: ChatRequest) -> list[Any]:
        """Return available tools (MCP + built-ins) with lazy loading optimization."""
        # Check if specific tools are requested
        required_tools = None
        if hasattr(chat_request, 'allowed_tools') and chat_request.allowed_tools:
            required_tools = chat_request.allowed_tools

        # Use lazy loader for performance optimization
        tools = await lazy_tool_loader.get_tools(required_tools)

        logger.debug(
            "Tools loaded for workflow",
            conversation_id=conversation.id,
            requested_tools=required_tools,
            loaded_count=len(tools)
        )

        return tools

    def _normalize_workflow(self, workflow_type: str) -> str:
        """Map API workflow types to internal modes."""
        m = (workflow_type or "").lower().strip()
        if m in ("plain", "basic"):
            return "plain"
        if m in ("rag",):
            return "rag"
        if m in ("tools",):
            return "tools"
        if m in ("full", "rag+tools", "tools+rag"):
            return "full"
        return "plain"

    def _to_public_mode(self, mode: str) -> str:
        """Return the public mode string used by LLMService.create_langgraph_workflow."""
        return {"plain": "plain", "rag": "rag", "tools": "tools", "full": "full"}.get(mode, "plain")

    @staticmethod
    def _extract_last_ai_message(messages: list[BaseMessage]) -> AIMessage | None:
        """Return the last AIMessage in a list of messages."""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                return msg
        return None
