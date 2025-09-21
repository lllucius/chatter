"""Unified workflow execution engine that handles all workflow types."""

from __future__ import annotations

import time
from collections.abc import AsyncGenerator
from typing import Any

from chatter.core.workflow_capabilities import WorkflowSpec
from chatter.models.conversation import (
    Conversation,
    Message,
    MessageRole,
)
from chatter.schemas.chat import ChatRequest, StreamingChatChunk
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class WorkflowExecutionError(Exception):
    """Base exception for workflow execution errors."""

    pass


class WorkflowNodeExecutor:
    """Executes individual workflow nodes."""

    def __init__(self, llm_service, message_service):
        self.llm_service = llm_service
        self.message_service = message_service

    async def execute_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute a single workflow node."""
        node_type = node.get('type') or node.get('data', {}).get(
            'nodeType'
        )

        if node_type == 'start':
            return await self._execute_start_node(
                node, context, conversation, spec
            )
        elif node_type == 'model' or node_type == 'llm':
            return await self._execute_llm_node(
                node, context, conversation, spec
            )
        elif node_type == 'retrieval':
            return await self._execute_retrieval_node(
                node, context, conversation, spec
            )
        elif node_type == 'tool':
            return await self._execute_tool_node(
                node, context, conversation, spec
            )
        elif node_type == 'end':
            return await self._execute_end_node(
                node, context, conversation, spec
            )
        else:
            logger.warning(f"Unknown node type: {node_type}")
            return context

    async def _execute_start_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute start node - initialize context."""
        context['workflow_started'] = True
        context['start_time'] = time.time()
        return context

    async def _execute_llm_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute LLM node - generate response."""
        node_config = node.get('data', {}).get('config', {})

        # Use node config or fall back to spec config
        provider = node_config.get('provider', spec.provider)
        model = node_config.get('model', spec.model)
        temperature = node_config.get('temperature', spec.temperature)
        max_tokens = node_config.get('max_tokens', spec.max_tokens)
        system_prompt = node_config.get(
            'system_prompt', spec.system_prompt
        )

        # Build prompt from context
        # Get conversation messages using the message service
        user_id = context.get('user_id')
        if not user_id:
            raise WorkflowExecutionError("user_id not found in context")
        
        conversation_messages = await self.message_service.get_conversation_messages(
            conversation.id, user_id, include_system=True
        )
        
        # Convert to LangChain format using the LLM service
        messages = self.llm_service.convert_conversation_to_messages(
            conversation, conversation_messages
        )

        # Add context from retrieval if available
        if context.get('retrieval_context'):
            context_prompt = (
                f"Context: {context['retrieval_context']}\n\n"
            )
            if messages and hasattr(messages[-1], 'content'):
                messages[-1].content = (
                    context_prompt + messages[-1].content
                )

        # Create ChatRequest for execution
        chat_request = ChatRequest(
            message=context.get('user_message', ''),
            conversation_id=conversation.id,
            provider=provider,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt_override=system_prompt,
            workflow_type=spec.capabilities.get_workflow_type(),
        )

        # Use the unified executor to process
        from chatter.core.unified_workflow_executor import (
            UnifiedWorkflowExecutor,
        )

        executor = UnifiedWorkflowExecutor(
            self.llm_service, self.message_service, None
        )

        # Generate correlation ID
        from chatter.utils.correlation import get_correlation_id

        correlation_id = get_correlation_id()

        # Execute through unified executor
        message, usage_info = await executor.execute(
            conversation, chat_request, correlation_id
        )

        context['llm_response'] = message.content
        context['usage_info'] = usage_info

        return context

    async def _execute_retrieval_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute retrieval node - fetch relevant documents."""
        if not spec.capabilities.enable_retrieval:
            logger.warning(
                "Retrieval node in workflow but retrieval not enabled"
            )
            return context

        node_config = node.get('data', {}).get('config', {})

        # Extract retrieval parameters
        top_k = node_config.get('k', node_config.get('top_k', 5))
        # score_threshold = node_config.get('score_threshold', 0.5)  # Not used
        # retriever_name = node_config.get('retriever', 'default')  # Not used

        # Use message service to get retrieval service
        try:
            # Get the user message for retrieval
            user_message = context.get('user_message', '')
            if not user_message and conversation.messages:
                # Get the last human message
                for msg in reversed(conversation.messages):
                    if msg.role == MessageRole.USER:
                        user_message = msg.content
                        break

            # Mock retrieval for now - in real implementation would use retrieval service
            context[
                'retrieval_context'
            ] = f"Retrieved context for: {user_message[:100]}..."
            context['retrieved_documents'] = []

            logger.info(f"Executed retrieval node with top_k={top_k}")

        except Exception as e:
            logger.error(f"Retrieval node execution failed: {e}")
            context['retrieval_error'] = str(e)

        return context

    async def _execute_tool_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute tool node - call external tools."""
        if not spec.capabilities.enable_tools:
            logger.warning(
                "Tool node in workflow but tools not enabled"
            )
            return context

        node_config = node.get('data', {}).get('config', {})

        # Extract tool parameters
        tool_name = node_config.get('tool_name', 'unknown')
        tool_params = node_config.get('tool_params', {})

        # Mock tool execution for now
        context['tool_results'] = {
            'tool_name': tool_name,
            'result': f"Mock result from {tool_name}",
            'parameters': tool_params,
        }

        logger.info(f"Executed tool node: {tool_name}")

        return context

    async def _execute_end_node(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict[str, Any]:
        """Execute end node - finalize execution."""
        context['workflow_completed'] = True
        context['end_time'] = time.time()

        if 'start_time' in context:
            context['execution_time_ms'] = int(
                (context['end_time'] - context['start_time']) * 1000
            )

        return context


class UnifiedWorkflowEngine:
    """Unified execution engine for all workflow types."""

    def __init__(
        self, llm_service, message_service, template_manager=None
    ):
        self.llm_service = llm_service
        self.message_service = message_service
        self.template_manager = template_manager
        self.node_executor = WorkflowNodeExecutor(
            llm_service, message_service
        )

    async def execute_workflow(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        input_data: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> tuple[Message, dict[str, Any]]:
        """Execute a workflow based on its specification."""
        start_time = time.time()

        try:
            # Initialize execution context
            context = {
                'user_id': user_id,
                'conversation_id': conversation.id,
                'input_data': input_data or {},
                'spec': spec,
                'user_message': (
                    input_data.get('message', '') if input_data else ''
                ),
            }

            if spec.nodes and spec.edges:
                # Execute defined workflow with nodes and edges
                result_context = await self._execute_defined_workflow(
                    spec, conversation, context
                )
            else:
                # Execute capability-based workflow
                result_context = (
                    await self._execute_capability_workflow(
                        spec, conversation, context
                    )
                )

            # Extract or create final message
            if 'llm_response' in result_context:
                # Create message from LLM response
                message = Message(
                    id=None,  # Will be set by database
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=result_context['llm_response'],
                    extra_metadata={
                        'workflow_spec': spec.__dict__,
                        'execution_context': {
                            k: v
                            for k, v in result_context.items()
                            if k not in ['spec', 'llm_response']
                        },
                    },
                )
            else:
                # Fallback message
                message = Message(
                    id=None,
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content="Workflow completed successfully.",
                    extra_metadata={'workflow_spec': spec.__dict__},
                )

            # Prepare usage info
            usage_info = result_context.get('usage_info', {})
            usage_info['execution_time_ms'] = int(
                (time.time() - start_time) * 1000
            )
            usage_info['nodes_executed'] = result_context.get(
                'nodes_executed', 0
            )

            return message, usage_info

        except Exception as e:
            logger.error(
                f"Workflow execution failed: {e}", exc_info=True
            )
            raise WorkflowExecutionError(
                f"Workflow execution failed: {str(e)}"
            ) from e

    async def _execute_defined_workflow(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a workflow with defined nodes and edges."""
        if not spec.nodes:
            raise WorkflowExecutionError("No nodes defined in workflow")

        # Build execution order from nodes and edges
        execution_order = self._build_execution_order(
            spec.nodes, spec.edges or []
        )

        nodes_executed = 0
        for node_id in execution_order:
            node = next(
                (n for n in spec.nodes if n['id'] == node_id), None
            )
            if not node:
                logger.warning(
                    f"Node {node_id} not found in workflow definition"
                )
                continue

            logger.info(
                f"Executing node: {node_id} ({node.get('type', 'unknown')})"
            )
            context = await self.node_executor.execute_node(
                node, context, conversation, spec
            )
            nodes_executed += 1

        context['nodes_executed'] = nodes_executed
        return context

    async def _execute_capability_workflow(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a capability-based workflow."""
        # Create a simple linear workflow based on capabilities
        nodes_executed = 0

        # Start node
        context = await self._simulate_start_node(context, spec)
        nodes_executed += 1

        # Retrieval node (if enabled)
        if spec.capabilities.enable_retrieval:
            context = await self._simulate_retrieval_node(
                context, conversation, spec
            )
            nodes_executed += 1

        # LLM node (always present)
        context = await self._simulate_llm_node(
            context, conversation, spec
        )
        nodes_executed += 1

        # Tool node (if enabled and tools needed)
        if spec.capabilities.enable_tools:
            context = await self._simulate_tool_node(
                context, conversation, spec
            )
            nodes_executed += 1

        # End node
        context = await self._simulate_end_node(context, spec)
        nodes_executed += 1

        context['nodes_executed'] = nodes_executed
        return context

    def _build_execution_order(
        self, nodes: list[dict], edges: list[dict]
    ) -> list[str]:
        """Build execution order from nodes and edges using topological sort."""
        # Simple implementation - in practice would use proper topological sort
        node_ids = [node['id'] for node in nodes]

        # Find start node
        start_nodes = [
            n['id'] for n in nodes if n.get('type') == 'start'
        ]
        if not start_nodes:
            # If no start node, use first node
            return node_ids

        # Build adjacency list
        graph = {node_id: [] for node_id in node_ids}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source in graph and target in node_ids:
                graph[source].append(target)

        # Simple DFS traversal from start node
        visited = set()
        order = []

        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            order.append(node_id)
            for neighbor in graph.get(node_id, []):
                dfs(neighbor)

        # Start with start nodes
        for start_node in start_nodes:
            dfs(start_node)

        # Add any unvisited nodes
        for node_id in node_ids:
            if node_id not in visited:
                dfs(node_id)

        return order

    async def _simulate_start_node(
        self, context: dict, spec: WorkflowSpec
    ) -> dict:
        """Simulate start node execution."""
        mock_start_node = {'type': 'start', 'data': {'config': {}}}
        return await self.node_executor.execute_node(
            mock_start_node, context, None, spec
        )

    async def _simulate_retrieval_node(
        self,
        context: dict,
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict:
        """Simulate retrieval node execution."""
        mock_retrieval_node = {
            'type': 'retrieval',
            'data': {
                'config': {
                    'top_k': spec.capabilities.max_documents,
                    'score_threshold': 0.5,
                }
            },
        }
        return await self.node_executor.execute_node(
            mock_retrieval_node, context, conversation, spec
        )

    async def _simulate_llm_node(
        self,
        context: dict,
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict:
        """Simulate LLM node execution."""
        mock_llm_node = {
            'type': 'model',
            'data': {
                'config': {
                    'provider': spec.provider,
                    'model': spec.model,
                    'temperature': spec.temperature,
                    'max_tokens': spec.max_tokens,
                    'system_prompt': spec.system_prompt,
                }
            },
        }
        return await self.node_executor.execute_node(
            mock_llm_node, context, conversation, spec
        )

    async def _simulate_tool_node(
        self,
        context: dict,
        conversation: Conversation,
        spec: WorkflowSpec,
    ) -> dict:
        """Simulate tool node execution."""
        mock_tool_node = {
            'type': 'tool',
            'data': {
                'config': {
                    'max_tool_calls': spec.capabilities.max_tool_calls
                }
            },
        }
        return await self.node_executor.execute_node(
            mock_tool_node, context, conversation, spec
        )

    async def _simulate_end_node(
        self, context: dict, spec: WorkflowSpec
    ) -> dict:
        """Simulate end node execution."""
        mock_end_node = {'type': 'end', 'data': {'config': {}}}
        return await self.node_executor.execute_node(
            mock_end_node, context, None, spec
        )

    async def execute_workflow_streaming(
        self,
        spec: WorkflowSpec,
        conversation: Conversation,
        input_data: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> AsyncGenerator[StreamingChatChunk, None]:
        """Execute workflow with streaming support."""
        # For now, execute non-streaming and yield result
        # In full implementation, would stream from individual nodes
        message, usage_info = await self.execute_workflow(
            spec, conversation, input_data, user_id
        )

        # Yield streaming chunks
        yield StreamingChatChunk(
            type="content",
            content=message.content,
            conversation_id=conversation.id,
            metadata=usage_info,
        )

        yield StreamingChatChunk(
            type="done",
            content="",
            conversation_id=conversation.id,
            metadata={"final": True},
        )
