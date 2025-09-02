"""Tests for workflow templates and common use cases."""

import pytest

from chatter.core.exceptions import (
    WorkflowConfigurationError,
    WorkflowTemplateError,
)
from chatter.core.workflow_templates import (
    WORKFLOW_TEMPLATES,
    CustomWorkflowBuilder,
    TemplateRegistry,
    WorkflowTemplate,
    WorkflowTemplateManager,
)


@pytest.mark.unit
class TestWorkflowTemplate:
    """Test WorkflowTemplate dataclass functionality."""

    def test_workflow_template_initialization(self):
        """Test WorkflowTemplate initialization."""
        # Arrange
        name = "test_template"
        workflow_type = "full"
        description = "A test template"
        default_params = {"param1": "value1"}
        required_tools = ["tool1", "tool2"]
        required_retrievers = ["retriever1"]

        # Act
        template = WorkflowTemplate(
            name=name,
            workflow_type=workflow_type,
            description=description,
            default_params=default_params,
            required_tools=required_tools,
            required_retrievers=required_retrievers,
        )

        # Assert
        assert template.name == name
        assert template.workflow_type == workflow_type
        assert template.description == description
        assert template.default_params == default_params
        assert template.required_tools == required_tools
        assert template.required_retrievers == required_retrievers

    def test_workflow_template_optional_fields(self):
        """Test WorkflowTemplate with optional fields as None."""
        # Act
        template = WorkflowTemplate(
            name="minimal_template",
            workflow_type="simple",
            description="Minimal template",
            default_params={},
        )

        # Assert
        assert template.required_tools is None
        assert template.required_retrievers is None


@pytest.mark.unit
class TestBuiltInTemplates:
    """Test built-in workflow templates."""

    def test_customer_support_template_exists(self):
        """Test customer support template is properly defined."""
        # Act
        template = WORKFLOW_TEMPLATES["customer_support"]

        # Assert
        assert template.name == "customer_support"
        assert template.workflow_type == "full"
        assert "customer support" in template.description.lower()
        assert template.default_params["enable_memory"] is True
        assert template.default_params["memory_window"] == 50
        assert "search_kb" in template.required_tools
        assert "support_docs" in template.required_retrievers

    def test_code_assistant_template_exists(self):
        """Test code assistant template is properly defined."""
        # Act
        template = WORKFLOW_TEMPLATES["code_assistant"]

        # Assert
        assert template.name == "code_assistant"
        assert template.workflow_type == "tools"
        assert "programming" in template.description.lower()
        assert template.default_params["memory_window"] == 100
        assert "execute_code" in template.required_tools

    def test_research_assistant_template_exists(self):
        """Test research assistant template is properly defined."""
        # Act
        template = WORKFLOW_TEMPLATES["research_assistant"]

        # Assert
        assert template.name == "research_assistant"
        assert template.workflow_type == "full"
        assert "research" in template.description.lower()
        assert template.default_params["enable_memory"] is True

    def test_content_writer_template_exists(self):
        """Test content writer template is properly defined."""
        # Act
        template = WORKFLOW_TEMPLATES["content_writer"]

        # Assert
        assert template.name == "content_writer"
        assert template.workflow_type == "plain"
        assert "content" in template.description.lower()

    def test_data_analyst_template_exists(self):
        """Test data analyst template is properly defined."""
        # Act
        template = WORKFLOW_TEMPLATES["data_analyst"]

        # Assert
        assert template.name == "data_analyst"
        assert template.workflow_type == "tools"
        assert "data" in template.description.lower()

    def test_all_templates_have_required_fields(self):
        """Test all built-in templates have required fields."""
        # Act & Assert
        for template_name, template in WORKFLOW_TEMPLATES.items():
            assert isinstance(template.name, str)
            assert template.name == template_name
            assert isinstance(template.workflow_type, str)
            assert isinstance(template.description, str)
            assert isinstance(template.default_params, dict)

    def test_template_system_messages_appropriate(self):
        """Test that template system messages are appropriate for their use case."""
        # Customer support should be helpful and professional
        cs_template = WORKFLOW_TEMPLATES["customer_support"]
        cs_message = cs_template.default_params["system_message"]
        assert "helpful" in cs_message.lower()
        assert "professional" in cs_message.lower()

        # Code assistant should mention programming
        code_template = WORKFLOW_TEMPLATES["code_assistant"]
        code_message = code_template.default_params["system_message"]
        assert "programming" in code_message.lower()
        assert "code" in code_message.lower()


@pytest.mark.unit
class TestWorkflowTemplateManager:
    """Test WorkflowTemplateManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = WorkflowTemplateManager()

    def test_get_template_existing(self):
        """Test getting an existing template."""
        # Act
        template = self.manager.get_template("customer_support")

        # Assert
        assert template is not None
        assert template.name == "customer_support"

    def test_get_template_nonexistent(self):
        """Test getting a non-existent template."""
        # Act & Assert
        with pytest.raises(WorkflowTemplateError) as exc_info:
            self.manager.get_template("nonexistent_template")

        assert "not found" in str(exc_info.value)

    def test_list_templates(self):
        """Test listing all available templates."""
        # Act
        templates = self.manager.list_templates()

        # Assert
        assert len(templates) > 0
        assert "customer_support" in templates
        assert "code_assistant" in templates

    def test_list_templates_by_type(self):
        """Test listing templates filtered by workflow type."""
        # Act
        full_templates = self.manager.list_templates_by_type("full")
        tools_templates = self.manager.list_templates_by_type("tools")
        plain_templates = self.manager.list_templates_by_type("plain")

        # Assert
        assert len(full_templates) > 0
        assert len(tools_templates) > 0
        assert len(plain_templates) > 0
        assert "customer_support" in full_templates
        assert "code_assistant" in tools_templates

    def test_create_workflow_from_template(self):
        """Test creating workflow configuration from template."""
        # Arrange
        template_name = "customer_support"
        custom_params = {"memory_window": 30, "user_name": "John Doe"}

        # Act
        workflow_config = self.manager.create_workflow_from_template(
            template_name, custom_params
        )

        # Assert
        assert workflow_config["workflow_type"] == "full"
        assert workflow_config["enable_memory"] is True
        assert workflow_config["memory_window"] == 30  # Custom override
        assert (
            workflow_config["user_name"] == "John Doe"
        )  # Custom addition

    def test_create_workflow_from_template_invalid_params(self):
        """Test creating workflow with invalid custom parameters."""
        # Arrange
        template_name = "customer_support"
        invalid_params = {
            "memory_window": "invalid_value",  # Should be integer
            "temperature": 2.5,  # Should be between 0 and 1
        }

        # Act & Assert
        with pytest.raises(WorkflowConfigurationError) as exc_info:
            self.manager.create_workflow_from_template(
                template_name, invalid_params
            )

        assert "invalid" in str(exc_info.value).lower()

    def test_validate_template_requirements(self):
        """Test validating template requirements."""
        # Arrange
        template_name = "customer_support"
        available_tools = [
            "search_kb",
            "create_ticket",
            "escalate",
            "other_tool",
        ]
        available_retrievers = ["support_docs", "faq_docs"]

        # Act
        result = self.manager.validate_template_requirements(
            template_name, available_tools, available_retrievers
        )

        # Assert
        assert result.valid is True

    def test_validate_template_requirements_missing_tools(self):
        """Test validating template with missing required tools."""
        # Arrange
        template_name = "customer_support"
        available_tools = [
            "search_kb"
        ]  # Missing create_ticket, escalate
        available_retrievers = ["support_docs"]

        # Act
        result = self.manager.validate_template_requirements(
            template_name, available_tools, available_retrievers
        )

        # Assert
        assert result.valid is False
        assert len(result.errors) > 0
        assert any("tool" in error.lower() for error in result.errors)

    def test_get_template_suggestions(self):
        """Test getting template suggestions based on use case."""
        # Act
        support_suggestions = self.manager.get_template_suggestions(
            "customer service"
        )
        code_suggestions = self.manager.get_template_suggestions(
            "programming help"
        )
        research_suggestions = self.manager.get_template_suggestions(
            "research project"
        )

        # Assert
        assert "customer_support" in support_suggestions
        assert "code_assistant" in code_suggestions
        assert "research_assistant" in research_suggestions

    def test_template_compatibility_check(self):
        """Test checking template compatibility with system capabilities."""
        # Arrange
        system_capabilities = {
            "max_memory_window": 200,
            "max_tool_calls": 15,
            "supported_workflow_types": ["full", "tools", "plain"],
            "available_models": ["gpt-4", "gpt-3.5-turbo"],
        }

        # Act
        compatible_templates = self.manager.get_compatible_templates(
            system_capabilities
        )

        # Assert
        assert len(compatible_templates) > 0
        assert "customer_support" in compatible_templates
        assert "code_assistant" in compatible_templates


@pytest.mark.unit
class TestCustomWorkflowBuilder:
    """Test CustomWorkflowBuilder functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.builder = CustomWorkflowBuilder()

    def test_build_from_template(self):
        """Test building custom workflow from template."""
        # Arrange
        base_template = "customer_support"
        customizations = {
            "name": "Premium Support",
            "memory_window": 100,
            "additional_tools": ["premium_escalate"],
            "custom_system_message": "You are a premium support assistant.",
        }

        # Act
        custom_workflow = self.builder.build_from_template(
            base_template, customizations
        )

        # Assert
        assert custom_workflow["name"] == "Premium Support"
        assert custom_workflow["memory_window"] == 100
        assert "premium_escalate" in custom_workflow["additional_tools"]

    def test_build_custom_template(self):
        """Test building completely custom template."""
        # Arrange
        custom_specs = {
            "name": "sales_assistant",
            "workflow_type": "full",
            "description": "AI assistant for sales teams",
            "default_params": {
                "enable_memory": True,
                "memory_window": 75,
                "system_message": "You are a sales assistant.",
            },
            "required_tools": ["crm_search", "lead_qualify"],
            "required_retrievers": ["sales_materials"],
        }

        # Act
        custom_template = self.builder.build_custom_template(
            custom_specs
        )

        # Assert
        assert custom_template.name == "sales_assistant"
        assert custom_template.workflow_type == "full"
        assert "sales" in custom_template.description.lower()
        assert "crm_search" in custom_template.required_tools

    def test_merge_template_configs(self):
        """Test merging template configurations."""
        # Arrange
        base_config = {
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 5,
            "tools": ["tool1", "tool2"],
        }
        override_config = {
            "memory_window": 100,  # Override
            "temperature": 0.7,  # Add new
            "tools": ["tool1", "tool3"],  # Override list
        }

        # Act
        merged_config = self.builder.merge_template_configs(
            base_config, override_config
        )

        # Assert
        assert merged_config["enable_memory"] is True  # Preserved
        assert merged_config["memory_window"] == 100  # Overridden
        assert merged_config["temperature"] == 0.7  # Added
        assert "tool3" in merged_config["tools"]  # List merged

    def test_validate_custom_template(self):
        """Test validating custom template specification."""
        # Arrange
        valid_spec = {
            "name": "valid_template",
            "workflow_type": "tools",
            "description": "A valid custom template",
            "default_params": {"temperature": 0.5, "max_tokens": 1000},
        }

        invalid_spec = {
            "name": "",  # Invalid empty name
            "workflow_type": "invalid_type",  # Invalid type
            "description": "Invalid template",
        }

        # Act
        valid_result = self.builder.validate_custom_template(valid_spec)
        invalid_result = self.builder.validate_custom_template(
            invalid_spec
        )

        # Assert
        assert valid_result.valid is True
        assert invalid_result.valid is False


@pytest.mark.unit
class TestTemplateRegistry:
    """Test TemplateRegistry functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.registry = TemplateRegistry()

    def test_register_custom_template(self):
        """Test registering a custom template."""
        # Arrange
        custom_template = WorkflowTemplate(
            name="custom_test",
            workflow_type="tools",
            description="Custom test template",
            default_params={"test_param": "test_value"},
        )

        # Act
        self.registry.register_template(custom_template)

        # Assert
        assert "custom_test" in self.registry.list_templates()
        retrieved = self.registry.get_template("custom_test")
        assert retrieved.name == "custom_test"

    def test_register_duplicate_template(self):
        """Test registering template with duplicate name."""
        # Arrange
        template1 = WorkflowTemplate(
            name="duplicate",
            workflow_type="tools",
            description="First template",
            default_params={},
        )
        template2 = WorkflowTemplate(
            name="duplicate",
            workflow_type="full",
            description="Second template",
            default_params={},
        )

        self.registry.register_template(template1)

        # Act & Assert
        with pytest.raises(WorkflowTemplateError) as exc_info:
            self.registry.register_template(template2)

        assert "already exists" in str(exc_info.value)

    def test_unregister_template(self):
        """Test unregistering a template."""
        # Arrange
        custom_template = WorkflowTemplate(
            name="temporary",
            workflow_type="plain",
            description="Temporary template",
            default_params={},
        )

        self.registry.register_template(custom_template)
        assert "temporary" in self.registry.list_templates()

        # Act
        self.registry.unregister_template("temporary")

        # Assert
        assert "temporary" not in self.registry.list_templates()

    def test_update_template(self):
        """Test updating an existing template."""
        # Arrange
        original_template = WorkflowTemplate(
            name="updateable",
            workflow_type="tools",
            description="Original description",
            default_params={"param1": "value1"},
        )

        updated_template = WorkflowTemplate(
            name="updateable",
            workflow_type="full",
            description="Updated description",
            default_params={
                "param1": "updated_value",
                "param2": "value2",
            },
        )

        self.registry.register_template(original_template)

        # Act
        self.registry.update_template(updated_template)

        # Assert
        retrieved = self.registry.get_template("updateable")
        assert retrieved.workflow_type == "full"
        assert retrieved.description == "Updated description"
        assert retrieved.default_params["param1"] == "updated_value"

    def test_template_versioning(self):
        """Test template versioning functionality."""
        # Arrange
        v1_template = WorkflowTemplate(
            name="versioned",
            workflow_type="tools",
            description="Version 1",
            default_params={"version": "1.0"},
        )

        v2_template = WorkflowTemplate(
            name="versioned",
            workflow_type="full",
            description="Version 2",
            default_params={"version": "2.0"},
        )

        # Act
        self.registry.register_template(v1_template, version="1.0")
        self.registry.register_template(v2_template, version="2.0")

        # Assert
        v1_retrieved = self.registry.get_template(
            "versioned", version="1.0"
        )
        v2_retrieved = self.registry.get_template(
            "versioned", version="2.0"
        )
        latest_retrieved = self.registry.get_template(
            "versioned"
        )  # Should get latest

        assert v1_retrieved.default_params["version"] == "1.0"
        assert v2_retrieved.default_params["version"] == "2.0"
        assert latest_retrieved.default_params["version"] == "2.0"


@pytest.mark.integration
class TestWorkflowTemplateIntegration:
    """Integration tests for workflow template system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = WorkflowTemplateManager()
        self.builder = CustomWorkflowBuilder()
        self.registry = TemplateRegistry()

    def test_end_to_end_template_usage(self):
        """Test complete template usage workflow."""
        # Step 1: Get template suggestions
        suggestions = self.manager.get_template_suggestions(
            "customer support"
        )
        assert "customer_support" in suggestions

        # Step 2: Validate template requirements
        available_tools = ["search_kb", "create_ticket", "escalate"]
        available_retrievers = ["support_docs"]

        validation = self.manager.validate_template_requirements(
            "customer_support", available_tools, available_retrievers
        )
        assert validation.valid is True

        # Step 3: Create workflow from template
        custom_params = {
            "memory_window": 75,
            "agent_name": "SupportBot",
            "escalation_threshold": 3,
        }

        workflow_config = self.manager.create_workflow_from_template(
            "customer_support", custom_params
        )

        # Step 4: Verify workflow configuration
        assert workflow_config["workflow_type"] == "full"
        assert workflow_config["memory_window"] == 75
        assert workflow_config["agent_name"] == "SupportBot"
        assert workflow_config["enable_memory"] is True

    def test_custom_template_creation_and_usage(self):
        """Test creating and using a custom template."""
        # Step 1: Build custom template
        custom_specs = {
            "name": "integration_test_template",
            "workflow_type": "tools",
            "description": "Integration test custom template",
            "default_params": {
                "enable_memory": False,
                "max_tool_calls": 8,
                "system_message": "Integration test assistant",
            },
            "required_tools": ["test_tool"],
            "required_retrievers": ["test_retriever"],
        }

        custom_template = self.builder.build_custom_template(
            custom_specs
        )

        # Step 2: Register custom template
        self.registry.register_template(custom_template)

        # Step 3: Use custom template via manager
        # First, we need to make the manager aware of the registry
        self.manager.registry = self.registry

        workflow_config = self.manager.create_workflow_from_template(
            "integration_test_template", {"temperature": 0.8}
        )

        # Step 4: Verify custom template usage
        assert workflow_config["workflow_type"] == "tools"
        assert workflow_config["enable_memory"] is False
        assert workflow_config["max_tool_calls"] == 8
        assert workflow_config["temperature"] == 0.8

    def test_template_inheritance_and_customization(self):
        """Test template inheritance and customization patterns."""
        # Step 1: Create base template
        self.manager.get_template("customer_support")

        # Step 2: Create specialized templates based on base
        enterprise_customizations = {
            "name": "Enterprise Support",
            "memory_window": 150,
            "max_tool_calls": 10,
            "additional_tools": [
                "enterprise_escalate",
                "priority_routing",
            ],
            "sla_requirements": {"response_time": 300},  # 5 minutes
        }

        basic_customizations = {
            "name": "Basic Support",
            "memory_window": 25,
            "max_tool_calls": 3,
            "excluded_tools": [
                "escalate"
            ],  # Basic users can't escalate
            "response_style": "friendly_but_concise",
        }

        # Step 3: Build customized workflows
        enterprise_workflow = self.builder.build_from_template(
            "customer_support", enterprise_customizations
        )

        basic_workflow = self.builder.build_from_template(
            "customer_support", basic_customizations
        )

        # Step 4: Verify customizations applied correctly
        assert enterprise_workflow["name"] == "Enterprise Support"
        assert enterprise_workflow["memory_window"] == 150
        assert (
            "enterprise_escalate"
            in enterprise_workflow["additional_tools"]
        )

        assert basic_workflow["name"] == "Basic Support"
        assert basic_workflow["memory_window"] == 25
        assert basic_workflow["max_tool_calls"] == 3

    @pytest.mark.asyncio
    async def test_template_performance_with_many_templates(self):
        """Test template system performance with many registered templates."""
        # Arrange - Register many custom templates
        template_count = 100

        for i in range(template_count):
            template = WorkflowTemplate(
                name=f"perf_test_template_{i}",
                workflow_type="tools",
                description=f"Performance test template {i}",
                default_params={"template_id": i},
            )
            self.registry.register_template(template)

        # Act - Perform operations that should remain fast
        import time

        start_time = time.time()

        # List all templates
        all_templates = self.registry.list_templates()

        # Get specific templates
        for i in range(0, template_count, 10):  # Every 10th template
            template = self.registry.get_template(
                f"perf_test_template_{i}"
            )
            assert template is not None

        # Search templates
        tool_templates = self.registry.list_templates_by_type("tools")

        end_time = time.time()
        execution_time = end_time - start_time

        # Assert - Operations complete in reasonable time
        assert len(all_templates) >= template_count
        assert len(tool_templates) >= template_count
        assert execution_time < 1.0  # Should complete in under 1 second
