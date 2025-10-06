"""Workflow management service for CRUD operations on workflows and templates."""

import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.core.validation import validate_workflow_definition
from chatter.models.workflow import (
    TemplateCategory,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowTemplate,
)
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


def _get_validation_errors_as_strings(validation_result) -> list[str]:
    """Extract error messages as strings from validation result."""
    errors = validation_result.errors
    if not errors:
        return []
    # Convert ValidationError objects to strings
    return [str(error) for error in errors]


def _is_validation_result_valid(validation_result) -> bool:
    """Check if validation result is valid."""
    return validation_result.is_valid


class WorkflowManagementService:
    """Service for managing workflow definitions and templates."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def _invalidate_workflow_caches(
        self, workflow_id: str | None = None
    ) -> None:
        """Invalidate workflow-related caches.

        Args:
            workflow_id: Specific workflow to invalidate, or None to invalidate all
        """
        try:
            from chatter.core.workflow_performance import (
                get_workflow_cache,
            )

            workflow_cache = get_workflow_cache()
            await workflow_cache.clear_all()

            logger.debug(
                "Invalidated workflow caches",
                workflow_id=workflow_id,
            )

        except Exception as e:
            # Don't fail the main operation if cache invalidation fails
            logger.warning(
                "Failed to invalidate workflow caches",
                error=str(e),
                workflow_id=workflow_id,
            )

    # Workflow Definition CRUD
    async def create_workflow_definition(
        self,
        owner_id: str,
        name: str,
        description: str | None,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
        template_id: str | None = None,
    ) -> WorkflowDefinition:
        """Create a new workflow definition.
        
        Phase 5: Now uses WorkflowValidator for comprehensive validation.
        """
        try:
            from chatter.core.workflow_validator import WorkflowValidator
            from chatter.utils.problem import BadRequestProblem
            
            # Validate the workflow definition
            definition_data = {
                "name": name,
                "description": description,
                "nodes": nodes,
                "edges": edges,
                "metadata": metadata or {},
            }

            validator = WorkflowValidator()
            validation_result = await validator.validate(
                workflow_data=definition_data,
                user_id=owner_id,
                context="workflow_definition",
            )

            if not validation_result.is_valid:
                error_messages = [str(e) for e in validation_result.errors]
                raise BadRequestProblem(
                    detail=f"Workflow validation failed: {'; '.join(error_messages)}"
                )

            # Log warnings if any
            if hasattr(validation_result, 'warnings') and validation_result.warnings:
                logger.warning(
                    f"Workflow validation warnings: {'; '.join(validation_result.warnings)}"
                )

            # Create workflow definition
            definition = WorkflowDefinition(
                owner_id=owner_id,
                name=name,
                description=description,
                nodes=nodes,
                edges=edges,
                workflow_metadata=metadata or {},
                template_id=template_id,
            )

            self.session.add(definition)
            await self.session.commit()
            await self.session.refresh(definition)

            # Validate that the created definition has a proper ULID
            try:
                from ulid import ULID

                ULID.from_str(definition.id)
            except ValueError as e:
                logger.error(
                    f"Created workflow definition has invalid ULID: {definition.id}"
                )
                await self.session.rollback()
                raise RuntimeError(
                    f"Failed to create workflow with valid ULID: {e}"
                ) from e

            # Invalidate workflow caches after creation
            await self._invalidate_workflow_caches(definition.id)

            logger.info(
                f"Created workflow definition {definition.id} for user {owner_id}"
            )
            return definition

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create workflow definition: {e}")
            raise

    async def get_workflow_definition(
        self,
        workflow_id: str,
        owner_id: str,
    ) -> WorkflowDefinition | None:
        """Get a workflow definition by ID."""
        try:
            logger.debug(
                "Searching for workflow definition",
                workflow_id=workflow_id,
                owner_id=owner_id,
            )

            result = await self.session.execute(
                select(WorkflowDefinition)
                .where(
                    and_(
                        WorkflowDefinition.id == workflow_id,
                        or_(
                            WorkflowDefinition.owner_id == owner_id,
                            WorkflowDefinition.is_public,
                        ),
                    )
                )
                .options(selectinload(WorkflowDefinition.template))
            )
            definition = result.scalar_one_or_none()

            if definition:
                logger.debug(
                    "Found workflow definition",
                    workflow_id=workflow_id,
                    owner_id=definition.owner_id,
                    is_public=definition.is_public,
                    requested_by=owner_id,
                )
                return definition

            # If not found, check if it exists with different access permissions
            logger.info(
                "Workflow definition not found with access permissions, checking existence",
                workflow_id=workflow_id,
                requested_by=owner_id,
            )

            # Check if workflow exists at all (without access control)
            existence_result = await self.session.execute(
                select(WorkflowDefinition).where(
                    WorkflowDefinition.id == workflow_id
                )
            )
            existing_workflow = existence_result.scalar_one_or_none()

            if existing_workflow:
                logger.warning(
                    "Workflow definition exists but access denied",
                    workflow_id=workflow_id,
                    actual_owner=existing_workflow.owner_id,
                    requested_by=owner_id,
                    is_public=existing_workflow.is_public,
                )
            else:
                logger.info(
                    "Workflow definition does not exist in database",
                    workflow_id=workflow_id,
                    requested_by=owner_id,
                )

            return None

        except Exception as e:
            logger.error(
                f"Failed to get workflow definition {workflow_id}: {e}"
            )
            raise

    async def list_workflow_definitions(
        self,
        owner_id: str,
        include_public: bool = True,
    ) -> list[WorkflowDefinition]:
        """List workflow definitions for a user."""
        try:
            conditions = [WorkflowDefinition.owner_id == owner_id]
            if include_public:
                conditions.append(WorkflowDefinition.is_public)

            result = await self.session.execute(
                select(WorkflowDefinition)
                .where(or_(*conditions))
                .options(selectinload(WorkflowDefinition.template))
                .order_by(WorkflowDefinition.updated_at.desc())
            )
            return list(result.scalars().all())

        except Exception as e:
            logger.error(
                f"Failed to list workflow definitions for user {owner_id}: {e}"
            )
            raise

    async def update_workflow_definition(
        self, workflow_id: str, owner_id: str, **updates
    ) -> WorkflowDefinition | None:
        """Update a workflow definition."""
        try:
            result = await self.session.execute(
                select(WorkflowDefinition).where(
                    and_(
                        WorkflowDefinition.id == workflow_id,
                        WorkflowDefinition.owner_id == owner_id,
                    )
                )
            )
            definition = result.scalar_one_or_none()

            if not definition:
                return None

            # Update fields
            for field, value in updates.items():
                if hasattr(definition, field):
                    setattr(definition, field, value)

            definition.version += 1

            await self.session.commit()
            await self.session.refresh(definition)

            # Invalidate workflow caches after update
            await self._invalidate_workflow_caches(workflow_id)

            logger.info(f"Updated workflow definition {workflow_id}")
            return definition

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Failed to update workflow definition {workflow_id}: {e}"
            )
            raise

    async def delete_workflow_definition(
        self,
        workflow_id: str,
        owner_id: str,
    ) -> bool:
        """Delete a workflow definition."""
        try:
            result = await self.session.execute(
                select(WorkflowDefinition).where(
                    and_(
                        WorkflowDefinition.id == workflow_id,
                        WorkflowDefinition.owner_id == owner_id,
                    )
                )
            )
            definition = result.scalar_one_or_none()

            if not definition:
                return False

            await self.session.delete(definition)
            await self.session.commit()

            # Invalidate workflow caches after deletion
            await self._invalidate_workflow_caches(workflow_id)

            logger.info(f"Deleted workflow definition {workflow_id}")
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Failed to delete workflow definition {workflow_id}: {e}"
            )
            raise

    # Workflow Execution CRUD
    async def create_workflow_execution(
        self,
        owner_id: str | None = None,
        definition_id: str | None = None,
        template_id: str | None = None,
        workflow_type: str = "chat",
        workflow_config: dict[str, Any] | None = None,
        input_data: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution.
        
        Updated in Phase 4 to support optional definition_id and direct
        template tracking. At least one of definition_id or template_id
        should be provided for non-chat workflows.
        
        Args:
            owner_id: User ID (optional for system executions)
            definition_id: Optional workflow definition ID
            template_id: Optional template ID
            workflow_type: Type of workflow (template/definition/custom/chat)
            workflow_config: Execution configuration
            input_data: Input data for execution
            
        Returns:
            Created WorkflowExecution instance
        """
        try:
            execution = WorkflowExecution(
                definition_id=definition_id,
                template_id=template_id,
                owner_id=owner_id,
                workflow_type=workflow_type,
                workflow_config=workflow_config,
                input_data=input_data or {},
                status="pending",
            )

            self.session.add(execution)
            await self.session.commit()
            await self.session.refresh(execution)

            logger.info(
                f"Created workflow execution {execution.id}",
                workflow_type=workflow_type,
                definition_id=definition_id,
                template_id=template_id,
            )
            return execution

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to create workflow execution: {e}")
            raise

    async def update_workflow_execution(
        self, execution_id: str, owner_id: str, **updates
    ) -> WorkflowExecution | None:
        """Update a workflow execution."""
        try:
            result = await self.session.execute(
                select(WorkflowExecution).where(
                    and_(
                        WorkflowExecution.id == execution_id,
                        WorkflowExecution.owner_id == owner_id,
                    )
                )
            )
            execution = result.scalar_one_or_none()

            if not execution:
                return None

            # Update fields
            for field, value in updates.items():
                if hasattr(execution, field):
                    setattr(execution, field, value)

            await self.session.commit()
            await self.session.refresh(execution)

            logger.info(f"Updated workflow execution {execution_id}")
            return execution

        except Exception as e:
            await self.session.rollback()
            logger.error(
                f"Failed to update workflow execution {execution_id}: {e}"
            )
            raise

    async def list_workflow_executions(
        self,
        definition_id: str,
        owner_id: str,
        limit: int = 50,
    ) -> list[WorkflowExecution]:
        """List workflow executions for a definition."""
        try:
            result = await self.session.execute(
                select(WorkflowExecution)
                .where(
                    and_(
                        WorkflowExecution.definition_id
                        == definition_id,
                        WorkflowExecution.owner_id == owner_id,
                    )
                )
                .order_by(WorkflowExecution.created_at.desc())
                .limit(limit)
            )
            return list(result.scalars().all())

        except Exception as e:
            logger.error(f"Failed to list workflow executions: {e}")
            raise

    async def list_all_workflow_executions(
        self,
        owner_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[WorkflowExecution], int]:
        """List all workflow executions for a user with pagination."""
        try:
            # Get total count
            count_result = await self.session.execute(
                select(WorkflowExecution).where(
                    WorkflowExecution.owner_id == owner_id
                )
            )
            total_count = len(list(count_result.scalars().all()))

            # Get paginated results
            result = await self.session.execute(
                select(WorkflowExecution)
                .where(WorkflowExecution.owner_id == owner_id)
                .order_by(WorkflowExecution.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            executions = list(result.scalars().all())

            return executions, total_count

        except Exception as e:
            logger.error(f"Failed to list all workflow executions: {e}")
            raise

    # Validation methods
    async def validate_workflow_definition(
        self,
        definition_data: dict[str, Any],
        owner_id: str,
    ) -> dict[str, Any]:
        """Validate a workflow definition using the unified validator.

        Phase 5: Now uses WorkflowValidator orchestrator instead of
        scattered validation logic.

        Args:
            definition_data: Workflow definition data to validate
            owner_id: Owner user ID (for security/capability checks)

        Returns:
            Validation result dictionary with valid, errors, warnings
        """
        try:
            from chatter.core.workflow_validator import WorkflowValidator
            
            validator = WorkflowValidator()
            
            validation_result = await validator.validate(
                workflow_data=definition_data,
                user_id=owner_id,
                context="workflow_definition",
            )

            return validation_result.to_api_response()

        except Exception as e:
            logger.error(f"Failed to validate workflow definition: {e}")
            raise

    async def get_workflow_execution_details(
        self,
        execution_id: str,
        owner_id: str,
    ) -> WorkflowExecution | None:
        """Get detailed information about a workflow execution."""
        try:
            result = await self.session.execute(
                select(WorkflowExecution)
                .options(selectinload(WorkflowExecution.definition))
                .where(
                    and_(
                        WorkflowExecution.id == execution_id,
                        WorkflowExecution.owner_id == owner_id,
                    )
                )
            )
            execution = result.scalar_one_or_none()

            if execution and execution.execution_log:
                # Parse and structure the execution logs
                from chatter.schemas.workflows import (
                    WorkflowExecutionLogEntry,
                )

                structured_logs = []
                for log_entry in execution.execution_log:
                    if isinstance(log_entry, dict):
                        try:
                            structured_logs.append(
                                WorkflowExecutionLogEntry(**log_entry)
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to parse log entry: {e}"
                            )

                # Add structured logs to the response
                execution._structured_logs = structured_logs

            return execution

        except Exception as e:
            logger.error(
                f"Failed to get workflow execution details {execution_id}: {e}"
            )
            raise

    async def get_workflow_execution_logs(
        self,
        execution_id: str,
        owner_id: str,
        log_level: str | None = None,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Get execution logs for a workflow execution."""
        try:
            result = await self.session.execute(
                select(WorkflowExecution.execution_log).where(
                    and_(
                        WorkflowExecution.id == execution_id,
                        WorkflowExecution.owner_id == owner_id,
                    )
                )
            )
            execution_log = result.scalar_one_or_none()

            if not execution_log:
                return []

            logs = (
                execution_log if isinstance(execution_log, list) else []
            )

            # Filter by log level if specified
            if log_level:
                logs = [
                    log
                    for log in logs
                    if log.get('level', '').upper() == log_level.upper()
                ]

            # Apply limit
            logs = logs[-limit:] if len(logs) > limit else logs

            return logs

        except Exception as e:
            logger.error(
                f"Failed to get execution logs {execution_id}: {e}"
            )
            raise

    # Template CRUD
    async def create_workflow_template(
        self,
        owner_id: str,
        name: str,
        description: str,
        category: str = "custom",
        default_params: dict[str, Any] | None = None,
        required_tools: list[str] | None = None,
        required_retrievers: list[str] | None = None,
        tags: list[str] | None = None,
        is_public: bool = False,
        workflow_definition_id: str | None = None,
        base_template_id: str | None = None,
    ) -> WorkflowTemplate:
        """Create a new workflow template."""
        try:
            category_enum = TemplateCategory(category)

            # Generate config hash
            config_str = f"{name}:{str(default_params or {})}"
            config_hash = hashlib.sha256(
                config_str.encode("utf-8")
            ).hexdigest()

            # Create template
            template = WorkflowTemplate(
                owner_id=owner_id,
                name=name,
                description=description,
                category=category_enum,
                default_params=default_params or {},
                required_tools=required_tools,
                required_retrievers=required_retrievers,
                base_template_id=base_template_id,
                is_public=is_public,
                is_dynamic=True,  # Mark new templates as dynamic
                execution_pattern="chat",  # Default to chat pattern
                tags=tags,
                config_hash=config_hash,
            )

            self.session.add(template)
            await self.session.commit()
            await self.session.refresh(template)

            logger.info(
                f"Created workflow template {template.id} for user {owner_id}"
            )
            return template

        except Exception as e:
            logger.error(f"Failed to create workflow template: {e}")
            await self.session.rollback()
            raise

    async def list_workflow_templates(
        self,
        owner_id: str,
    ) -> list[WorkflowTemplate]:
        """List workflow templates accessible to a user."""
        try:
            query = (
                select(WorkflowTemplate)
                .where(
                    or_(
                        WorkflowTemplate.owner_id == owner_id,
                        WorkflowTemplate.is_public,
                        WorkflowTemplate.is_builtin,
                    )
                )
                .options(selectinload(WorkflowTemplate.owner))
                .order_by(
                    WorkflowTemplate.is_builtin.desc(),
                    WorkflowTemplate.usage_count.desc(),
                    WorkflowTemplate.created_at.desc(),
                )
            )

            result = await self.session.execute(query)
            templates = result.scalars().all()

            return list(templates)

        except Exception as e:
            logger.error(
                f"Failed to list workflow templates for user {owner_id}: {e}"
            )
            raise

    async def get_workflow_template(
        self,
        template_id: str,
        owner_id: str | None = None,
    ) -> WorkflowTemplate | None:
        """Get a workflow template by ID."""
        try:
            query = select(WorkflowTemplate).where(
                WorkflowTemplate.id == template_id
            )

            # Add access control if owner_id provided
            if owner_id:
                query = query.where(
                    or_(
                        WorkflowTemplate.owner_id == owner_id,
                        WorkflowTemplate.is_public,
                        WorkflowTemplate.is_builtin,
                    )
                )

            result = await self.session.execute(query)
            template = result.scalar_one_or_none()

            return template

        except Exception as e:
            logger.error(
                f"Failed to get workflow template {template_id}: {e}"
            )
            raise

    async def update_workflow_template(
        self, template_id: str, owner_id: str, **updates
    ) -> WorkflowTemplate | None:
        """Update a workflow template."""
        try:
            # Get template with ownership check
            query = select(WorkflowTemplate).where(
                and_(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.owner_id == owner_id,
                )
            )

            result = await self.session.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                return None

            # Update fields
            for field, value in updates.items():
                if hasattr(template, field):
                    setattr(template, field, value)

            template.updated_at = datetime.utcnow()
            template.version += 1

            # Regenerate config hash if params changed
            if "default_params" in updates:
                config_str = (
                    f"{template.name}:{str(template.default_params)}"
                )
                template.config_hash = hashlib.sha256(
                    config_str.encode("utf-8")
                ).hexdigest()

            await self.session.commit()
            await self.session.refresh(template)

            logger.info(f"Updated workflow template {template_id}")
            return template

        except Exception as e:
            logger.error(
                f"Failed to update workflow template {template_id}: {e}"
            )
            await self.session.rollback()
            raise

    async def delete_workflow_template(
        self,
        template_id: str,
        owner_id: str,
    ) -> bool:
        """Delete a workflow template."""
        try:
            # Get template with ownership check
            query = select(WorkflowTemplate).where(
                and_(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.owner_id == owner_id,
                )
            )

            result = await self.session.execute(query)
            template = result.scalar_one_or_none()

            if not template:
                return False

            await self.session.delete(template)
            await self.session.commit()

            logger.info(f"Deleted workflow template {template_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to delete workflow template {template_id}: {e}"
            )
            await self.session.rollback()
            raise

    async def create_workflow_definition_from_template(
        self,
        template_id: str,
        owner_id: str,
        name_suffix: str = "",
        user_input: dict[str, Any] | None = None,
        is_temporary: bool = True,
    ) -> WorkflowDefinition:
        """Create a workflow definition from a template.

        Args:
            template_id: ID of the template to instantiate
            owner_id: ID of the user creating the definition
            name_suffix: Optional suffix for the definition name
            user_input: Optional user input to merge with template params
            is_temporary: Whether this is a temporary definition for execution

        Returns:
            Created workflow definition

        Raises:
            BadRequestProblem: If template not found or invalid
        """
        try:
            # Get the template
            template = await self.get_workflow_template(
                template_id, owner_id
            )
            if not template:
                from chatter.utils.problem import BadRequestProblem

                raise BadRequestProblem(
                    detail=f"Workflow template not found: {template_id}"
                )

            # Create name for the definition
            definition_name = f"{template.name}"
            if name_suffix:
                definition_name += f" {name_suffix}"
            elif is_temporary:
                definition_name += " (Execution)"

            # Merge template default params with user input
            merged_input = {**(template.default_params or {})}
            if user_input:
                merged_input.update(user_input)

            # Generate basic workflow structure based on template type
            nodes, edges = self._generate_workflow_from_template(
                template, merged_input
            )

            # Create the workflow definition
            definition = await self.create_workflow_definition(
                owner_id=owner_id,
                name=definition_name,
                description=f"Generated from template: {template.name}",
                nodes=nodes,
                edges=edges,
                metadata={
                    "generated_from_template": template_id,
                    "template_name": template.name,
                    "user_input": user_input,
                    "is_temporary": is_temporary,
                    "required_tools": template.required_tools,
                    "required_retrievers": template.required_retrievers,
                },
                template_id=template_id,
            )

            logger.info(
                f"Created workflow definition {definition.id} from template {template_id}"
            )

            return definition

        except Exception as e:
            logger.error(
                f"Failed to create workflow definition from template {template_id}: {e}"
            )
            raise

    async def create_workflow_definition_from_template_data(
        self,
        template_data: dict[str, Any],
        owner_id: str,
        user_input: dict[str, Any] | None = None,
        is_temporary: bool = True,
    ) -> WorkflowDefinition:
        """Create a workflow definition from template data without persisting the template.

        Args:
            template_data: Template data dictionary
            owner_id: ID of the user creating the definition
            user_input: Optional user input to merge with template params
            is_temporary: Whether this is a temporary definition for execution

        Returns:
            Created workflow definition

        Raises:
            BadRequestProblem: If template data is invalid
        """
        try:
            from chatter.utils.problem import BadRequestProblem

            # Validate required fields
            required_fields = ["name", "description"]
            for field in required_fields:
                if field not in template_data:
                    raise BadRequestProblem(
                        detail=f"Missing required field in template: {field}"
                    )

            # Create a temporary template object for workflow generation
            # This is not persisted to the database
            class TemporaryTemplate:
                """Temporary template object for workflow generation."""
                def __init__(self, data: dict[str, Any]):
                    self.name = data.get("name", "Temporary Template")
                    self.description = data.get("description", "")
                    self.category = data.get("category", "custom")
                    self.default_params = data.get("default_params", {})
                    self.required_tools = data.get("required_tools")
                    self.required_retrievers = data.get("required_retrievers")
                    self.tags = data.get("tags")
                    self.is_public = data.get("is_public", False)

            temp_template = TemporaryTemplate(template_data)

            # Create name for the definition
            definition_name = f"{temp_template.name}"
            if is_temporary:
                definition_name += " (Execution)"

            # Merge template default params with user input
            merged_input = {**(temp_template.default_params or {})}
            if user_input:
                merged_input.update(user_input)

            # Generate workflow structure based on template
            nodes, edges = self._generate_workflow_from_template(
                temp_template, merged_input
            )

            # Create the workflow definition
            definition = await self.create_workflow_definition(
                owner_id=owner_id,
                name=definition_name,
                description=f"Generated from temporary template: {temp_template.name}",
                nodes=nodes,
                edges=edges,
                metadata={
                    "generated_from_template_data": True,
                    "template_name": temp_template.name,
                    "user_input": user_input,
                    "is_temporary": is_temporary,
                    "required_tools": temp_template.required_tools,
                    "required_retrievers": temp_template.required_retrievers,
                },
                template_id=None,
            )

            logger.info(
                f"Created workflow definition {definition.id} from temporary template data"
            )

            return definition

        except BadRequestProblem:
            raise
        except Exception as e:
            logger.error(
                f"Failed to create workflow definition from template data: {e}"
            )
            raise

    def _generate_workflow_from_template(
        self,
        template: "WorkflowTemplate",
        input_params: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Generate workflow nodes and edges from a template using capability-based approach.

        This creates a workflow structure based on the template's configuration
        rather than hardcoded workflow types.

        Args:
            template: The workflow template
            input_params: Merged input parameters

        Returns:
            Tuple of (nodes, edges) for the workflow
        """
        from chatter.core.workflow_template_generator import (
            workflow_template_generator,
        )

        # Delegate to the centralized template generator
        return (
            workflow_template_generator.generate_workflow_from_template(
                template, input_params
            )
        )

    async def export_workflow_template(
        self, template_id: str, owner_id: str
    ) -> dict[str, Any] | None:
        """Export a workflow template to JSON format.

        Args:
            template_id: Template ID to export
            owner_id: Owner user ID

        Returns:
            Template data as dictionary, or None if not found
        """
        try:
            template = await self.get_workflow_template(
                template_id=template_id, owner_id=owner_id
            )

            if not template:
                return None

            # Export template with all metadata
            export_data = {
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "default_params": template.default_params,
                "required_tools": template.required_tools,
                "required_retrievers": template.required_retrievers,
                "tags": template.tags,
                "is_public": template.is_public,
                "version": template.version,
                "metadata": {
                    "config_hash": template.config_hash,
                    "estimated_complexity": template.estimated_complexity,
                    "export_version": "1.0",
                },
            }

            logger.info(
                f"Exported workflow template {template_id}",
                template_name=template.name,
            )

            return export_data

        except Exception as e:
            logger.error(
                f"Failed to export workflow template {template_id}: {e}"
            )
            raise

    async def import_workflow_template(
        self,
        template_data: dict[str, Any],
        owner_id: str,
        override_name: str | None = None,
        merge_with_existing: bool = False,
    ) -> WorkflowTemplate:
        """Import a workflow template from JSON format.

        Args:
            template_data: Template data to import
            owner_id: Owner user ID
            override_name: Optional name override
            merge_with_existing: Whether to merge with existing template

        Returns:
            Imported workflow template
        """
        try:
            # Validate required fields
            required_fields = ["name", "description", "category"]
            missing_fields = [
                field
                for field in required_fields
                if field not in template_data
            ]
            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )

            # Use override name if provided
            name = override_name or template_data["name"]

            # Check if template with same name exists
            if merge_with_existing:
                stmt = select(WorkflowTemplate).where(
                    and_(
                        WorkflowTemplate.owner_id == owner_id,
                        WorkflowTemplate.name == name,
                    )
                )
                result = await self.session.execute(stmt)
                existing_template = result.scalar_one_or_none()

                if existing_template:
                    # Update existing template
                    existing_template.description = template_data[
                        "description"
                    ]
                    existing_template.category = TemplateCategory(
                        template_data["category"]
                    )
                    existing_template.default_params = template_data.get(
                        "default_params", {}
                    )
                    existing_template.required_tools = template_data.get(
                        "required_tools"
                    )
                    existing_template.required_retrievers = (
                        template_data.get("required_retrievers")
                    )
                    existing_template.tags = template_data.get("tags")
                    existing_template.is_public = template_data.get(
                        "is_public", False
                    )
                    existing_template.version += 1

                    await self.session.commit()
                    await self.session.refresh(existing_template)

                    logger.info(
                        f"Updated existing workflow template {existing_template.id}",
                        template_name=name,
                    )

                    return existing_template

            # Create new template
            template = WorkflowTemplate(
                owner_id=owner_id,
                name=name,
                description=template_data["description"],
                category=TemplateCategory(template_data["category"]),
                default_params=template_data.get("default_params", {}),
                required_tools=template_data.get("required_tools"),
                required_retrievers=template_data.get("required_retrievers"),
                tags=template_data.get("tags"),
                is_public=template_data.get("is_public", False),
                version=1,
            )

            self.session.add(template)
            await self.session.commit()
            await self.session.refresh(template)

            logger.info(
                f"Imported new workflow template {template.id}",
                template_name=name,
            )

            return template

        except Exception as e:
            await self.session.rollback()
            logger.error(f"Failed to import workflow template: {e}")
            raise

    async def validate_workflow_template(
        self, template_data: dict[str, Any], owner_id: str
    ) -> dict[str, Any]:
        """Validate a workflow template using the unified validator.

        Phase 5: Now uses WorkflowValidator orchestrator with template-specific
        validation rules.

        Args:
            template_data: Template data to validate
            owner_id: Owner user ID

        Returns:
            Validation result dictionary
        """
        try:
            from chatter.core.workflow_validator import WorkflowValidator
            
            validator = WorkflowValidator()
            
            # Use template-specific validation
            validation_result = await validator.validate_template(
                template_data=template_data,
                user_id=owner_id,
            )
            
            # Check for duplicate name
            warnings = list(validation_result.warnings) if hasattr(validation_result, 'warnings') else []
            if "name" in template_data:
                stmt = select(WorkflowTemplate).where(
                    and_(
                        WorkflowTemplate.owner_id == owner_id,
                        WorkflowTemplate.name == template_data["name"],
                    )
                )
                result = await self.session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    warnings.append(
                        f"Template with name '{template_data['name']}' already exists"
                    )
            
            # Build response
            response = validation_result.to_api_response()
            
            # Add warnings if we found duplicate
            if warnings:
                response["warnings"] = warnings
            
            # Add template info if valid
            if validation_result.is_valid:
                template_info = {}
                for field in ["name", "description", "category", "tags"]:
                    if field in template_data:
                        template_info[field] = template_data[field]
                response["template_info"] = template_info
            
            # Ensure backward compatibility with is_valid key
            if "valid" in response and "is_valid" not in response:
                response["is_valid"] = response["valid"]
            
            return response

        except Exception as e:
            logger.error(f"Error during template validation: {e}")
            return {
                "is_valid": False,
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "warnings": [],
                "template_info": None,
            }
