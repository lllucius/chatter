"""Test schema-model consistency to catch mismatched fields."""

import pytest

from chatter.models.user import User
from chatter.schemas.auth import (
    UserRegistration,
    UserResponse,
    UserUpdate,
)


class TestSchemaModelConsistency:
    """Test that schemas and models have consistent field definitions."""

    def test_user_registration_schema_matches_model_fields(self):
        """Test that UserRegistration schema fields exist in User model."""
        # Get all fields from UserRegistration schema
        schema_fields = UserRegistration.model_fields.keys()

        # Get all column names from User model
        user_columns = set()
        for column in User.__table__.columns:
            user_columns.add(column.name)

        # Check for fields that exist in schema but not in model
        missing_in_model = []
        for field_name in schema_fields:
            # Skip password as it's stored as hashed_password
            if field_name == "password":
                continue
            if field_name not in user_columns:
                missing_in_model.append(field_name)

        # This should fail initially due to phone_number issue
        assert (
            not missing_in_model
        ), f"Fields in schema but missing in model: {missing_in_model}"

    def test_user_update_schema_matches_model_fields(self):
        """Test that UserUpdate schema fields exist in User model."""
        schema_fields = UserUpdate.model_fields.keys()

        user_columns = set()
        for column in User.__table__.columns:
            user_columns.add(column.name)

        missing_in_model = []
        for field_name in schema_fields:
            if field_name not in user_columns:
                missing_in_model.append(field_name)

        assert (
            not missing_in_model
        ), f"Fields in schema but missing in model: {missing_in_model}"

    def test_user_response_schema_matches_model_fields(self):
        """Test that UserResponse schema fields exist in User model."""
        schema_fields = UserResponse.model_fields.keys()

        user_columns = set()
        for column in User.__table__.columns:
            user_columns.add(column.name)

        missing_in_model = []
        for field_name in schema_fields:
            if field_name not in user_columns:
                missing_in_model.append(field_name)

        assert (
            not missing_in_model
        ), f"Fields in schema but missing in model: {missing_in_model}"

    def test_user_model_required_fields_in_schemas(self):
        """Test that required User model fields exist in schemas."""
        required_columns = []
        for column in User.__table__.columns:
            # Skip auto-generated fields
            if column.name in ["id", "created_at", "updated_at"]:
                continue
            if (
                not column.nullable
                and column.default is None
                and column.server_default is None
            ):
                required_columns.append(column.name)

        # Check if required fields are in UserRegistration
        registration_fields = UserRegistration.model_fields.keys()
        missing_required = []
        for col in required_columns:
            # hashed_password is derived from password
            if col == "hashed_password":
                if "password" not in registration_fields:
                    missing_required.append(f"{col} (password)")
            elif col not in registration_fields:
                missing_required.append(col)

        assert (
            not missing_required
        ), f"Required model fields missing in UserRegistration: {missing_required}"

    @pytest.mark.unit
    def test_phone_number_field_exists_in_user_model(self):
        """Specific test for phone_number field that's known to be missing."""
        # This test documents the specific issue we found
        user_columns = [
            column.name for column in User.__table__.columns
        ]

        # This should pass after we fix the issue
        assert (
            "phone_number" in user_columns
        ), "phone_number field is missing from User model but exists in schemas"

    def test_user_schema_validation_with_phone_number(self):
        """Test that phone_number can be validated in schemas."""
        # Test UserRegistration with phone_number
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "securepassword123",
            "phone_number": "+1234567890",
        }

        # This should work without error
        user_registration = UserRegistration(**user_data)
        assert user_registration.phone_number == "+1234567890"

    def test_user_model_can_store_phone_number(self):
        """Test that User model can store phone_number (will fail initially)."""
        # This test will fail until we add phone_number to the model
        import uuid

        unique_id = str(uuid.uuid4())[:8]
        try:
            user = User(
                email=f"test_{unique_id}@example.com",
                username=f"testuser_{unique_id}",
                hashed_password="hashedpass",
                phone_number="+1234567890",
            )
            # If we get here, the field exists
            assert hasattr(user, 'phone_number')
            assert user.phone_number == "+1234567890"
        except TypeError as e:
            pytest.fail(
                f"User model doesn't accept phone_number field: {e}"
            )
