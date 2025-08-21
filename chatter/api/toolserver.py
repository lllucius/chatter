"""Tool server management API endpoints."""

from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.api.auth import get_current_user
from chatter.models.user import User
from chatter.models.toolserver import ServerStatus, ToolStatus
from chatter.schemas.toolserver import (
    ToolServerCreate, ToolServerUpdate, ToolServerResponse,
    ToolServerStatusUpdate, ServerToolResponse, ServerToolUpdate,
    ToolUsageResponse, ToolServerMetrics, ToolServerAnalytics,
    ToolServerHealthCheck, BulkToolServerOperation, BulkOperationResult
)
from chatter.services.toolserver import ToolServerService, ToolServerServiceError
from chatter.utils.database import get_session
from chatter.utils.logging import get_logger

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

@router.post("/servers", response_model=ToolServerResponse, status_code=status.HTTP_201_CREATED)
async def create_tool_server(
    server_data: ToolServerCreate,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to create tool server", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create tool server"
        )


@router.get("/servers", response_model=List[ToolServerResponse])
async def list_tool_servers(
    status_filter: Optional[ServerStatus] = Query(None, alias="status"),
    include_builtin: bool = Query(True, description="Include built-in servers"),
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> List[ToolServerResponse]:
    """List tool servers with optional filtering.
    
    Args:
        status_filter: Filter by server status
        include_builtin: Whether to include built-in servers
        current_user: Current authenticated user
        service: Tool server service
        
    Returns:
        List of server responses
    """
    try:
        return await service.list_servers(
            status=status_filter,
            include_builtin=include_builtin
        )
    except Exception as e:
        logger.error("Failed to list tool servers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tool servers"
        )


@router.get("/servers/{server_id}", response_model=ToolServerResponse)
async def get_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool server not found"
        )
    return server


@router.put("/servers/{server_id}", response_model=ToolServerResponse)
async def update_tool_server(
    server_id: str,
    update_data: ToolServerUpdate,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool server not found"
            )
        return server
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to update tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update tool server"
        )


@router.delete("/servers/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> None:
    """Delete a tool server.
    
    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service
    """
    try:
        success = await service.delete_server(server_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tool server not found"
            )
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to delete tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete tool server"
        )


# Server Control Operations

@router.post("/servers/{server_id}/start")
async def start_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Server started successfully" if success else "Failed to start server"
        }
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to start tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start tool server"
        )


@router.post("/servers/{server_id}/stop")
async def stop_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Server stopped successfully" if success else "Failed to stop server"
        }
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to stop tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to stop tool server"
        )


@router.post("/servers/{server_id}/restart")
async def restart_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Server restarted successfully" if success else "Failed to restart server"
        }
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to restart tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to restart tool server"
        )


@router.post("/servers/{server_id}/enable")
async def enable_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Server enabled successfully" if success else "Failed to enable server"
        }
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to enable tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable tool server"
        )


@router.post("/servers/{server_id}/disable")
async def disable_tool_server(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Server disabled successfully" if success else "Failed to disable server"
        }
    except ToolServerServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to disable tool server", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable tool server"
        )


# Tool Management

@router.get("/servers/{server_id}/tools", response_model=List[ServerToolResponse])
async def get_server_tools(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> List[ServerToolResponse]:
    """Get tools for a specific server.
    
    Args:
        server_id: Server ID
        current_user: Current authenticated user
        service: Tool server service
        
    Returns:
        List of server tools
    """
    try:
        return await service.get_server_tools(server_id)
    except Exception as e:
        logger.error("Failed to get server tools", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get server tools"
        )


@router.post("/tools/{tool_id}/enable")
async def enable_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Tool enabled successfully" if success else "Tool not found"
        }
    except Exception as e:
        logger.error("Failed to enable tool", tool_id=tool_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to enable tool"
        )


@router.post("/tools/{tool_id}/disable")
async def disable_tool(
    tool_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
) -> Dict[str, Any]:
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
        return {
            "success": success,
            "message": "Tool disabled successfully" if success else "Tool not found"
        }
    except Exception as e:
        logger.error("Failed to disable tool", tool_id=tool_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable tool"
        )


# Analytics and Health

@router.get("/servers/{server_id}/metrics", response_model=ToolServerMetrics)
async def get_server_metrics(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Server not found"
            )
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get server metrics", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get server metrics"
        )


@router.get("/servers/{server_id}/health", response_model=ToolServerHealthCheck)
async def check_server_health(
    server_id: str,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Failed to check server health", server_id=server_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check server health"
        )


# Bulk Operations

@router.post("/servers/bulk", response_model=BulkOperationResult)
async def bulk_server_operation(
    operation_data: BulkToolServerOperation,
    current_user: User = Depends(get_current_user),
    service: ToolServerService = Depends(get_tool_server_service)
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
                    raise ValueError(f"Unknown operation: {operation_data.operation}")
                
                if success:
                    successful += 1
                    results.append({
                        "server_id": server_id,
                        "success": True,
                        "message": f"{operation_data.operation.title()} successful"
                    })
                else:
                    failed += 1
                    results.append({
                        "server_id": server_id,
                        "success": False,
                        "message": f"{operation_data.operation.title()} failed"
                    })
                    
            except Exception as e:
                failed += 1
                error_msg = f"Server {server_id}: {str(e)}"
                errors.append(error_msg)
                results.append({
                    "server_id": server_id,
                    "success": False,
                    "message": str(e)
                })
        
        return BulkOperationResult(
            total_requested=total_requested,
            successful=successful,
            failed=failed,
            results=results,
            errors=errors
        )
        
    except Exception as e:
        logger.error("Failed to perform bulk server operation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk server operation"
        )