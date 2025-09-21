"""Tests for workflow template database persistence."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import (
    TemplateSpec,
    UnifiedTemplateManager,
    WorkflowConfigurationError,
    WorkflowTemplate,
)


class TestWorkflowTemplatePersistence:
    """Test workflow template database persistence functionality."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock(spec=AsyncSession)
        session.execute = AsyncMock()
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        session.add = MagicMock()
        session.refresh = AsyncMock()
        session.delete = AsyncMock()
        return session

    @pytest.fixture
    def mock_db_template(self):
        """Mock database template for testing."""
        db_template = MagicMock()
        db_template.to_unified_template.return_value = {
            "name": "test_template",
            "workflow_type": "plain",
            "description": "Test template description",
            "default_params": {"system_message": "Test system message"},
            "required_tools": [],
            "required_retrievers": [],
        }
        return db_template

    def _setup_mock_template_query(
        self, mock_session, db_template=None, return_none=False
    ):
        """Helper to setup mock database query responses."""
        if return_none:
            mock_session.execute.return_value.scalar_one_or_none.return_value = (
                None
            )
            mock_session.execute.return_value.scalars.return_value.all.return_value = (
                []
            )
        else:
            mock_session.execute.return_value.scalar_one_or_none.return_value = (
                db_template
            )
            mock_session.execute.return_value.scalars.return_value.all.return_value = (
                [db_template] if db_template else []
            )

    @pytest.fixture
    def template_manager(self, mock_session):
        """Template manager with mocked database session."""
        return UnifiedTemplateManager(session=mock_session)

    def test_init_with_session(self, mock_session):
        """Test initialization with database session."""
        manager = UnifiedTemplateManager(session=mock_session)
        assert manager.session == mock_session
        assert manager.builder_history == []

    def test_init_without_session(self):
        """Test initialization without database session raises error."""
        with pytest.raises(
            ValueError, match="Database session is required"
        ):
            UnifiedTemplateManager()

    @pytest.mark.asyncio
    async def test_template_retrieval_from_db(
        self, template_manager, mock_session, mock_db_template
    ):
        """Test retrieval of templates from database."""
        # Setup mock to return a template
        self._setup_mock_template_query(mock_session, mock_db_template)

        # Test getting a template
        template = await template_manager.get_template("test_template")
        assert template.name == "test_template"
        assert template.workflow_type == "plain"
        assert template.description == "Test template description"

    @pytest.mark.asyncio
    async def test_list_templates_from_db(
        self, template_manager, mock_session, mock_db_template
    ):
        """Test listing templates from database."""
        # Setup mock to return templates
        self._setup_mock_template_query(mock_session, mock_db_template)

        templates = await template_manager.list_templates()
        assert "test_template" in templates

    @pytest.mark.asyncio
    async def test_get_template_info_from_db(
        self, template_manager, mock_session, mock_db_template
    ):
        """Test getting template info from database."""
        # Setup mock to return templates
        self._setup_mock_template_query(mock_session, mock_db_template)

        info = await template_manager.get_template_info()
        assert "test_template" in info
        assert info["test_template"]["is_builtin"] is False
        assert info["test_template"]["is_custom"] is True

    @pytest.mark.asyncio
    async def test_template_not_found(
        self, template_manager, mock_session
    ):
        """Test error handling when template is not found."""
        # Setup mock to return no templates
        self._setup_mock_template_query(mock_session, return_none=True)

        with pytest.raises(WorkflowConfigurationError) as exc_info:
            await template_manager.get_template("nonexistent_template")
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_template(self, template_manager):
        """Test validation of templates."""
        template = WorkflowTemplate(
            name="test_template",
            workflow_type="plain",
            description="Test template description",
            default_params={"system_message": "Test system message"},
        )
        result = await template_manager.validate_template(template)
        assert result.valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_create_custom_template_requires_db(self):
        """Test that creating custom template requires database session."""
        # Creating manager without session should raise error
        with pytest.raises(
            ValueError, match="Database session is required"
        ):
            UnifiedTemplateManager(session=None)

    @pytest.mark.asyncio
    async def test_create_custom_template_with_db(
        self, template_manager, mock_session
    ):
        """Test creating custom template with database session."""
        # Setup mock database response
        mock_db_template = MagicMock()
        mock_db_template.id = "template123"
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            None
        )

        spec = TemplateSpec(
            name="custom_test_template",
            description="Custom test template",
            workflow_type="tools",
            default_params={"system_message": "Custom test message"},
            required_tools=["test_tool"],
        )

        template = await template_manager.create_custom_template(
            spec, "user456"
        )

        # Verify template creation
        assert template.name == "custom_test_template"
        assert template.workflow_type == "tools"
        assert template.required_tools == ["test_tool"]

        # Verify database interaction
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_validation_errors(self, template_manager):
        """Test template validation with errors."""
        # Create invalid template
        invalid_template = WorkflowTemplate(
            name="",  # Empty name should cause error
            description="",  # Empty description should cause warning
            workflow_type="invalid_type",  # Invalid type should cause error
            default_params={},
        )

        result = await template_manager.validate_template(
            invalid_template
        )
        assert result.valid is False
        assert len(result.errors) > 0
        assert any(
            "name is required" in error for error in result.errors
        )
        assert any(
            "Invalid workflow type" in error for error in result.errors
        )
        assert len(result.warnings) > 0

    @pytest.mark.asyncio
    async def test_template_category_determination(
        self, template_manager
    ):
        """Test template category determination logic."""
        # Test customer support category
        category = template_manager._determine_template_category(
            "customer_support_template", "full"
        )
        assert category.value == "customer_support"

        # Test programming category
        category = template_manager._determine_template_category(
            "code_assistant", "tools"
        )
        assert category.value == "programming"

        # Test custom category (default)
        category = template_manager._determine_template_category(
            "my_template", "plain"
        )
        assert category.value == "custom"

    @pytest.mark.asyncio
    async def test_template_requirements_validation(
        self, template_manager, mock_session, mock_db_template
    ):
        """Test template requirements validation."""
        # Setup mock template with required tools
        mock_db_template.to_unified_template.return_value = {
            "name": "test_template",
            "workflow_type": "tools",
            "description": "Test template with tools",
            "default_params": {"system_message": "Test system message"},
            "required_tools": ["required_tool_1", "required_tool_2"],
            "required_retrievers": [],
        }
        self._setup_mock_template_query(mock_session, mock_db_template)

        # Test with missing tools
        result = await template_manager.validate_template_requirements(
            "test_template",
            available_tools=["some_other_tool"],
            available_retrievers=[],
        )

        assert result.valid is False
        assert len(result.errors) > 0
        assert result.missing_tools is not None
        assert len(result.missing_tools) > 0

    def test_stats_with_session(self, template_manager):
        """Test stats retrieval with database session."""
        stats = template_manager.get_stats()

        assert "builtin_templates_count" in stats
        assert "custom_templates_count" in stats
        assert "total_templates" in stats
        assert "builder_actions" in stats
        assert "template_types" in stats
        assert (
            stats["builtin_templates_count"] == 0
        )  # No longer tracked separately
        assert (
            stats["custom_templates_count"] == 0
        )  # Would need async DB query


@pytest.mark.integration
class TestWorkflowTemplateIntegration:
    """Integration tests for workflow template functionality."""

    @pytest.mark.asyncio
    async def test_end_to_end_template_lifecycle(self):
        """Test complete template lifecycle with mock database."""
        # Create mock session
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.execute = AsyncMock()
        mock_session.commit = AsyncMock()
        mock_session.rollback = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.refresh = AsyncMock()

        # Setup mock to return no existing templates initially
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            None
        )
        mock_session.execute.return_value.scalars.return_value.all.return_value = (
            []
        )

        manager = UnifiedTemplateManager(session=mock_session)

        # 1. List initial templates (should be empty)
        initial_templates = await manager.list_templates()
        assert len(initial_templates) == 0

        # 2. Get template info (should be empty)
        info = await manager.get_template_info()
        assert len(info) == 0

        # 3. Create custom template spec
        spec = TemplateSpec(
            name="integration_test_template",
            description="Integration test template",
            workflow_type="rag",
            default_params={
                "system_message": "Integration test system message",
                "max_documents": 10,
            },
            required_retrievers=["test_retriever"],
        )

        # 4. Create template
        template = await manager.create_custom_template(
            spec, "test_user"
        )
        assert template.name == "integration_test_template"

        # 5. Validate template
        validation = await manager.validate_template(template)
        assert validation.valid is True

        # 6. Build workflow spec (mock the template retrieval)
        mock_db_template = MagicMock()
        mock_db_template.to_unified_template.return_value = {
            "name": "integration_test_template",
            "workflow_type": "rag",
            "description": "Integration test template",
            "default_params": {
                "system_message": "Integration test system message",
                "max_documents": 10,
            },
            "required_tools": [],
            "required_retrievers": ["test_retriever"],
        }
        mock_session.execute.return_value.scalar_one_or_none.return_value = (
            mock_db_template
        )

        workflow_spec = await manager.build_workflow_spec(
            "integration_test_template",
            overrides={"parameters": {"temperature": 0.7}},
        )
        assert (
            workflow_spec["template_name"]
            == "integration_test_template"
        )
        assert workflow_spec["parameters"]["temperature"] == 0.7
