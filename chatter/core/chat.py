"""Chat service for conversation management."""

import uuid
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.models.profile import Profile
from chatter.schemas.chat import (
    ChatRequest,
    ConversationCreate,
    ConversationUpdate,
)
from chatter.services.llm import LLMProviderError, LLMService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ChatError(Exception):
    """Chat service error."""

    pass


class ConversationNotFoundError(ChatError):
    """Conversation not found error."""

    pass


class ChatService:
    """Service for managing conversations and chat interactions."""

    def __init__(self, session: AsyncSession, llm_service: LLMService):
        """Initialize chat service.

        Args:
            session: Database session
            llm_service: LLM service instance
        """
        self.session = session
        self.llm_service = llm_service

    async def create_conversation(
        self, user_id: str, conversation_data: ConversationCreate
    ) -> Conversation:
        """Create a new conversation.

        Args:
            user_id: User ID
            conversation_data: Conversation creation data

        Returns:
            Created conversation
        """
        # Get profile if specified
        profile = None
        if conversation_data.profile_id:
            result = await self.session.execute(
                select(Profile).where(
                    Profile.id == conversation_data.profile_id,
                    Profile.owner_id == user_id,
                )
            )
            profile = result.scalar_one_or_none()
            if not profile:
                raise ChatError(
                    "Profile not found or not accessible"
                ) from None

        # Create conversation
        conversation = Conversation(
            user_id=user_id,
            profile_id=profile.id if profile else None,
            title=conversation_data.title,
            description=conversation_data.description,
            system_prompt=conversation_data.system_prompt,
            enable_retrieval=conversation_data.enable_retrieval,
        )

        # Set LLM configuration from profile if available
        if profile:
            conversation.llm_provider = profile.llm_provider
            conversation.llm_model = profile.llm_model
            conversation.temperature = profile.temperature
            conversation.max_tokens = profile.max_tokens
            conversation.context_window = profile.context_window
            conversation.memory_enabled = profile.memory_enabled
            conversation.memory_strategy = profile.memory_strategy
            conversation.enable_retrieval = profile.enable_retrieval
            conversation.retrieval_limit = profile.retrieval_limit
            conversation.retrieval_score_threshold = (
                profile.retrieval_score_threshold
            )

        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)

        logger.info(
            "Conversation created",
            conversation_id=conversation.id,
            user_id=user_id,
        )
        return conversation

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = False,
    ) -> Conversation | None:
        """Get conversation by ID.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            include_messages: Whether to include messages

        Returns:
            Conversation if found, None otherwise
        """
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )

        if include_messages:
            query = query.options(selectinload(Conversation.messages))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def list_conversations(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> tuple[list[Conversation], int]:
        """List user's conversations.

        Args:
            user_id: User ID
            limit: Number of conversations to return
            offset: Offset for pagination

        Returns:
            Tuple of (conversations, total_count)
        """
        # Get conversations
        result = await self.session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .limit(limit)
            .offset(offset)
        )
        conversations = result.scalars().all()

        # Get total count
        count_result = await self.session.execute(
            select(Conversation).where(Conversation.user_id == user_id)
        )
        total_count = len(count_result.scalars().all())

        return list(conversations), total_count

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update_data: ConversationUpdate,
    ) -> Conversation:
        """Update conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            update_data: Update data

        Returns:
            Updated conversation

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        conversation = await self.get_conversation(
            conversation_id, user_id
        )
        if not conversation:
            raise ConversationNotFoundError(
                "Conversation not found"
            ) from None

        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(conversation, field, value)

        await self.session.commit()
        await self.session.refresh(conversation)

        logger.info(
            "Conversation updated", conversation_id=conversation_id
        )
        return conversation

    async def delete_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        """Delete conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)

        Returns:
            True if deleted successfully

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        conversation = await self.get_conversation(
            conversation_id, user_id
        )
        if not conversation:
            raise ConversationNotFoundError(
                "Conversation not found"
            ) from None

        await self.session.delete(conversation)
        await self.session.commit()

        logger.info(
            "Conversation deleted", conversation_id=conversation_id
        )
        return True

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        **metadata,
    ) -> Message:
        """Add message to conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            role: Message role
            content: Message content
            **metadata: Additional metadata

        Returns:
            Created message

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        conversation = await self.get_conversation(
            conversation_id, user_id
        )
        if not conversation:
            raise ConversationNotFoundError(
                "Conversation not found"
            ) from None

        # Get next sequence number
        last_message_result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.sequence_number))
            .limit(1)
        )
        last_message = last_message_result.scalar_one_or_none()
        sequence_number = (
            (last_message.sequence_number + 1) if last_message else 1
        )

        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            **metadata,
        )

        self.session.add(message)

        # Update conversation stats
        conversation.message_count = sequence_number
        conversation.last_message_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(message)

        return message

    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int | None = None,
    ) -> list[Message]:
        """Get conversation messages.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            limit: Maximum number of messages to return

        Returns:
            List of messages

        Raises:
            ConversationNotFoundError: If conversation not found
        """
        conversation = await self.get_conversation(
            conversation_id, user_id
        )
        if not conversation:
            raise ConversationNotFoundError(
                "Conversation not found"
            ) from None

        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number)
        )

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def chat(
        self, user_id: str, chat_request: ChatRequest
    ) -> tuple[Conversation, Message]:
        """Process chat request and generate response.

        Args:
            user_id: User ID
            chat_request: Chat request data

        Returns:
            Tuple of (conversation, assistant_message)
        """
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = await self.get_conversation(
                chat_request.conversation_id, user_id
            )
            if not conversation:
                raise ConversationNotFoundError(
                    "Conversation not found"
                ) from None
        else:
            # Create new conversation
            conversation_data = ConversationCreate(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                profile_id=chat_request.profile_id,
                enable_retrieval=chat_request.enable_retrieval or False,
            )
            conversation = await self.create_conversation(
                user_id, conversation_data
            )

        # Add user message
        await self.add_message(
            conversation.id,
            user_id,
            MessageRole.USER,
            chat_request.message,
        )

        # Get conversation history
        messages = await self.get_conversation_messages(
            conversation.id, user_id
        )

        # Get LLM provider
        provider = None
        if conversation.profile_id:
            profile_result = await self.session.execute(
                select(Profile).where(
                    Profile.id == conversation.profile_id
                )
            )
            profile = profile_result.scalar_one_or_none()
            if profile:
                provider = (
                    self.llm_service.create_provider_from_profile(
                        profile
                    )
                )

        if not provider:
            provider = self.llm_service.get_default_provider()

        # Convert to LangChain format
        langchain_messages = (
            self.llm_service.convert_conversation_to_messages(
                conversation, messages
            )
        )

        # Generate response
        try:
            generation_kwargs = {}
            if chat_request.temperature is not None:
                generation_kwargs[
                    "temperature"
                ] = chat_request.temperature
            if chat_request.max_tokens is not None:
                generation_kwargs[
                    "max_tokens"
                ] = chat_request.max_tokens

            (
                response_content,
                usage_info,
            ) = await self.llm_service.generate_response(
                langchain_messages, provider, **generation_kwargs
            )

            # Add assistant message
            assistant_message = await self.add_message(
                conversation.id,
                user_id,
                MessageRole.ASSISTANT,
                response_content,
                model_used=usage_info.get("model"),
                provider_used=usage_info.get("provider"),
                prompt_tokens=usage_info.get("prompt_tokens"),
                completion_tokens=usage_info.get("completion_tokens"),
                total_tokens=usage_info.get("total_tokens"),
                response_time_ms=usage_info.get("response_time_ms"),
            )

            # Update conversation stats
            if usage_info.get("total_tokens"):
                conversation.total_tokens += usage_info["total_tokens"]

            await self.session.commit()
            await self.session.refresh(conversation)

            return conversation, assistant_message

        except LLMProviderError as e:
            logger.error(
                "LLM generation failed",
                error=str(e),
                conversation_id=conversation.id,
            )
            raise ChatError(
                f"Failed to generate response: {str(e)}"
            ) from e

    async def chat_streaming(
        self, user_id: str, chat_request: ChatRequest
    ) -> AsyncGenerator[dict, None]:
        """Process chat request with streaming response.

        Args:
            user_id: User ID
            chat_request: Chat request data

        Yields:
            Streaming response chunks
        """
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = await self.get_conversation(
                chat_request.conversation_id, user_id
            )
            if not conversation:
                raise ConversationNotFoundError(
                    "Conversation not found"
                ) from None
        else:
            # Create new conversation
            conversation_data = ConversationCreate(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                profile_id=chat_request.profile_id,
                enable_retrieval=chat_request.enable_retrieval or False,
            )
            conversation = await self.create_conversation(
                user_id, conversation_data
            )

        # Add user message
        await self.add_message(
            conversation.id,
            user_id,
            MessageRole.USER,
            chat_request.message,
        )

        # Get conversation history
        messages = await self.get_conversation_messages(
            conversation.id, user_id
        )

        # Get LLM provider
        provider = None
        if conversation.profile_id:
            profile_result = await self.session.execute(
                select(Profile).where(
                    Profile.id == conversation.profile_id
                )
            )
            profile = profile_result.scalar_one_or_none()
            if profile:
                provider = (
                    self.llm_service.create_provider_from_profile(
                        profile
                    )
                )

        if not provider:
            provider = self.llm_service.get_default_provider()

        # Convert to LangChain format
        langchain_messages = (
            self.llm_service.convert_conversation_to_messages(
                conversation, messages
            )
        )

        # Generate streaming response
        try:
            generation_kwargs = {}
            if chat_request.temperature is not None:
                generation_kwargs[
                    "temperature"
                ] = chat_request.temperature
            if chat_request.max_tokens is not None:
                generation_kwargs[
                    "max_tokens"
                ] = chat_request.max_tokens

            full_content = ""
            message_id = str(uuid.uuid4())

            async for (
                chunk
            ) in self.llm_service.generate_streaming_response(
                langchain_messages, provider, **generation_kwargs
            ):
                if chunk["type"] == "token":
                    full_content += chunk["content"]
                    yield {
                        "type": "token",
                        "content": chunk["content"],
                        "conversation_id": conversation.id,
                        "message_id": message_id,
                    }
                elif chunk["type"] == "usage":
                    # Save assistant message
                    usage_info = chunk["usage"]
                    assistant_message = await self.add_message(
                        conversation.id,
                        user_id,
                        MessageRole.ASSISTANT,
                        full_content,
                        model_used=usage_info.get("model"),
                        provider_used=usage_info.get("provider"),
                        response_time_ms=usage_info.get(
                            "response_time_ms"
                        ),
                    )

                    # Update conversation stats
                    await self.session.commit()
                    await self.session.refresh(conversation)

                    yield {
                        "type": "usage",
                        "usage": usage_info,
                        "conversation_id": conversation.id,
                        "message_id": assistant_message.id,
                    }
                elif chunk["type"] == "end":
                    yield {
                        "type": "end",
                        "conversation_id": conversation.id,
                        "message_id": message_id,
                    }
                elif chunk["type"] == "error":
                    yield {
                        "type": "error",
                        "error": chunk["error"],
                        "conversation_id": conversation.id,
                    }

        except LLMProviderError as e:
            logger.error(
                "Streaming generation failed",
                error=str(e),
                conversation_id=conversation.id,
            )
            yield {
                "type": "error",
                "error": f"Failed to generate response: {str(e)}",
                "conversation_id": conversation.id,
            }

    async def chat_with_workflow(
        self,
        user_id: str,
        chat_request: ChatRequest,
        workflow_type: str = "basic",
    ) -> tuple[Conversation, Message]:
        """Send a chat message using LangGraph workflows.

        Args:
            user_id: User ID
            chat_request: Chat request data
            workflow_type: Type of workflow ("basic", "rag", "tools")

        Returns:
            Tuple of conversation and assistant message
        """
        from chatter.core.langgraph import (
            ConversationState,
            workflow_manager,
        )
        from chatter.core.vector_store import vector_store_manager
        from chatter.services.embeddings import EmbeddingService

        # Get conversation
        conversation = await self._get_conversation(
            chat_request.conversation_id, user_id
        )

        # Create user message
        user_message = Message(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=chat_request.message,
            metadata={"workflow_type": workflow_type},
        )
        self.session.add(user_message)
        await self.session.flush()

        try:
            # Get provider
            provider_name = conversation.llm_provider or "openai"

            # Build conversation history
            conversation_messages = (
                await self._build_conversation_messages(
                    conversation, chat_request.message
                )
            )

            # Create workflow based on type
            if workflow_type == "rag":
                # Create retriever for RAG workflow
                embedding_service = EmbeddingService()
                embeddings = embedding_service.get_default_embeddings()
                vector_store = vector_store_manager.get_default_store(
                    embeddings
                )
                retriever = vector_store.as_retriever(
                    search_kwargs={"k": 5}
                )

                workflow = (
                    await self.llm_service.create_langgraph_workflow(
                        provider_name=provider_name,
                        workflow_type="rag",
                        system_message=conversation.system_prompt,
                        retriever=retriever,
                    )
                )
            else:
                workflow = (
                    await self.llm_service.create_langgraph_workflow(
                        provider_name=provider_name,
                        workflow_type=workflow_type,
                        system_message=conversation.system_prompt,
                    )
                )

            # Prepare initial state
            initial_state: ConversationState = {
                "messages": conversation_messages,
                "user_id": user_id,
                "conversation_id": str(conversation.id),
                "retrieval_context": None,
                "tool_calls": [],
                "metadata": {
                    "workflow_type": workflow_type,
                    "provider": provider_name,
                },
            }

            # Run workflow
            result_state = await workflow_manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=f"{conversation.id}_{workflow_type}",
            )

            # Extract assistant response
            assistant_response = result_state["messages"][-1]

            # Create assistant message
            assistant_message = Message(
                conversation_id=conversation.id,
                role=MessageRole.ASSISTANT,
                content=assistant_response.content,
                metadata={
                    "workflow_type": workflow_type,
                    "tool_calls": result_state.get("tool_calls", []),
                    "retrieval_context": result_state.get(
                        "retrieval_context"
                    ),
                },
                provider_used=provider_name,
            )
            self.session.add(assistant_message)

            # Update conversation stats
            conversation.message_count += 2  # user + assistant
            conversation.updated_at = datetime.now(UTC)

            await self.session.commit()

            logger.info(
                "Workflow chat completed",
                conversation_id=conversation.id,
                workflow_type=workflow_type,
                user_id=user_id,
            )

            return conversation, assistant_message

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Workflow chat failed",
                error=str(e),
                conversation_id=conversation.id,
                workflow_type=workflow_type,
            )
            raise ChatError(f"Workflow chat failed: {str(e)}") from e

        finally:
            # Clean up any resources if needed
            pass
