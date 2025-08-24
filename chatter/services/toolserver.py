"""Enhanced tool server service with database persistence and CRUD operations."""

import asyncio
from datetime import UTC, datetime

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
from chatter.services.mcp import MCPToolService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ToolServerServiceError(Exception):
    """Tool server service error."""

    pass


class ToolServerService:
    """Enhanced service for managing tool servers with database persistence."""

    def __init__(self, session: AsyncSession):
        """Initialize tool server service.

        Args:
            session: Database session
        """
        self.session = session
        self.mcp_service = MCPToolService()
        self._health_check_interval = 300  # 5 minutes
        self._last_health_check = {}

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

            # Create server model
            server = ToolServer(
                name=server_data.name,
                display_name=server_data.display_name,
                description=server_data.description,
                command=server_data.command,
                args=server_data.args,
                env=server_data.env,
                auto_start=server_data.auto_start,
                auto_update=server_data.auto_update,
                max_failures=server_data.max_failures,
                created_by=user_id,
                status=ServerStatus.DISABLED,
            )

            self.session.add(server)
            await self.session.flush()

            # Auto-start if requested
            if server_data.auto_start:
                await self._start_server_internal(server)

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
            filters.append(ToolServer.is_builtin is False)

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

            success = await self._start_server_internal(server)
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

            # Auto-start if configured
            if server.auto_start:
                await self._start_server_internal(server)

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
            uptime_percentage=None,  # TODO: Implement uptime tracking
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

    async def _start_server_internal(self, server: ToolServer) -> bool:
        """Internal method to start a server.

        Args:
            server: Server model

        Returns:
            True if started successfully
        """
        try:
            server.status = ServerStatus.STARTING
            server.updated_at = datetime.now(UTC)

            # Add server to MCP service if not already there
            if server.name not in self.mcp_service.servers:
                from chatter.services.mcp import MCPServer

                mcp_server = MCPServer(
                    name=server.name,
                    command=server.command,
                    args=server.args,
                    env=server.env,
                )
                self.mcp_service.servers[server.name] = mcp_server

            # Start the server
            success = await self.mcp_service.start_server(server.name)

            if success:
                server.status = ServerStatus.ENABLED
                server.last_startup_success = datetime.now(UTC)
                server.last_startup_error = None
                server.consecutive_failures = 0

                # Discover and update tools
                await self._discover_server_tools(server)
            else:
                server.status = ServerStatus.ERROR
                server.last_startup_error = "Failed to start server"
                server.consecutive_failures += 1

                # Disable if too many failures
                if server.consecutive_failures >= server.max_failures:
                    server.status = ServerStatus.DISABLED

            server.updated_at = datetime.now(UTC)
            return success

        except Exception as e:
            server.status = ServerStatus.ERROR
            server.last_startup_error = str(e)
            server.consecutive_failures += 1
            server.updated_at = datetime.now(UTC)

            if server.consecutive_failures >= server.max_failures:
                server.status = ServerStatus.DISABLED

            logger.error(
                "Failed to start server",
                server_id=server.id,
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

            # Stop the server
            success = await self.mcp_service.stop_server(server.name)

            server.status = ServerStatus.DISABLED
            server.updated_at = datetime.now(UTC)

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
        """Discover and update tools for a server.

        Args:
            server: Server model
        """
        try:
            # Get tools from MCP service
            mcp_tools = self.mcp_service.tools_cache.get(
                server.name, []
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
            for mcp_tool in mcp_tools:
                tool_name = mcp_tool.name

                if tool_name in existing_tools:
                    # Update existing tool
                    tool = existing_tools[tool_name]
                    tool.description = mcp_tool.description
                    tool.args_schema = getattr(
                        mcp_tool, "args_schema", None
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
                        description=mcp_tool.description,
                        args_schema=getattr(
                            mcp_tool, "args_schema", None
                        ),
                        status=ToolStatus.ENABLED,
                        is_available=True,
                    )
                    self.session.add(tool)

            # Mark tools not found as unavailable
            found_tool_names = {tool.name for tool in mcp_tools}
            for tool_name, tool in existing_tools.items():
                if tool_name not in found_tool_names:
                    tool.is_available = False
                    tool.updated_at = datetime.now(UTC)

        except Exception as e:
            logger.error(
                "Failed to discover server tools",
                server_id=server.id,
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
                        "/tmp",
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
