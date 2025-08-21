"""Chat service for conversation management."""

import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator, List, Optional, Tuple

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.conversation import Conversation, Message, MessageRole
from chatter.models.profile import Profile
from chatter.models.user import User
from chatter.schemas.chat import ConversationCreate, ConversationUpdate, ChatRequest
from chatter.services.llm import LLMService, LLMProviderError
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
        self,
        user_id: str,
        conversation_data: ConversationCreate
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
                    Profile.owner_id == user_id
                )
            )
            profile = result.scalar_one_or_none()
            if not profile:
                raise ChatError("Profile not found or not accessible")
        
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
            conversation.retrieval_score_threshold = profile.retrieval_score_threshold
        
        self.session.add(conversation)
        await self.session.commit()
        await self.session.refresh(conversation)
        
        logger.info("Conversation created", conversation_id=conversation.id, user_id=user_id)
        return conversation
    
    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = False
    ) -> Optional[Conversation]:
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
            Conversation.user_id == user_id
        )
        
        if include_messages:
            query = query.options(selectinload(Conversation.messages))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> Tuple[List[Conversation], int]:
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
            select(Conversation)
            .where(Conversation.user_id == user_id)
        )
        total_count = len(count_result.scalars().all())
        
        return list(conversations), total_count
    
    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update_data: ConversationUpdate
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
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(conversation, field, value)
        
        await self.session.commit()
        await self.session.refresh(conversation)
        
        logger.info("Conversation updated", conversation_id=conversation_id)
        return conversation
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            
        Returns:
            True if deleted successfully
            
        Raises:
            ConversationNotFoundError: If conversation not found
        """
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")
        
        await self.session.delete(conversation)
        await self.session.commit()
        
        logger.info("Conversation deleted", conversation_id=conversation_id)
        return True
    
    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        **metadata
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
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")
        
        # Get next sequence number
        last_message_result = await self.session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.sequence_number))
            .limit(1)
        )
        last_message = last_message_result.scalar_one_or_none()
        sequence_number = (last_message.sequence_number + 1) if last_message else 1
        
        # Create message
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            **metadata
        )
        
        self.session.add(message)
        
        # Update conversation stats
        conversation.message_count = sequence_number
        conversation.last_message_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        await self.session.refresh(message)
        
        return message
    
    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
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
        conversation = await self.get_conversation(conversation_id, user_id)
        if not conversation:
            raise ConversationNotFoundError("Conversation not found")
        
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
        self,
        user_id: str,
        chat_request: ChatRequest
    ) -> Tuple[Conversation, Message]:
        """Process chat request and generate response.
        
        Args:
            user_id: User ID
            chat_request: Chat request data
            
        Returns:
            Tuple of (conversation, assistant_message)
        """
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = await self.get_conversation(chat_request.conversation_id, user_id)
            if not conversation:
                raise ConversationNotFoundError("Conversation not found")
        else:
            # Create new conversation
            conversation_data = ConversationCreate(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                profile_id=chat_request.profile_id,
                enable_retrieval=chat_request.enable_retrieval or False
            )
            conversation = await self.create_conversation(user_id, conversation_data)
        
        # Add user message
        user_message = await self.add_message(
            conversation.id,
            user_id,
            MessageRole.USER,
            chat_request.message
        )
        
        # Get conversation history
        messages = await self.get_conversation_messages(conversation.id, user_id)
        
        # Get LLM provider
        provider = None
        if conversation.profile_id:
            profile_result = await self.session.execute(
                select(Profile).where(Profile.id == conversation.profile_id)
            )
            profile = profile_result.scalar_one_or_none()
            if profile:
                provider = self.llm_service.create_provider_from_profile(profile)
        
        if not provider:
            provider = self.llm_service.get_default_provider()
        
        # Convert to LangChain format
        langchain_messages = self.llm_service.convert_conversation_to_messages(
            conversation, messages
        )
        
        # Generate response
        try:
            generation_kwargs = {}
            if chat_request.temperature is not None:
                generation_kwargs["temperature"] = chat_request.temperature
            if chat_request.max_tokens is not None:
                generation_kwargs["max_tokens"] = chat_request.max_tokens
            
            response_content, usage_info = await self.llm_service.generate_response(
                langchain_messages,
                provider,
                **generation_kwargs
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
            logger.error("LLM generation failed", error=str(e), conversation_id=conversation.id)
            raise ChatError(f"Failed to generate response: {str(e)}")
    
    async def chat_streaming(
        self,
        user_id: str,
        chat_request: ChatRequest
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
            conversation = await self.get_conversation(chat_request.conversation_id, user_id)
            if not conversation:
                raise ConversationNotFoundError("Conversation not found")
        else:
            # Create new conversation
            conversation_data = ConversationCreate(
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                profile_id=chat_request.profile_id,
                enable_retrieval=chat_request.enable_retrieval or False
            )
            conversation = await self.create_conversation(user_id, conversation_data)
        
        # Add user message
        user_message = await self.add_message(
            conversation.id,
            user_id,
            MessageRole.USER,
            chat_request.message
        )
        
        # Get conversation history
        messages = await self.get_conversation_messages(conversation.id, user_id)
        
        # Get LLM provider
        provider = None
        if conversation.profile_id:
            profile_result = await self.session.execute(
                select(Profile).where(Profile.id == conversation.profile_id)
            )
            profile = profile_result.scalar_one_or_none()
            if profile:
                provider = self.llm_service.create_provider_from_profile(profile)
        
        if not provider:
            provider = self.llm_service.get_default_provider()
        
        # Convert to LangChain format
        langchain_messages = self.llm_service.convert_conversation_to_messages(
            conversation, messages
        )
        
        # Generate streaming response
        try:
            generation_kwargs = {}
            if chat_request.temperature is not None:
                generation_kwargs["temperature"] = chat_request.temperature
            if chat_request.max_tokens is not None:
                generation_kwargs["max_tokens"] = chat_request.max_tokens
            
            full_content = ""
            message_id = str(uuid.uuid4())
            
            async for chunk in self.llm_service.generate_streaming_response(
                langchain_messages,
                provider,
                **generation_kwargs
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
                        response_time_ms=usage_info.get("response_time_ms"),
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
            logger.error("Streaming generation failed", error=str(e), conversation_id=conversation.id)
            yield {
                "type": "error",
                "error": f"Failed to generate response: {str(e)}",
                "conversation_id": conversation.id,
            }