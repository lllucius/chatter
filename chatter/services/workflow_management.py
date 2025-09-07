"""Workflow management service for CRUD operations on workflows and templates."""

import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.workflow import WorkflowTemplate, TemplateCategory, WorkflowType
from chatter.schemas.workflows import (
    WorkflowNode,
    WorkflowEdge,
    ValidationError,
)
from chatter.utils.database import generate_id
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowDefinition:
    """Simple workflow definition class for database-free operations."""
    
    def __init__(
        self,
        id: str,
        owner_id: str,
        name: str,
        description: Optional[str],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        version: int = 1,
        is_public: bool = False,
        tags: Optional[List[str]] = None,
    ):
        self.id = id
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.nodes = nodes
        self.edges = edges
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.version = version
        self.is_public = is_public
        self.tags = tags or []


class WorkflowManagementService:
    """Service for managing workflow definitions and templates."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self._in_memory_definitions: Dict[str, WorkflowDefinition] = {}
    
    # Workflow Definition CRUD
    async def create_workflow_definition(
        self,
        owner_id: str,
        name: str,
        description: Optional[str],
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> WorkflowDefinition:
        """Create a new workflow definition."""
        try:
            # Generate unique ID
            workflow_id = generate_id()
            
            # Create workflow definition
            definition = WorkflowDefinition(
                id=workflow_id,
                owner_id=owner_id,
                name=name,
                description=description,
                nodes=nodes,
                edges=edges,
                metadata=metadata,
            )
            
            # Store in memory (since we don't have a WorkflowDefinition model yet)
            self._in_memory_definitions[workflow_id] = definition
            
            logger.info(f"Created workflow definition {workflow_id} for user {owner_id}")
            return definition
            
        except Exception as e:
            logger.error(f"Failed to create workflow definition: {e}")
            raise
    
    async def get_workflow_definition(
        self,
        workflow_id: str,
        owner_id: str,
    ) -> Optional[WorkflowDefinition]:
        """Get a workflow definition by ID."""
        try:
            # Check in-memory storage
            definition = self._in_memory_definitions.get(workflow_id)
            if definition and (definition.owner_id == owner_id or definition.is_public):
                return definition
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get workflow definition {workflow_id}: {e}")
            raise
    
    async def list_workflow_definitions(
        self,
        owner_id: str,
    ) -> List[WorkflowDefinition]:
        """List workflow definitions for a user."""
        try:
            # Return definitions owned by user or public ones
            definitions = [
                definition for definition in self._in_memory_definitions.values()
                if definition.owner_id == owner_id or definition.is_public
            ]
            
            return definitions
            
        except Exception as e:
            logger.error(f"Failed to list workflow definitions for user {owner_id}: {e}")
            raise
    
    async def update_workflow_definition(
        self,
        workflow_id: str,
        owner_id: str,
        **updates
    ) -> Optional[WorkflowDefinition]:
        """Update a workflow definition."""
        try:
            # Check if definition exists and user has access
            definition = self._in_memory_definitions.get(workflow_id)
            if not definition or definition.owner_id != owner_id:
                return None
            
            # Update fields
            for field, value in updates.items():
                if hasattr(definition, field):
                    setattr(definition, field, value)
            
            definition.updated_at = datetime.utcnow()
            definition.version += 1
            
            logger.info(f"Updated workflow definition {workflow_id}")
            return definition
            
        except Exception as e:
            logger.error(f"Failed to update workflow definition {workflow_id}: {e}")
            raise
    
    async def delete_workflow_definition(
        self,
        workflow_id: str,
        owner_id: str,
    ) -> bool:
        """Delete a workflow definition."""
        try:
            # Check if definition exists and user has access
            definition = self._in_memory_definitions.get(workflow_id)
            if not definition or definition.owner_id != owner_id:
                return False
            
            # Delete from in-memory storage
            del self._in_memory_definitions[workflow_id]
            
            logger.info(f"Deleted workflow definition {workflow_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workflow definition {workflow_id}: {e}")
            raise
    
    # Template CRUD
    async def create_workflow_template(
        self,
        owner_id: str,
        name: str,
        description: str,
        workflow_type: str,
        category: str = "custom",
        default_params: Optional[Dict[str, Any]] = None,
        required_tools: Optional[List[str]] = None,
        required_retrievers: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_public: bool = False,
        workflow_definition_id: Optional[str] = None,
        base_template_id: Optional[str] = None,
    ) -> WorkflowTemplate:
        """Create a new workflow template."""
        try:
            # Map workflow type
            workflow_type_enum = WorkflowType(workflow_type)
            category_enum = TemplateCategory(category)
            
            # Generate config hash
            config_str = f"{name}:{workflow_type}:{str(default_params or {})}"
            config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()
            
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
            
            logger.info(f"Created workflow template {template.id} for user {owner_id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to create workflow template: {e}")
            await self.session.rollback()
            raise
    
    async def list_workflow_templates(
        self,
        owner_id: str,
    ) -> List[WorkflowTemplate]:
        """List workflow templates accessible to a user."""
        try:
            query = select(WorkflowTemplate).where(
                or_(
                    WorkflowTemplate.owner_id == owner_id,
                    WorkflowTemplate.is_public == True,
                    WorkflowTemplate.is_builtin == True,
                )
            ).options(
                selectinload(WorkflowTemplate.owner)
            ).order_by(
                WorkflowTemplate.is_builtin.desc(),
                WorkflowTemplate.usage_count.desc(),
                WorkflowTemplate.created_at.desc(),
            )
            
            result = await self.session.execute(query)
            templates = result.scalars().all()
            
            return list(templates)
            
        except Exception as e:
            logger.error(f"Failed to list workflow templates for user {owner_id}: {e}")
            raise
    
    async def get_workflow_template(
        self,
        template_id: str,
        owner_id: Optional[str] = None,
    ) -> Optional[WorkflowTemplate]:
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
                        WorkflowTemplate.is_public == True,
                        WorkflowTemplate.is_builtin == True,
                    )
                )
            
            result = await self.session.execute(query)
            template = result.scalar_one_or_none()
            
            return template
            
        except Exception as e:
            logger.error(f"Failed to get workflow template {template_id}: {e}")
            raise
    
    async def update_workflow_template(
        self,
        template_id: str,
        owner_id: str,
        **updates
    ) -> Optional[WorkflowTemplate]:
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
            if 'default_params' in updates:
                config_str = f"{template.name}:{template.workflow_type.value}:{str(template.default_params)}"
                template.config_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()
            
            await self.session.commit()
            await self.session.refresh(template)
            
            logger.info(f"Updated workflow template {template_id}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to update workflow template {template_id}: {e}")
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
            logger.error(f"Failed to delete workflow template {template_id}: {e}")
            await self.session.rollback()
            raise
    
    # Validation
    async def validate_workflow_definition(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Validate a workflow definition."""
        try:
            errors = []
            warnings = []
            suggestions = []
            
            # Basic validation
            if not nodes:
                errors.append(ValidationError(
                    type="missing_nodes",
                    message="Workflow must have at least one node",
                    severity="error"
                ))
            
            # Check for start node
            start_nodes = [node for node in nodes if node.get("data", {}).get("nodeType") == "start"]
            if not start_nodes:
                errors.append(ValidationError(
                    type="missing_start_node",
                    message="Workflow must have a start node",
                    severity="error"
                ))
            elif len(start_nodes) > 1:
                errors.append(ValidationError(
                    type="multiple_start_nodes",
                    message="Workflow can only have one start node",
                    severity="error"
                ))
            
            # Validate node references in edges
            node_ids = {node["id"] for node in nodes}
            for edge in edges:
                if edge["source"] not in node_ids:
                    errors.append(ValidationError(
                        type="invalid_edge_source",
                        message=f"Edge source '{edge['source']}' references non-existent node",
                        edge_id=edge["id"],
                        severity="error"
                    ))
                if edge["target"] not in node_ids:
                    errors.append(ValidationError(
                        type="invalid_edge_target",
                        message=f"Edge target '{edge['target']}' references non-existent node",
                        edge_id=edge["id"],
                        severity="error"
                    ))
            
            # Check for orphaned nodes (except start)
            connected_nodes = set()
            for edge in edges:
                connected_nodes.add(edge["source"])
                connected_nodes.add(edge["target"])
            
            for node in nodes:
                if node["id"] not in connected_nodes and node.get("data", {}).get("nodeType") != "start":
                    warnings.append(ValidationError(
                        type="orphaned_node",
                        message=f"Node '{node['id']}' is not connected to any other nodes",
                        node_id=node["id"],
                        severity="warning"
                    ))
            
            # Performance suggestions
            if len(nodes) > 20:
                suggestions.append("Consider breaking down large workflows into smaller, reusable components")
            
            # Check for potential infinite loops
            loop_nodes = [node for node in nodes if node.get("data", {}).get("nodeType") == "loop"]
            for loop_node in loop_nodes:
                loop_config = loop_node.get("data", {}).get("config", {})
                if not loop_config.get("maxIterations") and not loop_config.get("condition"):
                    warnings.append(ValidationError(
                        type="potential_infinite_loop",
                        message=f"Loop node '{loop_node['id']}' may cause infinite loop without max iterations or exit condition",
                        node_id=loop_node["id"],
                        severity="warning"
                    ))
            
            return {
                "is_valid": len(errors) == 0,
                "errors": [error.model_dump() for error in errors],
                "warnings": [warning.model_dump() for warning in warnings],
                "suggestions": suggestions,
            }
            
        except Exception as e:
            logger.error(f"Failed to validate workflow definition: {e}")
            raise
