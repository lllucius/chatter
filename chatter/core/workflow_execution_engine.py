"""Unified workflow execution engine.

This module provides the ExecutionEngine class which consolidates all workflow
execution paths into a single, unified execution pipeline. This replaces the
previous 4 separate execution methods with one unified approach.
"""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from typing import Any

from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from chatter.core.langgraph import workflow_manager
from chatter.core.monitoring import get_monitoring_service
from chatter.core.workflow_execution_context import (
    ExecutionConfig,
    ExecutionContext,
    WorkflowType,
)
from chatter.core.workflow_execution_result import ExecutionResult
from chatter.core.workflow_graph_builder import (
    WorkflowDefinition,
    create_workflow_definition_from_model,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid
from chatter.schemas.chat import StreamingChatChunk
from chatter.schemas.execution import ExecutionRequest
from chatter.services.llm import LLMService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class ExecutionEngine:
    """Single unified execution engine for all workflow types.

    This engine replaces the previous 4 execution methods:
    - _execute_with_universal_template()
    - _execute_with_dynamic_workflow()
    - _execute_streaming_with_universal_template()
    - _execute_streaming_with_dynamic_workflow()

    With a single, unified execution pipeline that handles:
    - All workflow types (template, definition, custom, chat)
    - Both streaming and non-streaming modes
    - All resource management (LLM, tools, retriever)
    - Unified state management
    """

    def __init__(
        self,
        session: AsyncSession,
        llm_service: LLMService,
        debug_mode: bool = False,
    ):
        """Initialize the execution engine.

        Args:
            session: Database session
            llm_service: LLM service for model access
            debug_mode: Enable debug logging
        """
        self.session = session
        self.llm_service = llm_service
        
        # Initialize unified tracker
        from chatter.core.workflow_tracker import WorkflowTracker
        self.tracker = WorkflowTracker(
            session=session,
            debug_mode=debug_mode,
        )

    async def execute(
        self,
        request: ExecutionRequest,
        user_id: str,
    ) -> ExecutionResult | AsyncGenerator[StreamingChatChunk, None]:
        """Execute a workflow with unified pipeline.

        This is the single entry point for all workflow execution,
        replacing multiple execution methods with one unified approach.

        Args:
            request: Unified execution request
            user_id: ID of the user executing the workflow

        Returns:
            ExecutionResult for non-streaming, or AsyncGenerator for streaming
        """
        # Create execution context
        context = await self._create_context(request, user_id)

        # Start unified tracking
        await self.tracker.start(context)

        try:
            # Build workflow graph
            graph = await self._build_graph(context)

            # Execute based on streaming flag
            if request.streaming:
                return self._execute_streaming(graph, context)
            else:
                return await self._execute_sync(graph, context)
        except Exception as e:
            # Track failure
            await self.tracker.fail(context, e)
            raise

    async def _create_context(
        self,
        request: ExecutionRequest,
        user_id: str,
    ) -> ExecutionContext:
        """Create execution context from request.

        This method handles all workflow types and creates a unified
        execution context.

        Args:
            request: Execution request
            user_id: User ID

        Returns:
            ExecutionContext with all necessary state and resources
        """
        # Generate execution ID
        execution_id = generate_ulid()

        # Determine workflow type
        workflow_type = self._determine_workflow_type(request)

        # Create config
        config = ExecutionConfig(
            input_data=request.input_data or {},
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            system_prompt=request.system_prompt,
            enable_memory=request.enable_memory,
            enable_retrieval=request.enable_retrieval,
            enable_tools=request.enable_tools,
            enable_streaming=request.streaming,
            memory_window=request.memory_window,
            max_tool_calls=request.max_tool_calls,
            max_documents=request.max_documents,
            allowed_tools=request.allowed_tools,
            tool_config=request.tool_config,
            document_ids=request.document_ids,
            workflow_config=request.workflow_config,
        )

        # Add message to input data if provided
        if request.message:
            config.input_data["message"] = request.message

        # Get LLM
        llm = await self.llm_service.get_llm(
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # Get tools if enabled
        tools = None
        if request.enable_tools:
            tools = await self._get_tools(user_id, request.allowed_tools)

        # Get retriever if enabled
        retriever = None
        if request.enable_retrieval and request.document_ids:
            retriever = await self._get_retriever(
                user_id, request.document_ids
            )

        # Create context
        context = ExecutionContext(
            execution_id=execution_id,
            user_id=user_id,
            conversation_id=request.conversation_id,
            workflow_type=workflow_type,
            source_template_id=request.template_id,
            source_definition_id=request.definition_id,
            config=config,
            llm=llm,
            tools=tools,
            retriever=retriever,
            started_at=datetime.now(UTC),
        )

        return context

    def _determine_workflow_type(
        self, request: ExecutionRequest
    ) -> WorkflowType:
        """Determine workflow type from request.

        Args:
            request: Execution request

        Returns:
            WorkflowType enum value
        """
        if request.template_id:
            return WorkflowType.TEMPLATE
        elif request.definition_id:
            return WorkflowType.DEFINITION
        elif request.nodes and request.edges:
            return WorkflowType.CUSTOM
        else:
            return WorkflowType.CHAT

    async def _get_tools(
        self, user_id: str, allowed_tools: list[str] | None
    ) -> list[Any]:
        """Get tools for execution.

        Args:
            user_id: User ID
            allowed_tools: Optional list of allowed tool names

        Returns:
            List of tool objects
        """
        try:
            from chatter.core.tool_registry import tool_registry

            tools = await tool_registry.get_enabled_tools_for_workspace(
                workspace_id=user_id,
                user_permissions=[],
                session=self.session,
            )

            # Filter by allowed tools if specified
            if allowed_tools:
                allowed_set = set(allowed_tools)
                tools = [
                    tool
                    for tool in tools
                    if tool_registry._get_tool_name(tool) in allowed_set
                ]

            logger.info(f"Loaded {len(tools)} tools for execution")
            return tools
        except Exception as e:
            logger.warning(f"Could not load tools: {e}")
            return []

    async def _get_retriever(
        self, user_id: str, document_ids: list[str]
    ) -> Any:
        """Get retriever for execution.

        Args:
            user_id: User ID
            document_ids: List of document IDs

        Returns:
            Retriever object or None
        """
        try:
            from chatter.core.vector_store import (
                get_vector_store_retriever,
            )

            retriever = await get_vector_store_retriever(
                user_id=user_id,
                document_ids=document_ids,
            )
            logger.info(
                f"Loaded retriever for {len(document_ids)} documents"
            )
            return retriever
        except Exception as e:
            logger.warning(f"Could not load retriever: {e}")
            return None

    async def _build_graph(self, context: ExecutionContext) -> Any:
        """Build workflow graph from context.

        Args:
            context: Execution context

        Returns:
            Compiled LangGraph workflow (Pregel)
        """
        # Get or create workflow definition
        if context.workflow_type == WorkflowType.DEFINITION:
            # Load from stored definition
            definition = await self._load_definition(
                context.source_definition_id
            )
            graph_definition = create_workflow_definition_from_model(
                definition
            )
        elif context.workflow_type == WorkflowType.TEMPLATE:
            # Load from template
            template = await self._load_template(
                context.source_template_id
            )
            graph_definition = create_workflow_definition_from_model(
                template
            )
        elif context.workflow_type == WorkflowType.CUSTOM:
            # Create from nodes and edges in config
            graph_definition = self._create_custom_definition(context)
        else:
            # Create simple chat workflow
            graph_definition = self._create_chat_definition(context)

        # Build and compile graph
        workflow = await workflow_manager.create_workflow_from_definition(
            definition=graph_definition,
            llm=context.llm,
            retriever=context.retriever,
            tools=context.tools,
            max_tool_calls=context.config.max_tool_calls,
            user_id=context.user_id,
            conversation_id=context.conversation_id,
        )

        return workflow

    async def _load_template(self, template_id: str | None) -> Any:
        """Load workflow template from database.

        Args:
            template_id: Template ID

        Returns:
            WorkflowTemplate model
        """
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        if not template_id:
            raise ValueError("Template ID is required for template workflow type")

        workflow_service = WorkflowManagementService(self.session)
        template = await workflow_service.get_workflow_template(
            template_id=template_id
        )

        if not template:
            raise ValueError(f"Template not found: {template_id}")

        return template

    async def _load_definition(self, definition_id: str | None) -> Any:
        """Load workflow definition from database.

        Args:
            definition_id: Definition ID

        Returns:
            WorkflowDefinition model
        """
        from chatter.services.workflow_management import (
            WorkflowManagementService,
        )

        workflow_service = WorkflowManagementService(self.session)
        # We'll need to get the owner_id - for now use a placeholder
        # This will be properly handled when integrating with the service
        definition = await workflow_service.get_workflow_definition(
            workflow_id=definition_id,
            owner_id=None,  # TODO: Get from context
        )
        return definition

    def _create_custom_definition(
        self, context: ExecutionContext
    ) -> WorkflowDefinition:
        """Create workflow definition from custom nodes/edges.

        Args:
            context: Execution context

        Returns:
            WorkflowDefinition for graph builder
        """
        definition = WorkflowDefinition()

        # Get nodes and edges from config
        nodes = context.config.workflow_config.get("nodes", [])
        edges = context.config.workflow_config.get("edges", [])

        # Add nodes
        for node in nodes:
            definition.add_node(
                node_id=node["id"],
                node_type=node["type"],
                config=node.get("config", {}),
            )

        # Add edges
        for edge in edges:
            definition.add_edge(
                source=edge["source"],
                target=edge["target"],
                condition=edge.get("condition"),
            )

        return definition

    def _create_chat_definition(
        self, context: ExecutionContext
    ) -> WorkflowDefinition:
        """Create simple chat workflow definition.

        Args:
            context: Execution context

        Returns:
            WorkflowDefinition for graph builder
        """
        from chatter.core.workflow_graph_builder import (
            create_simple_workflow_definition,
        )

        return create_simple_workflow_definition(
            enable_memory=context.config.enable_memory,
            enable_retrieval=context.config.enable_retrieval,
            enable_tools=context.config.enable_tools,
            memory_window=context.config.memory_window,
            max_tool_calls=context.config.max_tool_calls,
            system_message=context.config.system_prompt,
        )

    async def _execute_sync(
        self, graph: Any, context: ExecutionContext
    ) -> ExecutionResult:
        """Execute workflow synchronously.

        Args:
            graph: Compiled workflow graph
            context: Execution context

        Returns:
            ExecutionResult with workflow output
        """
        start_time = time.time()

        try:
            # Create initial state
            initial_state = self._create_initial_state(context)

            # Run workflow
            result = await workflow_manager.run_workflow(
                workflow=graph,
                initial_state=initial_state,
                thread_id=context.thread_id,
            )

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Create execution result
            execution_result = ExecutionResult.from_raw(
                raw_result=result,
                execution_id=context.execution_id,
                conversation_id=context.conversation_id,
                workflow_type=context.workflow_type.value,
            )
            execution_result.execution_time_ms = execution_time_ms

            # Update context
            context.completed_at = datetime.now(UTC)

            # Track completion
            await self.tracker.complete(context, execution_result)

            return execution_result
        except Exception as e:
            # Tracking of failure is done in execute() method
            raise

    async def _execute_streaming(
        self, graph: Any, context: ExecutionContext
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming.

        Args:
            graph: Compiled workflow graph
            context: Execution context

        Yields:
            StreamingChatChunk for each token
        """
        start_time = time.time()

        # Create initial state
        initial_state = self._create_initial_state(context)

        # Accumulate result data for final tracking
        content_buffer = ""
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0

        try:
            # Stream workflow execution
            async for update in workflow_manager.stream_workflow(
                workflow=graph,
                initial_state=initial_state,
                thread_id=context.thread_id,
            ):
                # Process streaming updates
                event_name = update.get("event")

                # Handle chat model streaming events
                if event_name in ["on_chat_model_stream", "on_llm_stream"]:
                    data = update.get("data", {})
                    chunk = data.get("chunk", {})

                    # Extract content
                    content = ""
                    if hasattr(chunk, "content"):
                        content = chunk.content
                    elif isinstance(chunk, dict):
                        content = chunk.get("content", "")

                    if content:
                        content_buffer += content
                        yield StreamingChatChunk(
                            type="token",
                            content=content,
                            metadata={"event": event_name},
                        )

                # Handle completion event
                elif event_name == "on_chat_model_end":
                    data = update.get("data", {})
                    output = data.get("output", {})

                    # Extract usage metadata
                    usage_metadata = {}
                    if hasattr(output, "usage_metadata"):
                        usage_metadata = output.usage_metadata or {}
                    elif isinstance(output, dict):
                        usage_metadata = output.get("usage_metadata", {})

                    # Capture token counts
                    total_tokens = usage_metadata.get("total_tokens", 0)
                    input_tokens = usage_metadata.get("input_tokens", 0)
                    output_tokens = usage_metadata.get("output_tokens", 0)

                    yield StreamingChatChunk(
                        type="complete",
                        content="",
                        metadata={
                            "streaming_complete": True,
                            "total_tokens": total_tokens,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                        },
                    )

            # Calculate execution time
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Send done marker
            yield StreamingChatChunk(
                type="done",
                content="",
                metadata={"execution_time_ms": execution_time_ms},
            )

            # Update context
            context.completed_at = datetime.now(UTC)

            # Create result for tracking
            execution_result = ExecutionResult(
                response=content_buffer,
                execution_time_ms=execution_time_ms,
                tokens_used=total_tokens,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
                execution_id=context.execution_id,
                conversation_id=context.conversation_id,
                workflow_type=context.workflow_type.value,
            )

            # Track completion
            await self.tracker.complete(context, execution_result)

        except Exception as e:
            # Tracking of failure is done in execute() method
            raise

    def _create_initial_state(
        self, context: ExecutionContext
    ) -> WorkflowNodeContext:
        """Create initial workflow state.

        Args:
            context: Execution context

        Returns:
            WorkflowNodeContext for execution
        """
        # Get message from input data
        message = context.config.input_data.get("message", "")

        # Create initial state
        initial_state: WorkflowNodeContext = {
            "messages": [HumanMessage(content=message)] if message else [],
            "user_id": context.user_id,
            "conversation_id": context.conversation_id or "",
            "retrieval_context": None,
            "conversation_summary": None,
            "tool_call_count": 0,
            "metadata": {
                "provider": context.config.provider,
                "model": context.config.model,
                "temperature": context.config.temperature,
                "max_tokens": context.config.max_tokens,
                "workflow_type": context.workflow_type.value,
                **context.metadata,
            },
            "variables": {},
            "loop_state": {},
            "error_state": {},
            "conditional_results": {},
            "execution_history": [],
            "usage_metadata": {},
        }

        return initial_state
