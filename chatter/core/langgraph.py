"""LangGraph workflows for advanced conversation logic."""

from collections.abc import Sequence
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.redis import RedisSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.pregel import Pregel

from chatter.models.base import generate_ulid

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)

# Import new workflow components with graceful fallback
try:
    from chatter.core.workflow_security import workflow_security_manager

    METRICS_ENABLED = False  # Metrics not currently implemented
    SECURITY_ENABLED = True
except ImportError:
    logger.warning("Workflow security module not available")
    METRICS_ENABLED = False
    SECURITY_ENABLED = False


class ConversationState(TypedDict):
    """State for conversation workflows."""

    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    conversation_id: str
    retrieval_context: str | None
    tool_calls: list[dict[str, Any]]
    metadata: dict[str, Any]
    # Advanced features
    conversation_summary: str | None
    parent_conversation_id: str | None  # For conversation branching
    branch_id: str | None  # For conversation forking
    memory_context: dict[str, Any]  # For conversation memory
    workflow_template: str | None  # For conversation templates
    a_b_test_group: str | None  # For A/B testing


WorkflowMode = Literal["plain", "rag", "tools", "full"]


class LangGraphWorkflowManager:
    """Manager for LangGraph conversation workflows."""

    def __init__(self) -> None:
        """Initialize the workflow manager."""
        self.checkpointer = None
        self._redis_context_manager = (
            None  # Store context manager for RedisSaver
        )

        # Lazy initialization flag to avoid async setup at import time
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure the workflow manager is initialized."""
        if self._initialized:
            return

        # Initialize checkpointer
        self.checkpointer = None
        try:
            if settings.langgraph_checkpoint_store == "redis":
                # Use Redis checkpointer for production
                try:
                    # Use Redis URL from settings for checkpoint store
                    redis_url = settings.redis_url_for_env

                    # Use RedisSaver with proper context manager handling
                    # RedisSaver.from_conn_string() returns a context manager
                    self._redis_context_manager = (
                        RedisSaver.from_conn_string(redis_url)
                    )
                    self.checkpointer = (
                        self._redis_context_manager.__enter__()
                    )
                    self.checkpointer.setup()
                    logger.info(
                        "LangGraph Redis checkpointer initialized"
                    )

                except Exception as redis_error:
                    logger.warning(
                        "Failed to initialize Redis checkpointer, falling back to memory",
                        error=str(redis_error),
                    )
                    # Clean up context manager if it was created
                    if self._redis_context_manager:
                        try:
                            self._redis_context_manager.__exit__(
                                None, None, None
                            )
                        except Exception:
                            pass  # Ignore cleanup errors
                        self._redis_context_manager = None
                    self.checkpointer = MemorySaver()
                    logger.info(
                        "LangGraph Memory checkpointer initialized (redis fallback)"
                    )
            else:
                # Fallback to in-memory checkpointer for development
                self.checkpointer = MemorySaver()
                logger.info("LangGraph Memory checkpointer initialized")
        except Exception as e:
            logger.warning(
                "Failed to initialize checkpointer, falling back to memory",
                error=str(e),
            )
            # Always ensure we have a working checkpointer - fallback to MemorySaver directly
            self.checkpointer = MemorySaver()
            logger.info(
                "LangGraph Memory checkpointer initialized (exception fallback)"
            )

        # Final safety check - ensure we always have a working checkpointer
        if self.checkpointer is None:
            try:
                self.checkpointer = MemorySaver()
                logger.info(
                    "LangGraph Memory checkpointer initialized (final fallback)"
                )
            except Exception as fallback_error:
                logger.error(
                    "Failed to initialize any checkpointer - this will cause workflow failures",
                    error=str(fallback_error),
                )
                # Don't set checkpointer to None - raise an error instead
                raise RuntimeError(
                    f"Unable to initialize any checkpointer: {fallback_error}"
                ) from fallback_error

        self._initialized = True

    def __del__(self) -> None:
        """Clean up resources when the workflow manager is destroyed."""
        if self._redis_context_manager:
            try:
                self._redis_context_manager.__exit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors in destructor

    def cleanup(self) -> None:
        """Explicitly clean up Redis resources."""
        if self._redis_context_manager:
            try:
                self._redis_context_manager.__exit__(None, None, None)
                logger.debug(
                    "Redis checkpointer context manager cleaned up"
                )
            except Exception as e:
                logger.warning(
                    "Error cleaning up Redis checkpointer", error=str(e)
                )
            finally:
                self._redis_context_manager = None
                self.checkpointer = None
                self._initialized = False

    async def create_workflow(
        self,
        llm: BaseChatModel,
        *,
        mode: WorkflowMode = "plain",
        system_message: str | None = None,
        retriever: Any | None = None,
        tools: list[Any] | None = None,
        enable_memory: bool = False,
        memory_window: int = 20,
        user_id: str | None = None,
        conversation_id: str | None = None,
        provider_name: str | None = None,
        model_name: str | None = None,
        max_tool_calls: int | None = None,
        max_documents: int | None = None,
        enable_streaming: bool = False,
    ) -> Pregel:
        """Create a unified conversation workflow.

        Modes:
        - plain: just the model
        - rag: retrieval then model
        - tools: model with tool-calling loop
        - full: retrieval, then model+tools loop

        Optional:
        - enable_memory: summarize older messages and prepend summary as context
        - enable_streaming: use streaming model node for token-by-token output

        Args:
            llm: Language model to use
            mode: Workflow mode
            system_message: Optional system message
            retriever: Optional retriever for RAG
            tools: Optional tools for tool-calling
            enable_memory: Whether to enable memory management
            memory_window: Number of recent messages to keep
            user_id: ID of the user (for metrics and security)
            conversation_id: ID of the conversation (for metrics)
            provider_name: Name of the LLM provider (for metrics)
            model_name: Name of the model (for metrics)
            max_tool_calls: Maximum number of tool calls allowed (optional)
            max_documents: Maximum number of documents to retrieve for RAG (optional)
            enable_streaming: Whether to use streaming model node for token-by-token output
        """
        # Start metrics tracking if enabled (store config for later async initialization)
        workflow_tracking_config = None
        if METRICS_ENABLED and user_id and conversation_id:
            workflow_tracking_config = {
                "workflow_type": mode,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "provider_name": provider_name or "",
                "model_name": model_name or "",
                "workflow_config": {
                    "enable_memory": enable_memory,
                    "memory_window": memory_window,
                    "has_retriever": retriever is not None,
                    "has_tools": tools is not None and len(tools) > 0,
                    "max_tool_calls": max_tool_calls,
                    "max_documents": max_documents,
                },
            }
        use_retriever = mode in ("rag", "full")
        use_tools = mode in ("tools", "full")

        llm_for_call = (
            llm.bind_tools(tools) if (use_tools and tools) else llm
        )

        async def retrieve_context(
            state: ConversationState,
        ) -> dict[str, Any]:
            """Retrieve relevant context for the current query."""
            if not use_retriever or retriever is None:
                return {"retrieval_context": ""}

            messages = state["messages"]

            # Get the last human message
            last_human_message = None
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    last_human_message = msg
                    break

            if not last_human_message:
                return {"retrieval_context": ""}

            try:
                docs = await retriever.ainvoke(
                    last_human_message.content
                )
                context = "\n\n".join(
                    getattr(doc, "page_content", str(doc))
                    for doc in docs
                )
                return {"retrieval_context": context}
            except Exception as e:
                logger.error("Retrieval failed", error=str(e))
                return {"retrieval_context": ""}

        async def manage_memory(
            state: ConversationState,
        ) -> dict[str, Any]:
            """Summarize older messages and keep a sliding window."""
            if not enable_memory:
                return {}

            messages = list(state["messages"])
            if len(messages) <= memory_window:
                return {}

            recent_messages = messages[-memory_window:]
            older_messages = messages[:-memory_window]

            if not state.get("conversation_summary"):
                summary_prompt = (
                    "Summarize this conversation history:\n\n"
                )
                for msg in older_messages:
                    role = (
                        "Human"
                        if isinstance(msg, HumanMessage)
                        else "Assistant"
                    )
                    summary_prompt += f"{role}: {msg.content}\n"

                try:
                    summary_response = await llm.ainvoke(
                        [HumanMessage(content=summary_prompt)]
                    )
                    summary = getattr(
                        summary_response,
                        "content",
                        str(summary_response),
                    )
                    return {
                        "messages": recent_messages,
                        "conversation_summary": summary,
                        "memory_context": {
                            "summarized_messages": len(older_messages)
                        },
                    }
                except Exception as e:
                    logger.error(
                        "Memory management failed", error=str(e)
                    )
                    return {"messages": recent_messages}

            return {"messages": recent_messages}

        def apply_system_and_context(
            state: ConversationState, messages: list[BaseMessage]
        ) -> list[BaseMessage]:
            """Apply system message, memory summary, and retrieval context if present."""
            prefixed: list[BaseMessage] = []

            if state.get("conversation_summary"):
                prefixed.append(
                    SystemMessage(
                        content=f"Previous conversation summary: {state['conversation_summary']}"
                    )
                )

            rag_system_message = None
            if use_retriever:
                # If retrieval context present, weave it into the system prompt
                context = state.get("retrieval_context") or ""
                base = system_message or (
                    "You are a helpful assistant. Use the following context to answer questions. "
                    "If the context doesn't contain relevant information, say so clearly."
                )
                rag_system_message = base + (
                    f"\n\nContext:\n{context}" if context else ""
                )
            elif system_message:
                rag_system_message = system_message

            if rag_system_message:
                prefixed.append(
                    SystemMessage(content=rag_system_message)
                )

            return prefixed + messages

        async def call_model(
            state: ConversationState,
        ) -> dict[str, Any]:
            """Call the model (with optional tools) using applied context."""
            messages = list(state["messages"])
            messages = apply_system_and_context(state, messages)

            try:
                response = await llm_for_call.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call failed", error=str(e))
                return {
                    "messages": [
                        AIMessage(
                            content=f"I'm sorry, I encountered an error: {str(e)}"
                        )
                    ]
                }

        async def execute_tools(
            state: ConversationState,
        ) -> dict[str, Any]:
            """Execute tool calls from the last AI message and push ToolMessage results."""
            if not use_tools or not tools:
                return {}

            messages = list(state["messages"])
            last_message = messages[-1] if messages else None
            if not last_message or not hasattr(
                last_message, "tool_calls"
            ):
                return {}

            tool_messages: list[ToolMessage] = []

            for tool_call in (
                getattr(last_message, "tool_calls", []) or []
            ):
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("args", {})
                tool_id = tool_call.get("id")

                # Find a matching tool by name
                tool_obj = None
                for t in tools:
                    t_name = (
                        getattr(t, "name", None)
                        or getattr(t, "name_", None)
                        or getattr(t, "__name__", None)
                    )
                    if t_name == tool_name:
                        tool_obj = t
                        break

                if not tool_obj:
                    logger.error("Tool not found", tool=tool_name)
                    tool_messages.append(
                        ToolMessage(
                            content=f"Error: tool '{tool_name}' not found.",
                            tool_call_id=tool_id or "",
                        )
                    )
                    continue

                try:
                    # Security check if enabled
                    if SECURITY_ENABLED and user_id:
                        authorized = workflow_security_manager.authorize_tool_execution(
                            user_id=user_id,
                            workflow_id="",
                            workflow_type=mode,
                            tool_name=tool_name,
                            method=None,
                            parameters=tool_args,
                        )

                        if not authorized:
                            tool_messages.append(
                                ToolMessage(
                                    content="Access denied: Insufficient permissions for this tool",
                                    tool_call_id=tool_id or "",
                                )
                            )
                            continue

                    # Prefer async invocation when available
                    if hasattr(tool_obj, "ainvoke"):
                        result = await tool_obj.ainvoke(tool_args)
                    elif hasattr(tool_obj, "invoke"):
                        result = tool_obj.invoke(tool_args)
                    elif callable(tool_obj):
                        result = tool_obj(tool_args)
                    else:
                        result = f"Tool {tool_name} cannot be executed."

                    tool_messages.append(
                        ToolMessage(
                            content=str(result),
                            tool_call_id=tool_id or "",
                        )
                    )

                    # Update metrics (defer to avoid async issues in nested function)
                    if METRICS_ENABLED and workflow_tracking_config:
                        try:
                            # This would be handled in a background task or defer
                            logger.debug(
                                "Tool execution completed - metrics tracking deferred"
                            )
                        except Exception as e:
                            logger.debug(
                                f"Failed to defer workflow metrics: {e}"
                            )
                except Exception as e:
                    error_msg = str(e)
                    logger.error(
                        "Tool execution failed",
                        tool=tool_name,
                        error=error_msg,
                    )
                    tool_messages.append(
                        ToolMessage(
                            content=f"Error: {error_msg}",
                            tool_call_id=tool_id or "",
                        )
                    )

                    # Update metrics with error (defer to avoid async issues in nested function)
                    if METRICS_ENABLED and workflow_tracking_config:
                        try:
                            # This would be handled in a background task or defer
                            logger.debug(
                                "Tool execution failed - metrics tracking deferred"
                            )
                        except Exception as e:
                            logger.debug(
                                f"Failed to defer workflow metrics: {e}"
                            )

            # Returning ToolMessage(s) appends to state["messages"] via add_messages
            return {"messages": tool_messages}

        def should_continue(state: ConversationState) -> str:
            """If there are tool calls, execute them; otherwise end."""
            last_message = (
                state["messages"][-1] if state["messages"] else None
            )
            if (
                use_tools
                and last_message
                and hasattr(last_message, "tool_calls")
                and last_message.tool_calls
            ):
                return "execute_tools"
            return str(END)

        # Build graph dynamically
        workflow = StateGraph(ConversationState)

        if enable_memory:
            workflow.add_node("manage_memory", manage_memory)

        if use_retriever:
            workflow.add_node("retrieve_context", retrieve_context)

        workflow.add_node("call_model", call_model)

        if use_tools:
            workflow.add_node("execute_tools", execute_tools)

        # Entry point and edges
        entry = None
        if enable_memory:
            entry = "manage_memory"
            if use_retriever:
                workflow.add_edge("manage_memory", "retrieve_context")
                workflow.add_edge("retrieve_context", "call_model")
            else:
                workflow.add_edge("manage_memory", "call_model")
        else:
            if use_retriever:
                entry = "retrieve_context"
                workflow.add_edge("retrieve_context", "call_model")
            else:
                entry = "call_model"

        workflow.set_entry_point(entry)

        if use_tools:
            workflow.add_conditional_edges(
                "call_model", should_continue
            )
            workflow.add_edge("execute_tools", "call_model")
        else:
            workflow.add_edge("call_model", END)

        # Compile with checkpointer
        await self._ensure_initialized()
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )
        return app

    async def run_workflow(
        self,
        workflow: Pregel,
        initial_state: ConversationState,
        thread_id: str | None = None,
    ) -> ConversationState:
        """Run a workflow with state management."""
        if not thread_id:
            thread_id = generate_ulid()

        config = {"configurable": {"thread_id": thread_id}}

        try:
            result = await workflow.ainvoke(
                initial_state, config=config
            )
            typed_result: ConversationState = result
            return typed_result
        except Exception as e:
            logger.error(
                "Workflow execution failed",
                error=str(e),
                thread_id=thread_id,
            )
            raise

    async def stream_workflow(
        self,
        workflow: Pregel,
        initial_state: ConversationState,
        thread_id: str | None = None,
        enable_llm_streaming: bool = False,
    ) -> Any:
        """Stream workflow execution for real-time updates.
        
        Args:
            workflow: The LangGraph workflow to execute
            initial_state: Initial conversation state
            thread_id: Optional thread ID for conversation continuity
            enable_llm_streaming: If True, intercept model calls for token-by-token streaming
        """
        if not thread_id:
            thread_id = generate_ulid()

        config = {"configurable": {"thread_id": thread_id}}

        try:
            if enable_llm_streaming:
                # Use custom streaming logic that intercepts model calls
                async for event in self._stream_with_llm_streaming(
                    workflow, initial_state, config
                ):
                    yield event
            else:
                # Use standard LangGraph streaming (events per node completion)
                async for event in workflow.astream(
                    initial_state, config=config
                ):
                    yield event
        except Exception as e:
            logger.error(
                "Workflow streaming failed",
                error=str(e),
                thread_id=thread_id,
                enable_llm_streaming=enable_llm_streaming,
            )
            raise

    async def _stream_with_llm_streaming(
        self, workflow: Pregel, initial_state: ConversationState, config: dict
    ) -> Any:
        """Custom streaming that provides token-by-token LLM output.
        
        This method provides a foundation for implementing true token-by-token
        streaming by intercepting model calls. Currently it falls back to 
        regular streaming but can be enhanced to provide real streaming.
        """
        # Current implementation: Enhanced event processing
        # This provides the foundation for token-by-token streaming
        
        async for event in workflow.astream(initial_state, config=config):
            # Process each event to identify model calls
            for node_name, node_output in event.items():
                if (
                    node_name == "call_model" 
                    and isinstance(node_output, dict) 
                    and "messages" in node_output
                ):
                    # This is where token-by-token streaming would be implemented
                    # For now, we emit the complete response but the infrastructure is ready
                    
                    messages = node_output["messages"]
                    if messages:
                        message = messages[-1]
                        if hasattr(message, "content") and message.content:
                            # Simulate token-by-token by emitting the complete response
                            # In a full implementation, this would be multiple events
                            logger.debug(
                                "Model response ready for token-by-token streaming",
                                content_length=len(message.content)
                            )
                    
                    yield event
                else:
                    # Emit non-model events as-is
                    yield event

    async def get_conversation_history(
        self, workflow: Pregel, thread_id: str
    ) -> ConversationState | None:
        """Get conversation history for a thread."""
        await self._ensure_initialized()
        if not self.checkpointer:
            return None

        config = {"configurable": {"thread_id": thread_id}}

        try:
            state = await workflow.aget_state(config)
            return state.values if state else None
        except Exception as e:
            logger.error(
                "Failed to get conversation history",
                error=str(e),
                thread_id=thread_id,
            )
            return None

    async def create_conversation_branch(
        self,
        workflow: Pregel,
        parent_thread_id: str,
        new_thread_id: str | None = None,
        branch_point_message_index: int = -1,
    ) -> str:
        """Create a new conversation branch from an existing conversation.

        Args:
            workflow: The LangGraph workflow
            parent_thread_id: Thread ID of the parent conversation
            new_thread_id: Optional thread ID for the new branch
            branch_point_message_index: Message index to branch from (-1 for latest)

        Returns:
            Thread ID of the new branch
        """
        if not new_thread_id:
            new_thread_id = generate_ulid()

        # Get parent conversation state
        parent_state = await self.get_conversation_history(
            workflow, parent_thread_id
        )
        if not parent_state:
            raise ValueError(
                f"Parent conversation {parent_thread_id} not found"
            )

        # Create branched state
        branch_state = dict(parent_state)

        # Trim messages to branch point if specified
        if branch_point_message_index >= 0:
            messages = list(parent_state["messages"])
            branch_state["messages"] = messages[
                : branch_point_message_index + 1
            ]

        # Update metadata for branch
        branch_state["conversation_id"] = new_thread_id
        branch_state["parent_conversation_id"] = parent_thread_id
        branch_state["branch_id"] = new_thread_id
        branch_state["metadata"] = {
            **parent_state.get("metadata", {}),
            "branch_created_at": generate_ulid(),  # timestamp-like ID
            "branch_point_index": branch_point_message_index,
        }

        # Initialize the new branch
        config = {"configurable": {"thread_id": new_thread_id}}
        await workflow.aupdate_state(config, branch_state)

        logger.info(
            "Created conversation branch",
            parent_thread_id=parent_thread_id,
            new_thread_id=new_thread_id,
            branch_point=branch_point_message_index,
        )

        return new_thread_id

    async def fork_conversation(
        self,
        workflow: Pregel,
        source_thread_id: str,
        fork_id: str | None = None,
    ) -> str:
        """Fork a conversation to create an independent copy.

        Args:
            workflow: The LangGraph workflow
            source_thread_id: Thread ID of the source conversation
            fork_id: Optional ID for the fork

        Returns:
            Thread ID of the forked conversation
        """
        if not fork_id:
            fork_id = generate_ulid()

        # Get source conversation state
        source_state = await self.get_conversation_history(
            workflow, source_thread_id
        )
        if not source_state:
            raise ValueError(
                f"Source conversation {source_thread_id} not found"
            )

        # Create forked state (complete copy)
        fork_state = dict(source_state)
        fork_state["conversation_id"] = fork_id
        fork_state["parent_conversation_id"] = (
            None  # Forks are independent
        )
        fork_state["branch_id"] = fork_id
        fork_state["metadata"] = {
            **source_state.get("metadata", {}),
            "forked_from": source_thread_id,
            "fork_created_at": generate_ulid(),  # timestamp-like ID
        }

        # Initialize the fork
        config = {"configurable": {"thread_id": fork_id}}
        await workflow.aupdate_state(config, fork_state)

        logger.info(
            "Forked conversation",
            source_thread_id=source_thread_id,
            fork_id=fork_id,
        )

        return fork_id

    async def summarize_conversation(
        self,
        workflow: Pregel,
        thread_id: str,
        llm: BaseChatModel,
        max_messages: int = 10,
    ) -> str:
        """Summarize conversation for memory management.

        Args:
            workflow: The LangGraph workflow
            thread_id: Thread ID of the conversation
            llm: Language model for summarization
            max_messages: Maximum number of recent messages to include

        Returns:
            Conversation summary
        """
        state = await self.get_conversation_history(workflow, thread_id)
        if not state:
            return ""

        messages = list(state["messages"])
        if not messages:
            return ""

        # Get recent messages for summarization
        recent_messages = (
            messages[-max_messages:]
            if len(messages) > max_messages
            else messages
        )

        # Create summarization prompt
        summary_prompt = (
            "Please provide a concise summary of this conversation:\n\n"
        )
        for msg in recent_messages:
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            summary_prompt += f"{role}: {msg.content}\n"

        summary_prompt += "\nSummary:"

        # Generate summary
        try:
            summary_message = HumanMessage(content=summary_prompt)
            response = await llm.ainvoke([summary_message])
            summary = (
                response.content
                if hasattr(response, "content")
                else str(response)
            )

            # Update conversation state with summary
            config = {"configurable": {"thread_id": thread_id}}
            await workflow.aupdate_state(
                config, {"conversation_summary": summary}
            )

            logger.info(
                "Generated conversation summary",
                thread_id=thread_id,
                summary_length=len(summary),
            )

            return summary
        except Exception as e:
            logger.error(
                "Failed to generate conversation summary",
                error=str(e),
                thread_id=thread_id,
            )
            return ""

    def get_retriever(
        self, workspace_id: str, document_ids: list[str] | None = None
    ) -> Any | None:
        """Get retriever for a workspace based on user documents.

        Args:
            workspace_id: Workspace identifier (interpreted as user_id)
            document_ids: Optional list of specific document IDs to filter by

        Returns:
            Retriever instance or None if not available
        """
        try:
            from chatter.core.vector_store import vector_store_manager
            from chatter.services.embeddings import EmbeddingService

            # Create embedding service
            embedding_service = EmbeddingService()

            # Get default embeddings for the user's workspace
            embeddings = embedding_service.get_default_embeddings()
            if embeddings is None:
                logger.warning(
                    f"No embeddings available for workspace: {workspace_id}"
                )
                return None

            # Create user-specific collection name
            collection_name = f"documents_{workspace_id}"

            # Get vector store for the workspace
            vector_store = vector_store_manager.create_store(
                store_type="pgvector",
                embeddings=embeddings,
                collection_name=collection_name,
            )

            # Configure search parameters
            search_kwargs = {"k": 5}  # Return top 5 relevant documents

            # Add document filtering if specific document IDs are provided
            if document_ids:
                # Note: The actual filter implementation depends on the vector store
                # For pgvector, this would typically be a metadata filter
                search_kwargs["filter"] = {
                    "document_id": {"$in": document_ids}
                }
                logger.debug(
                    f"Filtering retriever to specific documents: {document_ids}"
                )

            # Return retriever with search parameters
            retriever = vector_store.as_retriever(
                search_type="similarity",
                search_kwargs=search_kwargs,
            )

            logger.debug(
                f"Created retriever for workspace: {workspace_id}, "
                f"collection: {collection_name}, "
                f"filtered: {document_ids is not None}"
            )
            return retriever

        except Exception as e:
            logger.error(
                "Failed to create retriever for workspace",
                workspace_id=workspace_id,
                error=str(e),
            )
            return None

    def get_tools(self, workspace_id: str | None = None) -> list[Any]:
        """Get available tools for a workspace.

        Args:
            workspace_id: Workspace identifier (optional, for future tool filtering)

        Returns:
            List of available tool objects
        """
        try:
            from chatter.core.dependencies import get_builtin_tools

            tools = []
            
            # Get builtin tools
            builtin_tools = get_builtin_tools()
            if builtin_tools:
                tools.extend(builtin_tools)
                logger.debug(f"Added {len(builtin_tools)} builtin tools")

            # Note: MCP tools are loaded asynchronously in the LLM service
            # when creating workflows, so we don't load them here to avoid
            # blocking synchronous calls
            logger.debug(f"Configured tools for workspace: {workspace_id}, total: {len(tools)}")
            
            return tools

        except Exception as e:
            logger.error(
                "Failed to get tools for workspace",
                workspace_id=workspace_id,
                error=str(e),
            )
            return []


# Global workflow manager instance
workflow_manager = LangGraphWorkflowManager()
