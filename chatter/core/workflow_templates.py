"""Workflow templates for common use cases.

This module provides pre-configured workflow templates that make it easy to set up
workflows for common scenarios like customer support, code assistance, and research.
"""

from dataclasses import dataclass
from typing import Any

from chatter.core.exceptions import WorkflowConfigurationError


@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""

    name: str
    workflow_type: str
    description: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None


# Built-in workflow templates
WORKFLOW_TEMPLATES = {
    "customer_support": WorkflowTemplate(
        name="customer_support",
        workflow_type="full",
        description="Customer support with knowledge base and tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 5,
            "system_message": "You are a helpful customer support assistant. Use the knowledge base to find relevant information and available tools to help resolve customer issues. Always be polite, professional, and thorough in your responses.",
        },
        required_tools=["search_kb", "create_ticket", "escalate"],
        required_retrievers=["support_docs"],
    ),
    "code_assistant": WorkflowTemplate(
        name="code_assistant",
        workflow_type="tools",
        description="Programming assistant with code tools",
        default_params={
            "enable_memory": True,
            "memory_window": 100,
            "max_tool_calls": 10,
            "system_message": "You are an expert programming assistant. Help users with coding tasks, debugging, code review, and software development best practices. Use available tools to execute code, run tests, and access documentation when needed.",
        },
        required_tools=[
            "execute_code",
            "search_docs",
            "generate_tests",
        ],
    ),
    "research_assistant": WorkflowTemplate(
        name="research_assistant",
        workflow_type="rag",
        description="Research assistant with document retrieval",
        default_params={
            "enable_memory": True,
            "memory_window": 30,
            "max_documents": 10,
            "system_message": "You are a research assistant. Use the provided documents to answer questions accurately and thoroughly. Always cite your sources and explain your reasoning. If information is not available in the documents, clearly state this limitation.",
        },
        required_retrievers=["research_docs"],
    ),
    "general_chat": WorkflowTemplate(
        name="general_chat",
        workflow_type="plain",
        description="General conversation assistant",
        default_params={
            "enable_memory": True,
            "memory_window": 20,
            "system_message": "You are a helpful, harmless, and honest AI assistant. Engage in natural conversation while being informative and supportive.",
        },
    ),
    "document_qa": WorkflowTemplate(
        name="document_qa",
        workflow_type="rag",
        description="Document question answering with retrieval",
        default_params={
            "enable_memory": False,  # Each question should be independent
            "max_documents": 15,
            "similarity_threshold": 0.7,
            "system_message": "You are a document analysis assistant. Answer questions based solely on the provided documents. Be precise and cite specific sections when possible.",
        },
        required_retrievers=["document_store"],
    ),
    "data_analyst": WorkflowTemplate(
        name="data_analyst",
        workflow_type="tools",
        description="Data analysis assistant with computation tools",
        default_params={
            "enable_memory": True,
            "memory_window": 50,
            "max_tool_calls": 15,
            "system_message": "You are a data analyst assistant. Help users analyze data, create visualizations, and derive insights. Use computational tools to perform calculations and generate charts.",
        },
        required_tools=[
            "execute_python",
            "create_chart",
            "analyze_data",
        ],
    ),
}


class WorkflowTemplateManager:
    """Manages workflow templates and template-based workflow creation."""

    @classmethod
    def get_template(cls, template_name: str) -> WorkflowTemplate:
        """Get a workflow template by name.

        Args:
            template_name: Name of the template to retrieve

        Returns:
            WorkflowTemplate: The requested template

        Raises:
            WorkflowConfigurationError: If template is not found
        """
        if template_name not in WORKFLOW_TEMPLATES:
            available = ", ".join(WORKFLOW_TEMPLATES.keys())
            raise WorkflowConfigurationError(
                f"Template '{template_name}' not found. Available templates: {available}"
            )
        return WORKFLOW_TEMPLATES[template_name]

    @classmethod
    def list_templates(cls) -> list[str]:
        """List available template names.

        Returns:
            List of template names
        """
        return list(WORKFLOW_TEMPLATES.keys())

    @classmethod
    def get_template_info(cls) -> dict[str, dict[str, Any]]:
        """Get information about all available templates.

        Returns:
            Dictionary mapping template names to their information
        """
        return {
            name: {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "required_tools": template.required_tools or [],
                "required_retrievers": template.required_retrievers
                or [],
                "default_params": template.default_params,
            }
            for name, template in WORKFLOW_TEMPLATES.items()
        }

    @classmethod
    async def create_workflow_from_template(
        cls,
        template_name: str,
        llm_service: Any,
        provider_name: str,
        overrides: dict[str, Any] | None = None,
        retriever: Any = None,
        tools: list[Any] | None = None,
    ):
        """Create a workflow from a template.

        Args:
            template_name: Name of the template to use
            llm_service: LLM service instance
            provider_name: LLM provider name
            overrides: Parameter overrides for the template
            retriever: Retriever instance (if required by template)
            tools: List of tools (if required by template)

        Returns:
            Configured workflow instance

        Raises:
            WorkflowConfigurationError: If template requirements are not met
        """
        template = cls.get_template(template_name)
        params = template.default_params.copy()

        # Apply overrides
        if overrides:
            params.update(overrides)

        # Validate requirements
        if template.required_tools and not tools:
            raise WorkflowConfigurationError(
                f"Template '{template_name}' requires tools: {template.required_tools}"
            )

        if template.required_retrievers and not retriever:
            raise WorkflowConfigurationError(
                f"Template '{template_name}' requires retrievers: {template.required_retrievers}"
            )

        # Create workflow with template parameters
        workflow_kwargs = {
            "provider_name": provider_name,
            "workflow_type": template.workflow_type,
            **params,
        }

        # Add retriever and tools if provided
        if retriever:
            workflow_kwargs["retriever"] = retriever
        if tools:
            workflow_kwargs["tools"] = tools

        return await llm_service.create_langgraph_workflow(
            **workflow_kwargs
        )

    @classmethod
    def validate_template_requirements(
        cls,
        template_name: str,
        available_tools: list[str] | None = None,
        available_retrievers: list[str] | None = None,
    ) -> dict[str, Any]:
        """Validate if template requirements can be satisfied.

        Args:
            template_name: Name of the template to validate
            available_tools: List of available tool names
            available_retrievers: List of available retriever names

        Returns:
            Dictionary with validation results
        """
        template = cls.get_template(template_name)

        result = {
            "valid": True,
            "missing_tools": [],
            "missing_retrievers": [],
            "requirements_met": True,
        }

        # Check tool requirements
        if template.required_tools:
            available_tools = available_tools or []
            missing_tools = [
                tool
                for tool in template.required_tools
                if tool not in available_tools
            ]
            if missing_tools:
                result["missing_tools"] = missing_tools
                result["requirements_met"] = False

        # Check retriever requirements
        if template.required_retrievers:
            available_retrievers = available_retrievers or []
            missing_retrievers = [
                retriever
                for retriever in template.required_retrievers
                if retriever not in available_retrievers
            ]
            if missing_retrievers:
                result["missing_retrievers"] = missing_retrievers
                result["requirements_met"] = False

        result["valid"] = result["requirements_met"]
        return result


class CustomWorkflowBuilder:
    """Builder for creating custom workflows from templates and specifications."""

    def __init__(self):
        """Initialize custom workflow builder."""
        self.template_manager = WorkflowTemplateManager()
        self.custom_templates = {}
        self.builder_history = []

    def create_custom_template(
        self,
        name: str,
        description: str,
        workflow_type: str,
        base_template: str | None = None,
        **custom_params: Any,
    ) -> WorkflowTemplate:
        """Create a custom workflow template."""
        # Start with base template if provided
        if base_template:
            base = self.template_manager.get_template(base_template)
            default_params = base.default_params.copy()
            default_params.update(
                custom_params.get("default_params", {})
            )

            required_tools = custom_params.get(
                "required_tools", base.required_tools
            )
            required_retrievers = custom_params.get(
                "required_retrievers", base.required_retrievers
            )
        else:
            default_params = custom_params.get("default_params", {})
            required_tools = custom_params.get("required_tools")
            required_retrievers = custom_params.get(
                "required_retrievers"
            )

        # Create custom template
        custom_template = WorkflowTemplate(
            name=name,
            workflow_type=workflow_type,
            description=description,
            default_params=default_params,
            required_tools=required_tools,
            required_retrievers=required_retrievers,
        )

        # Store custom template
        self.custom_templates[name] = custom_template

        return custom_template

    def build_workflow_spec(
        self,
        template_name: str,
        customizations: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Build a complete workflow specification from template and customizations."""
        # Get template (custom or built-in)
        if template_name in self.custom_templates:
            template = self.custom_templates[template_name]
        else:
            template = self.template_manager.get_template(template_name)

        # Build specification
        spec = {
            "template_name": template_name,
            "workflow_type": template.workflow_type,
            "description": template.description,
            "parameters": template.default_params.copy(),
            "required_tools": template.required_tools or [],
            "required_retrievers": template.required_retrievers or [],
        }

        # Apply customizations
        if customizations:
            if "parameters" in customizations:
                spec["parameters"].update(customizations["parameters"])

            if "additional_tools" in customizations:
                spec["required_tools"].extend(
                    customizations["additional_tools"]
                )

            if "additional_retrievers" in customizations:
                spec["required_retrievers"].extend(
                    customizations["additional_retrievers"]
                )

            # Apply other customizations
            for key, value in customizations.items():
                if key not in [
                    "parameters",
                    "additional_tools",
                    "additional_retrievers",
                ]:
                    spec[key] = value

        return spec

    async def validate_workflow_spec(
        self, spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate a workflow specification."""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check required fields
        required_fields = ["workflow_type", "parameters"]
        for field in required_fields:
            if field not in spec:
                validation_result["errors"].append(
                    f"Missing required field: {field}"
                )
                validation_result["valid"] = False

        # Validate workflow type
        valid_types = ["plain", "tools", "rag", "full"]
        if spec.get("workflow_type") not in valid_types:
            validation_result["errors"].append(
                f"Invalid workflow type: {spec.get('workflow_type')}. Must be one of: {valid_types}"
            )
            validation_result["valid"] = False

        # Validate parameters
        params = spec.get("parameters", {})
        if "system_message" not in params:
            validation_result["warnings"].append(
                "No system message specified"
            )

        if "max_tool_calls" in params and params["max_tool_calls"] <= 0:
            validation_result["errors"].append(
                "max_tool_calls must be positive"
            )
            validation_result["valid"] = False

        # Check tool requirements
        if spec.get("required_tools"):
            # In a real implementation, you'd check against available tools
            validation_result["warnings"].append(
                f"Required tools specified: {spec['required_tools']}. Ensure they are available."
            )

        return validation_result

    def get_custom_templates(self) -> dict[str, WorkflowTemplate]:
        """Get all custom templates."""
        return self.custom_templates.copy()

    def delete_custom_template(self, name: str) -> bool:
        """Delete a custom template."""
        if name in self.custom_templates:
            del self.custom_templates[name]
            return True
        return False

    def export_template(self, name: str) -> dict[str, Any] | None:
        """Export a template as a dictionary."""
        template = None

        if name in self.custom_templates:
            template = self.custom_templates[name]
        else:
            try:
                template = self.template_manager.get_template(name)
            except:
                return None

        if template:
            return {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "default_params": template.default_params,
                "required_tools": template.required_tools,
                "required_retrievers": template.required_retrievers,
            }

        return None

    def import_template(
        self, template_data: dict[str, Any]
    ) -> WorkflowTemplate:
        """Import a template from dictionary data."""
        template = WorkflowTemplate(
            name=template_data["name"],
            workflow_type=template_data["workflow_type"],
            description=template_data["description"],
            default_params=template_data.get("default_params", {}),
            required_tools=template_data.get("required_tools"),
            required_retrievers=template_data.get(
                "required_retrievers"
            ),
        )

        self.custom_templates[template.name] = template
        return template


class TemplateRegistry:
    """Registry for managing workflow templates."""

    def __init__(self):
        """Initialize template registry."""
        self.templates = WORKFLOW_TEMPLATES.copy()
        self.custom_templates = {}

    def register_template(self, template: WorkflowTemplate) -> None:
        """Register a new template."""
        self.custom_templates[template.name] = template

    def get_template(self, name: str) -> WorkflowTemplate:
        """Get a template by name."""
        if name in self.custom_templates:
            return self.custom_templates[name]
        elif name in self.templates:
            return self.templates[name]
        else:
            raise WorkflowConfigurationError(
                f"Template '{name}' not found"
            )

    def list_templates(self) -> list[str]:
        """List all available template names."""
        return list(self.templates.keys()) + list(
            self.custom_templates.keys()
        )

    def remove_template(self, name: str) -> bool:
        """Remove a custom template."""
        if name in self.custom_templates:
            del self.custom_templates[name]
            return True
        return False
