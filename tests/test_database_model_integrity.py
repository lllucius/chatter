"""Test database model integrity and constraints."""

import pytest
from sqlalchemy import text

from chatter.models.user import User
from chatter.models.conversation import Conversation, Message
from chatter.models.document import Document
from chatter.models.profile import Profile


class TestDatabaseModelIntegrity:
    """Test database model constraints and relationships."""

    @pytest.mark.unit
    def test_user_model_has_required_constraints(self):
        """Test that User model has all expected constraints."""
        # Check table constraints exist
        constraint_names = [constraint.name for constraint in User.__table__.constraints]
        
        expected_constraints = [
            'check_daily_message_limit_positive',
            'check_monthly_message_limit_positive', 
            'check_max_file_size_positive',
            'check_email_format',
            'check_username_format'
        ]
        
        for constraint in expected_constraints:
            assert constraint in constraint_names, f"Missing constraint: {constraint}"

    @pytest.mark.unit
    def test_conversation_model_has_required_constraints(self):
        """Test that Conversation model has all expected constraints."""
        constraint_names = [constraint.name for constraint in Conversation.__table__.constraints]
        
        expected_constraints = [
            'check_temperature_range',
            'check_max_tokens_positive',
            'check_context_window_positive',
            'check_retrieval_limit_positive',
            'check_retrieval_score_threshold_range',
            'check_message_count_non_negative',
            'check_total_tokens_non_negative',
            'check_total_cost_non_negative',
            'check_title_not_empty'
        ]
        
        for constraint in expected_constraints:
            assert constraint in constraint_names, f"Missing constraint: {constraint}"

    @pytest.mark.unit
    def test_message_model_has_required_constraints(self):
        """Test that Message model has all expected constraints."""
        constraint_names = [constraint.name for constraint in Message.__table__.constraints]
        
        expected_constraints = [
            'check_prompt_tokens_non_negative',
            'check_completion_tokens_non_negative',
            'check_total_tokens_non_negative',
            'check_response_time_non_negative',
            'check_cost_non_negative',
            'check_retry_count_non_negative',
            'check_sequence_number_non_negative',
            'check_content_not_empty',
            'uq_conversation_sequence'
        ]
        
        for constraint in expected_constraints:
            assert constraint in constraint_names, f"Missing constraint: {constraint}"

    @pytest.mark.unit
    def test_user_relationships_are_properly_defined(self):
        """Test that User model relationships are properly configured."""
        user = User.__mapper__
        
        # Check that relationships exist
        assert 'conversations' in user.relationships
        assert 'documents' in user.relationships  
        assert 'profiles' in user.relationships
        assert 'prompts' in user.relationships
        
        # Check cascade settings
        conversations_rel = user.relationships['conversations']
        cascade_str = str(conversations_rel.cascade)
        assert 'delete-orphan' in cascade_str and 'delete' in cascade_str

    @pytest.mark.unit
    def test_foreign_key_references_are_valid(self):
        """Test that foreign key references point to valid tables."""
        # Test User model foreign keys
        user_fks = [fk.target_fullname for fk in User.__table__.foreign_keys]
        
        # User should have foreign key to profiles for default_profile_id
        assert 'profiles.id' in user_fks
        
        # Test Conversation model foreign keys
        conversation_fks = [fk.target_fullname for fk in Conversation.__table__.foreign_keys]
        assert 'users.id' in conversation_fks
        assert 'profiles.id' in conversation_fks
        
        # Test Message model foreign keys
        message_fks = [fk.target_fullname for fk in Message.__table__.foreign_keys]
        assert 'conversations.id' in message_fks

    @pytest.mark.unit
    def test_model_fields_match_schema_requirements(self):
        """Test that model fields support all schema requirements."""
        # Check User model has phone_number field (fixed in this PR)
        user_columns = [column.name for column in User.__table__.columns]
        assert 'phone_number' in user_columns
        
        # Check required fields exist
        required_user_fields = ['email', 'username', 'hashed_password']
        for field in required_user_fields:
            assert field in user_columns

    @pytest.mark.unit 
    def test_model_indexes_are_properly_defined(self):
        """Test that important indexes are defined for performance."""
        # Check User model indexes
        user_indexes = [idx.name for idx in User.__table__.indexes]
        
        # Should have indexes on commonly queried fields
        user_columns_with_indexes = []
        for column in User.__table__.columns:
            if column.index:
                user_columns_with_indexes.append(column.name)
        
        # Important fields should be indexed
        assert 'email' in user_columns_with_indexes
        assert 'username' in user_columns_with_indexes
        
        # Check Conversation model indexes
        conversation_indexes = [idx.name for idx in Conversation.__table__.indexes]
        expected_conversation_indexes = ['idx_user_status', 'idx_user_created']
        
        for idx in expected_conversation_indexes:
            assert idx in conversation_indexes

    @pytest.mark.unit
    def test_model_enum_fields_are_properly_configured(self):
        """Test that enum fields use proper SQLAlchemy enum types.""" 
        from chatter.models.conversation import ConversationStatus, MessageRole
        from chatter.models.document import DocumentStatus, DocumentType
        from chatter.models.profile import ProfileType
        
        # Check that enum columns exist and are properly typed
        conversation_columns = {col.name: col for col in Conversation.__table__.columns}
        assert 'status' in conversation_columns
        
        message_columns = {col.name: col for col in Message.__table__.columns}
        assert 'role' in message_columns
        
        # Verify enum values are reasonable
        assert len(ConversationStatus) >= 3  # Should have active, archived, deleted
        assert len(MessageRole) >= 4  # Should have user, assistant, system, tool
        assert len(DocumentStatus) >= 4  # Should have pending, processing, processed, failed
        assert len(DocumentType) >= 5  # Should have various document types

    @pytest.mark.unit
    def test_json_fields_are_properly_defined(self):
        """Test that JSON fields are properly configured."""
        # Check Conversation model JSON fields
        conversation_columns = {col.name: col for col in Conversation.__table__.columns}
        assert 'tags' in conversation_columns
        assert 'extra_metadata' in conversation_columns
        
        # Check Message model JSON fields
        message_columns = {col.name: col for col in Message.__table__.columns}
        assert 'tool_calls' in message_columns
        assert 'retrieved_documents' in message_columns
        assert 'extra_metadata' in message_columns