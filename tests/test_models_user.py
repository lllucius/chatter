"""Tests for User model."""

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.exc import IntegrityError

from chatter.models.user import User
from chatter.models.base import Keys


@pytest.mark.unit
class TestUserModel:
    """Test User model structure and properties."""

    def test_user_model_inheritance(self):
        """Test that User inherits from Base correctly."""
        # Act
        user = User()

        # Assert
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')
        assert hasattr(user, 'updated_at')

    def test_user_table_name(self):
        """Test User model table name."""
        # Assert
        assert User.__tablename__ == "users"

    def test_user_required_fields(self):
        """Test User model has all required fields."""
        # Act
        user = User()

        # Assert - Authentication fields
        assert hasattr(user, 'email')
        assert hasattr(user, 'username')
        assert hasattr(user, 'hashed_password')

        # Profile fields
        assert hasattr(user, 'full_name')
        assert hasattr(user, 'bio')
        assert hasattr(user, 'avatar_url')

        # Status fields
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'is_verified')
        assert hasattr(user, 'is_superuser')

        # API access
        assert hasattr(user, 'api_key')
        assert hasattr(user, 'api_key_name')

        # Preferences
        assert hasattr(user, 'default_llm_provider')
        assert hasattr(user, 'default_profile_id')

        # Usage limits
        assert hasattr(user, 'daily_message_limit')
        assert hasattr(user, 'monthly_message_limit')
        assert hasattr(user, 'max_file_size_mb')

        # Timestamps
        assert hasattr(user, 'last_login_at')

    def test_user_column_configurations(self):
        """Test User model column configurations."""
        # Arrange
        table = User.__table__
        
        # Act & Assert - Email column
        email_col = table.columns['email']
        assert isinstance(email_col.type, String)
        assert email_col.type.length == 255
        assert email_col.unique is True
        assert email_col.index is True
        assert email_col.nullable is False

        # Username column
        username_col = table.columns['username']
        assert isinstance(username_col.type, String)
        assert username_col.type.length == 50
        assert username_col.unique is True
        assert username_col.index is True
        assert username_col.nullable is False

        # Hashed password column
        password_col = table.columns['hashed_password']
        assert isinstance(password_col.type, String)
        assert password_col.type.length == 255
        assert password_col.nullable is False

        # Bio column
        bio_col = table.columns['bio']
        assert isinstance(bio_col.type, Text)
        assert bio_col.nullable is True

        # Boolean columns
        is_active_col = table.columns['is_active']
        assert isinstance(is_active_col.type, Boolean)
        assert is_active_col.nullable is False
        assert is_active_col.default.arg is True

        is_verified_col = table.columns['is_verified']
        assert isinstance(is_verified_col.type, Boolean)
        assert is_verified_col.nullable is False
        assert is_verified_col.default.arg is False

        is_superuser_col = table.columns['is_superuser']
        assert isinstance(is_superuser_col.type, Boolean)
        assert is_superuser_col.nullable is False
        assert is_superuser_col.default.arg is False

        # Timestamp column
        last_login_col = table.columns['last_login_at']
        assert isinstance(last_login_col.type, DateTime)
        assert last_login_col.type.timezone is True
        assert last_login_col.nullable is True

    def test_user_foreign_key_relationships(self):
        """Test User model foreign key relationships."""
        # Arrange
        table = User.__table__
        
        # Act & Assert - Default profile foreign key
        default_profile_col = table.columns['default_profile_id']
        assert isinstance(default_profile_col.type, String)
        assert default_profile_col.type.length == 26  # ULID length
        assert default_profile_col.nullable is True
        assert default_profile_col.index is True
        
        # Check foreign key constraint
        fks = [fk for fk in table.foreign_keys if fk.column.table.name == 'profiles']
        assert len(fks) == 1
        assert str(fks[0].target_fullname) == Keys.PROFILES.value

    def test_user_table_constraints(self):
        """Test User model table constraints."""
        # Arrange
        constraints = User.__table__.constraints
        constraint_names = {c.name for c in constraints if hasattr(c, 'name') and c.name}

        # Assert - Check constraints exist
        expected_constraints = {
            'check_daily_message_limit_positive',
            'check_monthly_message_limit_positive',
            'check_max_file_size_positive',
            'check_email_format',
            'check_username_format'
        }
        
        for expected in expected_constraints:
            assert expected in constraint_names

    def test_user_relationships(self):
        """Test User model relationships are defined."""
        # Act
        user = User()

        # Assert
        assert hasattr(user, 'conversations')
        assert hasattr(user, 'documents')
        assert hasattr(user, 'profiles')
        assert hasattr(user, 'prompts')
        assert hasattr(user, 'default_profile')


@pytest.mark.unit
class TestUserMethods:
    """Test User model methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123",
            full_name="Test User",
            bio="Test bio",
            avatar_url="https://example.com/avatar.jpg",
            is_active=True,
            is_verified=False,
            is_superuser=False,
            default_llm_provider="openai",
            daily_message_limit=100,
            monthly_message_limit=3000,
            max_file_size_mb=10
        )

    def test_user_repr(self):
        """Test User string representation."""
        # Act
        repr_str = repr(self.user)

        # Assert
        assert "User(" in repr_str
        assert "test@example.com" in repr_str
        assert "testuser" in repr_str
        assert "id=" in repr_str

    def test_display_name_with_full_name(self):
        """Test display_name property when full_name is set."""
        # Act
        display_name = self.user.display_name

        # Assert
        assert display_name == "Test User"

    def test_display_name_without_full_name(self):
        """Test display_name property when full_name is None."""
        # Arrange
        self.user.full_name = None

        # Act
        display_name = self.user.display_name

        # Assert
        assert display_name == "testuser"

    def test_to_dict_complete(self):
        """Test to_dict method with complete user data."""
        # Arrange
        # Mock datetime objects for consistent testing
        mock_created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_updated_at = datetime(2024, 1, 2, 12, 0, 0)
        mock_last_login = datetime(2024, 1, 3, 12, 0, 0)
        
        self.user.id = "test_user_id_123456789"
        self.user.created_at = mock_created_at
        self.user.updated_at = mock_updated_at
        self.user.last_login_at = mock_last_login

        # Act
        user_dict = self.user.to_dict()

        # Assert
        expected_dict = {
            "id": "test_user_id_123456789",
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "bio": "Test bio",
            "avatar_url": "https://example.com/avatar.jpg",
            "is_active": True,
            "is_verified": False,
            "default_llm_provider": "openai",
            "default_profile_id": None,
            "created_at": "2024-01-01T12:00:00",
            "updated_at": "2024-01-02T12:00:00",
            "last_login_at": "2024-01-03T12:00:00"
        }
        
        assert user_dict == expected_dict

    def test_to_dict_excludes_sensitive_data(self):
        """Test to_dict method excludes sensitive data."""
        # Act
        user_dict = self.user.to_dict()

        # Assert - Sensitive fields should not be included
        sensitive_fields = [
            'hashed_password', 'api_key', 'is_superuser', 
            'daily_message_limit', 'monthly_message_limit', 'max_file_size_mb'
        ]
        
        for field in sensitive_fields:
            assert field not in user_dict

    def test_to_dict_with_none_values(self):
        """Test to_dict method handles None values correctly."""
        # Arrange
        minimal_user = User(
            email="minimal@example.com",
            username="minimal",
            hashed_password="hash"
        )
        minimal_user.id = "minimal_id_123456789"

        # Act
        user_dict = minimal_user.to_dict()

        # Assert
        assert user_dict["full_name"] is None
        assert user_dict["bio"] is None
        assert user_dict["avatar_url"] is None
        assert user_dict["default_llm_provider"] is None
        assert user_dict["default_profile_id"] is None
        assert user_dict["last_login_at"] is None


@pytest.mark.unit
class TestUserValidation:
    """Test User model validation and constraints."""

    def test_user_creation_with_valid_data(self):
        """Test creating user with valid data."""
        # Act
        user = User(
            email="valid@example.com",
            username="validuser123",
            hashed_password="secure_hash_12345",
            full_name="Valid User",
            is_active=True
        )

        # Assert
        assert user.email == "valid@example.com"
        assert user.username == "validuser123"
        assert user.hashed_password == "secure_hash_12345"
        assert user.full_name == "Valid User"
        assert user.is_active is True

    def test_user_creation_with_minimal_data(self):
        """Test creating user with minimal required data."""
        # Act
        user = User(
            email="minimal@example.com",
            username="minimal",
            hashed_password="hash123"
        )

        # Assert
        assert user.email == "minimal@example.com"
        assert user.username == "minimal"
        assert user.hashed_password == "hash123"
        # Check default values
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_superuser is False

    def test_user_default_values(self):
        """Test User model default values."""
        # Act
        user = User()

        # Assert
        assert user.is_active is True
        assert user.is_verified is False
        assert user.is_superuser is False
        assert user.full_name is None
        assert user.bio is None
        assert user.avatar_url is None
        assert user.api_key is None
        assert user.api_key_name is None
        assert user.default_llm_provider is None
        assert user.default_profile_id is None
        assert user.daily_message_limit is None
        assert user.monthly_message_limit is None
        assert user.max_file_size_mb is None
        assert user.last_login_at is None


@pytest.mark.unit
class TestUserConstraints:
    """Test User model constraints and validation."""

    def test_email_constraint_validation(self):
        """Test email format constraint."""
        # This test would require actual database integration to test constraints
        # For unit testing, we'll test the constraint definition exists
        
        # Arrange
        constraints = User.__table__.constraints
        email_constraint = next(
            (c for c in constraints if hasattr(c, 'name') and c.name == 'check_email_format'), 
            None
        )
        
        # Assert
        assert email_constraint is not None

    def test_username_constraint_validation(self):
        """Test username format constraint."""
        # Arrange
        constraints = User.__table__.constraints
        username_constraint = next(
            (c for c in constraints if hasattr(c, 'name') and c.name == 'check_username_format'), 
            None
        )
        
        # Assert
        assert username_constraint is not None

    def test_message_limit_constraints(self):
        """Test message limit constraints exist."""
        # Arrange
        constraints = User.__table__.constraints
        constraint_names = {c.name for c in constraints if hasattr(c, 'name') and c.name}
        
        # Assert
        assert 'check_daily_message_limit_positive' in constraint_names
        assert 'check_monthly_message_limit_positive' in constraint_names

    def test_file_size_constraint(self):
        """Test file size constraint exists."""
        # Arrange
        constraints = User.__table__.constraints
        constraint_names = {c.name for c in constraints if hasattr(c, 'name') and c.name}
        
        # Assert
        assert 'check_max_file_size_positive' in constraint_names


@pytest.mark.integration
class TestUserModelIntegration:
    """Integration tests for User model."""

    def test_user_with_relationships(self):
        """Test User model with relationship attributes."""
        # Arrange
        user = User(
            email="relationship@example.com",
            username="reluser",
            hashed_password="hash123"
        )

        # Act & Assert - Test that relationship attributes exist and are lists
        assert hasattr(user, 'conversations')
        assert hasattr(user, 'documents')
        assert hasattr(user, 'profiles')
        assert hasattr(user, 'prompts')
        assert hasattr(user, 'default_profile')

        # These would be empty lists initially (before database persistence)
        # In a real integration test with database, we'd test actual relationships

    def test_user_lifecycle_methods(self):
        """Test complete user lifecycle: create, update, access."""
        # Arrange
        user = User(
            email="lifecycle@example.com",
            username="lifecycle",
            hashed_password="initial_hash"
        )

        # Act - Simulate user updates
        user.full_name = "Updated Name"
        user.bio = "Updated bio"
        user.is_verified = True
        user.last_login_at = datetime.utcnow()

        # Assert
        assert user.full_name == "Updated Name"
        assert user.bio == "Updated bio"
        assert user.is_verified is True
        assert user.last_login_at is not None
        assert user.display_name == "Updated Name"

        # Test to_dict after updates
        user_dict = user.to_dict()
        assert user_dict["full_name"] == "Updated Name"
        assert user_dict["bio"] == "Updated bio"
        assert user_dict["is_verified"] is True

    def test_user_api_key_management(self):
        """Test user API key functionality."""
        # Arrange
        user = User(
            email="api@example.com",
            username="apiuser",
            hashed_password="hash123"
        )

        # Act
        user.api_key = "sk_test_1234567890abcdef"
        user.api_key_name = "Primary API Key"

        # Assert
        assert user.api_key == "sk_test_1234567890abcdef"
        assert user.api_key_name == "Primary API Key"

        # Test that API key is not in to_dict output
        user_dict = user.to_dict()
        assert "api_key" not in user_dict
        assert "api_key_name" not in user_dict

    def test_user_preferences_management(self):
        """Test user preferences functionality."""
        # Arrange
        user = User(
            email="prefs@example.com",
            username="prefsuser",
            hashed_password="hash123"
        )

        # Act
        user.default_llm_provider = "anthropic"
        user.default_profile_id = "profile_id_123456789012345"
        user.daily_message_limit = 50
        user.monthly_message_limit = 1500
        user.max_file_size_mb = 25

        # Assert
        assert user.default_llm_provider == "anthropic"
        assert user.default_profile_id == "profile_id_123456789012345"
        assert user.daily_message_limit == 50
        assert user.monthly_message_limit == 1500
        assert user.max_file_size_mb == 25

        # Test that limits are not in to_dict output (sensitive data)
        user_dict = user.to_dict()
        assert "daily_message_limit" not in user_dict
        assert "monthly_message_limit" not in user_dict
        assert "max_file_size_mb" not in user_dict

    def test_user_status_management(self):
        """Test user status fields functionality."""
        # Arrange
        user = User(
            email="status@example.com",
            username="statususer",
            hashed_password="hash123"
        )

        # Act - Test status changes
        assert user.is_active is True  # Default
        assert user.is_verified is False  # Default
        assert user.is_superuser is False  # Default

        user.is_active = False
        user.is_verified = True
        user.is_superuser = True

        # Assert
        assert user.is_active is False
        assert user.is_verified is True
        assert user.is_superuser is True

        # Test to_dict includes some status but not superuser
        user_dict = user.to_dict()
        assert user_dict["is_active"] is False
        assert user_dict["is_verified"] is True
        assert "is_superuser" not in user_dict  # Sensitive field


@pytest.mark.unit
class TestUserEdgeCases:
    """Test edge cases in User model."""

    def test_user_with_empty_strings(self):
        """Test user with empty string values."""
        # Act
        user = User(
            email="",  # This would fail constraint in real DB
            username="",  # This would fail constraint in real DB
            hashed_password="",
            full_name="",
            bio="",
            avatar_url=""
        )

        # Assert - Object creation should work, but constraints would fail in DB
        assert user.email == ""
        assert user.username == ""
        assert user.full_name == ""
        assert user.bio == ""
        assert user.avatar_url == ""

    def test_user_display_name_with_empty_full_name(self):
        """Test display_name with empty full_name."""
        # Arrange
        user = User(username="testuser")
        user.full_name = ""

        # Act
        display_name = user.display_name

        # Assert
        assert display_name == "testuser"  # Falls back to username

    def test_user_to_dict_with_none_timestamps(self):
        """Test to_dict with None timestamp values."""
        # Arrange
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hash"
        )
        user.created_at = None
        user.updated_at = None
        user.last_login_at = None

        # Act
        user_dict = user.to_dict()

        # Assert
        assert user_dict["created_at"] is None
        assert user_dict["updated_at"] is None
        assert user_dict["last_login_at"] is None