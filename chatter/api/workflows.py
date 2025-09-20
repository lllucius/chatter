"""Comprehensive workflows API supporting advanced workflow editor features."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.api.dependencies import WorkflowId
from chatter.models.user import User
from chatter.schemas.chat import ChatResponse
from chatter.schemas.workflows import (
    ChatWorkflowRequest,
    ChatWorkflowTemplatesResponse,
    NodeTypeResponse,
    WorkflowAnalyticsResponse,
    WorkflowDefinitionCreate,
    WorkflowDefinitionResponse,
    WorkflowDefinitionsResponse,
    WorkflowDefinitionUpdate,
    WorkflowDeleteResponse,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowTemplateCreate,
    WorkflowTemplateResponse,
    WorkflowTemplatesResponse,
    WorkflowTemplateUpdate,
    WorkflowValidationResponse,
)
from chatter.services.simplified_workflow_analytics import (
    SimplifiedWorkflowAnalyticsService,
)
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
        definition = await workflow_service.create_workflow_definition(
            owner_id=current_user.id,
            name=workflow_definition.name,
            description=workflow_definition.description,
            nodes=workflow_definition.nodes,
            edges=workflow_definition.edges,
            metadata=workflow_definition.metadata,
        )
        return WorkflowDefinitionResponse.model_validate(definition)
    except Exception as e:
        logger.error(f"Failed to create workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to create workflow definition: {str(e)}"
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
                WorkflowDefinitionResponse.model_validate(definition)
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

        return WorkflowDefinitionResponse.model_validate(definition)
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

        return WorkflowDefinitionResponse.model_validate(definition)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to update workflow definition: {str(e)}"
        ) from e


@router.delete("/definitions/{workflow_id}", response_model=WorkflowDeleteResponse)
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
        return WorkflowTemplateResponse.model_validate(template_obj)
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
                WorkflowTemplateResponse.model_validate(template)
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

        return WorkflowTemplateResponse.model_validate(template_obj)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update workflow template: {e}")
        raise InternalServerProblem(
            detail=f"Failed to update workflow template: {str(e)}"
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
    execution_service: WorkflowExecutionService = Depends(
        get_workflow_execution_service
    ),
) -> WorkflowExecutionResponse:
    """Execute a workflow definition."""
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

        # Execute the workflow using the new workflow definition execution method
        result = await execution_service.execute_workflow_definition(
            definition=definition,
            input_data=execution_request.input_data,
            user_id=current_user.id,
        )
        return WorkflowExecutionResponse(**result)
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
    workflow_definition: WorkflowDefinitionCreate,
    current_user: User = Depends(get_current_user),
    workflow_service: WorkflowManagementService = Depends(
        get_workflow_management_service
    ),
) -> WorkflowValidationResponse:
    """Validate a workflow definition."""
    try:
        validation_result = (
            await workflow_service.validate_workflow_definition(
                definition_data=workflow_definition.model_dump(),
                owner_id=current_user.id,
            )
        )
        return WorkflowValidationResponse(**validation_result)
    except Exception as e:
        logger.error(f"Failed to validate workflow definition: {e}")
        raise InternalServerProblem(
            detail=f"Failed to validate workflow definition: {str(e)}"
        ) from e


# Node Types
@router.get("/node-types", response_model=list[NodeTypeResponse])
async def get_supported_node_types(
    current_user: User = Depends(get_current_user),
) -> list[NodeTypeResponse]:
    """Get list of supported workflow node types."""
    try:
        node_types = [
            {
                "type": "start",
                "name": "Start",
                "description": "Starting point of the workflow",
                "category": "control",
                "properties": [],
            },
            {
                "type": "model",
                "name": "Model",
                "description": "Language model processing node",
                "category": "processing",
                "properties": [
                    {
                        "name": "model",
                        "type": "string",
                        "required": True,
                        "description": "Model name",
                    },
                    {
                        "name": "system_message",
                        "type": "text",
                        "required": False,
                        "description": "System prompt",
                    },
                    {
                        "name": "temperature",
                        "type": "number",
                        "required": False,
                        "description": "Temperature (0-2)",
                    },
                    {
                        "name": "max_tokens",
                        "type": "number",
                        "required": False,
                        "description": "Maximum tokens",
                    },
                ],
            },
            {
                "type": "tool",
                "name": "Tool",
                "description": "Tool execution node",
                "category": "processing",
                "properties": [
                    {
                        "name": "tool_name",
                        "type": "string",
                        "required": True,
                        "description": "Tool name",
                    },
                    {
                        "name": "parameters",
                        "type": "object",
                        "required": False,
                        "description": "Tool parameters",
                    },
                ],
            },
            {
                "type": "memory",
                "name": "Memory",
                "description": "Memory storage and retrieval node",
                "category": "storage",
                "properties": [
                    {
                        "name": "operation",
                        "type": "select",
                        "options": ["store", "retrieve"],
                        "required": True,
                    },
                    {
                        "name": "key",
                        "type": "string",
                        "required": True,
                        "description": "Memory key",
                    },
                ],
            },
            {
                "type": "retrieval",
                "name": "Retrieval",
                "description": "Document retrieval node",
                "category": "data",
                "properties": [
                    {
                        "name": "query",
                        "type": "string",
                        "required": True,
                        "description": "Search query",
                    },
                    {
                        "name": "limit",
                        "type": "number",
                        "required": False,
                        "description": "Result limit",
                    },
                ],
            },
            {
                "type": "conditional",
                "name": "Conditional",
                "description": "Conditional logic node",
                "category": "control",
                "properties": [
                    {
                        "name": "condition",
                        "type": "string",
                        "required": True,
                        "description": "Condition expression",
                    },
                ],
            },
            {
                "type": "loop",
                "name": "Loop",
                "description": "Loop iteration node",
                "category": "control",
                "properties": [
                    {
                        "name": "max_iterations",
                        "type": "number",
                        "required": False,
                        "description": "Maximum iterations",
                    },
                    {
                        "name": "condition",
                        "type": "string",
                        "required": False,
                        "description": "Loop condition",
                    },
                ],
            },
            {
                "type": "variable",
                "name": "Variable",
                "description": "Variable manipulation node",
                "category": "data",
                "properties": [
                    {
                        "name": "operation",
                        "type": "select",
                        "options": [
                            "set",
                            "get",
                            "append",
                            "increment",
                            "decrement",
                        ],
                        "required": True,
                    },
                    {
                        "name": "variable_name",
                        "type": "string",
                        "required": True,
                        "description": "Variable name",
                    },
                    {
                        "name": "value",
                        "type": "any",
                        "required": False,
                        "description": "Variable value",
                    },
                ],
            },
            {
                "type": "error_handler",
                "name": "Error Handler",
                "description": "Error handling and recovery node",
                "category": "control",
                "properties": [
                    {
                        "name": "retry_count",
                        "type": "number",
                        "required": False,
                        "description": "Number of retries",
                    },
                    {
                        "name": "fallback_action",
                        "type": "string",
                        "required": False,
                        "description": "Fallback action",
                    },
                ],
            },
            {
                "type": "delay",
                "name": "Delay",
                "description": "Time delay node",
                "category": "utility",
                "properties": [
                    {
                        "name": "delay_type",
                        "type": "select",
                        "options": [
                            "fixed",
                            "random",
                            "exponential",
                            "dynamic",
                        ],
                        "required": True,
                    },
                    {
                        "name": "duration",
                        "type": "number",
                        "required": True,
                        "description": "Delay duration (ms)",
                    },
                    {
                        "name": "max_duration",
                        "type": "number",
                        "required": False,
                        "description": "Maximum duration for random/dynamic",
                    },
                ],
            },
        ]

        return [
            NodeTypeResponse(**node_type) for node_type in node_types
        ]
    except Exception as e:
        logger.error(f"Failed to get node types: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get node types: {str(e)}"
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
            WorkflowExecutionResponse.model_validate(exec)
            for exec in executions
        ]

    except Exception as e:
        logger.error(
            f"Failed to list executions for workflow {workflow_id}: {e}"
        )
        raise InternalServerProblem(
            detail=f"Failed to list executions: {str(e)}"
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
        conversation, message = await workflow_service.execute_chat_workflow(
            user_id=current_user.id,
            request=request
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
            "content": {"text/event-stream": {"schema": {"type": "string"}}},
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
            async for chunk in workflow_service.execute_chat_workflow_streaming(
                user_id=current_user.id,
                request=request
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


@router.get(
    "/templates/chat", response_model=ChatWorkflowTemplatesResponse
)
async def get_chat_workflow_templates(
    current_user: User = Depends(get_current_user),
) -> ChatWorkflowTemplatesResponse:
    """Get pre-built workflow templates optimized for chat."""
    try:
        from chatter.core.unified_template_manager import (
            get_template_manager_with_session,
        )
        from chatter.utils.database import get_session_generator

        session = await anext(get_session_generator())
        template_manager = get_template_manager_with_session(session)
        templates = await template_manager.get_chat_templates()

        return ChatWorkflowTemplatesResponse(
            templates=templates, total_count=len(templates)
        )
    except Exception as e:
        logger.error(f"Failed to get chat workflow templates: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get chat workflow templates: {str(e)}"
        ) from e
