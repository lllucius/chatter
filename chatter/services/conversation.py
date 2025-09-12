"""Conversation management service - extracted from ChatService for better separation of concerns."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.exceptions import NotFoundError, ValidationError
from chatter.models.conversation import Conversation, ConversationStatus
from chatter.schemas.chat import (
    ConversationCreate as ConversationCreateSchema,
)
from chatter.schemas.chat import (
    ConversationUpdate as ConversationUpdateSchema,
)
from chatter.utils.performance import (
    ConversationQueryService,
    get_conversation_optimized,
    get_user_conversations_optimized,
)
from chatter.utils.security_enhanced import get_secure_logger

logger = get_secure_logger(__name__)


class ConversationService:
    """Service for managing conversations - CRUD operations and queries."""

    def __init__(self, session: AsyncSession):
        """Initialize conversation service."""
        self.session = session
        self.query_service = ConversationQueryService(session)

    async def create_conversation(
        self,
        user_id: str,
        conversation_data: ConversationCreateSchema = None,
        title: str = None,
        model: str = None,
        **kwargs,
    ) -> Conversation:
        """Create a new conversation.

        Args:
            user_id: User ID creating the conversation
            conversation_data: Conversation creation data (optional)
            title: Conversation title (if not using conversation_data)
            model: Model to use (if not using conversation_data)
            **kwargs: Additional conversation parameters

        Returns:
            Created conversation

        Raises:
            ValidationError: If conversation data is invalid
        """
        try:
            # Support both styles of calling
            if conversation_data is None:
                # Create from individual parameters
                if not title:
                    raise ValueError("Title is required")
                if not model:
                    raise ValueError("Model is required")

                # Validate user_id format
                try:
                    from uuid import UUID

                    UUID(user_id)
                except ValueError as e:
                    raise ValueError("Invalid user ID format") from e

                # Prepare metadata with workflow_config
                metadata = kwargs.get("metadata", {})
                if kwargs.get("workflow_config") is not None:
                    metadata["workflow_config"] = kwargs.get(
                        "workflow_config"
                    )

                conversation = Conversation(
                    title=title,
                    user_id=user_id,
                    status=ConversationStatus.ACTIVE,
                    profile_id=kwargs.get("profile_id"),
                    temperature=kwargs.get("temperature", 0.7),
                    max_tokens=kwargs.get("max_tokens", 1000),
                    extra_metadata=metadata,
                )
            else:
                # Prepare metadata with workflow_config
                metadata = conversation_data.extra_metadata or {}
                if conversation_data.workflow_config is not None:
                    metadata["workflow_config"] = (
                        conversation_data.workflow_config
                    )

                # Use schema object
                conversation = Conversation(
                    title=conversation_data.title,
                    user_id=user_id,
                    profile_id=conversation_data.profile_id,
                    status=ConversationStatus.ACTIVE,
                    temperature=conversation_data.temperature,
                    max_tokens=conversation_data.max_tokens,
                    extra_metadata=metadata,
                )

            self.session.add(conversation)
            await self.session.flush()  # Get the ID without committing
            await self.session.refresh(conversation)

            logger.info(
                "Created conversation",
                conversation_id=conversation.id,
                user_id=user_id,
                title=conversation.title,
            )

            return conversation

        except Exception as e:
            logger.error(
                "Failed to create conversation",
                user_id=user_id,
                error=str(e),
            )
            raise ValidationError(
                f"Failed to create conversation: {e}"
            ) from e

    async def get_conversation(
        self,
        conversation_id: str,
        user_id: str,
        include_messages: bool = True,
    ) -> Conversation:
        """Get conversation by ID with access control.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            include_messages: Whether to include messages

        Returns:
            Conversation if found and accessible

        Raises:
            NotFoundError: If conversation not found or not accessible
        """
        conversation = await get_conversation_optimized(
            self.session,
            conversation_id,
            user_id,
            include_messages=include_messages,
        )

        if not conversation:
            raise NotFoundError(
                "Conversation not found or not accessible",
                resource_type="conversation",
                resource_id=conversation_id,
            )

        return conversation

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        sort_field: str = "updated_at",
        sort_order: str = "desc",
        status: ConversationStatus | None = None,
        llm_provider: str | None = None,
        llm_model: str | None = None,
        tags: list[str] | None = None,
        enable_retrieval: bool | None = None,
    ) -> Sequence[Conversation]:
        """List conversations for a user with filtering.

        Args:
            user_id: User ID
            limit: Maximum conversations to return
            offset: Number of conversations to skip
            sort_field: Field to sort by
            sort_order: Sort order (asc/desc)
            status: Filter by conversation status
            llm_provider: Filter by LLM provider
            llm_model: Filter by LLM model
            tags: Filter by tags (must contain all specified tags)
            enable_retrieval: Filter by retrieval enabled status

        Returns:
            List of conversations
        """
        try:
            # Build query with filters
            query = select(Conversation).where(
                Conversation.user_id == user_id
            )
            
            # Apply status filter (default: exclude deleted)
            if status is not None:
                query = query.where(Conversation.status == status)
            else:
                query = query.where(Conversation.status != ConversationStatus.DELETED)
                
            # Apply additional filters
            if llm_provider is not None:
                query = query.where(Conversation.llm_provider == llm_provider)
                
            if llm_model is not None:
                query = query.where(Conversation.llm_model == llm_model)
                
            if enable_retrieval is not None:
                query = query.where(Conversation.enable_retrieval == enable_retrieval)
                
            # Tags filter - check if all specified tags are present
            if tags is not None and len(tags) > 0:
                for tag in tags:
                    query = query.where(Conversation.tags.contains([tag]))
            
            # Apply sorting
            if sort_order.lower() == "desc":
                query = query.order_by(getattr(Conversation, sort_field).desc())
            else:
                query = query.order_by(getattr(Conversation, sort_field).asc())
                
            # Apply pagination
            query = query.offset(offset).limit(limit)
            
            # Execute query
            result = await self.session.execute(query)
            conversations = result.scalars().all()

            logger.debug(
                "Listed conversations with filters",
                user_id=user_id,
                count=len(conversations),
                limit=limit,
                offset=offset,
                sort_field=sort_field,
                sort_order=sort_order,
                status=status,
                llm_provider=llm_provider,
                llm_model=llm_model,
                tags=tags,
                enable_retrieval=enable_retrieval,
            )

            return conversations

        except Exception as e:
            logger.error(
                "Failed to list conversations",
                user_id=user_id,
                error=str(e),
            )
            raise

    async def update_conversation(
        self,
        conversation_id: str,
        user_id: str,
        update_data: ConversationUpdateSchema = None,
        title: str = None,
        **kwargs,
    ) -> Conversation:
        """Update conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control
            update_data: Update data (optional)
            title: New title (if not using update_data)
            **kwargs: Additional update parameters

        Returns:
            Updated conversation

        Raises:
            NotFoundError: If conversation not found or not accessible
            ValidationError: If update data is invalid
        """
        try:
            # Get existing conversation
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            # Support both styles
            if update_data is None:
                # Create update object from parameters
                update_data = type(
                    "UpdateData",
                    (),
                    {
                        "title": title,
                        "status": kwargs.get("status"),
                        "temperature": kwargs.get("temperature"),
                        "max_tokens": kwargs.get("max_tokens"),
                        "workflow_config": kwargs.get(
                            "workflow_config"
                        ),
                        "metadata": kwargs.get("metadata"),
                    },
                )()

            # Update fields if provided
            if update_data.title is not None:
                conversation.title = update_data.title

            if (
                hasattr(update_data, "status")
                and update_data.status is not None
            ):
                conversation.status = update_data.status

            if (
                hasattr(update_data, "temperature")
                and update_data.temperature is not None
            ):
                conversation.temperature = update_data.temperature

            if update_data.max_tokens is not None:
                conversation.max_tokens = update_data.max_tokens

            if update_data.workflow_config is not None:
                # Store workflow_config in extra_metadata
                if conversation.extra_metadata is None:
                    conversation.extra_metadata = {}
                conversation.extra_metadata["workflow_config"] = (
                    update_data.workflow_config
                )

            if update_data.extra_metadata is not None:
                # Merge metadata
                if conversation.extra_metadata:
                    conversation.extra_metadata.update(
                        update_data.extra_metadata
                    )
                else:
                    conversation.extra_metadata = (
                        update_data.extra_metadata
                    )

            await self.session.flush()
            await self.session.refresh(conversation)

            logger.info(
                "Updated conversation",
                conversation_id=conversation_id,
                user_id=user_id,
                updated_fields=update_data.model_dump(
                    exclude_unset=True
                ),
            )

            return conversation

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to update conversation",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e),
            )
            raise ValidationError(
                f"Failed to update conversation: {e}"
            ) from e

    async def delete_conversation(
        self, conversation_id: str, user_id: str
    ) -> None:
        """Delete conversation (soft delete by setting status).

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Raises:
            NotFoundError: If conversation not found or not accessible
        """
        try:
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=False
            )

            conversation.status = ConversationStatus.DELETED

            await self.session.flush()

            logger.info(
                "Deleted conversation",
                conversation_id=conversation_id,
                user_id=user_id,
            )

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to delete conversation",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e),
            )
            raise

    async def search_conversations(
        self,
        user_id: str,
        search_term: str,
        limit: int = 20,
        offset: int = 0,
    ) -> Sequence[Conversation]:
        """Search conversations by title or content.

        Args:
            user_id: User ID
            search_term: Search term
            limit: Maximum results to return
            offset: Number of results to skip

        Returns:
            List of matching conversations
        """
        try:
            conversations = (
                await self.query_service.search_conversations(
                    user_id, search_term, limit
                )
            )

            logger.debug(
                "Searched conversations",
                user_id=user_id,
                search_term=search_term,
                results_count=len(conversations),
                offset=offset,
                limit=limit,
            )

            return conversations

        except Exception as e:
            logger.error(
                "Failed to search conversations",
                user_id=user_id,
                search_term=search_term,
                error=str(e),
            )
            raise

    async def get_conversation_stats(
        self, conversation_id: str, user_id: str
    ) -> dict[str, Any]:
        """Get statistics for a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Returns:
            Conversation statistics

        Raises:
            NotFoundError: If conversation not found or not accessible
        """
        try:
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=True
            )

            total_messages = len(conversation.messages)
            user_messages = sum(
                1 for msg in conversation.messages if msg.role == "user"
            )
            assistant_messages = sum(
                1
                for msg in conversation.messages
                if msg.role == "assistant"
            )

            total_tokens = sum(
                (msg.prompt_tokens or 0) + (msg.completion_tokens or 0)
                for msg in conversation.messages
            )

            stats = {
                "conversation_id": conversation_id,
                "total_messages": total_messages,
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
                "total_tokens": total_tokens,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "status": conversation.status,
            }

            logger.debug(
                "Retrieved conversation stats",
                conversation_id=conversation_id,
                user_id=user_id,
                stats=stats,
            )

            return stats

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(
                "Failed to get conversation stats",
                conversation_id=conversation_id,
                user_id=user_id,
                error=str(e),
            )
            raise

    async def archive_old_conversations(
        self, user_id: str, days_old: int = 30, limit: int = 100
    ) -> int:
        """Archive conversations older than specified days.

        Args:
            user_id: User ID
            days_old: Number of days to consider "old"
            limit: Maximum conversations to archive in one operation

        Returns:
            Number of conversations archived
        """
        try:
            from datetime import datetime, timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Find old active conversations
            query = (
                select(Conversation)
                .where(
                    and_(
                        Conversation.user_id == user_id,
                        Conversation.status
                        == ConversationStatus.ACTIVE,
                        Conversation.updated_at < cutoff_date,
                    )
                )
                .limit(limit)
            )

            result = await self.session.execute(query)
            old_conversations = result.scalars().all()

            # Archive them
            archived_count = 0
            for conversation in old_conversations:
                conversation.status = ConversationStatus.ARCHIVED
                archived_count += 1

            await self.session.flush()

            logger.info(
                "Archived old conversations",
                user_id=user_id,
                archived_count=archived_count,
                days_old=days_old,
            )

            return archived_count

        except Exception as e:
            logger.error(
                "Failed to archive old conversations",
                user_id=user_id,
                error=str(e),
            )
            raise

    async def get_conversation_count(
        self,
        user_id: str,
        status: ConversationStatus | None = None,
        llm_provider: str | None = None,
        llm_model: str | None = None,
        tags: list[str] | None = None,
        enable_retrieval: bool | None = None,
    ) -> int:
        """Get total conversation count for user with optional filters.

        Args:
            user_id: User ID
            status: Filter by conversation status
            llm_provider: Filter by LLM provider
            llm_model: Filter by LLM model
            tags: Filter by tags (must contain all specified tags)
            enable_retrieval: Filter by retrieval enabled status

        Returns:
            Number of conversations matching the filters
        """
        try:
            # Build query with filters
            query = select(Conversation).where(
                Conversation.user_id == user_id
            )
            
            # Apply status filter (default: exclude deleted)
            if status is not None:
                query = query.where(Conversation.status == status)
            else:
                query = query.where(Conversation.status != ConversationStatus.DELETED)
                
            # Apply additional filters
            if llm_provider is not None:
                query = query.where(Conversation.llm_provider == llm_provider)
                
            if llm_model is not None:
                query = query.where(Conversation.llm_model == llm_model)
                
            if enable_retrieval is not None:
                query = query.where(Conversation.enable_retrieval == enable_retrieval)
                
            # Tags filter - check if all specified tags are present
            if tags is not None and len(tags) > 0:
                for tag in tags:
                    query = query.where(Conversation.tags.contains([tag]))
            
            result = await self.session.execute(query)
            conversations = result.scalars().all()
            return len(conversations)
        except Exception as e:
            logger.error(f"Failed to get conversation count: {e}")
            return 0

    async def archive_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        """Archive a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Returns:
            True if archived successfully
        """
        try:
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=False
            )
            conversation.status = ConversationStatus.ARCHIVED
            await self.session.flush()

            logger.info(f"Archived conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to archive conversation: {e}")
            return False

    async def unarchive_conversation(
        self, conversation_id: str, user_id: str
    ) -> bool:
        """Unarchive a conversation.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Returns:
            True if unarchived successfully
        """
        try:
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=False
            )
            conversation.status = ConversationStatus.ACTIVE
            await self.session.flush()

            logger.info(f"Unarchived conversation {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to unarchive conversation: {e}")
            return False

    async def get_conversation_metadata(
        self, conversation_id: str, user_id: str
    ) -> dict:
        """Get conversation metadata.

        Args:
            conversation_id: Conversation ID
            user_id: User ID for access control

        Returns:
            Conversation metadata
        """
        try:
            conversation = await self.get_conversation(
                conversation_id, user_id, include_messages=False
            )
            return {
                "id": conversation.id,
                "title": conversation.title,
                "status": conversation.status,
                "created_at": conversation.created_at,
                "updated_at": conversation.updated_at,
                "metadata": conversation.extra_metadata,
            }
        except Exception as e:
            logger.error(f"Failed to get conversation metadata: {e}")
            return {}

    async def bulk_delete_conversations(
        self, conversation_ids: list[str], user_id: str
    ) -> int:
        """Delete multiple conversations.

        Args:
            conversation_ids: List of conversation IDs
            user_id: User ID for access control

        Returns:
            Number of conversations deleted
        """
        deleted_count = 0
        for conv_id in conversation_ids:
            try:
                await self.delete_conversation(conv_id, user_id)
                deleted_count += 1
            except Exception as e:
                logger.error(
                    f"Failed to delete conversation {conv_id}: {e}"
                )

        logger.info(f"Bulk deleted {deleted_count} conversations")
        return deleted_count

    async def get_recent_conversations(
        self, user_id: str, limit: int = 10
    ) -> list[Conversation]:
        """Get recent conversations for user.

        Args:
            user_id: User ID
            limit: Maximum number to return

        Returns:
            List of recent conversations
        """
        try:
            conversations = await self.list_conversations(
                user_id, limit=limit
            )
            return list(conversations)
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []
