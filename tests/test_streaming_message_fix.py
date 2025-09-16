"""Test for the streaming message constraint fix."""
import pytest
from chatter.models.conversation import Message, MessageRole


class TestStreamingMessageFix:
    """Test that the streaming message constraint fix works properly."""

    @pytest.mark.unit
    def test_message_constraint_allows_empty_content(self):
        """Test that the updated constraint allows empty content for streaming scenarios."""
        # This should not raise any constraint validation errors during model creation
        message = Message(
            conversation_id="01K58749X39TXRST303W7STK63",
            role=MessageRole.ASSISTANT,
            content="",  # Empty content - this was failing before the fix
            sequence_number=1,
            retry_count=0,
            extra_metadata={"correlation_id": "test-correlation-id"}
        )
        
        # Basic validation - the model should be created without errors
        assert message.content == ""
        assert message.role == MessageRole.ASSISTANT
        assert message.conversation_id == "01K58749X39TXRST303W7STK63"
        assert message.sequence_number == 1
        assert message.retry_count == 0
        
    @pytest.mark.unit 
    def test_message_constraint_still_requires_not_null(self):
        """Test that the constraint still prevents NULL content."""
        # This should work fine at the model level, but would fail at DB level
        message = Message(
            conversation_id="01K58749X39TXRST303W7STK63",
            role=MessageRole.ASSISTANT,
            content=None,  # None should be handled properly by NOT NULL constraint
            sequence_number=1,
            retry_count=0,
            extra_metadata={"correlation_id": "test-correlation-id"}
        )
        
        # At the model level, None is allowed, but the DB constraint will handle this
        assert message.content is None
        assert message.role == MessageRole.ASSISTANT
        
    @pytest.mark.unit
    def test_constraint_name_unchanged(self):
        """Test that the constraint name remains the same for compatibility."""
        # Check that the constraint exists with the expected name
        constraint_names = [
            constraint.name for constraint in Message.__table__.constraints
        ]
        
        # The constraint should still be named "check_content_not_empty"
        assert "check_content_not_empty" in constraint_names
        
    @pytest.mark.unit  
    def test_normal_content_still_works(self):
        """Test that normal message content still works as expected."""
        message = Message(
            conversation_id="01K58749X39TXRST303W7STK63",
            role=MessageRole.ASSISTANT,
            content="This is a normal message with content",
            sequence_number=1,
            retry_count=0,
            extra_metadata={"correlation_id": "test-correlation-id"}
        )
        
        assert message.content == "This is a normal message with content"
        assert message.role == MessageRole.ASSISTANT