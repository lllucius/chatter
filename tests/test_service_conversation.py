"""Tests for conversation service functionality."""

from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from chatter.services.conversation import ConversationService


class TestConversationService:
    """Test conversation service functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.service = ConversationService(session=self.mock_session)

    @pytest.mark.asyncio
    async def test_create_conversation(self):
        """Test creating a new conversation."""
        user_id = str(uuid4())
        title = "Test Conversation"
        model = "gpt-4"
        
        # Mock database operations
        mock_conversation = Mock()
        mock_conversation.id = str(uuid4())
        mock_conversation.title = title
        mock_conversation.user_id = user_id
        mock_conversation.model = model
        mock_conversation.created_at = datetime.utcnow()
        mock_conversation.updated_at = datetime.utcnow()
        
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        with patch('chatter.models.conversation.Conversation', return_value=mock_conversation):
            result = await self.service.create_conversation(
                user_id=user_id,
                title=title,
                model=model
            )
            
            assert result.id == mock_conversation.id
            assert result.title == title
            assert result.user_id == user_id
            assert result.model == model
            
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self):
        """Test retrieving conversation by ID."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.title = "Test Conversation"
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = AsyncMock(return_value=mock_conversation)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        assert result == mock_conversation
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called()
        mock_query.first.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self):
        """Test retrieving non-existent conversation."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = AsyncMock(return_value=None)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        assert result is None

    @pytest.mark.asyncio
    async def test_list_conversations(self):
        """Test listing user conversations."""
        user_id = str(uuid4())
        
        mock_conversations = [
            Mock(id=str(uuid4()), title="Conv 1", user_id=user_id),
            Mock(id=str(uuid4()), title="Conv 2", user_id=user_id),
            Mock(id=str(uuid4()), title="Conv 3", user_id=user_id)
        ]
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.offset = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = AsyncMock(return_value=mock_conversations)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.list_conversations(
            user_id=user_id,
            offset=0,
            limit=10
        )
        
        assert len(result) == 3
        assert all(conv.user_id == user_id for conv in result)
        
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called()
        mock_query.offset.assert_called_with(0)
        mock_query.limit.assert_called_with(10)

    @pytest.mark.asyncio
    async def test_update_conversation_title(self):
        """Test updating conversation title."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        new_title = "Updated Title"
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.title = "Old Title"
        
        # Mock get_conversation to return the conversation
        with patch.object(self.service, 'get_conversation', return_value=mock_conversation):
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            result = await self.service.update_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=new_title
            )
            
            assert result.title == new_title
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_conversation(self):
        """Test deleting a conversation."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        
        with patch.object(self.service, 'get_conversation', return_value=mock_conversation):
            self.mock_session.delete = Mock()
            self.mock_session.commit = AsyncMock()
            
            result = await self.service.delete_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            assert result is True
            self.mock_session.delete.assert_called_once_with(mock_conversation)
            self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found(self):
        """Test deleting non-existent conversation."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        with patch.object(self.service, 'get_conversation', return_value=None):
            result = await self.service.delete_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            assert result is False

    @pytest.mark.asyncio
    async def test_get_conversation_count(self):
        """Test getting conversation count for user."""
        user_id = str(uuid4())
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.count = AsyncMock(return_value=5)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.get_conversation_count(user_id)
        
        assert result == 5
        mock_query.filter.assert_called()
        mock_query.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_conversations(self):
        """Test searching conversations by title."""
        user_id = str(uuid4())
        search_term = "test"
        
        mock_conversations = [
            Mock(id=str(uuid4()), title="Test conversation", user_id=user_id),
            Mock(id=str(uuid4()), title="Another test", user_id=user_id)
        ]
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.offset = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = AsyncMock(return_value=mock_conversations)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.search_conversations(
            user_id=user_id,
            search_term=search_term,
            offset=0,
            limit=10
        )
        
        assert len(result) == 2
        assert all(search_term.lower() in conv.title.lower() for conv in result)

    @pytest.mark.asyncio
    async def test_archive_conversation(self):
        """Test archiving a conversation."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.is_archived = False
        
        with patch.object(self.service, 'get_conversation', return_value=mock_conversation):
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            result = await self.service.archive_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            assert result.is_archived is True
            self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_unarchive_conversation(self):
        """Test unarchiving a conversation."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.is_archived = True
        
        with patch.object(self.service, 'get_conversation', return_value=mock_conversation):
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            result = await self.service.unarchive_conversation(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            assert result.is_archived is False
            self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_conversation_metadata(self):
        """Test getting conversation metadata."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = user_id
        mock_conversation.message_count = 10
        mock_conversation.total_tokens = 1500
        mock_conversation.last_activity = datetime.utcnow()
        
        with patch.object(self.service, 'get_conversation', return_value=mock_conversation):
            result = await self.service.get_conversation_metadata(
                conversation_id=conversation_id,
                user_id=user_id
            )
            
            assert result["message_count"] == 10
            assert result["total_tokens"] == 1500
            assert "last_activity" in result

    @pytest.mark.asyncio
    async def test_bulk_delete_conversations(self):
        """Test bulk deleting conversations."""
        user_id = str(uuid4())
        conversation_ids = [str(uuid4()), str(uuid4()), str(uuid4())]
        
        mock_conversations = [
            Mock(id=cid, user_id=user_id) for cid in conversation_ids
        ]
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.all = AsyncMock(return_value=mock_conversations)
        
        self.mock_session.query = Mock(return_value=mock_query)
        self.mock_session.delete = Mock()
        self.mock_session.commit = AsyncMock()
        
        result = await self.service.bulk_delete_conversations(
            conversation_ids=conversation_ids,
            user_id=user_id
        )
        
        assert result == len(conversation_ids)
        assert self.mock_session.delete.call_count == len(conversation_ids)
        self.mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_recent_conversations(self):
        """Test getting recent conversations."""
        user_id = str(uuid4())
        
        mock_conversations = [
            Mock(id=str(uuid4()), title="Recent 1", user_id=user_id),
            Mock(id=str(uuid4()), title="Recent 2", user_id=user_id)
        ]
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.order_by = Mock(return_value=mock_query)
        mock_query.limit = Mock(return_value=mock_query)
        mock_query.all = AsyncMock(return_value=mock_conversations)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        result = await self.service.get_recent_conversations(
            user_id=user_id,
            limit=5
        )
        
        assert len(result) == 2
        mock_query.limit.assert_called_with(5)

    @pytest.mark.asyncio
    async def test_conversation_access_control(self):
        """Test conversation access control."""
        conversation_id = str(uuid4())
        user_id = str(uuid4())
        other_user_id = str(uuid4())
        
        mock_conversation = Mock()
        mock_conversation.id = conversation_id
        mock_conversation.user_id = other_user_id  # Different user
        
        mock_query = Mock()
        mock_query.filter = Mock(return_value=mock_query)
        mock_query.first = AsyncMock(return_value=mock_conversation)
        
        self.mock_session.query = Mock(return_value=mock_query)
        
        # Should not return conversation for different user
        result = await self.service.get_conversation(
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        # Implementation should check user_id matches
        mock_query.filter.assert_called()

    @pytest.mark.asyncio
    async def test_conversation_service_error_handling(self):
        """Test conversation service error handling."""
        user_id = str(uuid4())
        
        # Mock database error
        self.mock_session.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            await self.service.list_conversations(user_id)

    @pytest.mark.asyncio
    async def test_conversation_pagination(self):
        """Test conversation pagination."""
        user_id = str(uuid4())
        
        # Test different pagination parameters
        pagination_tests = [
            (0, 10),  # First page
            (10, 10), # Second page
            (0, 5),   # Smaller page size
            (20, 50)  # Large offset
        ]
        
        for offset, limit in pagination_tests:
            mock_query = Mock()
            mock_query.filter = Mock(return_value=mock_query)
            mock_query.order_by = Mock(return_value=mock_query)
            mock_query.offset = Mock(return_value=mock_query)
            mock_query.limit = Mock(return_value=mock_query)
            mock_query.all = AsyncMock(return_value=[])
            
            self.mock_session.query = Mock(return_value=mock_query)
            
            await self.service.list_conversations(
                user_id=user_id,
                offset=offset,
                limit=limit
            )
            
            mock_query.offset.assert_called_with(offset)
            mock_query.limit.assert_called_with(limit)

    @pytest.mark.asyncio
    async def test_conversation_sorting(self):
        """Test conversation sorting options."""
        user_id = str(uuid4())
        
        # Test different sort options
        sort_options = [
            ("created_at", "desc"),  # Newest first
            ("created_at", "asc"),   # Oldest first
            ("title", "asc"),        # Alphabetical
            ("updated_at", "desc")   # Recently updated
        ]
        
        for sort_field, sort_order in sort_options:
            mock_query = Mock()
            mock_query.filter = Mock(return_value=mock_query)
            mock_query.order_by = Mock(return_value=mock_query)
            mock_query.offset = Mock(return_value=mock_query)
            mock_query.limit = Mock(return_value=mock_query)
            mock_query.all = AsyncMock(return_value=[])
            
            self.mock_session.query = Mock(return_value=mock_query)
            
            await self.service.list_conversations(
                user_id=user_id,
                sort_field=sort_field,
                sort_order=sort_order
            )
            
            mock_query.order_by.assert_called()

    @pytest.mark.asyncio
    async def test_conversation_validation(self):
        """Test conversation input validation."""
        # Test invalid user ID
        with pytest.raises(ValueError):
            await self.service.create_conversation(
                user_id="invalid-uuid",
                title="Test",
                model="gpt-4"
            )
        
        # Test empty title
        with pytest.raises(ValueError):
            await self.service.create_conversation(
                user_id=str(uuid4()),
                title="",
                model="gpt-4"
            )
        
        # Test invalid model
        with pytest.raises(ValueError):
            await self.service.create_conversation(
                user_id=str(uuid4()),
                title="Test",
                model=""
            )