"""LangGraph workflow manager with flexible node support.

This provides the main workflow management capabilities with support for
all defined node types including conditional, loop, variable, and error
handler nodes.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver

try:
    from langgraph.checkpoint.redis import RedisSaver
    REDIS_AVAILABLE = True
except ImportError:
    RedisSaver = None
    REDIS_AVAILABLE = False

from langgraph.pregel import Pregel

from chatter.config import settings
from chatter.core.workflow_graph_builder import (
    WorkflowDefinition,
    WorkflowGraphBuilder,
    create_simple_workflow_definition,
)
from chatter.core.workflow_node_factory import WorkflowNodeContext
from chatter.models.base import generate_ulid
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


# Define ConversationState for backward compatibility with tests
class ConversationState(WorkflowNodeContext):
    """Backward compatible state type for existing tests."""
    pass


class LangGraphWorkflowManager:
    """Workflow manager with flexible node support."""
    
    def __init__(self):
        """Initialize the modern workflow manager."""
        self.checkpointer = None
        self._redis_context_manager = None
        self._initialized = False
        self.graph_builder = WorkflowGraphBuilder()
        
    async def _ensure_initialized(self) -> None:
        """Ensure the workflow manager is initialized."""
        if self._initialized:
            return
            
        # Initialize checkpointer
        self.checkpointer = None
        try:
            if (
                settings.langgraph_checkpoint_store == "redis"
                and REDIS_AVAILABLE
            ):
                try:
                    redis_url = settings.redis_url_for_env
                    self._redis_context_manager = RedisSaver.from_conn_string(redis_url)
                    self.checkpointer = await self._redis_context_manager.__aenter__()
                    logger.info("Initialized Redis checkpointer")
                except Exception as e:
                    logger.warning(f"Failed to initialize Redis checkpointer: {e}")
                    self.checkpointer = MemorySaver()
                    logger.info("Fallback to memory checkpointer")
            else:
                self.checkpointer = MemorySaver()
                logger.info("Using memory checkpointer")
        except Exception as e:
            logger.error(f"Failed to initialize checkpointer: {e}")
            self.checkpointer = MemorySaver()
            
        self._initialized = True
        
    async def create_workflow_from_definition(
        self,
        definition: WorkflowDefinition,
        llm: BaseChatModel,
        retriever: Any = None,
        tools: List[Any] | None = None,
        max_tool_calls: int = 10,
        **kwargs
    ) -> Pregel:
        """Create a workflow from a flexible definition."""
        await self._ensure_initialized()
        
        # Build the graph
        workflow = self.graph_builder.build_graph(
            definition=definition,
            llm=llm,
            retriever=retriever,
            tools=tools,
            **kwargs
        )
        
        # Compile with checkpointer
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )
        
        # Configure recursion limit
        recursion_limit = max(max_tool_calls * 3 + 10, 25)
        app.recursion_limit = recursion_limit
        
        logger.debug(
            "Created modern workflow",
            nodes=len(definition.nodes),
            edges=len(definition.edges),
            recursion_limit=recursion_limit,
        )
        
        return app
        
    async def create_workflow(
        self,
        llm: BaseChatModel,
        *,
        enable_retrieval: bool = False,
        enable_tools: bool = False,
        system_message: str | None = None,
        retriever: Any | None = None,
        tools: list[Any] | None = None,
        enable_memory: bool = False,
        memory_window: int = 10,
        user_id: str | None = None,
        conversation_id: str | None = None,
        provider_name: str | None = None,
        model_name: str | None = None,
        max_tool_calls: int | None = None,
        max_documents: int | None = None,
        enable_streaming: bool = False,
        focus_mode: bool = False,
        **kwargs,
    ) -> Pregel:
        """Create a workflow using the modern flexible system.
        
        This method provides backward compatibility with the original API
        while using the new flexible node system underneath.
        """
        # Create a simple workflow definition that matches the original behavior
        definition = create_simple_workflow_definition(
            enable_memory=enable_memory,
            enable_retrieval=enable_retrieval,
            enable_tools=enable_tools,
            memory_window=memory_window,
            max_tool_calls=max_tool_calls or 10,
            system_message=system_message,
        )
        
        return await self.create_workflow_from_definition(
            definition=definition,
            llm=llm,
            retriever=retriever,
            tools=tools,
            max_tool_calls=max_tool_calls or 10,
            **kwargs
        )
        
    async def create_custom_workflow(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        llm: BaseChatModel,
        entry_point: str | None = None,
        retriever: Any = None,
        tools: List[Any] | None = None,
        max_tool_calls: int = 10,
        **kwargs
    ) -> Pregel:
        """Create a custom workflow from node and edge definitions.
        
        This method allows creating complex workflows with conditional nodes,
        loops, variables, and error handlers.
        
        Args:
            nodes: List of node definitions with id, type, and config
            edges: List of edge definitions with source, target, and optional condition
            llm: Language model to use
            entry_point: Optional explicit entry point
            retriever: Optional retriever for document search
            tools: Optional tools for tool-calling
            max_tool_calls: Maximum number of tool calls allowed
            **kwargs: Additional arguments passed to LLM calls
            
        Returns:
            Compiled LangGraph workflow
        """
        definition = WorkflowDefinition()
        
        # Add nodes
        for node in nodes:
            definition.add_node(
                node_id=node["id"],
                node_type=node["type"],
                config=node.get("config", {})
            )
            
        # Add edges
        for edge in edges:
            definition.add_edge(
                source=edge["source"],
                target=edge["target"],
                condition=edge.get("condition")
            )
            
        # Set entry point
        if entry_point:
            definition.set_entry_point(entry_point)
            
        return await self.create_workflow_from_definition(
            definition=definition,
            llm=llm,
            retriever=retriever,
            tools=tools,
            max_tool_calls=max_tool_calls,
            **kwargs
        )
        
    async def run_workflow(
        self,
        workflow: Pregel,
        initial_state: Dict[str, Any],
        thread_id: str | None = None,
    ) -> Dict[str, Any]:
        """Run a workflow with enhanced state management."""
        if not thread_id:
            thread_id = generate_ulid()
            
        config = {"configurable": {"thread_id": thread_id}}
        
        # Convert to modern context format if needed
        context = self._ensure_modern_context(initial_state)
        
        try:
            start_time = time.time()
            result = await workflow.ainvoke(context, config=config)
            execution_time = int((time.time() - start_time) * 1000)
            
            # Add execution metadata
            result["metadata"] = result.get("metadata", {})
            result["metadata"]["execution_time_ms"] = execution_time
            result["metadata"]["thread_id"] = thread_id
            
            return result
        except Exception as e:
            logger.error(
                "Modern workflow execution failed",
                error=str(e),
                thread_id=thread_id,
            )
            raise
            
    def _ensure_modern_context(self, state: Dict[str, Any]) -> WorkflowNodeContext:
        """Ensure the state has all required fields for modern context."""
        # Convert old ConversationState to new WorkflowNodeContext
        context: WorkflowNodeContext = {
            "messages": state.get("messages", []),
            "user_id": state.get("user_id", ""),
            "conversation_id": state.get("conversation_id", ""),
            "retrieval_context": state.get("retrieval_context"),
            "conversation_summary": state.get("conversation_summary"),
            "tool_call_count": state.get("tool_call_count", 0),
            "metadata": state.get("metadata", {}),
            
            # New fields for advanced features
            "variables": state.get("variables", {}),
            "loop_state": state.get("loop_state", {}),
            "error_state": state.get("error_state", {}),
            "conditional_results": state.get("conditional_results", {}),
            "execution_history": state.get("execution_history", []),
        }
        
        return context
        
    async def stream_workflow(
        self,
        workflow: Pregel,
        initial_state: Dict[str, Any],
        thread_id: str | None = None,
        enable_llm_streaming: bool = False,
        enable_node_tracing: bool = False,
    ) -> Any:
        """Stream workflow execution with enhanced context."""
        if not thread_id:
            thread_id = generate_ulid()
            
        config = {"configurable": {"thread_id": thread_id}}
        context = self._ensure_modern_context(initial_state)
        
        try:
            if enable_llm_streaming:
                # Use astream_events for token-by-token streaming
                async for event in workflow.astream_events(
                    context, config=config, version="v2"
                ):
                    if enable_node_tracing or event.get("name") in ["on_chat_model_stream"]:
                        yield event
            else:
                # Use regular astream for node-by-node updates
                async for update in workflow.astream(context, config=config):
                    yield update
        except Exception as e:
            logger.error(
                "Modern workflow streaming failed",
                error=str(e),
                thread_id=thread_id,
            )
            raise
            
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._redis_context_manager:
            try:
                await self._redis_context_manager.__aexit__(None, None, None)
            except Exception as e:
                logger.warning(f"Error cleaning up Redis context: {e}")
                
    def get_supported_node_types(self) -> List[str]:
        """Get list of supported node types."""
        from chatter.core.workflow_node_factory import WorkflowNodeFactory
        
        # Factory is now the single source of truth for all node types
        return WorkflowNodeFactory.get_supported_types()
        
    def validate_workflow_definition(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate a workflow definition and return validation results."""
        errors = []
        warnings = []
        
        try:
            definition = WorkflowDefinition()
            
            # Add nodes and validate
            for node in nodes:
                if "id" not in node:
                    errors.append("Node missing required 'id' field")
                    continue
                if "type" not in node:
                    errors.append(f"Node {node['id']} missing required 'type' field")
                    continue
                    
                node_type = node["type"]
                supported_types = self.get_supported_node_types()
                
                if node_type not in supported_types:
                    warnings.append(f"Unknown node type: {node_type}")
                else:
                    try:
                        definition.add_node(node["id"], node_type, node.get("config", {}))
                    except ValueError as e:
                        errors.append(f"Node {node['id']} configuration error: {str(e)}")
                        
            # Add edges and validate
            for edge in edges:
                if "source" not in edge or "target" not in edge:
                    errors.append("Edge missing required 'source' or 'target' field")
                    continue
                    
                definition.add_edge(edge["source"], edge["target"], edge.get("condition"))
                
            # Validate overall structure
            if definition.nodes:
                try:
                    self.graph_builder._validate_definition(definition)
                except ValueError as e:
                    errors.append(str(e))
                    
        except Exception as e:
            errors.append(f"Validation failed: {str(e)}")
            
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "supported_node_types": self.get_supported_node_types(),
        }


# Create a singleton instance
workflow_manager = LangGraphWorkflowManager()