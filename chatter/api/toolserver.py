"""Tool server management API endpoints."""


from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.schemas.toolserver import (
    BulkOperationResult,
    BulkToolServerOperation,
    ServerToolsRequest,
    ServerToolsResponse,
    ToolOperationResponse,
    ToolServerCreate,
    ToolServerDeleteResponse,
    ToolServerHealthCheck,
    ToolServerListRequest,
    ToolServerMetrics,
    ToolServerOperationResponse,
    ToolServerResponse,
    ToolServerUpdate,
)
from chatter.services.toolserver import (
    ToolServerService,
    ToolServerServiceError,
)
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger
from chatter.utils.problem import (
    BadRequestProblem,
    InternalServerProblem,
    NotFoundProblem,
    ProblemException,
)

logger = get_logger(__name__)
router = APIRouter()


async def get_tool_server_service(
    session: AsyncSession = Depends(get_session)
) -> ToolServerService:
    """Get tool server service instance.

    Args:
        session: Database session

    Returns:
        ToolServerService instance
    """
    return ToolServerService(session)


# Server CRUD Operations


@router.post(
    "/servers",
    response_model=ToolServerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_tool_server(
    server_data: ToolServerCreate,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerResponse:
    """Create a new tool server.

    Args:
        server_data: Server creation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Created server response
    """
    try:
        return await service.create_server(server_data, current_user.id)
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error("Failed to create tool server", error=str(e))
        raise InternalServerProblem(
            detail="Failed to create tool server"
        ) from None


@router.get("/servers", response_model=list[ToolServerResponse])
async def list_tool_servers(
    request: ToolServerListRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> list[ToolServerResponse]:
    """List tool servers with optional filtering.

    Args:
        request: List request with filter parameters
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server responses
    """
    try:
        return await service.list_servers(
            status=request.status,
            include_builtin=request.include_builtin,
        )
    except Exception as e:
        logger.error("Failed to list tool servers", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list tool servers"
        ) from None


@router.get("/servers/{server_id}", response_model=ToolServerResponse)
async def get_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerResponse:
    """Get a tool server by ID.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server response
    """
    server = await service.get_server(server_id)
    if not server:
        raise NotFoundProblem(
            detail="Tool server not found", resource_type="tool_server"
        ) from None
    return server


@router.put("/servers/{server_id}", response_model=ToolServerResponse)
async def update_tool_server(
    server_id: str,
    update_data: ToolServerUpdate,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerResponse:
    """Update a tool server.

    Args:
        server_id: Server ID
        update_data: Update data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Updated server response
    """
    try:
        server = await service.update_server(server_id, update_data)
        if not server:
            raise NotFoundProblem(
                detail="Tool server not found",
                resource_type="tool_server",
            ) from None
        return server
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to update tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to update tool server"
        ) from None


@router.delete(
    "/servers/{server_id}", response_model=ToolServerDeleteResponse
)
async def delete_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerDeleteResponse:
    """Delete a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Success message
    """
    try:
        success = await service.delete_server(server_id)
        if not success:
            raise NotFoundProblem(
                detail="Tool server not found",
                resource_type="tool_server",
            ) from None
        return ToolServerDeleteResponse(
            message="Tool server deleted successfully"
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to delete tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to delete tool server"
        ) from None


# Server Control Operations


@router.post(
    "/servers/{server_id}/start",
    response_model=ToolServerOperationResponse,
)
async def start_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerOperationResponse:
    """Start a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.start_server(server_id)
        return ToolServerOperationResponse(
            success=success,
            message="Server started successfully"
            if success
            else "Failed to start server",
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to start tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to start tool server"
        ) from None


@router.post(
    "/servers/{server_id}/stop",
    response_model=ToolServerOperationResponse,
)
async def stop_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerOperationResponse:
    """Stop a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.stop_server(server_id)
        return ToolServerOperationResponse(
            success=success,
            message="Server stopped successfully"
            if success
            else "Failed to stop server",
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to stop tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to stop tool server"
        ) from None


@router.post(
    "/servers/{server_id}/restart",
    response_model=ToolServerOperationResponse,
)
async def restart_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerOperationResponse:
    """Restart a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.restart_server(server_id)
        return ToolServerOperationResponse(
            success=success,
            message="Server restarted successfully"
            if success
            else "Failed to restart server",
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to restart tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to restart tool server"
        ) from None


@router.post(
    "/servers/{server_id}/enable",
    response_model=ToolServerOperationResponse,
)
async def enable_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerOperationResponse:
    """Enable a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.enable_server(server_id)
        return ToolServerOperationResponse(
            success=success,
            message="Server enabled successfully"
            if success
            else "Failed to enable server",
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to enable tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to enable tool server"
        ) from None


@router.post(
    "/servers/{server_id}/disable",
    response_model=ToolServerOperationResponse,
)
async def disable_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerOperationResponse:
    """Disable a tool server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.disable_server(server_id)
        return ToolServerOperationResponse(
            success=success,
            message="Server disabled successfully"
            if success
            else "Failed to disable server",
        )
    except ToolServerServiceError as e:
        raise BadRequestProblem(detail=str(e)) from e
    except Exception as e:
        logger.error(
            "Failed to disable tool server",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to disable tool server"
        ) from None


# Tool Management


@router.get(
    "/servers/{server_id}/tools", response_model=ServerToolsResponse
)
async def get_server_tools(
    server_id: str,
    request: ServerToolsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ServerToolsResponse:
    """Get tools for a specific server.

    Args:
        server_id: Server ID
        request: Server tools request with pagination
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        List of server tools with pagination
    """
    try:
        tools = await service.get_server_tools(server_id)

        # Apply pagination manually for now
        total_count = len(tools)
        start_index = request.offset
        end_index = start_index + request.limit
        paginated_tools = tools[start_index:end_index]

        return ServerToolsResponse(
            tools=paginated_tools,
            total_count=total_count,
            limit=request.limit,
            offset=request.offset,
        )
    except Exception as e:
        logger.error(
            "Failed to get server tools",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get server tools"
        ) from None


@router.post(
    "/tools/{tool_id}/enable", response_model=ToolOperationResponse
)
async def enable_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolOperationResponse:
    """Enable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.enable_tool(tool_id)
        return ToolOperationResponse(
            success=success,
            message="Tool enabled successfully"
            if success
            else "Tool not found",
        )
    except Exception as e:
        logger.error(
            "Failed to enable tool", tool_id=tool_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to enable tool"
        ) from None


@router.post(
    "/tools/{tool_id}/disable", response_model=ToolOperationResponse
)
async def disable_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolOperationResponse:
    """Disable a specific tool.

    Args:
        tool_id: Tool ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Operation result
    """
    try:
        success = await service.disable_tool(tool_id)
        return ToolOperationResponse(
            success=success,
            message="Tool disabled successfully"
            if success
            else "Tool not found",
        )
    except Exception as e:
        logger.error(
            "Failed to disable tool", tool_id=tool_id, error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to disable tool"
        ) from None


# Analytics and Health


@router.get(
    "/servers/{server_id}/metrics", response_model=ToolServerMetrics
)
async def get_server_metrics(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerMetrics:
    """Get analytics for a specific server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Server metrics
    """
    try:
        metrics = await service.get_server_analytics(server_id)
        if not metrics:
            raise NotFoundProblem(
                detail="Server not found", resource_type="tool_server"
            ) from None
        return metrics
    except ProblemException:
        raise
    except Exception as e:
        logger.error(
            "Failed to get server metrics",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to get server metrics"
        ) from None


@router.get(
    "/servers/{server_id}/health", response_model=ToolServerHealthCheck
)
async def check_server_health(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> ToolServerHealthCheck:
    """Perform health check on a server.

    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Health check result
    """
    try:
        return await service.health_check_server(server_id)
    except ToolServerServiceError as e:
        raise NotFoundProblem(
            detail=str(e), resource_type="tool_server"
        ) from None
    except Exception as e:
        logger.error(
            "Failed to check server health",
            server_id=server_id,
            error=str(e),
        )
        raise InternalServerProblem(
            detail="Failed to check server health"
        ) from None


# Bulk Operations


@router.post("/servers/bulk", response_model=BulkOperationResult)
async def bulk_server_operation(
    operation_data: BulkToolServerOperation,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service),
) -> BulkOperationResult:
    """Perform bulk operations on multiple servers.

    Args:
        operation_data: Bulk operation data
        current_user: Current authenticated user
        service: Tool server service

    Returns:
        Bulk operation result
    """
    try:
        total_requested = len(operation_data.server_ids)
        successful = 0
        failed = 0
        results = []
        errors = []

        for server_id in operation_data.server_ids:
            try:
                if operation_data.operation == "start":
                    success = await service.start_server(server_id)
                elif operation_data.operation == "stop":
                    success = await service.stop_server(server_id)
                elif operation_data.operation == "restart":
                    success = await service.restart_server(server_id)
                elif operation_data.operation == "enable":
                    success = await service.enable_server(server_id)
                elif operation_data.operation == "disable":
                    success = await service.disable_server(server_id)
                else:
                    raise ValueError(
                        f"Unknown operation: {operation_data.operation}"
                    ) from None

                if success:
                    successful += 1
                    results.append(
                        {
                            "server_id": server_id,
                            "success": True,
                            "message": f"{operation_data.operation.title()} successful",
                        }
                    )
                else:
                    failed += 1
                    results.append(
                        {
                            "server_id": server_id,
                            "success": False,
                            "message": f"{operation_data.operation.title()} failed",
                        }
                    )

            except Exception as e:
                failed += 1
                error_msg = f"Server {server_id}: {str(e)}"
                errors.append(error_msg)
                results.append(
                    {
                        "server_id": server_id,
                        "success": False,
                        "message": str(e),
                    }
                )

        return BulkOperationResult(
            total_requested=total_requested,
            successful=successful,
            failed=failed,
            results=results,
            errors=errors,
        )

    except Exception as e:
        logger.error(
            "Failed to perform bulk server operation", error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to perform bulk server operation"
        ) from None


@router.get("/tools/all", response_model=list[dict])
async def list_all_tools(
    current_user: User = Depends(get_current_user),
    tool_server_service: ToolServerService = Depends(get_tool_server_service),
) -> list[dict]:
    """List all tools across all servers.

    Args:
        current_user: Current authenticated user
        tool_server_service: Tool server service

    Returns:
        List of all available tools across all servers
    """
    try:
        all_tools = await tool_server_service.list_all_tools()
        return all_tools

    except Exception as e:
        logger.error("Failed to list all tools", error=str(e))
        raise InternalServerProblem(
            detail="Failed to list all tools"
        ) from None


@router.post("/servers/{server_id}/test-connectivity", response_model=dict)
async def test_server_connectivity(
    server_id: str,
    current_user: User = Depends(get_current_user),
    tool_server_service: ToolServerService = Depends(get_tool_server_service),
) -> dict:
    """Test connectivity to an external MCP server.

    Args:
        server_id: Tool server ID
        current_user: Current authenticated user
        tool_server_service: Tool server service

    Returns:
        Connectivity test results
    """
    try:
        result = await tool_server_service.test_connectivity(server_id)
        
        if not result:
            raise NotFoundProblem(
                detail="Tool server not found",
                resource_type="tool_server",
                resource_id=server_id,
            ) from None

        return result

    except Exception as e:
        logger.error(
            "Failed to test server connectivity", 
            server_id=server_id, 
            error=str(e)
        )
        raise InternalServerProblem(
            detail="Failed to test server connectivity"
        ) from None
