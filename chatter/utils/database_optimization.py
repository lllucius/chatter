"""Database query optimization utilities for eager loading and performance enhancement."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql import Select

from chatter.models.conversation import Conversation, Message
from chatter.models.document import Document
from chatter.models.user import User
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class QueryOptimizer:
    """Utility class for optimizing database queries with eager loading."""

    @staticmethod
    def optimize_conversation_query(
        query: Select[tuple[Conversation]],
        include_messages: bool = True,
        include_user: bool = True,
        include_profile: bool = True,
        message_limit: int | None = None
    ) -> Select[tuple[Conversation]]:
        """Optimize conversation query with eager loading.

        Args:
            query: Base query to optimize
            include_messages: Whether to include messages
            include_user: Whether to include user data
            include_profile: Whether to include profile data
            message_limit: Limit number of messages to load

        Returns:
            Optimized query with eager loading
        """
        # Use joinedload for small related objects (user, profile)
        if include_user:
            query = query.options(joinedload(Conversation.user))

        if include_profile:
            query = query.options(joinedload(Conversation.profile))

        # Use selectinload for potentially large collections (messages)
        if include_messages:
            if message_limit:
                # For limited messages, we need a subquery approach
                message_options = selectinload(Conversation.messages).options(
                    # Order by created_at desc to get most recent messages
                    # Note: This requires a separate optimization in the service layer
                )
            else:
                message_options = selectinload(Conversation.messages)

            query = query.options(message_options)

        return query

    @staticmethod
    def optimize_message_query(
        query: Select[tuple[Message]],
        include_conversation: bool = True,
        include_user: bool = False
    ) -> Select[tuple[Message]]:
        """Optimize message query with eager loading.

        Args:
            query: Base query to optimize
            include_conversation: Whether to include conversation data
            include_user: Whether to include user data through conversation

        Returns:
            Optimized query with eager loading
        """
        if include_conversation:
            query = query.options(joinedload(Message.conversation))

            if include_user:
                query = query.options(
                    joinedload(Message.conversation).joinedload(Conversation.user)
                )

        return query

    @staticmethod
    def optimize_user_query(
        query: Select[tuple[User]],
        include_conversations: bool = False,
        include_profiles: bool = True
    ) -> Select[tuple[User]]:
        """Optimize user query with eager loading.

        Args:
            query: Base query to optimize
            include_conversations: Whether to include conversations (use sparingly)
            include_profiles: Whether to include profiles

        Returns:
            Optimized query with eager loading
        """
        if include_profiles:
            query = query.options(selectinload(User.profiles))

        if include_conversations:
            # Only include conversations if explicitly requested (can be large)
            query = query.options(selectinload(User.conversations))

        return query

    @staticmethod
    def optimize_document_query(
        query: Select[tuple[Document]],
        include_user: bool = True,
        include_chunks: bool = False
    ) -> Select[tuple[Document]]:
        """Optimize document query with eager loading.

        Args:
            query: Base query to optimize
            include_user: Whether to include user data
            include_chunks: Whether to include document chunks

        Returns:
            Optimized query with eager loading
        """
        if include_user:
            query = query.options(joinedload(Document.user))

        if include_chunks:
            # Use selectinload for potentially large chunk collections
            query = query.options(selectinload(Document.chunks))

        return query


class ConversationQueryService:
    """Specialized service for optimized conversation queries."""

    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session

    async def get_conversation_with_recent_messages(
        self,
        conversation_id: str,
        message_limit: int = 50,
        user_id: str | None = None
    ) -> Conversation | None:
        """Get conversation with most recent messages using optimized query.

        Args:
            conversation_id: Conversation ID
            message_limit: Maximum number of recent messages to load
            user_id: Optional user ID for access control

        Returns:
            Conversation with recent messages or None
        """
        # First, get the conversation with user and profile
        conv_query = select(Conversation).where(Conversation.id == conversation_id)

        if user_id:
            conv_query = conv_query.where(Conversation.user_id == user_id)

        conv_query = QueryOptimizer.optimize_conversation_query(
            conv_query,
            include_messages=False,  # We'll load messages separately
            include_user=True,
            include_profile=True
        )

        result = await self.session.execute(conv_query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            return None

        # Then load recent messages separately for better performance
        messages_query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(message_limit)
        )

        messages_result = await self.session.execute(messages_query)
        messages = list(messages_result.scalars().all())

        # Reverse to get chronological order
        messages.reverse()

        # Manually assign messages to avoid additional query
        conversation.messages = messages

        return conversation

    async def get_conversations_for_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        include_recent_message: bool = True
    ) -> Sequence[Conversation]:
        """Get conversations for user with optimization.

        Args:
            user_id: User ID
            limit: Maximum conversations to return
            offset: Number of conversations to skip
            include_recent_message: Whether to include most recent message

        Returns:
            List of conversations
        """
        query = (
            select(Conversation)
            .where(and_(
                Conversation.user_id == user_id,
                Conversation.status != "deleted"
            ))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        # Optimize based on what we need
        if include_recent_message:
            # Load conversations with a single recent message each
            query = QueryOptimizer.optimize_conversation_query(
                query,
                include_messages=False,  # We'll handle this specially
                include_user=False,      # User is known
                include_profile=True
            )
        else:
            query = QueryOptimizer.optimize_conversation_query(
                query,
                include_messages=False,
                include_user=False,
                include_profile=True
            )

        result = await self.session.execute(query)
        conversations = list(result.scalars().all())

        if include_recent_message and conversations:
            # Load most recent message for each conversation in a single query
            conv_ids = [conv.id for conv in conversations]

            # Get most recent message for each conversation
            recent_messages_query = (
                select(Message)
                .where(Message.conversation_id.in_(conv_ids))
                .order_by(Message.conversation_id, Message.created_at.desc())
                .distinct(Message.conversation_id)
            )

            recent_messages_result = await self.session.execute(recent_messages_query)
            recent_messages = {msg.conversation_id: msg for msg in recent_messages_result.scalars().all()}

            # Assign recent messages to conversations
            for conv in conversations:
                if conv.id in recent_messages:
                    conv.messages = [recent_messages[conv.id]]
                else:
                    conv.messages = []

        return conversations

    async def search_conversations(
        self,
        user_id: str,
        search_term: str,
        limit: int = 20
    ) -> Sequence[Conversation]:
        """Search conversations by title or content with optimization.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results to return

        Returns:
            List of matching conversations
        """
        # Search in conversation title or message content
        query = (
            select(Conversation)
            .join(Message, Message.conversation_id == Conversation.id, isouter=True)
            .where(and_(
                Conversation.user_id == user_id,
                Conversation.status != "deleted",
                or_(
                    Conversation.title.ilike(f"%{search_term}%"),
                    Message.content.ilike(f"%{search_term}%")
                )
            ))
            .distinct()
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        query = QueryOptimizer.optimize_conversation_query(
            query,
            include_messages=False,
            include_user=False,
            include_profile=True
        )

        result = await self.session.execute(query)
        return result.scalars().all()


# Utility functions for common optimized queries
async def get_conversation_optimized(
    session: AsyncSession,
    conversation_id: str,
    user_id: str | None = None,
    include_messages: bool = True,
    message_limit: int | None = None
) -> Conversation | None:
    """Get conversation with optimized loading.

    Args:
        session: Database session
        conversation_id: Conversation ID
        user_id: Optional user ID for access control
        include_messages: Whether to include messages
        message_limit: Optional limit on messages

    Returns:
        Conversation or None
    """
    service = ConversationQueryService(session)

    if include_messages and message_limit:
        return await service.get_conversation_with_recent_messages(
            conversation_id, message_limit, user_id
        )
    else:
        query = select(Conversation).where(Conversation.id == conversation_id)

        if user_id:
            query = query.where(Conversation.user_id == user_id)

        query = QueryOptimizer.optimize_conversation_query(
            query,
            include_messages=include_messages,
            include_user=True,
            include_profile=True
        )

        result = await session.execute(query)
        return result.scalar_one_or_none()


async def get_user_conversations_optimized(
    session: AsyncSession,
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> Sequence[Conversation]:
    """Get user conversations with optimization.

    Args:
        session: Database session
        user_id: User ID
        limit: Maximum conversations to return
        offset: Number of conversations to skip

    Returns:
        List of conversations
    """
    service = ConversationQueryService(session)
    return await service.get_conversations_for_user(
        user_id, limit, offset, include_recent_message=True
    )
