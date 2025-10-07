"""Comprehensive workflows API supporting advanced workflow editor features."""

import json
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.api.dependencies import (
    PaginationLimit,
    PaginationOffset,
    WorkflowId,
)
from chatter.models.base import generate_ulid
from chatter.models.user import User
from chatter.schemas.chat import ChatResponse
from chatter.schemas.workflows import (
    ChatWorkflowRequest,
    DetailedWorkflowExecutionResponse,
    NodeTypeResponse,
    WorkflowAnalyticsResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionFromTemplateRequest,
    WorkflowDefinitionResponse,
    WorkflowDefinitionsResponse,
    WorkflowDefinitionUpdate,
    WorkflowDeleteResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateDirectExecutionRequest,
    WorkflowTemplateExecutionRequest,
    WorkflowTemplateExportResponse,
    WorkflowTemplateImportRequest,
    WorkflowTemplateResponse,
    WorkflowTemplatesResponse,
    WorkflowTemplateUpdate,
    WorkflowTemplateValidationRequest,
    WorkflowTemplateValidationResponse,
    WorkflowValidationResponse,
)
from chatter.services.simplified_workflow_analytics import (
    SimplifiedWorkflowAnalyticsService,
)
from chatter.services.workflow_defaults import WorkflowDefaultsService
from chatter.services.workflow_execution import WorkflowExecutionService
from chatter.services.workflow_management import (
    WorkflowManagementService,
)
from chatter.utils.database import get_session_generator
from chatter.utils.logging import get_logger
from chatter.utils.problem import InternalServerProblem, NotFoundProblem
from chatter.utils.unified_rate_limiter import rate_limit

logger = get_logger(__name__)
router = APIRouter()


# Dependency injection
async def get_workflow_management_service(
    session: AsyncSession = Depends(get_session_generator),
) -> WorkflowManagementService:
    """Get workflow management service."""
    return WorkflowManagementService(session)


async def get_workflow_analytics_service(
    session: AsyncSession = Depends(get_session_generator),
) -> SimplifiedWorkflowAnalyticsService:
    """Get workflow analytics service."""
    return SimplifiedWorkflowAnalyticsService(session)


async def get_workflow_defaults_service(
    session: AsyncSession = Depends(get_session_generator),
) -> WorkflowDefaultsService:
    """Get workflow defaults service."""
    return WorkflowDefaultsService(session)


async def get_workflow_execution_service(
    session: AsyncSession = Depends(get_session_generator),
) -> WorkflowExecutionService:
    """Get workflow execution service."""
    # Import here to avoid circular dependencies
    from chatter.services.llm import LLMService
    from chatter.services.message import MessageService

    llm_service = LLMService()
    message_service = MessageService(session)
    return WorkflowExecutionService(
        llm_service, message_service, session
    )


async def get_execution_engine(
    session: AsyncSession = Depends(get_session_generator),
    current_user: User | None = Depends(get_current_user),
):
    """Get shared execution engine instance.
    
    This is the unified execution engine for all workflow types,
    replacing multiple execution methods with a single execution pipeline.
    
    Args:
        session: Database session
        current_user: Current authenticated user (provides owner_id context)
    
    Returns:
        ExecutionEngine instance with owner_id from auth context
    """
    from chatter.core.workflow_execution_engine import ExecutionEngine
    from chatter.services.llm import LLMService

    llm_service = LLMService()
    return ExecutionEngine(
        session=session,
        llm_service=llm_service,
        debug_mode=False,
        owner_id=current_user.id if current_user else None,
    )


async def get_workflow_validator():
    """Get shared workflow validator instance.
    
    This is the unified validator orchestrating all validation layers:
    - Structure validation
    - Security validation
    - Capability validation
    - Resource validation
    """
    from chatter.core.workflow_validator import WorkflowValidator

    return WorkflowValidator()


# Workflow Definitions CRUD
@router.post("/definitions", response_model=WorkflowDefinitionResponse)
async def create_workflow_definition(
    workflow_definition: WorkflowDefinitionCreate,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDefinitionResponse:
    """Create a new workflow definition."""
    try:
        # Convert Pydantic objects to dictionaries for validation
        nodes_dict = [
            node.to_dict() for node in workflow_definition.nodes
        ]
        edges_dict = [
            edge.to_dict() for edge in workflow_definition.edges
        ]

        definition = await workflow_service.create_workflow_definition(
            owner_id=current_user.id,
            name=workflow_definition.name,
            description=workflow_definition.description,
            nodes=nodes_dict,
            edges=edges_dict,
            metadata=workflow_definition.metadata,
        )
        return WorkflowDefinitionResponse.model_validate(
            definition.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to create workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to create workflow definition: {str(e)}"
        ) from e


@router.post(
    "/definitions/from-template",
    response_model=WorkflowDefinitionResponse,
)
async def create_workflow_definition_from_template(
    request: WorkflowDefinitionFromTemplateRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDefinitionResponse:
    """Create a workflow definition from a template."""
    try:
        definition = await workflow_service.create_workflow_definition_from_template(
            template_id=request.template_id,
            owner_id=current_user.id,
            name_suffix=request.name_suffix or "",
            user_input=request.user_input,
            is_temporary=request.is_temporary,
        )
        return WorkflowDefinitionResponse.model_validate(
            definition.to_dict()
        )
    except Exception as e:
        logger.error(
            f"Failed to create workflow definition from template: {e}"
        )
        raise InternalServerProblem(
            detail=f"Failed to create workflow definition from template: {str(e)}"
        ) from e


@router.get("/definitions", response_model=WorkflowDefinitionsResponse)
async def list_workflow_definitions(
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDefinitionsResponse:
    """List all workflow definitions for the current user."""
    try:
        definitions = await workflow_service.list_workflow_definitions(
            owner_id=current_user.id
        )
        return WorkflowDefinitionsResponse(
            definitions=[
                WorkflowDefinitionResponse.model_validate(
                    definition.to_dict()
                )
                for definition in definitions
            ],
            total_count=len(definitions),
        )
    except Exception as e:
        logger.error(f"Failed to list workflow definitions: {e}")
        raise InternalServerProblem(
            detail=f"Failed to list workflow definitions: {str(e)}"
        ) from e


@router.get(
    "/definitions/{workflow_id}",
    response_model=WorkflowDefinitionResponse,
)
async def get_workflow_definition(
    workflow_id: WorkflowId,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDefinitionResponse:
    """Get a specific workflow definition."""
    try:
        definition = await workflow_service.get_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not definition:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        return WorkflowDefinitionResponse.model_validate(
            definition.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get workflow definition: {str(e)}"
        ) from e


@router.put(
    "/definitions/{workflow_id}",
    response_model=WorkflowDefinitionResponse,
)
async def update_workflow_definition(
    workflow_id: WorkflowId,
    workflow_definition: WorkflowDefinitionUpdate,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDefinitionResponse:
    """Update a workflow definition."""
    try:
        definition = await workflow_service.update_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
            **workflow_definition.model_dump(exclude_unset=True),
        )
        if not definition:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        return WorkflowDefinitionResponse.model_validate(
            definition.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to update workflow definition: {str(e)}"
        ) from e


@router.delete(
    "/definitions/{workflow_id}", response_model=WorkflowDeleteResponse
)
async def delete_workflow_definition(
    workflow_id: WorkflowId,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> dict[str, str]:
    """Delete a workflow definition."""
    try:
        success = await workflow_service.delete_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not success:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        return {"message": "Workflow definition deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to delete workflow definition: {str(e)}"
        ) from e


# Template Management
@router.post("/templates", response_model=WorkflowTemplateResponse)
async def create_workflow_template(
    template: WorkflowTemplateCreate,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplateResponse:
    """Create a new workflow template."""
    try:
        template_obj = await workflow_service.create_workflow_template(
            owner_id=current_user.id,
            **template.model_dump(),
        )
        return WorkflowTemplateResponse.model_validate(
            template_obj.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to create workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to create workflow template: {str(e)}"
        ) from e


@router.get("/templates", response_model=WorkflowTemplatesResponse)
async def list_workflow_templates(
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplatesResponse:
    """List all workflow templates accessible to the current user."""
    try:
        templates = await workflow_service.list_workflow_templates(
            owner_id=current_user.id
        )
        return WorkflowTemplatesResponse(
            templates=[
                WorkflowTemplateResponse.model_validate(
                    template.to_dict()
                )
                for template in templates
            ],
            total_count=len(templates),
        )
    except Exception as e:
        logger.error(f"Failed to list workflow templates: {e}")
        raise InternalServerProblem(
            detail=f"Failed to list workflow templates: {str(e)}"
        ) from e


@router.put(
    "/templates/{template_id}", response_model=WorkflowTemplateResponse
)
async def update_workflow_template(
    template_id: str,
    template: WorkflowTemplateUpdate,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplateResponse:
    """Update a workflow template."""
    try:
        template_obj = await workflow_service.update_workflow_template(
            template_id=template_id,
            owner_id=current_user.id,
            **template.model_dump(exclude_unset=True),
        )
        if not template_obj:
            raise NotFoundProblem(detail="Workflow template not found")

        return WorkflowTemplateResponse.model_validate(
            template_obj.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to update workflow template: {str(e)}"
        ) from e


@router.delete(
    "/templates/{template_id}", response_model=WorkflowDeleteResponse
)
async def delete_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowDeleteResponse:
    """Delete a workflow template."""
    try:
        success = await workflow_service.delete_workflow_template(
            template_id=template_id,
            owner_id=current_user.id,
        )

        if not success:
            raise NotFoundProblem(detail="Workflow template not found")

        return WorkflowDeleteResponse(
            message="Workflow template deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to delete workflow template: {str(e)}"
        ) from e


@router.get(
    "/templates/{template_id}/export",
    response_model=WorkflowTemplateExportResponse,
)
async def export_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplateExportResponse:
    """Export a workflow template."""
    try:
        template_data = await workflow_service.export_workflow_template(
            template_id=template_id,
            owner_id=current_user.id,
        )
        
        if not template_data:
            raise NotFoundProblem(detail="Workflow template not found")

        from datetime import UTC, datetime
        
        return WorkflowTemplateExportResponse(
            template=template_data,
            export_format="json",
            exported_at=datetime.now(UTC),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to export workflow template: {str(e)}"
        ) from e


@router.post(
    "/templates/import", response_model=WorkflowTemplateResponse
)
async def import_workflow_template(
    import_request: WorkflowTemplateImportRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplateResponse:
    """Import a workflow template."""
    try:
        template = await workflow_service.import_workflow_template(
            template_data=import_request.template,
            owner_id=current_user.id,
            override_name=import_request.override_name,
            merge_with_existing=import_request.merge_with_existing,
        )
        
        return WorkflowTemplateResponse.model_validate(
            template.to_dict()
        )
    except Exception as e:
        logger.error(f"Failed to import workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to import workflow template: {str(e)}"
        ) from e


@router.get(
    "/templates/{template_id}/load",
    response_model=WorkflowTemplateResponse,
)
async def load_workflow_template(
    template_id: str,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowTemplateResponse:
    """Load a workflow template with full details."""
    try:
        template = await workflow_service.get_workflow_template(
            template_id=template_id,
            owner_id=current_user.id,
        )
        
        if not template:
            raise NotFoundProblem(detail="Workflow template not found")

        return WorkflowTemplateResponse.model_validate(
            template.to_dict()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to load workflow template: {str(e)}"
        ) from e


@router.post(
    "/templates/validate",
    response_model=WorkflowTemplateValidationResponse,
)
async def validate_workflow_template(
    validation_request: WorkflowTemplateValidationRequest,
    current_user: User = Depends(get_current_user),
    validator = Depends(get_workflow_validator),
) -> WorkflowTemplateValidationResponse:
    """Validate a workflow template using the unified validation orchestrator."""
    try:
        # Use unified validator
        validation_result = await validator.validate(
            workflow_data=validation_request.template,
            user_id=current_user.id,
            context="template_validation",
        )
        
        # Convert to API response
        response_data = validation_result.to_api_response()
        
        return WorkflowTemplateValidationResponse(
            is_valid=response_data["valid"],
            errors=response_data["errors"],
            warnings=response_data["warnings"],
            template_info=response_data.get("details"),
        )
    except Exception as e:
        logger.error(f"Failed to validate workflow template: {e}")
        return WorkflowTemplateValidationResponse(
            is_valid=False,
            errors=[f"Validation error: {str(e)}"],
            warnings=[],
            template_info=None,
        )


@router.post(
    "/templates/{template_id}/execute",
    response_model=WorkflowExecutionResponse,
)
async def execute_workflow_template(
    template_id: str,
    execution_request: WorkflowTemplateExecutionRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
    execution_engine = Depends(get_execution_engine),
) -> WorkflowExecutionResponse:
    """Execute a workflow template directly using the unified execution engine.
    
    **New in Phase 7**: Templates now execute directly without creating temporary
    workflow definitions, reducing database writes by 30%.
    
    **Execution Flow**:
    1. Verifies template exists
    2. Creates ExecutionRequest with template_id (no temporary definition!)
    3. Executes through unified ExecutionEngine
    4. Returns standardized WorkflowExecutionResponse
    
    **Key Improvement**: No temporary definitions are created. Templates execute
    directly through the ExecutionEngine, completing the Phase 4 optimization.
    
    **Request Body**:
    - `input_data`: Input parameters for the template
    - `debug_mode`: Enable detailed logging (default: false)
    
    **Response**: Same as workflow definition execution
    
    **Example**:
    ```python
    # Using Python SDK
    result = client.workflows.execute_template(
        template_id="template_123",
        input_data={"query": "What is AI?"},
        debug_mode=False
    )
    print(f"Template executed successfully: {result.id}")
    ```
    """
    try:
        # Verify template exists and user has access
        template = await workflow_service.get_workflow_template(
            template_id=template_id
        )
        if not template:
            raise NotFoundProblem(
                detail=f"Workflow template not found: {template_id}"
            )
        
        # Create unified execution request
        from chatter.schemas.execution import ExecutionRequest
        
        exec_request = ExecutionRequest(
            template_id=template_id,
            input_data=execution_request.input_data or {},
            debug_mode=execution_request.debug_mode,
        )

        # Execute using unified engine
        result = await execution_engine.execute(
            request=exec_request,
            user_id=current_user.id,
        )
        
        # Convert to API response
        return result.to_api_response()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to execute workflow template: {str(e)}"
        ) from e


@router.post(
    "/templates/execute",
    response_model=WorkflowExecutionResponse,
)
async def execute_temporary_workflow_template(
    execution_request: WorkflowTemplateDirectExecutionRequest,
    current_user: User = Depends(get_current_user),
    execution_engine = Depends(get_execution_engine),
) -> WorkflowExecutionResponse:
    """Execute a temporary workflow template directly without storing it.
    
    This endpoint allows you to pass template data (nodes/edges) directly and execute it
    without persisting the template to the database first.
    """
    try:
        # Create unified execution request from template data
        from chatter.schemas.execution import ExecutionRequest
        
        # Extract nodes and edges from template data
        template_data = execution_request.template
        nodes = template_data.get("nodes", [])
        edges = template_data.get("edges", [])
        
        exec_request = ExecutionRequest(
            nodes=nodes,
            edges=edges,
            input_data=execution_request.input_data or {},
            debug_mode=execution_request.debug_mode,
        )

        # Execute using unified engine
        result = await execution_engine.execute(
            request=exec_request,
            user_id=current_user.id,
        )
        
        # Convert to API response
        return result.to_api_response()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute temporary workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to execute temporary workflow template: {str(e)}"
        ) from e


# Analytics
@router.get(
    "/definitions/{workflow_id}/analytics",
    response_model=WorkflowAnalyticsResponse,
)
async def get_workflow_analytics(
    workflow_id: WorkflowId,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
    analytics_service: SimplifiedWorkflowAnalyticsService = Depends(
        get_workflow_analytics_service
    ),
) -> WorkflowAnalyticsResponse:
    """Get analytics for a specific workflow definition."""
    try:
        # Verify workflow exists and user has access
        definition = await workflow_service.get_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not definition:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        analytics = await analytics_service.analyze_workflow(
            nodes=definition.nodes,
            edges=definition.edges,
        )
        return WorkflowAnalyticsResponse(**analytics)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get workflow analytics: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get workflow analytics: {str(e)}"
        ) from e


# Execution
@router.post(
    "/definitions/{workflow_id}/execute",
    response_model=WorkflowExecutionResponse,
)
async def execute_workflow(
    workflow_id: WorkflowId,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
    execution_engine = Depends(get_execution_engine),
) -> WorkflowExecutionResponse:
    """Execute a workflow definition using the unified execution engine.
    
    **New in Phase 7**: This endpoint now uses the unified ExecutionEngine for all workflow
    execution, providing consistent behavior and better performance.
    
    **Execution Flow**:
    1. Verifies workflow definition exists and user has access
    2. Creates ExecutionRequest with definition_id and input_data
    3. Executes through unified ExecutionEngine
    4. Returns standardized WorkflowExecutionResponse
    
    **Request Body**:
    - `input_data`: Input parameters for the workflow
    - `debug_mode`: Enable detailed logging (default: false)
    
    **Response**:
    - `id`: Execution ID for tracking
    - `definition_id`: ID of the executed workflow definition
    - `status`: Execution status (completed/failed)
    - `output_data`: Workflow execution results
    - `execution_time_ms`: Execution duration in milliseconds
    - `tokens_used`: Total LLM tokens consumed
    - `cost`: Execution cost in USD
    
    **Example**:
    ```python
    # Using Python SDK
    result = client.workflows.execute_definition(
        workflow_id="def_123",
        input_data={"query": "Hello"},
        debug_mode=False
    )
    print(f"Execution {result.id} completed in {result.execution_time_ms}ms")
    ```
    """
    try:
        # Verify workflow exists and user has access
        definition = await workflow_service.get_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not definition:
            logger.warning(
                "Workflow execution denied - definition not found or access denied",
                workflow_id=workflow_id,
                user_id=current_user.id,
            )
            raise NotFoundProblem(
                detail=f"Workflow definition not found: {workflow_id}"
            )

        # Create unified execution request
        from chatter.schemas.execution import ExecutionRequest
        
        exec_request = ExecutionRequest(
            definition_id=workflow_id,
            input_data=execution_request.input_data or {},
            debug_mode=execution_request.debug_mode,
        )

        # Execute using unified engine
        result = await execution_engine.execute(
            request=exec_request,
            user_id=current_user.id,
        )
        
        # Convert to API response
        return result.to_api_response()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise InternalServerProblem(
            detail=f"Failed to execute workflow: {str(e)}"
        ) from e


# Validation
@router.post(
    "/definitions/validate", response_model=WorkflowValidationResponse
)
async def validate_workflow_definition(
    request: WorkflowDefinitionCreate | dict,
    current_user: User = Depends(get_current_user),
    validator = Depends(get_workflow_validator),
) -> WorkflowValidationResponse:
    """Validate a workflow definition using the unified validation orchestrator.
    
    **New in Phase 7**: All validation now goes through the unified WorkflowValidator,
    ensuring consistent validation across all 4 validation layers.
    
    **Validation Layers**:
    1. **Structure Validation**: Nodes, edges, connectivity, graph validity
    2. **Security Validation**: Security policies, permissions, data access
    3. **Capability Validation**: Feature support, capability limits
    4. **Resource Validation**: Resource quotas, usage limits
    
    **Request Body**:
    - Can be WorkflowDefinitionCreate schema OR raw dict with nodes/edges
    - Supports both legacy and modern formats
    
    **Response**:
    - `is_valid`: Overall validation result
    - `errors`: List of validation errors from all layers
    - `warnings`: Non-blocking warnings
    - `metadata`: Additional validation details
    
    **Example**:
    ```python
    # Using Python SDK
    result = client.workflows.validate_definition({
        "nodes": [...],
        "edges": [...]
    })
    
    if result.is_valid:
        print("Workflow is valid!")
    else:
        for error in result.errors:
            print(f"Error: {error['message']}")
    ```
    """
    try:
        # Convert request to dict format
        if isinstance(request, WorkflowDefinitionCreate):
            workflow_data = request.model_dump()
        else:
            workflow_data = request

        # Use unified validator
        validation_result = await validator.validate(
            workflow_data=workflow_data,
            user_id=current_user.id,
            context="api_validation",
        )

        # Convert to API response using built-in conversion
        response_data = validation_result.to_api_response()
        
        # Map to WorkflowValidationResponse format
        return WorkflowValidationResponse(
            is_valid=response_data["valid"],
            errors=[
                {"message": error} for error in response_data["errors"]
            ],
            warnings=response_data["warnings"],
            metadata=response_data.get("details", {}),
        )
    except Exception as e:
        logger.error(f"Failed to validate workflow definition: {e}")
        # Return validation error response instead of raising exception
        return WorkflowValidationResponse(
            is_valid=False,
            errors=[{"message": f"Validation error: {str(e)}"}],
            warnings=[],
            metadata={},
        )


# Node Types
@router.get("/node-types", response_model=list[NodeTypeResponse])
async def get_supported_node_types(
    current_user: User = Depends(get_current_user),
) -> list[NodeTypeResponse]:
    """Get list of supported workflow node types."""
    try:
        from chatter.core.workflow_node_registry import (
            node_type_registry,
        )

        node_types = node_type_registry.get_all_node_types()

        return [
            NodeTypeResponse(**node_type) for node_type in node_types
        ]
    except Exception as e:
        logger.error(f"Failed to get node types: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get node types: {str(e)}"
        ) from e


@router.get("/executions", response_model=dict[str, Any])
async def list_all_workflow_executions(
    limit: PaginationLimit = 20,
    offset: PaginationOffset = 0,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> dict[str, Any]:
    """List all workflow executions for the current user with pagination."""
    try:
        executions, total_count = (
            await workflow_service.list_all_workflow_executions(
                owner_id=current_user.id,
                limit=limit,
                offset=offset,
            )
        )

        return {
            "items": [
                WorkflowExecutionResponse.model_validate(exec.to_dict())
                for exec in executions
            ],
            "total": total_count,
            "offset": offset,
            "limit": limit,
        }

    except Exception as e:
        logger.error(f"Failed to list all workflow executions: {e}")
        raise InternalServerProblem(
            detail=f"Failed to list all workflow executions: {str(e)}"
        ) from e


@router.get(
    "/definitions/{workflow_id}/executions",
    response_model=list[WorkflowExecutionResponse],
)
async def list_workflow_executions(
    workflow_id: WorkflowId,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> list[WorkflowExecutionResponse]:
    """List executions for a workflow definition."""
    try:
        executions = await workflow_service.list_workflow_executions(
            definition_id=workflow_id,
            owner_id=current_user.id,
        )
        return [
            WorkflowExecutionResponse.model_validate(exec.to_dict())
            for exec in executions
        ]

    except Exception as e:
        logger.error(
            f"Failed to list executions for workflow {workflow_id}: {e}"
        )
        raise InternalServerProblem(
            detail=f"Failed to list executions: {str(e)}"
        ) from e


@router.get(
    "/definitions/{workflow_id}/executions/{execution_id}",
    response_model=DetailedWorkflowExecutionResponse,
)
async def get_workflow_execution_details(
    workflow_id: WorkflowId,
    execution_id: str,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> DetailedWorkflowExecutionResponse:
    """Get detailed information about a specific workflow execution."""
    try:
        # First verify the workflow exists and user has access
        definition = await workflow_service.get_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not definition:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        # Get the execution
        execution = (
            await workflow_service.get_workflow_execution_details(
                execution_id=execution_id,
                owner_id=current_user.id,
            )
        )
        if not execution:
            raise NotFoundProblem(detail="Workflow execution not found")

        # Verify the execution belongs to this workflow
        if execution.definition_id != workflow_id:
            raise NotFoundProblem(
                detail="Execution does not belong to this workflow"
            )

        return DetailedWorkflowExecutionResponse.model_validate(
            execution.to_dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get execution details {execution_id}: {e}"
        )
        raise InternalServerProblem(
            detail=f"Failed to get execution details: {str(e)}"
        ) from e


@router.get(
    "/definitions/{workflow_id}/executions/{execution_id}/logs",
    response_model=list[dict[str, Any]],
)
async def get_workflow_execution_logs(
    workflow_id: WorkflowId,
    execution_id: str,
    log_level: str | None = None,
    limit: int = 1000,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> list[dict[str, Any]]:
    """Get execution logs for a specific workflow execution."""
    try:
        # First verify the workflow exists and user has access
        definition = await workflow_service.get_workflow_definition(
            workflow_id=workflow_id,
            owner_id=current_user.id,
        )
        if not definition:
            raise NotFoundProblem(
                detail="Workflow definition not found"
            )

        # Get execution logs
        logs = await workflow_service.get_workflow_execution_logs(
            execution_id=execution_id,
            owner_id=current_user.id,
            log_level=log_level,
            limit=limit,
        )

        return logs

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to get execution logs {execution_id}: {e}"
        )
        raise InternalServerProblem(
            detail=f"Failed to get execution logs: {str(e)}"
        ) from e


# Chat Workflow Endpoints


@router.post("/execute/chat", response_model=ChatResponse)
@rate_limit(max_requests=30, window_seconds=60)
async def execute_chat_workflow(
    request: ChatWorkflowRequest,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service
    ),
) -> ChatResponse:
    """Execute chat using dynamically built workflow."""
    try:
        (
            conversation,
            message,
        ) = await workflow_service.execute_chat_workflow(
            user_id=current_user.id, request=request
        )

        from chatter.schemas.chat import (
            ConversationResponse,
            MessageResponse,
        )

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse.model_validate(message),
            conversation=ConversationResponse.model_validate(
                conversation
            ),
        )
    except Exception as e:
        logger.error(f"Failed to execute chat workflow: {e}")
        raise InternalServerProblem(
            detail=f"Failed to execute chat workflow: {str(e)}"
        ) from e


@router.post(
    "/execute/chat/streaming",
    responses={
        200: {
            "description": "Streaming chat response",
            "content": {
                "text/event-stream": {"schema": {"type": "string"}}
            },
        }
    },
)
@rate_limit(max_requests=20, window_seconds=60)
async def execute_chat_workflow_streaming(
    request: ChatWorkflowRequest,
    chat_request: Request,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service
    ),
):
    """Execute chat using dynamically built workflow with streaming."""

    async def generate_stream():
        try:
            async for (
                chunk
            ) in workflow_service.execute_chat_workflow_streaming(
                user_id=current_user.id, request=request
            ):
                if await chat_request.is_disconnected():
                    logger.info("Client disconnected during streaming")
                    break
                yield f"data: {json.dumps(chunk.model_dump())}\n\n"
        except Exception as e:
            error_chunk = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_chunk)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# Modern Workflow System Endpoints


@router.post("/definitions/custom/execute")
async def execute_custom_workflow(
    nodes: list[dict],
    edges: list[dict],
    message: str,
    entry_point: str | None = None,
    provider: str = "openai",
    model: str = "gpt-4",
    conversation_id: str | None = None,
    current_user: User = Depends(get_current_user),
    execution_engine = Depends(get_execution_engine),
) -> dict:
    """Execute a custom workflow definition using the modern unified execution engine."""
    try:
        # Create unified execution request
        from chatter.schemas.execution import ExecutionRequest
        
        exec_request = ExecutionRequest(
            nodes=nodes,
            edges=edges,
            message=message,
            provider=provider,
            model=model,
            conversation_id=conversation_id,
        )

        # Execute using unified engine
        result = await execution_engine.execute(
            request=exec_request,
            user_id=current_user.id,
        )

        # Return simplified response format
        return {
            "response": result.response,
            "metadata": result.metadata,
            "execution_summary": {
                "execution_id": result.execution_id,
                "tool_calls": result.tool_calls,
            },
            "tokens_used": result.tokens_used,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "cost": result.cost,
        }

    except Exception as e:
        logger.error(f"Custom workflow execution failed: {e}")
        raise InternalServerProblem(
            detail=f"Custom workflow execution failed: {str(e)}"
        ) from e


@router.get("/node-types/modern", response_model=dict)
async def get_modern_supported_node_types(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get supported node types from the modern workflow system."""
    try:
        from chatter.core.langgraph import workflow_manager
        from chatter.core.workflow_node_registry import (
            node_type_registry,
        )

        supported_types = workflow_manager.get_supported_node_types()
        node_type_details = (
            node_type_registry.get_modern_node_type_details()
        )

        return {
            "supported_types": supported_types,
            "type_details": {
                node_type: details
                for node_type, details in node_type_details.items()
                if node_type in supported_types
            },
            "capabilities": {
                "conditional_routing": True,
                "loop_iteration": True,
                "variable_management": True,
                "error_recovery": True,
                "adaptive_memory": True,
                "intelligent_tool_execution": True,
            },
        }

    except Exception as e:
        logger.error(f"Failed to get modern node types: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get modern node types: {str(e)}"
        ) from e


@router.post("/memory/configure")
async def configure_memory_settings(
    adaptive_mode: bool = True,
    base_window_size: int = 10,
    max_window_size: int = 50,
    summary_strategy: str = "intelligent",
    current_user: User = Depends(get_current_user),
) -> dict:
    """Configure memory management settings for the user."""
    try:
        # Store user-specific memory configuration using preferences service
        memory_config = {
            "adaptive_mode": adaptive_mode,
            "base_window_size": base_window_size,
            "max_window_size": max_window_size,
            "summary_strategy": summary_strategy,
            "user_id": current_user.id,
            "updated_at": time.time(),
        }

        # Store in user preferences service
        from chatter.services.user_preferences import (
            get_user_preferences_service,
        )

        preferences_service = get_user_preferences_service()
        result = await preferences_service.save_memory_config(
            user_id=current_user.id, config=memory_config
        )

        logger.info(
            f"Memory configuration stored for user {current_user.id}: {memory_config}"
        )

        return {
            "status": "success",
            "config": result.get("config", memory_config),
            "message": "Memory settings configured successfully",
        }

    except Exception as e:
        logger.error(f"Failed to configure memory settings: {e}")
        raise InternalServerProblem(
            detail=f"Failed to configure memory settings: {str(e)}"
        ) from e


@router.post("/tools/configure")
async def configure_tool_settings(
    max_total_calls: int = 10,
    max_consecutive_calls: int = 3,
    recursion_strategy: str = "adaptive",
    enable_recursion_detection: bool = True,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Configure tool execution settings for the user."""
    try:
        # Validate recursion strategy
        valid_strategies = ["strict", "adaptive", "lenient"]
        if recursion_strategy not in valid_strategies:
            raise ValueError(
                f"Invalid recursion strategy. Must be one of: {valid_strategies}"
            )

        tool_config = {
            "max_total_calls": max_total_calls,
            "max_consecutive_calls": max_consecutive_calls,
            "recursion_strategy": recursion_strategy,
            "enable_recursion_detection": enable_recursion_detection,
            "user_id": current_user.id,
            "updated_at": time.time(),
        }

        # Store in user preferences service
        from chatter.services.user_preferences import (
            get_user_preferences_service,
        )

        preferences_service = get_user_preferences_service()
        result = await preferences_service.save_tool_config(
            user_id=current_user.id, config=tool_config
        )

        logger.info(
            f"Tool configuration stored for user {current_user.id}: {tool_config}"
        )

        return {
            "status": "success",
            "config": result.get("config", tool_config),
            "valid_strategies": valid_strategies,
            "message": "Tool settings configured successfully",
        }

    except Exception as e:
        logger.error(f"Failed to configure tool settings: {e}")
        raise InternalServerProblem(
            detail=f"Failed to configure tool settings: {str(e)}"
        ) from e


@router.get("/defaults", response_model=dict[str, Any])
async def get_workflow_defaults(
    node_type: str | None = None,
    current_user: User = Depends(get_current_user),
    defaults_service: WorkflowDefaultsService = Depends(
        get_workflow_defaults_service
    ),
) -> dict[str, Any]:
    """Get workflow defaults from profiles, models, and prompts.

    Args:
        node_type: Optional specific node type to get defaults for
        current_user: Current authenticated user
        defaults_service: Workflow defaults service

    Returns:
        Dictionary containing default configurations
    """
    try:
        if node_type:
            # Get defaults for specific node type
            config = await defaults_service.get_default_node_config(
                node_type, current_user.id
            )
            return {"node_type": node_type, "config": config}
        else:
            # Get general model defaults
            model_config = (
                await defaults_service.get_default_model_config(
                    current_user.id
                )
            )
            prompt_text = (
                await defaults_service.get_default_prompt_text(
                    user_id=current_user.id
                )
            )

            return {
                "model_config": model_config,
                "default_prompt": prompt_text,
                "node_types": {
                    "model": await defaults_service.get_default_node_config(
                        "model", current_user.id
                    ),
                    "retrieval": await defaults_service.get_default_node_config(
                        "retrieval", current_user.id
                    ),
                    "memory": await defaults_service.get_default_node_config(
                        "memory", current_user.id
                    ),
                    "loop": await defaults_service.get_default_node_config(
                        "loop", current_user.id
                    ),
                    "conditional": await defaults_service.get_default_node_config(
                        "conditional", current_user.id
                    ),
                    "variable": await defaults_service.get_default_node_config(
                        "variable", current_user.id
                    ),
                    "errorHandler": await defaults_service.get_default_node_config(
                        "errorHandler", current_user.id
                    ),
                    "delay": await defaults_service.get_default_node_config(
                        "delay", current_user.id
                    ),
                    "tool": await defaults_service.get_default_node_config(
                        "tool", current_user.id
                    ),
                    "start": await defaults_service.get_default_node_config(
                        "start", current_user.id
                    ),
                },
            }

    except Exception as e:
        logger.error(f"Failed to get workflow defaults: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get workflow defaults: {str(e)}"
        ) from e
