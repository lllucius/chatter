"""Database Model tests."""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from chatter.models.conversation import User, Conversation, Message
from chatter.models.profile import Profile


@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""

    async def test_user_creation_and_validation(self, test_session: AsyncSession):
        """Test user creation and validation."""
        # Create a valid user
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password_123"
        )
        
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password_hash == "hashed_password_123"
        assert user.created_at is not None
        assert user.is_active is True

    async def test_email_uniqueness_constraint(self, test_session: AsyncSession):
        """Test email uniqueness constraint."""
        # Create first user
        user1 = User(
            email="unique@example.com",
            username="user1",
            password_hash="hash1"
        )
        test_session.add(user1)
        await test_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",  # Same email
            username="user2",
            password_hash="hash2"
        )
        test_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_username_uniqueness_constraint(self, test_session: AsyncSession):
        """Test username uniqueness constraint."""
        # Create first user
        user1 = User(
            email="user1@example.com",
            username="uniqueuser",
            password_hash="hash1"
        )
        test_session.add(user1)
        await test_session.commit()
        
        # Try to create second user with same username
        user2 = User(
            email="user2@example.com",
            username="uniqueuser",  # Same username
            password_hash="hash2"
        )
        test_session.add(user2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_password_hashing_integration(self, test_session: AsyncSession):
        """Test password hashing integration."""
        from chatter.utils.security import hash_password, verify_password
        
        plain_password = "MySecurePassword123!"
        hashed_password = hash_password(plain_password)
        
        user = User(
            email="password@example.com",
            username="passworduser",
            password_hash=hashed_password
        )
        
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Verify password can be checked
        assert verify_password(plain_password, user.password_hash)
        assert not verify_password("wrong_password", user.password_hash)

    async def test_soft_delete_functionality(self, test_session: AsyncSession):
        """Test soft delete functionality."""
        user = User(
            email="delete@example.com",
            username="deleteuser",
            password_hash="hash"
        )
        
        test_session.add(user)
        await test_session.commit()
        user_id = user.id
        
        # Soft delete
        user.is_active = False
        user.deleted_at = datetime.utcnow()
        await test_session.commit()
        
        # User should still exist in database
        await test_session.refresh(user)
        assert user.is_active is False
        assert user.deleted_at is not None

    async def test_user_relationships(self, test_session: AsyncSession):
        """Test user relationship management."""
        # Create user
        user = User(
            email="relationships@example.com",
            username="reluser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create conversations for the user
        conv1 = Conversation(
            title="Test Conversation 1",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        conv2 = Conversation(
            title="Test Conversation 2",
            user_id=user.id,
            model="gpt-4"
        )
        
        test_session.add_all([conv1, conv2])
        await test_session.commit()
        
        # Test relationship access
        await test_session.refresh(user)
        conversations = await user.get_conversations(test_session)
        assert len(conversations) == 2

    async def test_user_timestamps(self, test_session: AsyncSession):
        """Test automatic timestamp management."""
        user = User(
            email="timestamps@example.com",
            username="timestampuser",
            password_hash="hash"
        )
        
        creation_time = datetime.utcnow()
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Created timestamp should be set
        assert user.created_at is not None
        assert user.created_at >= creation_time
        
        # Update user
        original_created = user.created_at
        await asyncio.sleep(0.01)  # Small delay
        user.email = "updated@example.com"
        await test_session.commit()
        await test_session.refresh(user)
        
        # Created timestamp should not change
        assert user.created_at == original_created


@pytest.mark.unit
class TestConversationModel:
    """Test Conversation model functionality."""

    async def test_conversation_lifecycle_management(self, test_session: AsyncSession):
        """Test conversation lifecycle management."""
        # Create user first
        user = User(
            email="conv@example.com",
            username="convuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create conversation
        conversation = Conversation(
            title="Test Conversation",
            user_id=user.id,
            model="gpt-3.5-turbo",
            system_prompt="You are a helpful assistant."
        )
        
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        assert conversation.id is not None
        assert conversation.title == "Test Conversation"
        assert conversation.user_id == user.id
        assert conversation.model == "gpt-3.5-turbo"
        assert conversation.system_prompt == "You are a helpful assistant."
        assert conversation.created_at is not None

    async def test_user_conversation_relationships(self, test_session: AsyncSession):
        """Test user-conversation relationships."""
        # Create user
        user = User(
            email="userconv@example.com",
            username="userconvuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create multiple conversations
        conversations = []
        for i in range(3):
            conv = Conversation(
                title=f"Conversation {i+1}",
                user_id=user.id,
                model="gpt-3.5-turbo"
            )
            conversations.append(conv)
            test_session.add(conv)
        
        await test_session.commit()
        
        # Test relationship access
        user_conversations = await user.get_conversations(test_session)
        assert len(user_conversations) == 3
        
        # Test conversation belongs to user
        for conv in conversations:
            await test_session.refresh(conv)
            assert conv.user_id == user.id

    async def test_message_associations(self, test_session: AsyncSession):
        """Test message associations with conversations."""
        # Create user and conversation
        user = User(
            email="msgconv@example.com",
            username="msgconvuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        conversation = Conversation(
            title="Message Test Conversation",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Create messages
        messages = [
            Message(
                conversation_id=conversation.id,
                role="user",
                content="Hello, how are you?"
            ),
            Message(
                conversation_id=conversation.id,
                role="assistant",
                content="I'm doing well, thank you! How can I help you today?"
            ),
            Message(
                conversation_id=conversation.id,
                role="user",
                content="Can you help me with Python?"
            )
        ]
        
        test_session.add_all(messages)
        await test_session.commit()
        
        # Test message retrieval
        conv_messages = await conversation.get_messages(test_session)
        assert len(conv_messages) == 3
        assert conv_messages[0].role == "user"
        assert conv_messages[1].role == "assistant"
        assert conv_messages[2].role == "user"

    async def test_conversation_metadata_handling(self, test_session: AsyncSession):
        """Test conversation metadata handling."""
        # Create user
        user = User(
            email="metadata@example.com",
            username="metadatauser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create conversation with metadata
        metadata = {
            "temperature": 0.7,
            "max_tokens": 1000,
            "top_p": 0.9,
            "tags": ["programming", "help"],
            "custom_field": "custom_value"
        }
        
        conversation = Conversation(
            title="Metadata Test",
            user_id=user.id,
            model="gpt-4",
            metadata=metadata
        )
        
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Test metadata retrieval
        assert conversation.metadata["temperature"] == 0.7
        assert conversation.metadata["max_tokens"] == 1000
        assert "programming" in conversation.metadata["tags"]
        assert conversation.metadata["custom_field"] == "custom_value"

    async def test_model_configuration_storage(self, test_session: AsyncSession):
        """Test model configuration storage."""
        # Create user
        user = User(
            email="modelconf@example.com",
            username="modelconfuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Test different model configurations
        models_config = [
            {
                "model": "gpt-3.5-turbo",
                "config": {
                    "temperature": 0.7,
                    "max_tokens": 1000,
                    "provider": "openai"
                }
            },
            {
                "model": "claude-3-sonnet",
                "config": {
                    "temperature": 0.5,
                    "max_tokens": 2000,
                    "provider": "anthropic"
                }
            }
        ]
        
        conversations = []
        for model_data in models_config:
            conv = Conversation(
                title=f"Test {model_data['model']}",
                user_id=user.id,
                model=model_data["model"],
                model_config=model_data["config"]
            )
            conversations.append(conv)
            test_session.add(conv)
        
        await test_session.commit()
        
        # Verify configurations
        for i, conv in enumerate(conversations):
            await test_session.refresh(conv)
            expected_config = models_config[i]["config"]
            assert conv.model_config["temperature"] == expected_config["temperature"]
            assert conv.model_config["provider"] == expected_config["provider"]


@pytest.mark.unit
class TestProfileModel:
    """Test Profile model functionality."""

    async def test_user_profile_management(self, test_session: AsyncSession):
        """Test user profile management."""
        # Create user
        user = User(
            email="profile@example.com",
            username="profileuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            display_name="John Doe",
            bio="Software developer and AI enthusiast",
            timezone="UTC",
            language="en"
        )
        
        test_session.add(profile)
        await test_session.commit()
        await test_session.refresh(profile)
        
        assert profile.user_id == user.id
        assert profile.display_name == "John Doe"
        assert profile.bio == "Software developer and AI enthusiast"
        assert profile.timezone == "UTC"
        assert profile.language == "en"

    async def test_settings_and_preferences_storage(self, test_session: AsyncSession):
        """Test settings and preferences storage."""
        # Create user
        user = User(
            email="settings@example.com",
            username="settingsuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create profile with preferences
        preferences = {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": False,
                "desktop": True
            },
            "ai_settings": {
                "default_model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "privacy": {
                "data_sharing": False,
                "analytics": True
            }
        }
        
        profile = Profile(
            user_id=user.id,
            display_name="Settings User",
            preferences=preferences
        )
        
        test_session.add(profile)
        await test_session.commit()
        await test_session.refresh(profile)
        
        # Test preference retrieval
        assert profile.preferences["theme"] == "dark"
        assert profile.preferences["notifications"]["email"] is True
        assert profile.preferences["ai_settings"]["default_model"] == "gpt-4"
        assert profile.preferences["privacy"]["data_sharing"] is False

    async def test_profile_updates_and_validation(self, test_session: AsyncSession):
        """Test profile updates and validation."""
        # Create user and profile
        user = User(
            email="update@example.com",
            username="updateuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        profile = Profile(
            user_id=user.id,
            display_name="Original Name",
            bio="Original bio",
            timezone="UTC"
        )
        test_session.add(profile)
        await test_session.commit()
        original_created = profile.created_at
        
        # Update profile
        await asyncio.sleep(0.01)  # Small delay
        profile.display_name = "Updated Name"
        profile.bio = "Updated bio with more details"
        profile.timezone = "America/New_York"
        
        await test_session.commit()
        await test_session.refresh(profile)
        
        # Verify updates
        assert profile.display_name == "Updated Name"
        assert profile.bio == "Updated bio with more details"
        assert profile.timezone == "America/New_York"
        assert profile.created_at == original_created  # Should not change
        assert profile.updated_at > original_created  # Should be updated

    async def test_default_value_handling(self, test_session: AsyncSession):
        """Test default value handling."""
        # Create user
        user = User(
            email="defaults@example.com",
            username="defaultsuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create minimal profile (test defaults)
        profile = Profile(
            user_id=user.id,
            display_name="Minimal User"
        )
        
        test_session.add(profile)
        await test_session.commit()
        await test_session.refresh(profile)
        
        # Test default values
        assert profile.display_name == "Minimal User"
        assert profile.bio is None or profile.bio == ""
        assert profile.timezone == "UTC"  # Default timezone
        assert profile.language == "en"   # Default language
        assert profile.preferences == {} or profile.preferences is None

    async def test_profile_user_relationship(self, test_session: AsyncSession):
        """Test profile-user relationship."""
        # Create user
        user = User(
            email="relationship@example.com",
            username="relationshipuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            display_name="Relationship Test"
        )
        test_session.add(profile)
        await test_session.commit()
        await test_session.refresh(profile)
        
        # Test relationship access
        profile_user = await profile.get_user(test_session)
        assert profile_user.id == user.id
        assert profile_user.email == "relationship@example.com"
        
        # Test reverse relationship
        user_profile = await user.get_profile(test_session)
        assert user_profile.id == profile.id
        assert user_profile.display_name == "Relationship Test"


@pytest.mark.unit
class TestMessageModel:
    """Test Message model functionality."""

    async def test_message_creation_and_validation(self, test_session: AsyncSession):
        """Test message creation and validation."""
        # Create user and conversation
        user = User(
            email="message@example.com",
            username="messageuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        conversation = Conversation(
            title="Message Test",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Create message
        message = Message(
            conversation_id=conversation.id,
            role="user",
            content="Hello, this is a test message."
        )
        
        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)
        
        assert message.id is not None
        assert message.conversation_id == conversation.id
        assert message.role == "user"
        assert message.content == "Hello, this is a test message."
        assert message.created_at is not None

    async def test_message_ordering(self, test_session: AsyncSession):
        """Test message ordering within conversations."""
        # Create user and conversation
        user = User(
            email="ordering@example.com",
            username="orderinguser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        conversation = Conversation(
            title="Ordering Test",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Create messages in specific order
        messages_data = [
            ("user", "First message"),
            ("assistant", "First response"),
            ("user", "Second message"),
            ("assistant", "Second response")
        ]
        
        for role, content in messages_data:
            message = Message(
                conversation_id=conversation.id,
                role=role,
                content=content
            )
            test_session.add(message)
            await test_session.commit()
            await asyncio.sleep(0.001)  # Ensure different timestamps
        
        # Retrieve messages and verify order
        messages = await conversation.get_messages(test_session, order_by="created_at")
        assert len(messages) == 4
        assert messages[0].content == "First message"
        assert messages[1].content == "First response"
        assert messages[2].content == "Second message"
        assert messages[3].content == "Second response"

    async def test_message_metadata(self, test_session: AsyncSession):
        """Test message metadata storage."""
        # Create user and conversation
        user = User(
            email="msgmeta@example.com",
            username="msgmetauser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        conversation = Conversation(
            title="Metadata Test",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Create message with metadata
        metadata = {
            "token_count": 25,
            "processing_time": 1.5,
            "model_used": "gpt-3.5-turbo",
            "temperature": 0.7,
            "finish_reason": "stop"
        }
        
        message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content="This is a response with metadata.",
            metadata=metadata
        )
        
        test_session.add(message)
        await test_session.commit()
        await test_session.refresh(message)
        
        # Verify metadata
        assert message.metadata["token_count"] == 25
        assert message.metadata["processing_time"] == 1.5
        assert message.metadata["model_used"] == "gpt-3.5-turbo"
        assert message.metadata["finish_reason"] == "stop"


@pytest.mark.integration
class TestModelIntegration:
    """Integration tests for model interactions."""

    async def test_complete_conversation_model_workflow(self, test_session: AsyncSession):
        """Test complete conversation workflow with all models."""
        # 1. Create user
        user = User(
            email="workflow@example.com",
            username="workflowuser",
            password_hash="hashed_password"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        # 2. Create user profile
        profile = Profile(
            user_id=user.id,
            display_name="Workflow User",
            preferences={
                "theme": "dark",
                "default_model": "gpt-4"
            }
        )
        test_session.add(profile)
        await test_session.commit()
        
        # 3. Create conversation
        conversation = Conversation(
            title="Complete Workflow Test",
            user_id=user.id,
            model="gpt-4",
            system_prompt="You are a helpful assistant.",
            metadata={"test_type": "integration"}
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # 4. Create conversation messages
        messages_data = [
            ("user", "Hello, can you help me?"),
            ("assistant", "Of course! I'd be happy to help you."),
            ("user", "What's the weather like?"),
            ("assistant", "I don't have access to real-time weather data, but I can help you find weather information.")
        ]
        
        for role, content in messages_data:
            message = Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                metadata={"timestamp": datetime.utcnow().isoformat()}
            )
            test_session.add(message)
        
        await test_session.commit()
        
        # 5. Verify complete workflow
        # Check user has conversation
        user_conversations = await user.get_conversations(test_session)
        assert len(user_conversations) == 1
        assert user_conversations[0].title == "Complete Workflow Test"
        
        # Check conversation has messages
        conv_messages = await conversation.get_messages(test_session)
        assert len(conv_messages) == 4
        
        # Check user has profile
        user_profile = await user.get_profile(test_session)
        assert user_profile.display_name == "Workflow User"

    async def test_model_constraint_validation(self, test_session: AsyncSession):
        """Test model constraint validation."""
        # Test user email constraint
        with pytest.raises(IntegrityError):
            user1 = User(
                email="duplicate@example.com",
                username="user1",
                password_hash="hash1"
            )
            user2 = User(
                email="duplicate@example.com",  # Duplicate email
                username="user2",
                password_hash="hash2"
            )
            test_session.add_all([user1, user2])
            await test_session.commit()

    async def test_cascade_operations(self, test_session: AsyncSession):
        """Test cascade delete operations."""
        # Create user with conversation and messages
        user = User(
            email="cascade@example.com",
            username="cascadeuser",
            password_hash="hash"
        )
        test_session.add(user)
        await test_session.commit()
        await test_session.refresh(user)
        
        conversation = Conversation(
            title="Cascade Test",
            user_id=user.id,
            model="gpt-3.5-turbo"
        )
        test_session.add(conversation)
        await test_session.commit()
        await test_session.refresh(conversation)
        
        # Add messages
        for i in range(3):
            message = Message(
                conversation_id=conversation.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i+1}"
            )
            test_session.add(message)
        
        await test_session.commit()
        
        # Verify setup
        messages = await conversation.get_messages(test_session)
        assert len(messages) == 3
        
        # Test soft delete (if implemented)
        # This would depend on the actual cascade configuration
        # For now, we'll just verify the relationships exist
        user_conversations = await user.get_conversations(test_session)
        assert len(user_conversations) == 1