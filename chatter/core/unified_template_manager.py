"""Unified template manager for workflow templates.

This module consolidates the WorkflowTemplateManager, CustomWorkflowBuilder, 
and TemplateRegistry classes into a single unified interface to eliminate
code duplication and provide a consistent API.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any


class WorkflowConfigurationError(Exception):
    """Workflow configuration error."""
    pass


def get_secure_logger(name: str):
    """Get a simple logger - placeholder for security logger."""
    import logging
    return logging.getLogger(name)


logger = get_secure_logger(__name__)


@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""

    name: str
    workflow_type: str
    description: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None


@dataclass
class TemplateSpec:
    """Specification for creating custom templates."""
    
    name: str
    description: str
    workflow_type: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None
    base_template: str | None = None


@dataclass
class ValidationResult:
    """Result of template validation."""
    
    valid: bool
    errors: list[str]
    warnings: list[str]
    requirements_met: bool = True
    missing_tools: list[str] | None = None
    missing_retrievers: list[str] | None = None


class UnifiedTemplateManager:
    """Consolidated template manager combining all template operations.
    
    This class replaces WorkflowTemplateManager, CustomWorkflowBuilder,
    and TemplateRegistry to provide a single interface for all template
    operations including built-in templates, custom template creation,
    validation, and registry management.
    """

    def __init__(self):
        """Initialize unified template manager."""
        self.builtin_templates = self._load_builtin_templates()
        self.custom_templates: dict[str, WorkflowTemplate] = {}
        self.builder_history: list[dict[str, Any]] = []
        
    def _load_builtin_templates(self) -> dict[str, WorkflowTemplate]:
        """Load built-in workflow templates."""
        return {
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

    # Core operations (from WorkflowTemplateManager)
    async def get_template(self, name: str) -> WorkflowTemplate:
        """Get a workflow template by name.

        Args:
            name: Name of the template to retrieve

        Returns:
            WorkflowTemplate: The requested template

        Raises:
            WorkflowConfigurationError: If template is not found
        """
        # Check custom templates first
        if name in self.custom_templates:
            logger.debug(f"Retrieved custom template: {name}")
            return self.custom_templates[name]
        
        # Check built-in templates
        if name in self.builtin_templates:
            logger.debug(f"Retrieved built-in template: {name}")
            return self.builtin_templates[name]
        
        # Template not found
        available = await self.list_templates()
        raise WorkflowConfigurationError(
            f"Template '{name}' not found. Available templates: {', '.join(available)}"
        )

    async def list_templates(self, include_custom: bool = True) -> list[str]:
        """List available template names.

        Args:
            include_custom: Whether to include custom templates

        Returns:
            List of template names
        """
        templates = list(self.builtin_templates.keys())
        if include_custom:
            templates.extend(self.custom_templates.keys())
        return sorted(templates)

    async def get_template_info(self) -> dict[str, dict[str, Any]]:
        """Get information about all available templates.

        Returns:
            Dictionary mapping template names to their information
        """
        info = {}
        
        # Add built-in templates
        for name, template in self.builtin_templates.items():
            info[name] = {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "required_tools": template.required_tools or [],
                "required_retrievers": template.required_retrievers or [],
                "default_params": template.default_params,
                "is_custom": False,
            }
        
        # Add custom templates
        for name, template in self.custom_templates.items():
            info[name] = {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "required_tools": template.required_tools or [],
                "required_retrievers": template.required_retrievers or [],
                "default_params": template.default_params,
                "is_custom": True,
            }
        
        return info

    # Custom template features (from CustomWorkflowBuilder)
    async def create_custom_template(self, spec: TemplateSpec) -> WorkflowTemplate:
        """Create a custom workflow template.

        Args:
            spec: Template specification

        Returns:
            WorkflowTemplate: The created custom template

        Raises:
            WorkflowConfigurationError: If template creation fails
        """
        logger.debug(f"Creating custom template: {spec.name}")
        
        # Start with base template if provided
        if spec.base_template:
            base = await self.get_template(spec.base_template)
            default_params = base.default_params.copy()
            default_params.update(spec.default_params)
            
            required_tools = spec.required_tools or base.required_tools
            required_retrievers = spec.required_retrievers or base.required_retrievers
        else:
            default_params = spec.default_params
            required_tools = spec.required_tools
            required_retrievers = spec.required_retrievers

        # Create custom template
        custom_template = WorkflowTemplate(
            name=spec.name,
            workflow_type=spec.workflow_type,
            description=spec.description,
            default_params=default_params,
            required_tools=required_tools,
            required_retrievers=required_retrievers,
        )

        # Validate template
        validation_result = await self.validate_template(custom_template)
        if not validation_result.valid:
            raise WorkflowConfigurationError(
                f"Template validation failed: {', '.join(validation_result.errors)}"
            )

        # Store custom template
        self.custom_templates[spec.name] = custom_template

        # Record in builder history
        self.builder_history.append({
            "action": "create_custom_template",
            "template_name": spec.name,
            "base_template": spec.base_template,
            "timestamp": asyncio.get_event_loop().time(),
        })

        logger.info(f"Created custom template: {spec.name}")
        return custom_template

    async def build_workflow_spec(
        self, 
        name: str, 
        overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Build a complete workflow specification from template and customizations.

        Args:
            name: Template name
            overrides: Parameter overrides for the template

        Returns:
            Complete workflow specification dictionary
        """
        template = await self.get_template(name)

        # Build specification
        spec = {
            "template_name": name,
            "workflow_type": template.workflow_type,
            "description": template.description,
            "parameters": template.default_params.copy(),
            "required_tools": template.required_tools or [],
            "required_retrievers": template.required_retrievers or [],
        }

        # Apply overrides
        if overrides:
            if "parameters" in overrides:
                spec["parameters"].update(overrides["parameters"])

            if "additional_tools" in overrides:
                spec["required_tools"].extend(overrides["additional_tools"])

            if "additional_retrievers" in overrides:
                spec["required_retrievers"].extend(overrides["additional_retrievers"])

            # Apply other overrides
            for key, value in overrides.items():
                if key not in ["parameters", "additional_tools", "additional_retrievers"]:
                    spec[key] = value

        return spec

    # Registry features (from TemplateRegistry)
    async def register_template(self, template: WorkflowTemplate) -> None:
        """Register a new template in the registry.

        Args:
            template: Template to register
        """
        # Validate template before registration
        validation_result = await self.validate_template(template)
        if not validation_result.valid:
            raise WorkflowConfigurationError(
                f"Cannot register invalid template: {', '.join(validation_result.errors)}"
            )

        self.custom_templates[template.name] = template
        logger.info(f"Registered template: {template.name}")

    async def remove_template(self, name: str, custom_only: bool = True) -> bool:
        """Remove a template from the registry.

        Args:
            name: Template name to remove
            custom_only: If True, only remove custom templates (default)

        Returns:
            True if template was removed, False if not found

        Raises:
            WorkflowConfigurationError: If trying to remove built-in template
        """
        if name in self.custom_templates:
            del self.custom_templates[name]
            logger.info(f"Removed custom template: {name}")
            return True
        elif name in self.builtin_templates and not custom_only:
            raise WorkflowConfigurationError(
                f"Cannot remove built-in template: {name}"
            )
        
        return False

    # Unified validation (consolidates scattered validation)
    async def validate_template(self, template: WorkflowTemplate) -> ValidationResult:
        """Validate a workflow template.

        Args:
            template: Template to validate

        Returns:
            ValidationResult with validation details
        """
        errors = []
        warnings = []
        
        # Check required fields
        if not template.name:
            errors.append("Template name is required")
        if not template.workflow_type:
            errors.append("Workflow type is required")
        if not template.description:
            warnings.append("Template description is empty")

        # Validate workflow type
        valid_types = ["plain", "tools", "rag", "full"]
        if template.workflow_type not in valid_types:
            errors.append(
                f"Invalid workflow type: {template.workflow_type}. Must be one of: {valid_types}"
            )

        # Validate parameters
        params = template.default_params or {}
        if "system_message" not in params:
            warnings.append("No system message specified")

        if "max_tool_calls" in params and params["max_tool_calls"] <= 0:
            errors.append("max_tool_calls must be positive")

        # Check for naming conflicts
        if template.name in self.builtin_templates and template.name in self.custom_templates:
            warnings.append(f"Custom template '{template.name}' shadows built-in template")

        # Use simple validation for now (to avoid circular imports)
        # In a real implementation, this would use the validation engine
        validation_errors = []
        if not workflow_spec.get('workflow_type'):
            validation_errors.append("workflow_type is required")
        
        if validation_errors:
            errors.extend(validation_errors)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            requirements_met=True,  # Will be set by validate_template_requirements
        )

    async def validate_template_requirements(
        self,
        template_name: str,
        available_tools: list[str] | None = None,
        available_retrievers: list[str] | None = None,
    ) -> ValidationResult:
        """Validate if template requirements can be satisfied.

        Args:
            template_name: Name of the template to validate
            available_tools: List of available tool names
            available_retrievers: List of available retriever names

        Returns:
            ValidationResult with requirement validation details
        """
        template = await self.get_template(template_name)

        errors = []
        warnings = []
        missing_tools = []
        missing_retrievers = []

        # Check tool requirements
        if template.required_tools:
            available_tools = available_tools or []
            missing_tools = [
                tool
                for tool in template.required_tools
                if tool not in available_tools
            ]
            if missing_tools:
                errors.append(f"Missing required tools: {', '.join(missing_tools)}")

        # Check retriever requirements  
        if template.required_retrievers:
            available_retrievers = available_retrievers or []
            missing_retrievers = [
                retriever
                for retriever in template.required_retrievers
                if retriever not in available_retrievers
            ]
            if missing_retrievers:
                errors.append(f"Missing required retrievers: {', '.join(missing_retrievers)}")

        requirements_met = len(errors) == 0

        return ValidationResult(
            valid=requirements_met,
            errors=errors,
            warnings=warnings,
            requirements_met=requirements_met,
            missing_tools=missing_tools if missing_tools else None,
            missing_retrievers=missing_retrievers if missing_retrievers else None,
        )

    # Workflow creation (from WorkflowTemplateManager)
    async def create_workflow_from_template(
        self,
        template_name: str,
        llm_service: Any,
        provider_name: str,
        overrides: dict[str, Any] | None = None,
        retriever: Any = None,
        tools: list[Any] | None = None,
    ) -> Any:
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
        template = await self.get_template(template_name)
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

        logger.debug(
            f"Creating workflow from template: {template_name}",
            workflow_type=template.workflow_type,
        )

        return await llm_service.create_langgraph_workflow(**workflow_kwargs)

    # Import/Export functionality
    async def export_template(self, name: str) -> dict[str, Any] | None:
        """Export a template as a dictionary.

        Args:
            name: Template name to export

        Returns:
            Template data as dictionary, or None if not found
        """
        try:
            template = await self.get_template(name)
            return {
                "name": template.name,
                "workflow_type": template.workflow_type,
                "description": template.description,
                "default_params": template.default_params,
                "required_tools": template.required_tools,
                "required_retrievers": template.required_retrievers,
            }
        except WorkflowConfigurationError:
            return None

    async def import_template(self, template_data: dict[str, Any]) -> WorkflowTemplate:
        """Import a template from dictionary data.

        Args:
            template_data: Template data dictionary

        Returns:
            Imported WorkflowTemplate

        Raises:
            WorkflowConfigurationError: If import fails
        """
        template = WorkflowTemplate(
            name=template_data["name"],
            workflow_type=template_data["workflow_type"],
            description=template_data["description"],
            default_params=template_data.get("default_params", {}),
            required_tools=template_data.get("required_tools"),
            required_retrievers=template_data.get("required_retrievers"),
        )

        await self.register_template(template)
        return template

    # Additional utility methods
    async def get_templates_by_type(self, workflow_type: str) -> list[WorkflowTemplate]:
        """Get all templates of a specific workflow type.

        Args:
            workflow_type: Type of workflow to filter by

        Returns:
            List of templates matching the workflow type
        """
        templates = []
        
        # Check built-in templates
        for template in self.builtin_templates.values():
            if template.workflow_type == workflow_type:
                templates.append(template)
        
        # Check custom templates
        for template in self.custom_templates.values():
            if template.workflow_type == workflow_type:
                templates.append(template)
        
        return templates

    async def get_custom_templates(self) -> dict[str, WorkflowTemplate]:
        """Get all custom templates.

        Returns:
            Dictionary of custom templates
        """
        return self.custom_templates.copy()

    def get_builder_history(self) -> list[dict[str, Any]]:
        """Get the builder history.

        Returns:
            List of builder actions
        """
        return self.builder_history.copy()

    def get_stats(self) -> dict[str, Any]:
        """Get template manager statistics.

        Returns:
            Dictionary containing template usage statistics
        """
        return {
            "builtin_templates_count": len(self.builtin_templates),
            "custom_templates_count": len(self.custom_templates),
            "total_templates": len(self.builtin_templates) + len(self.custom_templates),
            "builder_actions": len(self.builder_history),
            "template_types": {
                workflow_type: len([
                    t for t in list(self.builtin_templates.values()) + list(self.custom_templates.values())
                    if t.workflow_type == workflow_type
                ])
                for workflow_type in ["plain", "tools", "rag", "full"]
            },
        }


# Global instance for backward compatibility
unified_template_manager = UnifiedTemplateManager()