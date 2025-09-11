"""Workflow management service for CRUD operations on workflows and templates."""

import hashlib
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.core.workflow_validation import workflow_validation_service
from chatter.models.workflow import (
    TemplateCategory,
    WorkflowDefinition,
    WorkflowExecution,
    WorkflowTemplate,
    WorkflowType,
)
from chatter.schemas.workflows import ValidationError
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


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
            from chatter.core.cache_factory import get_persistent_cache

            workflow_cache = get_persistent_cache()

            if workflow_id:
                # For now, we don't have a way to invalidate specific workflows
                # So we clear all workflows when any workflow changes
                await workflow_cache.clear()
                logger.debug(
                    "Invalidated workflow cache for workflow",
                    workflow_id=workflow_id,
                )
            else:
                await workflow_cache.clear()
                logger.debug("Invalidated all workflow caches")

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
        """Create a new workflow definition."""
        try:
            # Validate the workflow definition
            definition_data = {
                "name": name,
                "description": description,
                "nodes": nodes,
                "edges": edges,
                "metadata": metadata or {},
            }

            validation_result = workflow_validation_service.validate_workflow_definition(
                definition_data, owner_id
            )

            if not validation_result.valid:
                from chatter.utils.problem import BadRequestProblem

                raise BadRequestProblem(
                    detail=f"Workflow validation failed: {'; '.join(validation_result.errors)}"
                )

            # Log warnings if any
            if validation_result.warnings:
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
            return result.scalar_one_or_none()

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
        definition_id: str,
        owner_id: str,
        input_data: dict[str, Any] | None = None,
    ) -> WorkflowExecution:
        """Create a new workflow execution."""
        try:
            execution = WorkflowExecution(
                definition_id=definition_id,
                owner_id=owner_id,
                input_data=input_data or {},
                status="pending",
            )

            self.session.add(execution)
            await self.session.commit()
            await self.session.refresh(execution)

            logger.info(
                f"Created workflow execution {execution.id} for definition {definition_id}"
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

    # Validation methods
    async def validate_workflow_definition(
        self,
        definition_data: dict[str, Any],
        owner_id: str,
    ) -> dict[str, Any]:
        """Validate a workflow definition and return validation results."""
        try:
            validation_result = workflow_validation_service.validate_workflow_definition(
                definition_data, owner_id
            )

            return {
                "valid": validation_result.valid,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "requirements_met": validation_result.requirements_met,
            }

        except Exception as e:
            logger.error(f"Failed to validate workflow definition: {e}")
            raise

    # Template CRUD
    async def create_workflow_template(
        self,
        owner_id: str,
        name: str,
        description: str,
        workflow_type: str,
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
            # Map workflow type
            workflow_type_enum = WorkflowType(workflow_type)
            category_enum = TemplateCategory(category)

            # Generate config hash
            config_str = (
                f"{name}:{workflow_type}:{str(default_params or {})}"
            )
            config_hash = hashlib.sha256(
                config_str.encode("utf-8")
            ).hexdigest()

            # Create template
            template = WorkflowTemplate(
                owner_id=owner_id,
                name=name,
                description=description,
                workflow_type=workflow_type_enum,
                category=category_enum,
                default_params=default_params or {},
                required_tools=required_tools,
                required_retrievers=required_retrievers,
                base_template_id=base_template_id,
                is_public=is_public,
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
                config_str = f"{template.name}:{template.workflow_type.value}:{str(template.default_params)}"
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

    # Validation
    async def validate_workflow_structure(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Validate a workflow definition."""
        try:
            errors = []
            warnings = []
            suggestions = []

            # Basic validation
            if not nodes:
                errors.append(
                    ValidationError(
                        type="missing_nodes",
                        message="Workflow must have at least one node",
                        severity="error",
                    )
                )

            # Check for start node
            start_nodes = [
                node
                for node in nodes
                if node.get("data", {}).get("nodeType") == "start"
            ]
            if not start_nodes:
                errors.append(
                    ValidationError(
                        type="missing_start_node",
                        message="Workflow must have a start node",
                        severity="error",
                    )
                )
            elif len(start_nodes) > 1:
                errors.append(
                    ValidationError(
                        type="multiple_start_nodes",
                        message="Workflow can only have one start node",
                        severity="error",
                    )
                )

            # Validate node references in edges
            node_ids = {node["id"] for node in nodes}
            for edge in edges:
                if edge["source"] not in node_ids:
                    errors.append(
                        ValidationError(
                            type="invalid_edge_source",
                            message=f"Edge source '{edge['source']}' references non-existent node",
                            edge_id=edge["id"],
                            severity="error",
                        )
                    )
                if edge["target"] not in node_ids:
                    errors.append(
                        ValidationError(
                            type="invalid_edge_target",
                            message=f"Edge target '{edge['target']}' references non-existent node",
                            edge_id=edge["id"],
                            severity="error",
                        )
                    )

            # Check for orphaned nodes (except start)
            connected_nodes = set()
            for edge in edges:
                connected_nodes.add(edge["source"])
                connected_nodes.add(edge["target"])

            for node in nodes:
                if (
                    node["id"] not in connected_nodes
                    and node.get("data", {}).get("nodeType") != "start"
                ):
                    warnings.append(
                        ValidationError(
                            type="orphaned_node",
                            message=f"Node '{node['id']}' is not connected to any other nodes",
                            node_id=node["id"],
                            severity="warning",
                        )
                    )

            # Performance suggestions
            if len(nodes) > 20:
                suggestions.append(
                    "Consider breaking down large workflows into smaller, reusable components"
                )

            # Check for potential infinite loops
            loop_nodes = [
                node
                for node in nodes
                if node.get("data", {}).get("nodeType") == "loop"
            ]
            for loop_node in loop_nodes:
                loop_config = loop_node.get("data", {}).get(
                    "config", {}
                )
                if not loop_config.get(
                    "maxIterations"
                ) and not loop_config.get("condition"):
                    warnings.append(
                        ValidationError(
                            type="potential_infinite_loop",
                            message=f"Loop node '{loop_node['id']}' may cause infinite loop without max iterations or exit condition",
                            node_id=loop_node["id"],
                            severity="warning",
                        )
                    )

            return {
                "is_valid": len(errors) == 0,
                "errors": [error.model_dump() for error in errors],
                "warnings": [
                    warning.model_dump() for warning in warnings
                ],
                "suggestions": suggestions,
            }

        except Exception as e:
            logger.error(f"Failed to validate workflow definition: {e}")
            raise
