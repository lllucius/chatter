"""Unit tests for database seeding system fixes."""

from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.models.profile import ProfileType
from chatter.models.prompt import PromptCategory
from chatter.utils.configurable_seeding import ConfigurableSeeder
from chatter.utils.seeding import DatabaseSeeder, SeedingMode


class TestSeedingEnumFixes:
    """Test enum reference fixes."""

    def test_prompt_category_enums_exist(self):
        """Test that corrected enum values exist."""
        assert hasattr(PromptCategory, 'CODING')
        assert hasattr(PromptCategory, 'ANALYTICAL')
        assert PromptCategory.CODING.value == "coding"
        assert PromptCategory.ANALYTICAL.value == "analytical"

    def test_profile_type_enums_exist(self):
        """Test that profile type enums exist."""
        assert hasattr(ProfileType, 'ANALYTICAL')
        assert hasattr(ProfileType, 'CREATIVE')
        assert hasattr(ProfileType, 'CONVERSATIONAL')


class TestDatabaseSeederBasics:
    """Test basic DatabaseSeeder functionality."""

    def test_seeder_initialization(self):
        """Test seeder can be initialized."""
        seeder = DatabaseSeeder(session=None)
        assert seeder.session is None
        assert seeder._should_close_session is True

        mock_session = Mock(spec=AsyncSession)
        seeder_with_session = DatabaseSeeder(session=mock_session)
        assert seeder_with_session.session is mock_session
        assert seeder_with_session._should_close_session is False

    @pytest.mark.asyncio
    async def test_count_users_mock(self):
        """Test user counting with mocked session."""
        mock_session = AsyncMock(spec=AsyncSession)
        mock_result = Mock()
        mock_result.scalar.return_value = 5
        mock_session.execute.return_value = mock_result

        seeder = DatabaseSeeder(session=mock_session)
        count = await seeder._count_users()

        assert count == 5
        mock_session.execute.assert_called_once()


class TestConfigurableSeederBasics:
    """Test basic ConfigurableSeeder functionality."""

    def test_configurable_seeder_initialization(self):
        """Test configurable seeder can be initialized."""
        seeder = ConfigurableSeeder(config_path=None, session=None)
        assert seeder.session is None
        # Config path might find seed_data.yaml or be empty if not found
        assert isinstance(seeder.config_path, str)
        assert isinstance(seeder.config, dict)

    def test_yaml_config_loading_with_missing_file(self):
        """Test YAML config loading with missing file."""
        seeder = ConfigurableSeeder(
            config_path="/nonexistent/path.yaml", session=None
        )
        assert (
            seeder.config == {}
        )  # Should handle missing file gracefully


class TestSeedingModes:
    """Test seeding mode enumeration."""

    def test_seeding_modes_exist(self):
        """Test all expected seeding modes exist."""
        modes = [
            SeedingMode.MINIMAL,
            SeedingMode.DEVELOPMENT,
            SeedingMode.DEMO,
            SeedingMode.TESTING,
            SeedingMode.PRODUCTION,
        ]

        for mode in modes:
            assert isinstance(mode.value, str)
            assert len(mode.value) > 0

    def test_seeding_mode_values(self):
        """Test seeding mode values are correct."""
        assert SeedingMode.MINIMAL.value == "minimal"
        assert SeedingMode.DEVELOPMENT.value == "development"
        assert SeedingMode.DEMO.value == "demo"
        assert SeedingMode.TESTING.value == "testing"
        assert SeedingMode.PRODUCTION.value == "production"


class TestMethodImplementations:
    """Test that previously missing methods are now implemented."""

    @pytest.mark.asyncio
    async def test_demo_embedding_spaces_method_exists(self):
        """Test _create_demo_embedding_spaces method exists and has implementation."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock no embedding model found
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        seeder = DatabaseSeeder(session=mock_session)
        result = await seeder._create_demo_embedding_spaces(
            skip_existing=True
        )

        # Should return empty list when no embedding model found
        assert isinstance(result, list)
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_test_registry_data_method_exists(self):
        """Test _create_test_registry_data method exists and has implementation."""
        mock_session = AsyncMock(spec=AsyncSession)
        seeder = DatabaseSeeder(session=mock_session)

        # Should not raise an exception
        await seeder._create_test_registry_data(skip_existing=True)

    @pytest.mark.asyncio
    async def test_test_conversations_method_exists(self):
        """Test _create_test_conversations method exists and has implementation."""
        mock_session = AsyncMock(spec=AsyncSession)
        seeder = DatabaseSeeder(session=mock_session)

        # Test with empty user list
        result = await seeder._create_test_conversations(
            [], skip_existing=True
        )
        assert result == 0

    @pytest.mark.asyncio
    async def test_test_documents_method_exists(self):
        """Test _create_test_documents method exists and has implementation."""
        mock_session = AsyncMock(spec=AsyncSession)
        seeder = DatabaseSeeder(session=mock_session)

        # Test with empty user list
        result = await seeder._create_test_documents(
            [], skip_existing=True
        )
        assert result == 0


class TestErrorHandling:
    """Test error handling improvements."""

    @pytest.mark.asyncio
    async def test_seeding_handles_exceptions(self):
        """Test that seeding properly handles and reports exceptions."""
        mock_session = AsyncMock(spec=AsyncSession)

        # Mock count_users to raise exception
        seeder = DatabaseSeeder(session=mock_session)
        seeder._count_users = AsyncMock(
            side_effect=Exception("Database error")
        )

        with pytest.raises(Exception):
            await seeder.seed_database(
                mode=SeedingMode.MINIMAL, force=False
            )


class TestSkipExistingLogic:
    """Test skip existing data logic."""

    @pytest.mark.asyncio
    async def test_skip_existing_when_users_exist(self):
        """Test that seeding is skipped when users exist and force=False."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)
        seeder._count_users = AsyncMock(return_value=5)  # Users exist

        result = await seeder.seed_database(
            mode=SeedingMode.DEVELOPMENT, force=False
        )

        assert "skipped" in result
        assert result["skipped"]["reason"] == "Database not empty"

    @pytest.mark.asyncio
    async def test_force_mode_bypasses_existing_check(self):
        """Test that force mode bypasses existing user check."""
        mock_session = AsyncMock(spec=AsyncSession)

        seeder = DatabaseSeeder(session=mock_session)
        seeder._count_users = AsyncMock(return_value=5)  # Users exist
        seeder._seed_development_data = (
            AsyncMock()
        )  # Mock the seeding method

        result = await seeder.seed_database(
            mode=SeedingMode.DEVELOPMENT, force=True
        )

        # Should not skip seeding
        assert "skipped" not in result or "reason" not in result.get(
            "skipped", {}
        )
        seeder._seed_development_data.assert_called_once()


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__])
