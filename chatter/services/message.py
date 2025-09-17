"""Message management service - extracted from ChatService for better separation of concerns."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.exceptions import (
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from chatter.models.conversation import Message, MessageRole
from chatter.utils.performance import (
    QueryOptimizer,
    get_performance_monitor,
)
from chatter.utils.security_enhanced import get_secure_logger

logger = get_secure_logger(__name__)


class MessageService:
    """Service for managing messages within conversations with performance optimization."""

    def __init__(self, session: AsyncSession):
        """Initialize message service with performance monitoring."""
        self.session = session
        self.performance_monitor = get_performance_monitor()

    async def get_conversation_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int | None = None,
        offset: int = 0,
        include_system: bool = True,
    ) -> Sequence[Message]:
        """Get messages for a conversation with access control and optimization.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            limit: Optional limit on number of messages
            offset: Number of messages to skip
            include_system: Whether to include system messages

        Returns:
            List of messages

        Raises:
            AuthorizationError: If user doesn't have access to conversation
        """
        async with self.performance_monitor.measure_query(
            "get_conversation_messages"
        ):
            try:
                # First verify user has access to conversation
                from chatter.services.conversation import (
                    ConversationService,
                )

                conv_service = ConversationService(self.session)
                await conv_service.get_conversation(
                    conversation_id, user_id, include_messages=False
                )

                # Build optimized query for messages
                query = (
                    select(Message)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(Message.created_at)
                )

                # Apply query optimization with eager loading
                query = QueryOptimizer.optimize_message_query(
                    query,
                    include_conversation=False,  # We already validated access
                    include_user=False,  # Not needed for basic message retrieval
                )

                if not include_system:
                    query = query.where(
                        Message.role != MessageRole.SYSTEM
                    )

                if offset > 0:
                    query = query.offset(offset)

                if limit is not None:
                    query = query.limit(limit)

                result = await self.session.execute(query)
                messages = result.scalars().all()

                logger.debug(
                    "Retrieved conversation messages",
                    conversation_id=conversation_id,
                    user_id=user_id,
                    message_count=len(messages),
                    limit=limit,
                    offset=offset,
                )

                return messages

            except NotFoundError as e:
                raise AuthorizationError(
                    "Access denied to conversation messages"
                ) from e
            except Exception as e:
                logger.error(
                    "Failed to get conversation messages",
                    conversation_id=conversation_id,
                    user_id=user_id,
                    error=str(e),
                )
            raise

    async def add_message_to_conversation(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        metadata: dict[str, Any] | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        cost: float | None = None,
        provider: str | None = None,
    ) -> Message:
        """Add a new message to a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID (for access control)
            role: Message role
            content: Message content
            metadata: Optional metadata
            input_tokens: Optional input token count
            output_tokens: Optional output token count
            cost: Optional cost
            provider: Optional provider name

        Returns:
            Created message

        Raises:
            AuthorizationError: If user doesn't have access to conversation
            ValidationError: If message data is invalid
        """
        async with self.performance_monitor.measure_query(
            "add_message_to_conversation"
        ):
            try:
                # Verify user has access to conversation
                from chatter.services.conversation import (
                    ConversationService,
                )

                conv_service = ConversationService(self.session)
                conversation = await conv_service.get_conversation(
                    conversation_id, user_id, include_messages=False
                )

                # Get the next sequence number for this conversation
                next_seq_query = (
                    select(Message.sequence_number)
                    .where(Message.conversation_id == conversation_id)
                    .order_by(desc(Message.sequence_number))
                    .limit(1)
                )

                result = await self.session.execute(next_seq_query)
                last_sequence = result.scalar()
                next_sequence = (
                    0 if last_sequence is None else last_sequence + 1
                )

                # Create the message
                message = Message(
                    conversation_id=conversation_id,
                    role=role,
                    content=content,
                    extra_metadata=metadata or {},
                    prompt_tokens=input_tokens,
                    completion_tokens=output_tokens,
                    cost=cost,
                    provider_used=provider,
                    sequence_number=next_sequence,
                )

                self.session.add(message)
                await self.session.flush()
                await self.session.refresh(message)

                # Update conversation's updated_at timestamp
                conversation.updated_at = message.created_at
                
                # Ensure the message and conversation changes are committed to the database
                await self.session.commit()

                logger.info(
                    "Added message to conversation",
                    conversation_id=conversation_id,
                    message_id=message.id,
                    role=role.value,
                    user_id=user_id,
                    content_length=len(content),
                )

                return message

            except NotFoundError as e:
                raise AuthorizationError(
                    "Access denied to conversation"
                ) from e
            except Exception as e:
                logger.error(
                    "Failed to add message to conversation",
                    conversation_id=conversation_id,
                    user_id=user_id,
                    role=role.value if role else None,
                    error=str(e),
                )
                raise ValidationError(
                    f"Failed to add message: {e}"
                ) from e

    async def delete_message(
        self, conversation_id: str, message_id: str, user_id: str
    ) -> None:
        """Delete a message from a conversation.

        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            user_id: User ID for access control

        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have access
        """
        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Find and delete the message
            query = select(Message).where(
                and_(
                    Message.id == message_id,
                    Message.conversation_id == conversation_id,
                )
            )

            result = await self.session.execute(query)
            message = result.scalar_one_or_none()

            if not message:
                raise NotFoundError(
                    "Message not found",
                    resource_type="message",
                    resource_id=message_id,
                )

            await self.session.delete(message)
            await self.session.flush()

            logger.info(
                "Deleted message",
                conversation_id=conversation_id,
                message_id=message_id,
                user_id=user_id,
            )

        except (NotFoundError, AuthorizationError):
            raise
        except Exception as e:
            logger.error(
                "Failed to delete message",
                conversation_id=conversation_id,
                message_id=message_id,
                user_id=user_id,
                error=str(e),
            )
            raise

    async def update_message_rating(
        self,
        conversation_id: str,
        message_id: str,
        user_id: str,
        rating: float,
    ) -> Message:
        """Update the rating for a message.

        Args:
            conversation_id: Conversation ID
            message_id: Message ID
            user_id: User ID for access control
            rating: Rating value (0.0 to 5.0)

        Returns:
            Updated message

        Raises:
            NotFoundError: If message not found
            AuthorizationError: If user doesn't have access
            ValidationError: If rating is invalid
        """
        if rating < 0.0 or rating > 5.0:
            raise ValidationError("Rating must be between 0.0 and 5.0")

        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Find the message
            query = select(Message).where(
                and_(
                    Message.id == message_id,
                    Message.conversation_id == conversation_id,
                )
            )

            result = await self.session.execute(query)
            message = result.scalar_one_or_none()

            if not message:
                raise NotFoundError(
                    "Message not found",
                    resource_type="message",
                    resource_id=message_id,
                )

            # Update rating - using simple average for now
            if message.rating is None:
                # First rating
                message.rating = rating
                message.rating_count = 1
            else:
                # Update existing rating with new average
                total_score = (
                    message.rating * message.rating_count + rating
                )
                message.rating_count += 1
                message.rating = total_score / message.rating_count

            await self.session.flush()

            logger.info(
                "Updated message rating",
                conversation_id=conversation_id,
                message_id=message_id,
                user_id=user_id,
                rating=rating,
                new_average=message.rating,
                rating_count=message.rating_count,
            )

            return message

        except (NotFoundError, AuthorizationError, ValidationError):
            raise
        except Exception as e:
            logger.error(
                "Failed to update message rating",
                conversation_id=conversation_id,
                message_id=message_id,
                user_id=user_id,
                rating=rating,
                error=str(e),
            )
            raise

    async def get_recent_messages(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 10,
        include_system: bool = False,
    ) -> Sequence[Message]:
        """Get recent messages from a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            limit: Number of recent messages to get
            include_system: Whether to include system messages

        Returns:
            List of recent messages (newest first)

        Raises:
            AuthorizationError: If user doesn't have access to conversation
        """
        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Get recent messages
            query = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(desc(Message.created_at))
                .limit(limit)
            )

            if not include_system:
                query = query.where(Message.role != MessageRole.SYSTEM)

            result = await self.session.execute(query)
            messages = list(result.scalars().all())

            # Reverse to get chronological order (oldest first)
            messages.reverse()

            logger.debug(
                "Retrieved recent messages",
                conversation_id=conversation_id,
                user_id=user_id,
                count=len(messages),
            )

            return messages

        except NotFoundError as e:
            raise AuthorizationError(
                "Access denied to conversation"
            ) from e
        except Exception as e:
            logger.error(
                "Failed to get recent messages",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e),
            )
            raise

    async def search_messages(
        self,
        conversation_id: str,
        user_id: str,
        search_term: str,
        limit: int = 20,
    ) -> Sequence[Message]:
        """Search messages within a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            search_term: Search term
            limit: Maximum results to return

        Returns:
            List of matching messages

        Raises:
            AuthorizationError: If user doesn't have access to conversation
        """
        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Search messages
            query = (
                select(Message)
                .where(
                    and_(
                        Message.conversation_id == conversation_id,
                        Message.content.ilike(f"%{search_term}%"),
                    )
                )
                .order_by(desc(Message.created_at))
                .limit(limit)
            )

            result = await self.session.execute(query)
            messages = result.scalars().all()

            logger.debug(
                "Searched messages",
                conversation_id=conversation_id,
                user_id=user_id,
                search_term=search_term,
                results_count=len(messages),
            )

            return messages

        except NotFoundError as e:
            raise AuthorizationError(
                "Access denied to conversation"
            ) from e
        except Exception as e:
            logger.error(
                "Failed to search messages",
                conversation_id=conversation_id,
                user_id=user_id,
                search_term=search_term,
                error=str(e),
            )
            raise

    async def get_message_statistics(
        self, conversation_id: str, user_id: str
    ) -> dict[str, Any]:
        """Get statistics for messages in a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Returns:
            Message statistics

        Raises:
            AuthorizationError: If user doesn't have access to conversation
        """
        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Get all messages for statistics
            messages = await self.get_conversation_messages(
                conversation_id, user_id, include_system=True
            )

            # Calculate statistics
            total_messages = len(messages)
            messages_by_role = {}
            total_tokens = 0
            total_cost = 0.0
            providers_used = set()

            for message in messages:
                # Count by role
                role = message.role.value
                if role not in messages_by_role:
                    messages_by_role[role] = 0
                messages_by_role[role] += 1

                # Sum tokens and cost
                if message.prompt_tokens:
                    total_tokens += message.prompt_tokens
                if message.completion_tokens:
                    total_tokens += message.completion_tokens
                if message.cost:
                    total_cost += message.cost
                if message.provider_used:
                    providers_used.add(message.provider_used)

            stats = {
                "conversation_id": conversation_id,
                "total_messages": total_messages,
                "messages_by_role": messages_by_role,
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "providers_used": list(providers_used),
                "avg_tokens_per_message": (
                    total_tokens / total_messages
                    if total_messages > 0
                    else 0
                ),
                "avg_cost_per_message": (
                    total_cost / total_messages
                    if total_messages > 0
                    else 0.0
                ),
            }

            logger.debug(
                "Calculated message statistics",
                conversation_id=conversation_id,
                user_id=user_id,
                stats=stats,
            )

            return stats

        except NotFoundError as e:
            raise AuthorizationError(
                "Access denied to conversation"
            ) from e
        except Exception as e:
            logger.error(
                "Failed to get message statistics",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e),
            )
            raise

    async def bulk_delete_messages(
        self, conversation_id: str, user_id: str, message_ids: list[str]
    ) -> int:
        """Delete multiple messages from a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            message_ids: List of message IDs to delete

        Returns:
            Number of messages deleted

        Raises:
            AuthorizationError: If user doesn't have access to conversation
        """
        try:
            # Verify user has access to conversation
            from chatter.services.conversation import (
                ConversationService,
            )

            conv_service = ConversationService(self.session)
            await conv_service.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Find messages to delete
            query = select(Message).where(
                and_(
                    Message.conversation_id == conversation_id,
                    Message.id.in_(message_ids),
                )
            )

            result = await self.session.execute(query)
            messages_to_delete = result.scalars().all()

            # Delete messages
            deleted_count = 0
            for message in messages_to_delete:
                await self.session.delete(message)
                deleted_count += 1

            await self.session.flush()

            logger.info(
                "Bulk deleted messages",
                conversation_id=conversation_id,
                user_id=user_id,
                requested_count=len(message_ids),
                deleted_count=deleted_count,
            )

            return deleted_count

        except NotFoundError as e:
            raise AuthorizationError(
                "Access denied to conversation"
            ) from e
        except Exception as e:
            logger.error(
                "Failed to bulk delete messages",
                conversation_id=conversation_id,
                user_id=user_id,
                message_count=len(message_ids),
                error=str(e),
            )
            raise

    async def update_message_content(
        self, message_id: str, content: str
    ) -> Message:
        """Update message content.

        Args:
            message_id: Message ID to update
            content: New content

        Returns:
            Updated message

        Raises:
            NotFoundError: If message not found
        """
        async with self.performance_monitor.measure_query(
            "update_message_content"
        ):
            try:
                # Get the message
                query = select(Message).where(Message.id == message_id)
                result = await self.session.execute(query)
                message = result.scalar_one_or_none()

                if not message:
                    raise NotFoundError(f"Message {message_id} not found")

                # Update the content
                message.content = content
                await self.session.flush()
                await self.session.refresh(message)

                logger.debug(
                    "Updated message content",
                    message_id=message_id,
                    content_length=len(content),
                )

                return message

            except NotFoundError:
                raise
            except Exception as e:
                logger.error(
                    "Failed to update message content",
                    message_id=message_id,
                    error=str(e),
                )
                raise
