"""Comprehensive workflows API supporting advanced workflow editor features."""

import json
import time
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.api.dependencies import WorkflowId
from chatter.models.base import generate_ulid
from chatter.models.user import User
from chatter.schemas.chat import ChatResponse
from chatter.schemas.workflows import (
    ChatWorkflowRequest,
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
from chatter.services.workflow_defaults import WorkflowDefaultsService
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
            logger.warning(
                "Workflow execution denied - definition not found or access denied",
                workflow_id=workflow_id,
                user_id=current_user.id,
            )
            raise NotFoundProblem(
                detail=f"Workflow definition not found: {workflow_id}"
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
            {
                "type": "llm",
                "name": "LLM",
                "description": "Language model processing node (capability-based)",
                "category": "processing",
                "properties": [
                    {
                        "name": "provider",
                        "type": "string",
                        "required": False,
                        "description": "Model provider (openai, anthropic, etc.)",
                    },
                    {
                        "name": "model",
                        "type": "string",
                        "required": False,
                        "description": "Model name",
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
                    {
                        "name": "system_prompt",
                        "type": "text",
                        "required": False,
                        "description": "System prompt",
                    },
                ],
            },
            {
                "type": "tools",
                "name": "Tools",
                "description": "Multi-tool execution node",
                "category": "processing",
                "properties": [
                    {
                        "name": "available_tools",
                        "type": "array",
                        "required": False,
                        "description": "List of available tools",
                    },
                    {
                        "name": "tool_timeout_ms",
                        "type": "number",
                        "required": False,
                        "description": "Tool execution timeout",
                    },
                ],
            },
            {
                "type": "end",
                "name": "End",
                "description": "End point of the workflow",
                "category": "control",
                "properties": [],
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

@router.post("/definitions/validate", response_model=WorkflowValidationResponse)
async def validate_workflow_definition(
    nodes: list[dict],
    edges: list[dict],
    current_user: User = Depends(get_current_user),
) -> WorkflowValidationResponse:
    """Validate a workflow definition using the modern system."""
    try:
        from chatter.core.langgraph import workflow_manager
        
        validation_result = workflow_manager.validate_workflow_definition(nodes, edges)
        
        return WorkflowValidationResponse(
            is_valid=validation_result["valid"],
            errors=[{"message": error} for error in validation_result["errors"]],
            warnings=validation_result["warnings"],
            metadata={
                "supported_node_types": validation_result["supported_node_types"],
                "validation_timestamp": time.time(),
            }
        )
    except Exception as e:
        logger.error(f"Workflow validation failed: {e}")
        return WorkflowValidationResponse(
            is_valid=False,
            errors=[{"message": f"Validation error: {str(e)}"}],
            warnings=[],
            metadata={}
        )


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
    workflow_service: WorkflowExecutionService = Depends(get_workflow_execution_service),
) -> dict:
    """Execute a custom workflow definition using the modern system."""
    try:
        from chatter.core.langgraph import workflow_manager
        from chatter.services.llm import LLMService
        from langchain_core.messages import HumanMessage
        
        # Validate the workflow first
        validation = workflow_manager.validate_workflow_definition(nodes, edges)
        if not validation["valid"]:
            raise ValueError(f"Invalid workflow: {', '.join(validation['errors'])}")
        
        # Get LLM
        llm_service = LLMService()
        llm = await llm_service.get_llm(provider=provider, model=model)
        
        # Create workflow
        workflow = await workflow_manager.create_custom_workflow(
            nodes=nodes,
            edges=edges,
            llm=llm,
            entry_point=entry_point,
            tools=None,  # TODO: Add tool support
            retriever=None,  # TODO: Add retriever support
        )
        
        # Create initial state
        from chatter.core.workflow_node_factory import WorkflowNodeContext
        initial_state: WorkflowNodeContext = {
            "messages": [HumanMessage(content=message)],
            "user_id": current_user.id,
            "conversation_id": conversation_id or generate_ulid(),
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {},
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
        }
        
        # Execute workflow
        result = await workflow_manager.run_workflow(
            workflow=workflow,
            initial_state=initial_state,
        )
        
        # Extract response
        messages = result.get("messages", [])
        last_message = messages[-1] if messages else None
        response_content = getattr(last_message, "content", "No response generated")
        
        return {
            "response": response_content,
            "metadata": result.get("metadata", {}),
            "execution_summary": {
                "nodes_executed": len(result.get("execution_history", [])),
                "tool_calls": result.get("tool_call_count", 0),
                "variables": result.get("variables", {}),
                "conditional_results": result.get("conditional_results", {}),
            }
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
        
        supported_types = workflow_manager.get_supported_node_types()
        
        # Enhanced node type information
        node_type_details = {
            "conditional": {
                "description": "Conditional logic and branching node",
                "required_config": ["condition"],
                "optional_config": [],
                "examples": ["message contains 'hello'", "tool_calls > 3", "variable user_type equals 'premium'"]
            },
            "loop": {
                "description": "Loop iteration and repetitive execution node", 
                "required_config": [],
                "optional_config": ["max_iterations", "condition"],
                "examples": ["max_iterations: 5", "condition: 'variable counter < 10'"]
            },
            "variable": {
                "description": "Variable manipulation and state management node",
                "required_config": ["variable_name", "operation"],
                "optional_config": ["value"],
                "examples": ["set counter to 0", "increment counter", "get user_preference"]
            },
            "error_handler": {
                "description": "Error handling and recovery node",
                "required_config": [],
                "optional_config": ["retry_count", "fallback_action"],
                "examples": ["retry_count: 3", "fallback_action: 'continue'"]
            },
            "delay": {
                "description": "Time delay and pacing node",
                "required_config": ["duration"],
                "optional_config": ["delay_type", "max_duration"],
                "examples": ["duration: 1000 (ms)", "delay_type: 'exponential'"]
            },
            "memory": {
                "description": "Memory management and summarization node",
                "required_config": [],
                "optional_config": ["memory_window"],
                "examples": ["memory_window: 20"]
            },
            "retrieval": {
                "description": "Document retrieval and context gathering node",
                "required_config": [],
                "optional_config": ["max_documents", "collection"],
                "examples": ["max_documents: 5", "collection: 'knowledge_base'"]
            }
        }
        
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
            }
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
        # Store user-specific memory configuration
        # This would typically be stored in user preferences/settings
        memory_config = {
            "adaptive_mode": adaptive_mode,
            "base_window_size": base_window_size,
            "max_window_size": max_window_size,
            "summary_strategy": summary_strategy,
            "user_id": current_user.id,
            "updated_at": time.time(),
        }
        
        # TODO: Store in database user preferences table
        logger.info(f"Memory configuration updated for user {current_user.id}: {memory_config}")
        
        return {
            "status": "success",
            "config": memory_config,
            "message": "Memory settings configured successfully"
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
            raise ValueError(f"Invalid recursion strategy. Must be one of: {valid_strategies}")
        
        tool_config = {
            "max_total_calls": max_total_calls,
            "max_consecutive_calls": max_consecutive_calls,
            "recursion_strategy": recursion_strategy,
            "enable_recursion_detection": enable_recursion_detection,
            "user_id": current_user.id,
            "updated_at": time.time(),
        }
        
        # TODO: Store in database user preferences table
        logger.info(f"Tool configuration updated for user {current_user.id}: {tool_config}")
        
        return {
            "status": "success",
            "config": tool_config,
            "valid_strategies": valid_strategies,
            "message": "Tool settings configured successfully"
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
    defaults_service: WorkflowDefaultsService = Depends(get_workflow_defaults_service),
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
            return {
                "node_type": node_type,
                "config": config
            }
        else:
            # Get general model defaults
            model_config = await defaults_service.get_default_model_config(
                current_user.id
            )
            prompt_text = await defaults_service.get_default_prompt_text(
                user_id=current_user.id
            )
            
            return {
                "model_config": model_config,
                "default_prompt": prompt_text,
                "node_types": {
                    "model": await defaults_service.get_default_node_config("model", current_user.id),
                    "retrieval": await defaults_service.get_default_node_config("retrieval", current_user.id),
                    "memory": await defaults_service.get_default_node_config("memory", current_user.id),
                    "loop": await defaults_service.get_default_node_config("loop", current_user.id),
                    "conditional": await defaults_service.get_default_node_config("conditional", current_user.id),
                    "variable": await defaults_service.get_default_node_config("variable", current_user.id),
                    "errorHandler": await defaults_service.get_default_node_config("errorHandler", current_user.id),
                    "delay": await defaults_service.get_default_node_config("delay", current_user.id),
                    "tool": await defaults_service.get_default_node_config("tool", current_user.id),
                    "start": await defaults_service.get_default_node_config("start", current_user.id),
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to get workflow defaults: {e}")
        raise InternalServerProblem(
            detail=f"Failed to get workflow defaults: {str(e)}"
        ) from e
