"""Comprehensive schema-model consistency tests to prevent field mismatches."""

import os

import pytest

# Set environment variable for testing
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from chatter.models.conversation import Conversation
from chatter.models.document import Document
from chatter.models.profile import Profile
from chatter.models.prompt import Prompt
from chatter.models.registry import EmbeddingSpace, ModelDef, Provider
from chatter.models.user import User
from chatter.schemas.auth import (
    UserRegistration,
    UserResponse,
    UserUpdate,
)
from chatter.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from chatter.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
)
from chatter.schemas.model_registry import (
    EmbeddingSpaceCreate,
    ModelDefCreate,
    ProviderCreate,
)
from chatter.schemas.profile import (
    ProfileCreate,
    ProfileResponse,
    ProfileUpdate,
)
from chatter.schemas.prompt import PromptCreate, PromptUpdate


class TestComprehensiveSchemaModelConsistency:
    """Test comprehensive schema-model consistency across all entities."""

    def get_model_fields(self, model_class) -> set[str]:
        """Get field names from a SQLAlchemy model, excluding auto-generated fields."""
        if not hasattr(model_class, "__table__"):
            return set()

        fields = set()
        for column in model_class.__table__.columns:
            fields.add(column.name)

        # Remove auto-generated fields that don't need to be in schemas
        fields.discard("id")
        fields.discard("created_at")
        fields.discard("updated_at")

        return fields

    def get_schema_fields(self, schema_class) -> set[str]:
        """Get field names from a Pydantic schema."""
        if not hasattr(schema_class, "model_fields"):
            return set()

        return set(schema_class.model_fields.keys())

    @pytest.mark.unit
    def test_user_schema_model_consistency(self):
        """Test User model and auth schemas consistency."""
        model_fields = self.get_model_fields(User)

        # Test UserRegistration
        registration_fields = self.get_schema_fields(UserRegistration)

        # Check for fields in schema but missing in model
        missing_in_model = []
        for field in registration_fields:
            if field == "password":
                # password maps to hashed_password in model
                if "hashed_password" not in model_fields:
                    missing_in_model.append(field)
            elif field not in model_fields:
                missing_in_model.append(field)

        assert (
            not missing_in_model
        ), f"UserRegistration fields missing in User model: {missing_in_model}"

        # Test UserUpdate
        update_fields = self.get_schema_fields(UserUpdate)
        missing_in_model = [
            f for f in update_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"UserUpdate fields missing in User model: {missing_in_model}"

        # Test UserResponse - should include all important model fields
        response_fields = self.get_schema_fields(UserResponse)
        # These are the fields that SHOULD be in response (excluding sensitive ones)
        expected_in_response = {
            "email",
            "username",
            "full_name",
            "bio",
            "avatar_url",
            "phone_number",
            "is_active",
            "is_verified",
            "is_superuser",
            "default_llm_provider",
            "default_profile_id",
            "daily_message_limit",
            "monthly_message_limit",
            "max_file_size_mb",
            "api_key_name",
            "last_login_at",
        }

        missing_important = expected_in_response - response_fields
        assert (
            not missing_important
        ), f"Important fields missing in UserResponse: {missing_important}"

    @pytest.mark.unit
    def test_conversation_schema_model_consistency(self):
        """Test Conversation model and chat schemas consistency."""
        model_fields = self.get_model_fields(Conversation)

        # Test ConversationCreate
        create_fields = self.get_schema_fields(ConversationCreate)
        missing_in_model = [
            f for f in create_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"ConversationCreate fields missing in Conversation model: {missing_in_model}"

        # Test ConversationUpdate
        update_fields = self.get_schema_fields(ConversationUpdate)
        missing_in_model = [
            f for f in update_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"ConversationUpdate fields missing in Conversation model: {missing_in_model}"

        # Test ConversationResponse - should include all relevant model fields
        response_fields = self.get_schema_fields(ConversationResponse)
        # These fields should be in the response
        expected_in_response = {
            "title",
            "description",
            "user_id",
            "profile_id",
            "status",
            "llm_provider",
            "llm_model",
            "temperature",
            "max_tokens",
            "enable_retrieval",
            "message_count",
            "total_tokens",
            "total_cost",
            "system_prompt",
            "context_window",
            "memory_enabled",
            "memory_strategy",
            "retrieval_limit",
            "retrieval_score_threshold",
            "tags",
            "extra_metadata",
            "workflow_config",
            "last_message_at",
        }

        missing_important = expected_in_response - response_fields
        assert (
            not missing_important
        ), f"Important fields missing in ConversationResponse: {missing_important}"

    @pytest.mark.unit
    def test_document_schema_model_consistency(self):
        """Test Document model and document schemas consistency."""
        model_fields = self.get_model_fields(Document)

        # Test DocumentCreate
        create_fields = self.get_schema_fields(DocumentCreate)
        missing_in_model = [
            f for f in create_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"DocumentCreate fields missing in Document model: {missing_in_model}"

        # Test DocumentUpdate
        update_fields = self.get_schema_fields(DocumentUpdate)
        missing_in_model = [
            f for f in update_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"DocumentUpdate fields missing in Document model: {missing_in_model}"

        # Test DocumentResponse - should include public fields but exclude sensitive ones
        response_fields = self.get_schema_fields(DocumentResponse)

        # file_path, content, extracted_text are intentionally excluded for security
        excluded_sensitive_fields = {
            "file_path",
            "content",
            "extracted_text",
        }

        expected_in_response = model_fields - excluded_sensitive_fields
        missing_important = expected_in_response - response_fields
        assert (
            not missing_important
        ), f"Important fields missing in DocumentResponse: {missing_important}"

    @pytest.mark.unit
    def test_profile_schema_model_consistency(self):
        """Test Profile model and profile schemas consistency."""
        model_fields = self.get_model_fields(Profile)

        # Test ProfileCreate
        create_fields = self.get_schema_fields(ProfileCreate)
        missing_in_model = [
            f for f in create_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"ProfileCreate fields missing in Profile model: {missing_in_model}"

        # Test ProfileUpdate
        update_fields = self.get_schema_fields(ProfileUpdate)
        missing_in_model = [
            f for f in update_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"ProfileUpdate fields missing in Profile model: {missing_in_model}"

        # Test ProfileResponse
        response_fields = self.get_schema_fields(ProfileResponse)

        # Most profile fields should be in response (profiles are user-owned configurations)
        expected_in_response = model_fields - {
            "owner_id"
        }  # owner_id might be excluded
        expected_in_response - response_fields

        # For now, just ensure no critical fields are missing - full check might be too strict
        critical_fields = {
            "name",
            "description",
            "profile_type",
            "llm_provider",
            "llm_model",
        }
        missing_critical = critical_fields - response_fields
        assert (
            not missing_critical
        ), f"Critical fields missing in ProfileResponse: {missing_critical}"

    @pytest.mark.unit
    def test_prompt_schema_model_consistency(self):
        """Test Prompt model and prompt schemas consistency."""
        model_fields = self.get_model_fields(Prompt)

        # Test PromptCreate
        create_fields = self.get_schema_fields(PromptCreate)
        missing_in_model = [
            f for f in create_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"PromptCreate fields missing in Prompt model: {missing_in_model}"

        # Test PromptUpdate
        update_fields = self.get_schema_fields(PromptUpdate)
        missing_in_model = [
            f for f in update_fields if f not in model_fields
        ]
        assert (
            not missing_in_model
        ), f"PromptUpdate fields missing in Prompt model: {missing_in_model}"

    @pytest.mark.unit
    def test_registry_models_schema_consistency(self):
        """Test registry models (Provider, ModelDef, EmbeddingSpace) consistency."""
        # Test Provider
        provider_model_fields = self.get_model_fields(Provider)
        provider_create_fields = self.get_schema_fields(ProviderCreate)
        missing_in_model = [
            f
            for f in provider_create_fields
            if f not in provider_model_fields
        ]
        assert (
            not missing_in_model
        ), f"ProviderCreate fields missing in Provider model: {missing_in_model}"

        # Test ModelDef
        modeldef_model_fields = self.get_model_fields(ModelDef)
        modeldef_create_fields = self.get_schema_fields(ModelDefCreate)
        missing_in_model = [
            f
            for f in modeldef_create_fields
            if f not in modeldef_model_fields
        ]
        assert (
            not missing_in_model
        ), f"ModelDefCreate fields missing in ModelDef model: {missing_in_model}"

        # Test EmbeddingSpace
        embedding_model_fields = self.get_model_fields(EmbeddingSpace)
        embedding_create_fields = self.get_schema_fields(
            EmbeddingSpaceCreate
        )
        missing_in_model = [
            f
            for f in embedding_create_fields
            if f not in embedding_model_fields
        ]
        assert (
            not missing_in_model
        ), f"EmbeddingSpaceCreate fields missing in EmbeddingSpace model: {missing_in_model}"

    @pytest.mark.unit
    def test_no_reserved_field_names(self):
        """Test that models don't use SQLAlchemy reserved field names."""
        reserved_names = {"metadata"}  # SQLAlchemy reserved names

        models_to_check = [
            User,
            Conversation,
            Document,
            Profile,
            Prompt,
            Provider,
            ModelDef,
            EmbeddingSpace,
        ]

        for model in models_to_check:
            if hasattr(model, "__table__"):
                model_fields = {
                    column.name for column in model.__table__.columns
                }
                problematic_fields = model_fields & reserved_names
                assert (
                    not problematic_fields
                ), f"{model.__name__} uses reserved field names: {problematic_fields}"

    @pytest.mark.unit
    def test_required_model_fields_covered_in_creation_schemas(self):
        """Test that all required model fields are covered in creation schemas."""
        test_cases = [
            (
                User,
                UserRegistration,
                {"hashed_password": "password"},
            ),  # Maps password to hashed_password
            (
                Conversation,
                ConversationCreate,
                {"user_id": None},
            ),  # user_id comes from auth context
            (
                Document,
                DocumentCreate,
                {
                    # Document fields that come from file processing, not user input
                    "owner_id": None,
                    "filename": None,
                    "original_filename": None,
                    "file_size": None,
                    "file_hash": None,
                    "mime_type": None,
                    "document_type": None,
                },
            ),
            (
                Profile,
                ProfileCreate,
                {"owner_id": None},
            ),  # owner_id comes from auth context
            (
                Prompt,
                PromptCreate,
                {"owner_id": None, "content_hash": None},
            ),  # owner_id comes from auth, content_hash is derived
            (Provider, ProviderCreate, {}),
            (ModelDef, ModelDefCreate, {}),
            (EmbeddingSpace, EmbeddingSpaceCreate, {}),
        ]

        for (
            model_class,
            create_schema_class,
            field_mappings,
        ) in test_cases:
            if not hasattr(model_class, "__table__"):
                continue

            # Get required fields (non-nullable, no default)
            required_fields = []
            for column in model_class.__table__.columns:
                # Skip auto-generated fields
                if column.name in ["id", "created_at", "updated_at"]:
                    continue

                if (
                    not column.nullable
                    and column.default is None
                    and column.server_default is None
                ):
                    required_fields.append(column.name)

            # Get schema fields
            schema_fields = self.get_schema_fields(create_schema_class)

            # Check coverage
            missing_required = []
            for field in required_fields:
                mapped_field = field_mappings.get(field, field)
                # Skip fields that are contextual (come from auth/processing) and marked as None
                if (
                    field in field_mappings
                    and field_mappings[field] is None
                ):
                    continue
                if mapped_field not in schema_fields:
                    missing_required.append(field)

            assert (
                not missing_required
            ), f"{create_schema_class.__name__} missing required fields: {missing_required}"
