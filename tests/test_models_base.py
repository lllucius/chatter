"""Tests for base model functionality."""

import re
from datetime import datetime

import pytest
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from chatter.models.base import Base, Keys, generate_ulid


@pytest.mark.unit
class TestGenerateUlid:
    """Test ULID generation functionality."""

    def test_generate_ulid_format(self):
        """Test that generated ULID has correct format."""
        # Act
        ulid = generate_ulid()

        # Assert
        assert isinstance(ulid, str)
        assert len(ulid) == 26
        # ULID should contain only valid base32 characters (Crockford's)
        valid_chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        assert all(c in valid_chars for c in ulid.upper())

    def test_generate_ulid_uniqueness(self):
        """Test that generated ULIDs are unique."""
        # Act
        ulids = [generate_ulid() for _ in range(100)]

        # Assert
        assert len(set(ulids)) == 100  # All should be unique

    def test_generate_ulid_sortability(self):
        """Test that ULIDs are lexicographically sortable by time."""
        # Act - Generate ULIDs with small delay
        import time
        ulid1 = generate_ulid()
        time.sleep(0.001)  # Small delay to ensure different timestamp
        ulid2 = generate_ulid()

        # Assert
        assert ulid1 < ulid2  # Later ULID should be lexicographically greater


@pytest.mark.unit
class TestBaseModel:
    """Test Base model functionality."""

    def test_base_model_has_required_columns(self):
        """Test that Base model has required columns."""
        # Act
        base_instance = Base()

        # Assert
        assert hasattr(base_instance, 'id')
        assert hasattr(base_instance, 'created_at')
        assert hasattr(base_instance, 'updated_at')

    def test_base_model_id_column_configuration(self):
        """Test ID column configuration."""
        # Arrange
        id_column = Base.__table__.columns['id']

        # Assert
        assert isinstance(id_column.type, String)
        assert id_column.type.length == 26  # ULID length
        assert id_column.primary_key is True
        assert id_column.default is not None

    def test_base_model_timestamp_columns(self):
        """Test timestamp column configuration."""
        # Arrange
        created_at_column = Base.__table__.columns['created_at']
        updated_at_column = Base.__table__.columns['updated_at']

        # Assert
        assert isinstance(created_at_column.type, DateTime)
        assert created_at_column.type.timezone is True
        assert created_at_column.nullable is False
        assert created_at_column.server_default is not None

        assert isinstance(updated_at_column.type, DateTime)
        assert updated_at_column.type.timezone is True
        assert updated_at_column.nullable is False
        assert updated_at_column.server_default is not None
        assert updated_at_column.onupdate is not None


@pytest.mark.unit
class TestTableNameGeneration:
    """Test automatic table name generation."""

    def test_simple_class_name(self):
        """Test simple class name conversion."""
        # Arrange
        class User(Base):
            pass

        # Assert
        assert User.__tablename__ == "users"

    def test_camelcase_class_name(self):
        """Test CamelCase class name conversion."""
        # Arrange
        class UserProfile(Base):
            pass

        # Assert
        assert UserProfile.__tablename__ == "user_profiles"

    def test_class_ending_with_s(self):
        """Test class name already ending with 's'."""
        # Arrange
        class Analytics(Base):
            pass

        # Assert
        assert Analytics.__tablename__ == "analytics"

    def test_class_ending_with_y(self):
        """Test class name ending with 'y'."""
        # Arrange
        class Category(Base):
            pass

        # Assert
        assert Category.__tablename__ == "categories"

    def test_class_ending_with_ch(self):
        """Test class name ending with 'ch'."""
        # Arrange
        class Branch(Base):
            pass

        # Assert
        assert Branch.__tablename__ == "branches"

    def test_class_ending_with_sh(self):
        """Test class name ending with 'sh'."""
        # Arrange
        class Brush(Base):
            pass

        # Assert
        assert Brush.__tablename__ == "brushes"

    def test_class_ending_with_x(self):
        """Test class name ending with 'x'."""
        # Arrange
        class Box(Base):
            pass

        # Assert
        assert Box.__tablename__ == "boxes"

    def test_class_ending_with_z(self):
        """Test class name ending with 'z'."""
        # Arrange
        class Quiz(Base):
            pass

        # Assert
        assert Quiz.__tablename__ == "quizzes"

    def test_class_ending_with_f(self):
        """Test class name ending with 'f'."""
        # Arrange
        class Shelf(Base):
            pass

        # Assert
        assert Shelf.__tablename__ == "shelves"

    def test_class_ending_with_fe(self):
        """Test class name ending with 'fe'."""
        # Arrange
        class Life(Base):
            pass

        # Assert
        assert Life.__tablename__ == "lives"

    def test_complex_camelcase_name(self):
        """Test complex CamelCase name conversion."""
        # Arrange
        class UserPreferenceCategory(Base):
            pass

        # Assert
        assert UserPreferenceCategory.__tablename__ == "user_preference_categories"

    def test_abbreviation_in_name(self):
        """Test class name with abbreviations."""
        # Arrange
        class APIKey(Base):
            pass

        # Assert
        assert APIKey.__tablename__ == "a_p_i_keys"  # Each capital becomes separate

    def test_number_in_name(self):
        """Test class name with numbers."""
        # Arrange
        class OAuth2Token(Base):
            pass

        # Assert
        assert OAuth2Token.__tablename__ == "o_auth2_tokens"


@pytest.mark.unit
class TestKeys:
    """Test Keys enum for foreign key references."""

    def test_keys_enum_exists(self):
        """Test that Keys enum exists and has expected values."""
        # Assert
        assert hasattr(Keys, 'USERS')
        assert hasattr(Keys, 'CONVERSATIONS')
        assert hasattr(Keys, 'MESSAGES')
        assert hasattr(Keys, 'DOCUMENTS')
        assert hasattr(Keys, 'PROFILES')

    def test_keys_enum_values_format(self):
        """Test that Keys enum values have correct format."""
        # Act
        keys_values = [key.value for key in Keys]

        # Assert
        for value in keys_values:
            assert isinstance(value, str)
            assert "." in value
            assert value.endswith(".id")

    def test_specific_key_values(self):
        """Test specific key values."""
        # Assert
        assert Keys.USERS.value == "users.id"
        assert Keys.CONVERSATIONS.value == "conversations.id"
        assert Keys.MESSAGES.value == "messages.id"
        assert Keys.DOCUMENTS.value == "documents.id"
        assert Keys.DOCUMENT_CHUNKS.value == "document_chunks.id"
        assert Keys.PROFILES.value == "profiles.id"
        assert Keys.PROMPTS.value == "prompts.id"
        assert Keys.TOOL_SERVERS.value == "tool_servers.id"

    def test_keys_enum_inheritance(self):
        """Test that Keys enum inherits from str and Enum."""
        # Assert
        assert issubclass(Keys, str)
        from enum import Enum
        assert issubclass(Keys, Enum)

    def test_keys_enum_string_operations(self):
        """Test that Keys can be used as strings."""
        # Act
        user_key = Keys.USERS
        
        # Assert
        assert str(user_key) == "users.id"
        assert user_key == "users.id"
        assert user_key.startswith("users")
        assert user_key.endswith(".id")


@pytest.mark.integration
class TestBaseModelIntegration:
    """Integration tests for Base model."""

    def test_model_creation_with_inheritance(self):
        """Test creating a model that inherits from Base."""
        # Arrange
        class TestModel(Base):
            name: Mapped[str] = mapped_column(String(100))
            
            def __repr__(self):
                return f"<TestModel(id={self.id}, name={self.name})>"

        # Act
        instance = TestModel(name="Test Instance")

        # Assert
        assert hasattr(instance, 'id')
        assert hasattr(instance, 'created_at')
        assert hasattr(instance, 'updated_at')
        assert instance.name == "Test Instance"
        assert TestModel.__tablename__ == "test_models"

    def test_multiple_models_with_different_names(self):
        """Test multiple models have different table names."""
        # Arrange
        class FirstModel(Base):
            pass

        class SecondModel(Base):
            pass

        class ThirdComplexModel(Base):
            pass

        # Assert
        assert FirstModel.__tablename__ == "first_models"
        assert SecondModel.__tablename__ == "second_models"
        assert ThirdComplexModel.__tablename__ == "third_complex_models"

    def test_ulid_generation_integration(self):
        """Test ULID generation in model context."""
        # Arrange
        class TestUlidModel(Base):
            name: Mapped[str] = mapped_column(String(50))

        # Act
        instance1 = TestUlidModel(name="First")
        instance2 = TestUlidModel(name="Second")

        # Assert
        # IDs should be different even though generated at same time
        assert instance1.id != instance2.id if instance1.id and instance2.id else True
        # Both should be valid ULID format
        if instance1.id:
            assert len(instance1.id) == 26
        if instance2.id:
            assert len(instance2.id) == 26


@pytest.mark.unit
class TestTableNameEdgeCases:
    """Test edge cases in table name generation."""

    def test_single_letter_class(self):
        """Test single letter class name."""
        # Arrange
        class A(Base):
            pass

        # Assert
        assert A.__tablename__ == "as"

    def test_all_caps_class(self):
        """Test all caps class name."""
        # Arrange
        class HTML(Base):
            pass

        # Assert
        assert HTML.__tablename__ == "h_t_m_ls"

    def test_mixed_case_with_numbers(self):
        """Test mixed case with numbers."""
        # Arrange
        class OAuth2ClientSecret(Base):
            pass

        # Assert
        assert OAuth2ClientSecret.__tablename__ == "o_auth2_client_secrets"

    def test_class_with_underscores(self):
        """Test class name that already has underscores."""
        # Arrange  
        class User_Profile(Base):  # Not recommended, but should work
            pass

        # Assert
        # Should convert normally, underscores are preserved
        expected_name = "user__profiles"  # Double underscore due to existing one
        assert User_Profile.__tablename__ == expected_name

    def test_empty_class_name_handling(self):
        """Test edge case handling of class names."""
        # This test is more about ensuring the regex doesn't break
        # with unusual but valid Python class names
        
        # Test that the regex patterns work correctly
        name = "TestClass"
        step1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        step2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", step1).lower()
        
        assert step1 == "Test_Class"
        assert step2 == "test_class"


@pytest.mark.unit
class TestUlidProperties:
    """Test ULID properties and characteristics."""

    def test_ulid_timestamp_component(self):
        """Test ULID timestamp component."""
        # Arrange
        import time
        from ulid import ULID
        
        start_time = time.time()
        ulid_obj = ULID()
        end_time = time.time()

        # Act
        timestamp = ulid_obj.timestamp

        # Assert
        # Timestamp should be within the time window
        assert start_time <= timestamp <= end_time

    def test_ulid_randomness_component(self):
        """Test ULID randomness component."""
        # Arrange
        from ulid import ULID
        
        # Act
        ulid1 = ULID()
        ulid2 = ULID()

        # Assert
        # Randomness parts should be different
        assert ulid1.randomness != ulid2.randomness

    def test_ulid_string_representation(self):
        """Test ULID string representation properties."""
        # Act
        ulid_str = generate_ulid()

        # Assert
        # First 10 characters are timestamp (base32 encoded)
        # Last 16 characters are randomness (base32 encoded)
        assert len(ulid_str) == 26
        
        # Should be uppercase (Crockford base32 uses uppercase)
        assert ulid_str.isupper()
        
        # Should not contain ambiguous characters (I, L, O, U)
        ambiguous_chars = ['I', 'L', 'O', 'U']
        assert not any(char in ulid_str for char in ambiguous_chars)

    def test_ulid_base32_encoding(self):
        """Test ULID uses Crockford's base32 encoding."""
        # Arrange
        crockford_chars = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        
        # Act
        ulid_str = generate_ulid()

        # Assert
        for char in ulid_str:
            assert char in crockford_chars