"""Tool server service with database persistence and CRUD operations."""

import asyncio
import os
from datetime import UTC, datetime
from typing import Any

from pydantic import HttpUrl
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from chatter.models.toolserver import (
    ServerStatus,
    ServerTool,
    ToolServer,
    ToolStatus,
    ToolUsage,
)
from chatter.schemas.toolserver import (
    ServerToolResponse,
    ToolServerCreate,
    ToolServerHealthCheck,
    ToolServerMetrics,
    ToolServerResponse,
    ToolServerUpdate,
    ToolUsageCreate,
)
from chatter.utils.logging import get_logger

# Moved to function level to avoid circular import: from chatter.services.mcp import MCPToolService
from chatter.utils.security_enhanced import get_secret_manager

logger = get_logger(__name__)


class ToolServerServiceError(Exception):
    """Tool server service error."""

    pass


class ToolServerService:
    """Service for managing tool servers with database persistence."""

    def __init__(self, session: AsyncSession):
        """Initialize tool server service.

        Args:
            session: Database session
        """
        self.session = session
        self._mcp_service = None  # Lazy loaded to avoid circular import
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = {}

    @property
    def mcp_service(self):
        """Lazy load MCP service to avoid circular import."""
        if self._mcp_service is None:
            from chatter.services.mcp import MCPToolService

            self._mcp_service = MCPToolService()
        return self._mcp_service

    # CRUD Operations for Tool Servers

    async def create_server(
        self, server_data: ToolServerCreate, user_id: str | None = None
    ) -> ToolServerResponse:
        """Create a new tool server.

        Args:
            server_data: Server creation data
            user_id: User ID creating the server

        Returns:
            Created server response
        """
        try:
            # Check if server name already exists
            existing = await self.session.execute(
                select(ToolServer).where(
                    ToolServer.name == server_data.name
                )
            )
            if existing.scalar_one_or_none():
                raise ToolServerServiceError(
                    f"Server with name '{server_data.name}' already exists"
                ) from None

            # Create server model for remote server
            secret_manager = get_secret_manager()

            # Encrypt OAuth secrets if present
            oauth_client_secret = None
            if (
                server_data.oauth_config
                and server_data.oauth_config.client_secret
            ):
                oauth_client_secret = secret_manager.encrypt(
                    server_data.oauth_config.client_secret
                )

            server = ToolServer(
                name=server_data.name,
                display_name=server_data.display_name,
                description=server_data.description,
                base_url=str(server_data.base_url),
                transport_type=server_data.transport_type,
                oauth_client_id=(
                    server_data.oauth_config.client_id
                    if server_data.oauth_config
                    else None
                ),
                oauth_client_secret=oauth_client_secret,
                oauth_token_url=(
                    str(server_data.oauth_config.token_url)
                    if server_data.oauth_config
                    else None
                ),
                oauth_scope=(
                    server_data.oauth_config.scope
                    if server_data.oauth_config
                    else None
                ),
                headers=server_data.headers,
                timeout=server_data.timeout,
                auto_start=server_data.auto_start,
                max_failures=server_data.max_failures,
                created_by=user_id,
                status=ServerStatus.DISABLED,
            )

            self.session.add(server)
            await self.session.flush()

            # Auto-connect if requested (but not for built-in servers)
            if server_data.auto_start and not server.is_builtin:
                await self._connect_remote_server(server)

            await self.session.commit()

            # Load with tools for response
            await self.session.refresh(server, ["tools"])

            logger.info(
                "Tool server created",
                server_id=server.id,
                name=server.name,
            )
            return ToolServerResponse.model_validate(server)

        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to create tool server", error=str(e))
            raise

    async def get_server(
        self, server_id: str
    ) -> ToolServerResponse | None:
        """Get a tool server by ID.

        Args:
            server_id: Server ID

        Returns:
            Server response or None if not found
        """
        result = await self.session.execute(
            select(ToolServer)
            .options(selectinload(ToolServer.tools))
            .where(ToolServer.id == server_id)
        )
        server = result.scalar_one_or_none()

        if server:
            return ToolServerResponse.model_validate(server)
        return None

    async def get_server_by_name(
        self, name: str
    ) -> ToolServerResponse | None:
        """Get a tool server by name.

        Args:
            name: Server name

        Returns:
            Server response or None if not found
        """
        result = await self.session.execute(
            select(ToolServer)
            .options(selectinload(ToolServer.tools))
            .where(ToolServer.name == name)
        )
        server = result.scalar_one_or_none()

        if server:
            return ToolServerResponse.model_validate(server)
        return None

    async def list_servers(
        self,
        status: ServerStatus | None = None,
        user_id: str | None = None,
        include_builtin: bool = True,
    ) -> list[ToolServerResponse]:
        """List tool servers with optional filtering.

        Args:
            status: Filter by server status
            user_id: Filter by creator user ID
            include_builtin: Whether to include built-in servers

        Returns:
            List of server responses
        """
        query = select(ToolServer).options(
            selectinload(ToolServer.tools)
        )

        filters = []
        if status:
            filters.append(ToolServer.status == status)
        if user_id:
            filters.append(ToolServer.created_by == user_id)
        if not include_builtin:
            filters.append(not ToolServer.is_builtin)

        if filters:
            query = query.where(and_(*filters))

        result = await self.session.execute(
            query.order_by(ToolServer.created_at)
        )
        servers = result.scalars().all()

        return [
            ToolServerResponse.model_validate(server)
            for server in servers
        ]

    async def update_server(
        self, server_id: str, update_data: ToolServerUpdate
    ) -> ToolServerResponse | None:
        """Update a tool server.

        Args:
            server_id: Server ID
            update_data: Update data

        Returns:
            Updated server response or None if not found
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                return None

            # Update fields
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(server, field, value)

            server.updated_at = datetime.now(UTC)

            await self.session.commit()

            # Reload with tools
            await self.session.refresh(server, ["tools"])

            logger.info(
                "Tool server updated",
                server_id=server.id,
                name=server.name,
            )
            return ToolServerResponse.model_validate(server)

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to update tool server",
                server_id=server_id,
                error=str(e),
            )
            raise

    async def delete_server(self, server_id: str) -> bool:
        """Delete a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                return False

            # Stop server if running
            if server.status in [
                ServerStatus.ENABLED,
                ServerStatus.STARTING,
            ]:
                await self._stop_server_internal(server)

            # Delete from database (cascade will handle related records)
            await self.session.delete(server)
            await self.session.commit()

            logger.info(
                "Tool server deleted",
                server_id=server.id,
                name=server.name,
            )
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to delete tool server",
                server_id=server_id,
                error=str(e),
            )
            raise

    # Server Control Operations

    async def start_server(self, server_id: str) -> bool:
        """Start a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if started successfully
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                raise ToolServerServiceError(
                    f"Server not found: {server_id}"
                ) from None

            # Only connect remote servers, not built-in ones
            if not server.is_builtin:
                success = await self._connect_remote_server(server)
            else:
                # For built-in servers, just mark as enabled
                server.status = ServerStatus.ENABLED
                server.last_startup_success = datetime.now(UTC)
                server.last_startup_error = None
                server.consecutive_failures = 0
                success = True
            await self.session.commit()
            await self.session.refresh(server)

            return success

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to start server",
                server_id=server_id,
                error=str(e),
            )
            raise

    async def stop_server(self, server_id: str) -> bool:
        """Stop a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if stopped successfully
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                raise ToolServerServiceError(
                    f"Server not found: {server_id}"
                ) from None

            success = await self._stop_server_internal(server)
            await self.session.commit()
            await self.session.refresh(server)

            return success

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to stop server",
                server_id=server_id,
                error=str(e),
            )
            raise

    async def restart_server(self, server_id: str) -> bool:
        """Restart a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if restarted successfully
        """
        try:
            stop_success = await self.stop_server(server_id)
            if stop_success:
                # Brief delay before restart
                await asyncio.sleep(1)
                return await self.start_server(server_id)
            return False
        except Exception as e:
            logger.error(
                "Failed to restart server",
                server_id=server_id,
                error=str(e),
            )
            raise

    async def enable_server(self, server_id: str) -> bool:
        """Enable a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if enabled successfully
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                return False

            server.status = ServerStatus.ENABLED
            server.updated_at = datetime.now(UTC)

            # Auto-start if configured (but only for remote servers)
            if server.auto_start and not server.is_builtin:
                await self._connect_remote_server(server)

            await self.session.commit()
            await self.session.refresh(server)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to enable server",
                server_id=server_id,
                error=str(e),
            )
            raise

    async def disable_server(self, server_id: str) -> bool:
        """Disable a tool server.

        Args:
            server_id: Server ID

        Returns:
            True if disabled successfully
        """
        try:
            result = await self.session.execute(
                select(ToolServer).where(ToolServer.id == server_id)
            )
            server = result.scalar_one_or_none()

            if not server:
                return False

            # Stop if running
            if server.status in [
                ServerStatus.ENABLED,
                ServerStatus.STARTING,
            ]:
                await self._stop_server_internal(server)

            server.status = ServerStatus.DISABLED
            server.updated_at = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(server)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to disable server",
                server_id=server_id,
                error=str(e),
            )
            raise

    # Tool Management

    async def get_server_tools(
        self, server_id: str
    ) -> list[ServerToolResponse]:
        """Get tools for a specific server.

        Args:
            server_id: Server ID

        Returns:
            List of server tools
        """
        result = await self.session.execute(
            select(ServerTool).where(ServerTool.server_id == server_id)
        )
        tools = result.scalars().all()

        return [
            ServerToolResponse.model_validate(tool) for tool in tools
        ]

    async def list_all_tools(self) -> list[dict]:
        """List all tools across all servers.

        Returns:
            List of all available tools across all servers
        """
        result = await self.session.execute(
            select(ServerTool).options(selectinload(ServerTool.server))
        )
        tools = result.scalars().all()

        return [
            {
                "id": tool.id,
                "name": tool.name,
                "description": tool.description,
                "server_id": tool.server_id,
                "server_name": (
                    tool.server.name if tool.server else None
                ),
                "status": tool.status.value if tool.status else None,
                "enabled": tool.status == ToolStatus.ENABLED,
                "total_calls": tool.total_calls,
                "total_errors": tool.total_errors,
                "avg_response_time_ms": tool.avg_response_time_ms,
                "last_called": (
                    tool.last_called.isoformat()
                    if tool.last_called
                    else None
                ),
                "last_error": tool.last_error,
                "created_at": (
                    tool.created_at.isoformat()
                    if tool.created_at
                    else None
                ),
                "updated_at": (
                    tool.updated_at.isoformat()
                    if tool.updated_at
                    else None
                ),
            }
            for tool in tools
        ]

    async def enable_tool(self, tool_id: str) -> bool:
        """Enable a specific tool.

        Args:
            tool_id: Tool ID

        Returns:
            True if enabled successfully
        """
        try:
            result = await self.session.execute(
                select(ServerTool).where(ServerTool.id == tool_id)
            )
            tool = result.scalar_one_or_none()

            if not tool:
                return False

            tool.status = ToolStatus.ENABLED
            tool.updated_at = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(tool)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to enable tool", tool_id=tool_id, error=str(e)
            )
            raise

    async def disable_tool(self, tool_id: str) -> bool:
        """Disable a specific tool.

        Args:
            tool_id: Tool ID

        Returns:
            True if disabled successfully
        """
        try:
            result = await self.session.execute(
                select(ServerTool).where(ServerTool.id == tool_id)
            )
            tool = result.scalar_one_or_none()

            if not tool:
                return False

            tool.status = ToolStatus.DISABLED
            tool.updated_at = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(tool)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to disable tool", tool_id=tool_id, error=str(e)
            )
            raise

    # Usage Tracking

    async def record_tool_usage(
        self,
        server_id: str,
        tool_name: str,
        usage_data: ToolUsageCreate,
    ) -> bool:
        """Record tool usage for analytics.

        Args:
            server_id: Server ID
            tool_name: Tool name
            usage_data: Usage data

        Returns:
            True if recorded successfully
        """
        try:
            # Get tool ID
            result = await self.session.execute(
                select(ServerTool).where(
                    and_(
                        ServerTool.server_id == server_id,
                        ServerTool.name == tool_name,
                    )
                )
            )
            tool = result.scalar_one_or_none()

            if not tool:
                logger.warning(
                    "Tool not found for usage tracking",
                    server_id=server_id,
                    tool_name=tool_name,
                )
                return False

            # Create usage record
            usage = ToolUsage(
                server_id=server_id,
                tool_id=tool.id,
                tool_name=tool_name,
                user_id=usage_data.user_id,
                conversation_id=usage_data.conversation_id,
                arguments=usage_data.arguments,
                result=usage_data.result,
                response_time_ms=usage_data.response_time_ms,
                success=usage_data.success,
                error_message=usage_data.error_message,
            )

            self.session.add(usage)

            # Update tool statistics
            tool.total_calls += 1
            if not usage_data.success:
                tool.total_errors += 1

            tool.last_called = datetime.now(UTC)
            if usage_data.error_message:
                tool.last_error = usage_data.error_message

            # Update average response time
            if usage_data.response_time_ms is not None:
                if tool.avg_response_time_ms is None:
                    tool.avg_response_time_ms = (
                        usage_data.response_time_ms
                    )
                else:
                    # Exponential moving average
                    alpha = 0.1
                    tool.avg_response_time_ms = (
                        alpha * usage_data.response_time_ms
                        + (1 - alpha) * tool.avg_response_time_ms
                    )

            tool.updated_at = datetime.now(UTC)

            await self.session.commit()
            await self.session.refresh(tool)
            return True

        except Exception as e:
            await self.session.rollback()
            logger.error("Failed to record tool usage", error=str(e))
            raise

    # Analytics and Health

    async def get_server_analytics(
        self, server_id: str
    ) -> ToolServerMetrics | None:
        """Get analytics for a specific server.

        Args:
            server_id: Server ID

        Returns:
            Server metrics or None if not found
        """
        result = await self.session.execute(
            select(ToolServer)
            .options(selectinload(ToolServer.tools))
            .where(ToolServer.id == server_id)
        )
        server = result.scalar_one_or_none()

        if not server:
            return None

        # Calculate metrics from tools
        total_tools = len(server.tools)
        enabled_tools = sum(
            1
            for tool in server.tools
            if tool.status == ToolStatus.ENABLED
        )
        total_calls = sum(tool.total_calls for tool in server.tools)
        total_errors = sum(tool.total_errors for tool in server.tools)
        success_rate = (
            (total_calls - total_errors) / total_calls
            if total_calls > 0
            else 1.0
        )

        # Calculate average response time
        response_times = [
            t.avg_response_time_ms
            for t in server.tools
            if t.avg_response_time_ms
        ]
        avg_response_time = (
            sum(response_times) / len(response_times)
            if response_times
            else None
        )

        # Get last activity
        last_calls = [
            t.last_called for t in server.tools if t.last_called
        ]
        last_activity = max(last_calls) if last_calls else None

        # Calculate uptime percentage based on recent health checks and startup time
        uptime_percentage = None
        if server.last_startup_success and server.last_health_check:
            # Simple uptime calculation: if health check is recent and server started successfully
            now = datetime.now(UTC)
            startup_time = server.last_startup_success
            last_check = server.last_health_check

            # If last health check was within 5 minutes and no consecutive failures
            health_check_age = (now - last_check).total_seconds()
            running_time = (now - startup_time).total_seconds()

            if health_check_age < 300:  # 5 minutes
                if server.consecutive_failures == 0:
                    uptime_percentage = 100.0
                else:
                    # Reduce uptime based on failure rate
                    failure_ratio = min(
                        server.consecutive_failures
                        / server.max_failures,
                        1.0,
                    )
                    uptime_percentage = max(
                        0.0, 100.0 * (1.0 - failure_ratio)
                    )
            elif running_time > 300:  # Been running more than 5 minutes
                # Assume moderate uptime if no recent health check
                uptime_percentage = 75.0

        return ToolServerMetrics(
            server_id=server.id,
            server_name=server.name,
            status=server.status,
            total_tools=total_tools,
            enabled_tools=enabled_tools,
            total_calls=total_calls,
            total_errors=total_errors,
            success_rate=success_rate,
            avg_response_time_ms=avg_response_time,
            last_activity=last_activity,
            uptime_percentage=uptime_percentage,  # Now properly implemented
        )

    async def health_check_server(
        self, server_id: str
    ) -> ToolServerHealthCheck:
        """Perform health check on a server.

        Args:
            server_id: Server ID

        Returns:
            Health check result
        """
        result = await self.session.execute(
            select(ToolServer).where(ToolServer.id == server_id)
        )
        server = result.scalar_one_or_none()

        if not server:
            raise ToolServerServiceError(
                f"Server not found: {server_id}"
            ) from None

        # Check if we need to perform health check
        now = datetime.now(UTC)
        last_check = self._last_health_check.get(server_id)

        if (
            last_check is None
            or (now - last_check).total_seconds()
            > self._health_check_interval
        ):
            # Perform actual health check
            is_running = server.name in self.mcp_service.tools_cache
            is_responsive = False
            tools_count = 0
            error_message = None

            if is_running:
                try:
                    # Try to get tools to check responsiveness
                    tools = await self.mcp_service.get_tools(
                        [server.name]
                    )
                    tools_count = len(tools)
                    is_responsive = True
                except Exception as e:
                    error_message = str(e)
                    logger.warning(
                        "Server health check failed",
                        server_id=server_id,
                        error=error_message,
                    )

            # Update last health check
            server.last_health_check = now
            await self.session.commit()
            await self.session.refresh(server)

            self._last_health_check[server_id] = now

            # Trigger health changed event
            try:
                from chatter.services.sse_events import (
                    trigger_tool_server_health_changed,
                )

                await trigger_tool_server_health_changed(
                    str(server.id),
                    server.name,
                    "healthy" if is_responsive else "unhealthy",
                    {
                        "is_running": is_running,
                        "is_responsive": is_responsive,
                        "tools_count": tools_count,
                        "error_message": error_message,
                    },
                )
            except Exception as e:
                logger.warning(
                    "Failed to trigger tool server health changed event",
                    error=str(e),
                )
        else:
            # Use cached data
            is_running = server.name in self.mcp_service.tools_cache
            tools_count = len(
                self.mcp_service.tools_cache.get(server.name, [])
            )
            is_responsive = is_running
            error_message = server.last_startup_error

        return ToolServerHealthCheck(
            server_id=server.id,
            server_name=server.name,
            status=server.status,
            is_running=is_running,
            is_responsive=is_responsive,
            tools_count=tools_count,
            last_check=server.last_health_check or now,
            error_message=error_message,
        )

    async def _connect_remote_server(self, server: ToolServer) -> bool:
        """Internal method to connect to a remote server.

        Args:
            server: Server model

        Returns:
            True if connected successfully
        """
        try:
            server.status = ServerStatus.STARTING
            server.updated_at = datetime.now(UTC)

            # Create OAuth config if present
            oauth_config = None
            if (
                server.oauth_client_id
                and server.oauth_client_secret
                and server.oauth_token_url
            ):
                from chatter.services.mcp import OAuthConfig

                # Decrypt the client secret
                secret_manager = get_secret_manager()
                try:
                    decrypted_secret = secret_manager.decrypt(
                        server.oauth_client_secret
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to decrypt OAuth client secret, using as plain text",
                        server_id=server.id,
                        error=str(e),
                    )
                    # Fallback to plain text for backward compatibility
                    decrypted_secret = server.oauth_client_secret

                oauth_config = OAuthConfig(
                    client_id=server.oauth_client_id,
                    client_secret=decrypted_secret,
                    token_url=server.oauth_token_url,
                    scope=server.oauth_scope,
                )

            # Create remote server config
            from chatter.services.mcp import RemoteMCPServer

            remote_server = RemoteMCPServer(
                name=server.name,
                base_url=HttpUrl(server.base_url),
                transport_type=server.transport_type,
                oauth_config=oauth_config,
                headers=server.headers,
                timeout=server.timeout,
                enabled=True,
            )

            # Add to MCP service
            success = await self.mcp_service.add_remote_server(
                remote_server
            )

            if success:
                server.status = ServerStatus.ENABLED
                server.last_startup_success = datetime.now(UTC)
                server.last_startup_error = None
                server.consecutive_failures = 0

                # Trigger tool server started event
                try:
                    from chatter.services.sse_events import (
                        trigger_tool_server_started,
                    )

                    await trigger_tool_server_started(
                        str(server.id), server.name
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to trigger tool server started event",
                        error=str(e),
                    )

                # Discover and update tools
                await self._discover_server_tools(server)
            else:
                server.status = ServerStatus.ERROR
                server.last_startup_error = (
                    "Failed to connect to remote server"
                )
                server.consecutive_failures += 1

                # Trigger tool server error event
                try:
                    from chatter.services.sse_events import (
                        EventType,
                        sse_service,
                    )

                    await sse_service.trigger_event(
                        EventType.TOOL_SERVER_ERROR,
                        {
                            "server_id": str(server.id),
                            "server_name": server.name,
                            "error": "Failed to connect to remote server",
                        },
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to trigger error event", error=str(e)
                    )

            server.updated_at = datetime.now(UTC)
            return success

        except Exception as e:
            server.status = ServerStatus.ERROR
            server.last_startup_error = str(e)
            server.consecutive_failures += 1
            server.updated_at = datetime.now(UTC)

            # Trigger tool server error event
            try:
                from chatter.services.sse_events import (
                    EventType,
                    sse_service,
                )

                await sse_service.trigger_event(
                    EventType.TOOL_SERVER_ERROR,
                    {
                        "server_id": str(server.id),
                        "server_name": server.name,
                        "error": str(e),
                        "consecutive_failures": server.consecutive_failures,
                    },
                )
            except Exception as event_e:
                logger.warning(
                    "Failed to trigger tool server error event",
                    error=str(event_e),
                )

            # Disable if too many failures
            if server.consecutive_failures >= server.max_failures:
                server.status = ServerStatus.DISABLED

            logger.error(
                "Failed to connect to remote server",
                server_id=server.id,
                server_name=server.name,
                error=str(e),
            )
            return False

    async def _stop_server_internal(self, server: ToolServer) -> bool:
        """Internal method to stop a server.

        Args:
            server: Server model

        Returns:
            True if stopped successfully
        """
        try:
            server.status = ServerStatus.STOPPING
            server.updated_at = datetime.now(UTC)

            # Stop the server (only disable remote servers in MCP service)
            success = True
            if not server.is_builtin:
                success = await self.mcp_service.disable_server(
                    server.name
                )

            server.status = ServerStatus.DISABLED
            server.updated_at = datetime.now(UTC)

            # Trigger tool server stopped event
            try:
                from chatter.services.sse_events import (
                    trigger_tool_server_stopped,
                )

                await trigger_tool_server_stopped(
                    str(server.id), server.name
                )
            except Exception as e:
                logger.warning(
                    "Failed to trigger tool server stopped event",
                    error=str(e),
                )

            return success

        except Exception as e:
            server.status = ServerStatus.ERROR
            server.last_startup_error = str(e)
            server.updated_at = datetime.now(UTC)
            logger.error(
                "Failed to stop server",
                server_id=server.id,
                error=str(e),
            )
            return False

    async def _discover_server_tools(self, server: ToolServer) -> None:
        """Discover and update tools for a remote server.

        Args:
            server: Server model
        """
        try:
            # Get tools from remote MCP service
            remote_tools = await self.mcp_service.discover_tools(
                server.name
            )

            # Get existing tools from database
            result = await self.session.execute(
                select(ServerTool).where(
                    ServerTool.server_id == server.id
                )
            )
            existing_tools = {
                tool.name: tool for tool in result.scalars().all()
            }

            # Update or create tools
            for tool_data in remote_tools:
                # Handle LangChain BaseTool objects instead of dicts
                tool_name = (
                    tool_data.name
                    if hasattr(tool_data, "name")
                    else None
                )
                if not tool_name:
                    continue

                if tool_name in existing_tools:
                    # Update existing tool
                    tool = existing_tools[tool_name]
                    tool.description = (
                        tool_data.description
                        if hasattr(tool_data, "description")
                        else None
                    )
                    tool.args_schema = getattr(
                        tool_data, "args_schema", None
                    )
                    tool.is_available = True
                    tool.updated_at = datetime.now(UTC)
                else:
                    # Create new tool
                    tool = ServerTool(
                        server_id=server.id,
                        name=tool_name,
                        display_name=tool_name.replace(
                            "_", " "
                        ).title(),
                        description=(
                            tool_data.description
                            if hasattr(tool_data, "description")
                            else None
                        ),
                        args_schema=getattr(
                            tool_data, "args_schema", None
                        ),
                        status=ToolStatus.ENABLED,
                        is_available=True,
                    )
                    self.session.add(tool)

            # Mark tools not found as unavailable
            found_tool_names = {
                tool_data.name
                for tool_data in remote_tools
                if hasattr(tool_data, "name") and tool_data.name
            }
            for tool_name, tool in existing_tools.items():
                if tool_name not in found_tool_names:
                    tool.is_available = False
                    tool.updated_at = datetime.now(UTC)

        except Exception as e:
            logger.error(
                "Failed to discover remote server tools",
                server_id=server.id,
                server_name=server.name,
                error=str(e),
            )

    async def initialize_builtin_servers(self) -> None:
        """Initialize built-in servers from configuration."""
        try:
            # Define built-in servers
            builtin_servers = [
                {
                    "name": "filesystem",
                    "display_name": "File System",
                    "description": "Access to file system operations",
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        os.environ.get(
                            "CHATTER_WORKSPACE_DIR",
                            "/tmp/chatter_workspace",
                        ),  # nosec B108 - configurable via env var
                    ],
                    "env": None,
                },
                {
                    "name": "browser",
                    "display_name": "Web Browser",
                    "description": "Web browsing and search capabilities",
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-brave-search",
                    ],
                    "env": {"BRAVE_API_KEY": "your_brave_api_key"},
                },
                {
                    "name": "calculator",
                    "display_name": "Calculator",
                    "description": "Mathematical calculations",
                    "command": "python",
                    "args": ["-m", "mcp_math_server"],
                    "env": None,
                },
            ]

            for server_data in builtin_servers:
                # Check if server already exists
                existing = await self.session.execute(
                    select(ToolServer).where(
                        ToolServer.name == server_data["name"]
                    )
                )

                if not existing.scalar_one_or_none():
                    # Create built-in server
                    server = ToolServer(
                        name=server_data["name"],
                        display_name=server_data["display_name"],
                        description=server_data["description"],
                        command=server_data["command"],
                        args=server_data["args"],
                        env=server_data["env"],
                        base_url=None,  # Built-in servers don't have remote URLs
                        transport_type="stdio",  # Built-in servers use stdio transport
                        is_builtin=True,
                        auto_start=True,
                        status=ServerStatus.DISABLED,
                    )

                    self.session.add(server)

            await self.session.commit()
            logger.info("Built-in servers initialized")

        except Exception as e:
            await self.session.rollback()
            logger.error(
                "Failed to initialize built-in servers", error=str(e)
            )
            raise

    async def test_connectivity(self, server_id: str) -> dict[str, Any]:
        """Test connectivity to a tool server."""
        try:
            # Get the server
            query = select(ToolServer).where(ToolServer.id == server_id)
            result = await self.session.execute(query)
            server = result.scalar_one_or_none()

            if not server:
                return {
                    "success": False,
                    "error": "Server not found",
                    "status": "not_found",
                }

            # Test connection based on server type
            if not server.is_builtin:
                # For remote servers, attempt connection
                success = await self._connect_remote_server(server)
            else:
                # For local servers, check if they're enabled/running
                success = server.status in [
                    ServerStatus.ENABLED,
                    ServerStatus.STARTING,
                ]

            server_type = (
                "remote" if not server.is_builtin else "builtin"
            )

            return {
                "success": success,
                "status": "connected" if success else "failed",
                "server_id": server_id,
                "server_name": server.name,
                "server_type": server_type,
                "is_builtin": server.is_builtin,
                "current_status": server.status.value,
            }

        except Exception as e:
            logger.error(
                "Failed to test server connectivity",
                server_id=server_id,
                error=str(e),
            )
            return {
                "success": False,
                "error": str(e),
                "status": "error",
            }

    async def discover_server_tools(self, server: ToolServer) -> None:
        """Public method to discover tools for a server."""
        await self._discover_server_tools(server)
