"""Tests for workflow template database persistence."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.unified_template_manager import (
    UnifiedTemplateManager,
    WorkflowTemplate,
    TemplateSpec,
    WorkflowConfigurationError,
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
    def template_manager(self, mock_session):
        """Template manager with mocked database session."""
        return UnifiedTemplateManager(session=mock_session)

    def test_init_with_session(self, mock_session):
        """Test initialization with database session."""
        manager = UnifiedTemplateManager(session=mock_session)
        assert manager.session == mock_session
        assert len(manager.builtin_templates) > 0
        assert manager.builder_history == []

    def test_init_without_session(self):
        """Test initialization without database session."""
        manager = UnifiedTemplateManager()
        assert manager.session is None
        assert len(manager.builtin_templates) > 0
        assert manager.builder_history == []

    @pytest.mark.asyncio
    async def test_builtin_template_retrieval(self, template_manager):
        """Test retrieval of built-in templates."""
        # Test getting a built-in template
        template = await template_manager.get_template("general_chat")
        assert template.name == "general_chat"
        assert template.workflow_type == "plain"
        assert template.description == "General conversation assistant"

    @pytest.mark.asyncio
    async def test_list_builtin_templates(self, template_manager):
        """Test listing built-in templates."""
        templates = await template_manager.list_templates(include_custom=False)
        assert "general_chat" in templates
        assert "customer_support" in templates
        assert "code_assistant" in templates
        assert len(templates) > 0

    @pytest.mark.asyncio
    async def test_get_template_info_builtin_only(self, template_manager):
        """Test getting template info for built-in templates."""
        info = await template_manager.get_template_info()
        assert "general_chat" in info
        assert info["general_chat"]["is_builtin"] is True
        assert info["general_chat"]["is_custom"] is False

    @pytest.mark.asyncio
    async def test_template_not_found(self, template_manager):
        """Test error handling when template is not found."""
        with pytest.raises(WorkflowConfigurationError) as exc_info:
            await template_manager.get_template("nonexistent_template")
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_builtin_template(self, template_manager):
        """Test validation of built-in templates."""
        template = await template_manager.get_template("general_chat")
        result = await template_manager.validate_template(template)
        assert result.valid is True
        assert len(result.errors) == 0

    @pytest.mark.asyncio
    async def test_create_custom_template_without_db(self):
        """Test creating custom template without database session."""
        manager = UnifiedTemplateManager(session=None)
        
        spec = TemplateSpec(
            name="test_template",
            description="Test template",
            workflow_type="plain",
            default_params={"system_message": "Test message"},
        )
        
        # Should work but not persist to database
        template = await manager.create_custom_template(spec, "user123")
        assert template.name == "test_template"
        assert len(manager.builder_history) == 1

    @pytest.mark.asyncio
    async def test_create_custom_template_with_db(self, template_manager, mock_session):
        """Test creating custom template with database session."""
        # Setup mock database response
        mock_db_template = MagicMock()
        mock_db_template.id = "template123"
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        
        spec = TemplateSpec(
            name="custom_test_template",
            description="Custom test template",
            workflow_type="tools",
            default_params={"system_message": "Custom test message"},
            required_tools=["test_tool"],
        )
        
        template = await template_manager.create_custom_template(spec, "user456")
        
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
        
        result = await template_manager.validate_template(invalid_template)
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("name is required" in error for error in result.errors)
        assert any("Invalid workflow type" in error for error in result.errors)
        assert len(result.warnings) > 0

    @pytest.mark.asyncio
    async def test_template_category_determination(self, template_manager):
        """Test template category determination logic."""
        # Test customer support category
        category = template_manager._determine_template_category("customer_support_template", "full")
        assert category.value == "customer_support"
        
        # Test programming category
        category = template_manager._determine_template_category("code_assistant", "tools")
        assert category.value == "programming"
        
        # Test custom category (default)
        category = template_manager._determine_template_category("my_template", "plain")
        assert category.value == "custom"

    @pytest.mark.asyncio
    async def test_template_requirements_validation(self, template_manager):
        """Test template requirements validation."""
        # Test with missing tools
        result = await template_manager.validate_template_requirements(
            "code_assistant",
            available_tools=["some_other_tool"],
            available_retrievers=[],
        )
        
        assert result.valid is False
        assert len(result.errors) > 0
        assert result.missing_tools is not None
        assert len(result.missing_tools) > 0

    def test_stats_without_db(self):
        """Test stats retrieval without database."""
        manager = UnifiedTemplateManager(session=None)
        stats = manager.get_stats()
        
        assert "builtin_templates_count" in stats
        assert "custom_templates_count" in stats
        assert "total_templates" in stats
        assert "builder_actions" in stats
        assert "template_types" in stats
        assert stats["builtin_templates_count"] > 0
        assert stats["custom_templates_count"] == 0  # No DB access


@pytest.mark.integration
class TestWorkflowTemplateIntegration:
    """Integration tests for workflow template functionality."""

    @pytest.mark.asyncio
    async def test_end_to_end_template_lifecycle(self):
        """Test complete template lifecycle without real database."""
        # This test would require a real database connection in a full integration test
        # For now, we'll test the logical flow with mocks
        
        manager = UnifiedTemplateManager(session=None)
        
        # 1. List initial templates
        initial_templates = await manager.list_templates(include_custom=False)
        assert len(initial_templates) > 0
        
        # 2. Get template info
        info = await manager.get_template_info()
        assert len(info) == len(initial_templates)
        
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
            base_template="document_qa",
        )
        
        # 4. Create template
        template = await manager.create_custom_template(spec, "test_user")
        assert template.name == "integration_test_template"
        
        # 5. Validate template
        validation = await manager.validate_template(template)
        assert validation.valid is True
        
        # 6. Build workflow spec
        workflow_spec = await manager.build_workflow_spec(
            "integration_test_template",
            overrides={"parameters": {"temperature": 0.7}},
        )
        assert workflow_spec["template_name"] == "integration_test_template"
        assert workflow_spec["parameters"]["temperature"] == 0.7