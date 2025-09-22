"""Unified template manager for workflow templates.

This module consolidates the WorkflowTemplateManager, CustomWorkflowBuilder,
and TemplateRegistry classes into a single unified interface to eliminate
code duplication and provide a consistent API. Now includes database persistence
for custom templates and specs.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.core.exceptions import ValidationError
from chatter.core.simplified_workflow_validation import (
    simplified_workflow_validation_service as workflow_validation_service,
)

# Use the centralized validation result from the workflow validation service
from chatter.core.validation.results import ValidationResult
from chatter.models.workflow import TemplateCategory
from chatter.schemas.workflows import (
    ChatWorkflowConfig,
    ModelConfig,
    RetrievalConfig,
    ToolConfig,
)


class WorkflowConfigurationError(Exception):
    """Workflow configuration error."""

    pass


def get_secure_logger(name: str):
    """Get a simple logger - placeholder for security logger."""
    import logging

    return logging.getLogger(name)


logger = get_secure_logger(__name__)


@dataclass
@dataclass
class WorkflowTemplate:
    """Pre-configured workflow template."""

    name: str
    workflow_mode: str
    description: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None


@dataclass
class TemplateSpec:
    """Specification for creating custom templates."""

    name: str
    description: str
    workflow_mode: str
    default_params: dict[str, Any]
    required_tools: list[str] | None = None
    required_retrievers: list[str] | None = None
    base_template: str | None = None


class UnifiedTemplateManager:
    """Consolidated template manager combining all template operations.

    This class replaces WorkflowTemplateManager, CustomWorkflowBuilder,
    and TemplateRegistry to provide a single interface for all template
    operations including built-in templates, custom template creation,
    validation, and registry management. Now supports database persistence
    for custom templates and specs.
    """

    def __init__(self, session: AsyncSession | None = None):
        """Initialize unified template manager.

        Args:
            session: Database session for template persistence (required)
        """
        if not session:
            raise ValueError(
                "Database session is required for template operations"
            )
        self.session = session
        self.builder_history: list[dict[str, Any]] = []

    async def _get_templates_from_db(
        self, owner_id: str | None = None
    ) -> dict[str, WorkflowTemplate]:
        """Load templates from database.

        Args:
            owner_id: Optional user ID to filter templates by owner

        Returns:
            Dictionary of templates
        """
        if not self.session:
            return {}

        try:
            from chatter.models.workflow import (
                WorkflowTemplate as DBWorkflowTemplate,
            )

            query = select(DBWorkflowTemplate).options(
                selectinload(DBWorkflowTemplate.owner)
            )

            if owner_id:
                # Get user's private templates + all public templates (including builtin)
                query = query.where(
                    (DBWorkflowTemplate.owner_id == owner_id)
                    | (DBWorkflowTemplate.is_public)
                )
            else:
                # Only get public templates (including builtin)
                query = query.where(DBWorkflowTemplate.is_public)

            result = await self.session.execute(query)
            db_templates = result.scalars().all()

            # Convert DB models to in-memory format
            templates = {}
            for db_template in db_templates:
                template_data = db_template.to_unified_template()
                templates[template_data["name"]] = WorkflowTemplate(
                    name=template_data["name"],
                    workflow_mode=template_data["workflow_mode"],
                    description=template_data["description"],
                    default_params=template_data["default_params"],
                    required_tools=template_data["required_tools"],
                    required_retrievers=template_data[
                        "required_retrievers"
                    ],
                )

            return templates

        except Exception as e:
            logger.warning(
                f"Failed to load custom templates from database: {e}"
            )
            return {}

    # Core operations (from WorkflowTemplateManager)
    async def get_template(
        self, name: str, owner_id: str | None = None
    ) -> WorkflowTemplate:
        """Get a workflow template by name.

        Args:
            name: Name of the template to retrieve
            owner_id: Optional user ID for accessing private templates

        Returns:
            WorkflowTemplate: The requested template

        Raises:
            WorkflowConfigurationError: If template is not found
        """
        try:
            from chatter.models.workflow import (
                WorkflowTemplate as DBWorkflowTemplate,
            )

            query = select(DBWorkflowTemplate).where(
                DBWorkflowTemplate.name == name
            )

            # If owner_id provided, include their private templates
            if owner_id:
                query = query.where(
                    (DBWorkflowTemplate.owner_id == owner_id)
                    | (DBWorkflowTemplate.is_public)
                )
            else:
                # Only public templates
                query = query.where(DBWorkflowTemplate.is_public)

            result = await self.session.execute(query)
            db_template = result.scalar_one_or_none()

            if db_template:
                template_data = db_template.to_unified_template()
                logger.debug(
                    f"Retrieved template from database: {name}"
                )
                return WorkflowTemplate(
                    name=template_data["name"],
                    workflow_mode=template_data["workflow_mode"],
                    description=template_data["description"],
                    default_params=template_data["default_params"],
                    required_tools=template_data["required_tools"],
                    required_retrievers=template_data[
                        "required_retrievers"
                    ],
                )
        except Exception as e:
            logger.warning(
                f"Error retrieving template from database: {e}"
            )

        # Template not found
        available = await self.list_templates(owner_id=owner_id)
        raise WorkflowConfigurationError(
            f"Template '{name}' not found. Available templates: {', '.join(available)}"
        )

    async def list_templates(
        self, include_custom: bool = True, owner_id: str | None = None
    ) -> list[str]:
        """List available template names.

        Args:
            include_custom: Deprecated - all templates are now stored in database
            owner_id: Optional user ID for accessing private templates

        Returns:
            List of template names
        """
        try:
            templates = await self._get_templates_from_db(owner_id)
            return sorted(templates.keys())
        except Exception as e:
            logger.warning(f"Error loading templates: {e}")
            return []

    async def get_template_info(
        self, owner_id: str | None = None
    ) -> dict[str, dict[str, Any]]:
        """Get information about all available templates.

        Args:
            owner_id: Optional user ID for accessing private templates

        Returns:
            Dictionary mapping template names to their information
        """
        info = {}

        # Get all templates from database
        try:
            templates = await self._get_templates_from_db(owner_id)
            for name, template in templates.items():
                info[name] = {
                    "name": template.name,
                    "workflow_mode": template.workflow_mode,
                    "description": template.description,
                    "required_tools": template.required_tools or [],
                    "required_retrievers": template.required_retrievers
                    or [],
                    "default_params": template.default_params,
                    "is_custom": True,  # All templates are now stored in DB
                    "is_builtin": False,  # Builtin is now determined by DB flag
                }
        except Exception as e:
            logger.warning(f"Error loading template info: {e}")

        return info

    # Custom template features (from CustomWorkflowBuilder)
    async def create_custom_template(
        self, spec: TemplateSpec, owner_id: str
    ) -> WorkflowTemplate:
        """Create a custom workflow template.

        Args:
            spec: Template specification
            owner_id: ID of the user creating the template

        Returns:
            WorkflowTemplate: The created custom template

        Raises:
            WorkflowConfigurationError: If template creation fails
        """
        logger.debug(f"Creating custom template: {spec.name}")

        # Start with base template if provided
        if spec.base_template:
            base = await self.get_template(spec.base_template, owner_id)
            default_params = base.default_params.copy()
            default_params.update(spec.default_params)

            required_tools = spec.required_tools or base.required_tools
            required_retrievers = (
                spec.required_retrievers or base.required_retrievers
            )
        else:
            default_params = spec.default_params
            required_tools = spec.required_tools
            required_retrievers = spec.required_retrievers

        # Create custom template in memory for validation
        custom_template = WorkflowTemplate(
            name=spec.name,
            workflow_mode=spec.workflow_mode,
            description=spec.description,
            default_params=default_params,
            required_tools=required_tools,
            required_retrievers=required_retrievers,
        )

        # Validate template
        validation_result = await self.validate_template(
            custom_template
        )
        if not validation_result.is_valid:
            raise WorkflowConfigurationError(
                f"Template validation failed: {', '.join(str(error) for error in validation_result.errors)}"
            )

        # Save to database if session available
        if self.session:
            try:
                from chatter.models.workflow import (
                    WorkflowTemplate as DBWorkflowTemplate,
                )

                # Determine category based on name/type
                category = self._determine_template_category(
                    spec.name, spec.workflow_mode
                )

                db_template = DBWorkflowTemplate(
                    owner_id=owner_id,
                    name=spec.name,
                    description=spec.description,
                    workflow_mode=spec.workflow_mode,
                    category=category,
                    default_params=default_params,
                    required_tools=required_tools,
                    required_retrievers=required_retrievers,
                    is_builtin=False,
                    is_public=False,  # Default to private
                )

                if spec.base_template:
                    # Try to find the base template ID
                    from sqlalchemy import select

                    base_query = select(DBWorkflowTemplate).where(
                        DBWorkflowTemplate.name == spec.base_template
                    )
                    base_result = await self.session.execute(base_query)
                    base_db_template = base_result.scalar_one_or_none()
                    if base_db_template:
                        db_template.base_template_id = (
                            base_db_template.id
                        )

                self.session.add(db_template)
                await self.session.commit()
                await self.session.refresh(db_template)

                logger.info(
                    f"Saved custom template to database: {spec.name} (ID: {db_template.id})"
                )

            except Exception as e:
                logger.error(
                    f"Failed to save custom template to database: {e}"
                )
                if self.session:
                    await self.session.rollback()
                raise WorkflowConfigurationError(
                    f"Failed to save template: {str(e)}"
                ) from e

        # Record in builder history
        self.builder_history.append(
            {
                "action": "create_custom_template",
                "template_name": spec.name,
                "base_template": spec.base_template,
                "owner_id": owner_id,
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        logger.info(f"Created custom template: {spec.name}")
        return custom_template

    def _determine_template_category(
        self, name: str, workflow_mode: str
    ) -> TemplateCategory:
        """Determine template category based on name and type."""
        name_lower = name.lower()
        if "support" in name_lower or "customer" in name_lower:
            return TemplateCategory.CUSTOMER_SUPPORT
        elif (
            "code" in name_lower
            or "programming" in name_lower
            or "dev" in name_lower
        ):
            return TemplateCategory.PROGRAMMING
        elif "research" in name_lower or "document" in name_lower:
            return TemplateCategory.RESEARCH
        elif (
            "data" in name_lower
            or "analyst" in name_lower
            or "analytics" in name_lower
        ):
            return TemplateCategory.DATA_ANALYSIS
        elif "creative" in name_lower or "writing" in name_lower:
            return TemplateCategory.CREATIVE
        elif "business" in name_lower:
            return TemplateCategory.BUSINESS
        elif "education" in name_lower or "learning" in name_lower:
            return TemplateCategory.EDUCATIONAL
        else:
            return TemplateCategory.CUSTOM

    async def build_workflow_spec(
        self,
        name: str,
        overrides: dict[str, Any] | None = None,
        owner_id: str | None = None,
    ) -> dict[str, Any]:
        """Build a complete workflow specification from template and customizations.

        Args:
            name: Template name
            overrides: Parameter overrides for the template
            owner_id: Optional user ID for accessing private templates

        Returns:
            Complete workflow specification dictionary
        """
        template = await self.get_template(name, owner_id)

        # Build specification
        spec = {
            "template_name": name,
            "workflow_mode": template.workflow_mode,
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
                spec["required_tools"].extend(
                    overrides["additional_tools"]
                )

            if "additional_retrievers" in overrides:
                spec["required_retrievers"].extend(
                    overrides["additional_retrievers"]
                )

            # Apply other overrides
            for key, value in overrides.items():
                if key not in [
                    "parameters",
                    "additional_tools",
                    "additional_retrievers",
                ]:
                    spec[key] = value

        return spec

    # Registry features (from TemplateRegistry)
    async def register_template(
        self, template: WorkflowTemplate, owner_id: str
    ) -> None:
        """Register a new template in the registry.

        Args:
            template: Template to register
            owner_id: ID of the user registering the template
        """
        # Validate template before registration
        validation_result = await self.validate_template(template)
        if not validation_result.is_valid:
            raise WorkflowConfigurationError(
                f"Cannot register invalid template: {', '.join(str(error) for error in validation_result.errors)}"
            )

        if self.session:
            try:
                from chatter.models.workflow import (
                    WorkflowTemplate as DBWorkflowTemplate,
                )

                category = self._determine_template_category(
                    template.name, template.workflow_mode
                )

                db_template = DBWorkflowTemplate(
                    owner_id=owner_id,
                    name=template.name,
                    description=template.description,
                    workflow_mode=template.workflow_mode,
                    category=category,
                    default_params=template.default_params,
                    required_tools=template.required_tools,
                    required_retrievers=template.required_retrievers,
                    is_builtin=False,
                    is_public=False,
                )

                self.session.add(db_template)
                await self.session.commit()
                logger.info(
                    f"Registered template in database: {template.name}"
                )
            except Exception as e:
                logger.error(
                    f"Failed to register template in database: {e}"
                )
                if self.session:
                    await self.session.rollback()
                raise WorkflowConfigurationError(
                    f"Failed to register template: {str(e)}"
                ) from e
        else:
            logger.info(
                f"Registered template in memory: {template.name}"
            )

    async def remove_template(
        self, name: str, owner_id: str, custom_only: bool = True
    ) -> bool:
        """Remove a template from the registry.

        Args:
            name: Template name to remove
            owner_id: ID of the user removing the template
            custom_only: If True, only remove custom templates (default)

        Returns:
            True if template was removed, False if not found

        Raises:
            WorkflowConfigurationError: If trying to remove built-in template
        """
        # Built-in templates are now stored in database with is_builtin=True
        # The database constraints will prevent removal of builtin templates

        try:
            from chatter.models.workflow import (
                WorkflowTemplate as DBWorkflowTemplate,
            )

            query = select(DBWorkflowTemplate).where(
                DBWorkflowTemplate.name == name,
                DBWorkflowTemplate.owner_id == owner_id,
            )

            result = await self.session.execute(query)
            db_template = result.scalar_one_or_none()

            if db_template:
                await self.session.delete(db_template)
                await self.session.commit()
                logger.info(f"Removed template from database: {name}")
                return True
        except Exception as e:
            logger.error(
                f"Failed to remove template from database: {e}"
            )
            await self.session.rollback()
            raise WorkflowConfigurationError(
                f"Failed to remove template: {str(e)}"
            ) from e

        return False

    # Unified validation (consolidates scattered validation)
    async def validate_template(
        self, template: WorkflowTemplate
    ) -> ValidationResult:
        """Validate a workflow template using centralized validation service.

        Args:
            template: Template to validate

        Returns:
            ValidationResult with validation details
        """
        try:
            # Use centralized validation service
            return workflow_validation_service.validate_workflow_template(
                template  # type: ignore # Template compatibility handled by validation service
            )
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[
                    ValidationError(f"Validation failed: {str(e)}")
                ],
                warnings=[],
            )

    async def validate_template_requirements(
        self,
        template_name: str,
        available_tools: list[str] | None = None,
        available_retrievers: list[str] | None = None,
        owner_id: str | None = None,
    ) -> ValidationResult:
        """Validate if template requirements can be satisfied.

        Args:
            template_name: Name of the template to validate
            available_tools: List of available tool names
            available_retrievers: List of available retriever names
            owner_id: Optional user ID for accessing private templates

        Returns:
            ValidationResult with requirement validation details
        """
        template = await self.get_template(template_name, owner_id)

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
                errors.append(
                    f"Missing required tools: {', '.join(missing_tools)}"
                )

        # Check retriever requirements
        if template.required_retrievers:
            available_retrievers = available_retrievers or []
            missing_retrievers = [
                retriever
                for retriever in template.required_retrievers
                if retriever not in available_retrievers
            ]
            if missing_retrievers:
                errors.append(
                    f"Missing required retrievers: {', '.join(missing_retrievers)}"
                )

        requirements_met = len(errors) == 0

        return ValidationResult(
            is_valid=requirements_met,
            errors=[ValidationError(error) for error in errors],
            warnings=warnings,
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
        owner_id: str | None = None,
    ) -> Any:
        """Create a workflow from a template.

        Args:
            template_name: Name of the template to use
            llm_service: LLM service instance
            provider_name: LLM provider name
            overrides: Parameter overrides for the template
            retriever: Retriever instance (if required by template)
            tools: List of tools (if required by template)
            owner_id: Optional user ID for accessing private templates

        Returns:
            Configured workflow instance

        Raises:
            WorkflowConfigurationError: If template requirements are not met
        """
        template = await self.get_template(template_name, owner_id)
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
            "workflow_mode": template.workflow_mode,
            **params,
        }

        # Add retriever and tools if provided
        if retriever:
            workflow_kwargs["retriever"] = retriever
        if tools:
            workflow_kwargs["tools"] = tools

        logger.debug(
            f"Creating workflow from template: {template_name}",
            workflow_mode=template.workflow_mode,
        )

        return await llm_service.create_langgraph_workflow(
            **workflow_kwargs
        )

    # Import/Export functionality
    async def export_template(
        self, name: str, owner_id: str | None = None
    ) -> dict[str, Any] | None:
        """Export a template as a dictionary.

        Args:
            name: Template name to export
            owner_id: Optional user ID for accessing private templates

        Returns:
            Template data as dictionary, or None if not found
        """
        try:
            template = await self.get_template(name, owner_id)
            return {
                "name": template.name,
                "workflow_mode": template.workflow_mode,
                "description": template.description,
                "default_params": template.default_params,
                "required_tools": template.required_tools,
                "required_retrievers": template.required_retrievers,
            }
        except WorkflowConfigurationError:
            return None

    async def import_template(
        self, template_data: dict[str, Any], owner_id: str
    ) -> WorkflowTemplate:
        """Import a template from dictionary data.

        Args:
            template_data: Template data dictionary
            owner_id: ID of the user importing the template

        Returns:
            Imported WorkflowTemplate

        Raises:
            WorkflowConfigurationError: If import fails
        """
        template = WorkflowTemplate(
            name=template_data["name"],
            workflow_mode=template_data["workflow_mode"],
            description=template_data["description"],
            default_params=template_data.get("default_params", {}),
            required_tools=template_data.get("required_tools"),
            required_retrievers=template_data.get(
                "required_retrievers"
            ),
        )

        await self.register_template(template, owner_id)
        return template

    # Additional utility methods
    async def get_templates_by_type(
        self, workflow_mode: str, owner_id: str | None = None
    ) -> list[WorkflowTemplate]:
        """Get all templates of a specific workflow type.

        Args:
            workflow_mode: Type of workflow to filter by
            owner_id: Optional user ID for accessing private templates

        Returns:
            List of templates matching the workflow type
        """
        templates = []

        # Check templates from database
        try:
            all_templates = await self._get_templates_from_db(owner_id)
            for template in all_templates.values():
                if template.workflow_mode == workflow_mode:
                    templates.append(template)
        except Exception as e:
            logger.warning(f"Error loading templates by type: {e}")

        return templates

    async def get_custom_templates(
        self, owner_id: str | None = None
    ) -> dict[str, WorkflowTemplate]:
        """Get all templates (formerly custom templates).

        Args:
            owner_id: Optional user ID for accessing private templates

        Returns:
            Dictionary of templates
        """
        return await self._get_templates_from_db(owner_id)

    def get_builder_history(self) -> list[dict[str, Any]]:
        """Get the builder history.

        Returns:
            List of builder actions
        """
        return self.builder_history.copy()

    def get_stats(self, owner_id: str | None = None) -> dict[str, Any]:
        """Get template manager statistics.

        Args:
            owner_id: Optional user ID for user-specific stats

        Returns:
            Dictionary containing template usage statistics
        """
        # This is a synchronous method, so we can't easily get DB stats here
        # In a real implementation, this would be refactored to be async

        # For now, return basic stats - this could be enhanced to query the DB
        return {
            "builtin_templates_count": 0,  # No longer tracked separately
            "custom_templates_count": 0,  # Would need async DB query
            "total_templates": 0,  # Would need async DB query
            "builder_actions": len(self.builder_history),
            "template_types": {},  # Would need async DB query
        }

    # Chat Workflow Template Methods



def get_template_manager_with_session(
    session: AsyncSession,
) -> UnifiedTemplateManager:
    """Get a template manager instance with database session.

    Args:
        session: Database session for template persistence

    Returns:
        UnifiedTemplateManager instance with database support
    """
    return UnifiedTemplateManager(session)
