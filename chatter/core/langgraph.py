"""LangGraph workflows for advanced conversation logic."""

from collections.abc import Sequence
from typing import Annotated, Any, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.checkpoint.memory import MemorySaver

try:
    from langgraph.checkpoint.redis import RedisSaver

    REDIS_AVAILABLE = True
except ImportError:
    RedisSaver = None
    REDIS_AVAILABLE = False
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.pregel import Pregel

from chatter.config import settings
from chatter.models.base import generate_ulid
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
    # Tool call tracking for recursion prevention
    tool_call_count: int


# Remove static workflow mode - now use dynamic capability flags


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
            if (
                settings.langgraph_checkpoint_store == "redis"
                and REDIS_AVAILABLE
            ):
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
                # Fallback to in-memory checkpointer for development or when Redis unavailable
                self.checkpointer = MemorySaver()
                if not REDIS_AVAILABLE:
                    logger.info(
                        "LangGraph Memory checkpointer initialized (redis not available)"
                    )
                else:
                    logger.info(
                        "LangGraph Memory checkpointer initialized"
                    )
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
        enable_retrieval: bool = False,
        enable_tools: bool = False,
        system_message: str | None = None,
        retriever: Any | None = None,
        tools: list[Any] | None = None,
        enable_memory: bool = False,
        memory_window: int = 4,
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
        """Create a unified conversation workflow.

        Capabilities:
        - enable_retrieval: Add document retrieval capability
        - enable_tools: Add tool-calling capability
        - Both can be combined for full feature workflows

        Optional:
        - enable_memory: summarize older messages and prepend summary as context
        - enable_streaming: use streaming model node for token-by-token output
        - focus_mode: use only the last user message for focused responses

        Args:
            llm: Language model to use
            enable_retrieval: Whether to enable document retrieval
            enable_tools: Whether to enable tool calling
            system_message: Optional system message
            retriever: Optional retriever for document search
            tools: Optional tools for tool-calling
            enable_memory: Whether to enable memory management
            memory_window: Number of recent messages to keep (default: 4 for 2 exchanges)
            user_id: ID of the user (for metrics and security)
            conversation_id: ID of the conversation (for metrics)
            provider_name: Name of the LLM provider (for metrics)
            model_name: Name of the model (for metrics)
            max_tool_calls: Maximum number of tool calls allowed (optional)
            max_documents: Maximum number of documents to retrieve for RAG (optional)
            enable_streaming: Whether to use streaming model node for token-by-token output
            focus_mode: If True, only use the last user message for focused responses
            **kwargs: Additional provider options (e.g., temperature, max_tokens) passed to LLM calls
        """
        # Start metrics tracking if enabled (store config for later async initialization)
        workflow_tracking_config = None
        if METRICS_ENABLED and user_id and conversation_id:
            workflow_tracking_config = {
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
        use_retriever = enable_retrieval
        use_tools = enable_tools

        llm_for_call = (
            llm.bind_tools(tools) if (use_tools and tools) else llm
        )

        # LLM for final response without tools
        llm_for_final = llm  # Always without tools for final response

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
                # Create a more focused summary prompt with strict formatting instructions
                summary_prompt = (
                    "You are a conversation summarizer. Your task is to create a concise, factual summary of the conversation below. "
                    "Do not engage in conversation or ask questions. Only provide a summary in the format: "
                    "'Summary: [key topics and facts discussed]'. If there is insufficient content to summarize, respond only with 'Summary: Conversation just started.'\n\n"
                    "Conversation to summarize:\n"
                )
                for msg in older_messages:
                    role = (
                        "Human"
                        if isinstance(msg, HumanMessage)
                        else "Assistant"
                    )
                    summary_prompt += f"{role}: {msg.content}\n"

                summary_prompt += "\nProvide only a factual summary without conversational elements:"

                try:
                    summary_response = await llm.ainvoke(
                        [HumanMessage(content=summary_prompt)]
                    )
                    raw_summary = getattr(
                        summary_response,
                        "content",
                        str(summary_response),
                    )

                    # Clean the summary to ensure it's just factual content
                    # Remove conversational elements that might confuse the main model
                    summary = raw_summary.strip()

                    # If the summary looks like a conversational response rather than a summary,
                    # replace it with a simple summary
                    if any(
                        phrase in summary.lower()
                        for phrase in [
                            "there is no conversation history",
                            "conversation just started",
                            "what would you like",
                            "i can help",
                            "how can i assist",
                        ]
                    ):
                        summary = "Summary: Initial conversation with basic greetings and introductions."

                    # Ensure summary is prefixed appropriately for context use
                    if not summary.lower().startswith("summary:"):
                        summary = f"Summary: {summary}"

                    logger.debug(
                        "Created conversation summary",
                        summary_length=len(summary),
                        older_messages_count=len(older_messages),
                        recent_messages_count=len(recent_messages),
                    )

                    return {
                        "messages": recent_messages,
                        "conversation_summary": summary,
                        "memory_context": {
                            "summarized_messages": len(older_messages),
                            "kept_messages": len(recent_messages),
                            "summary_created": True,
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

            # In focus mode, only use the last human message for focused responses
            if focus_mode:
                # Find the last human message
                last_human_message = None
                for msg in reversed(messages):
                    if isinstance(msg, HumanMessage):
                        last_human_message = msg
                        break

                if last_human_message:
                    # Create a focused context with just system message and last user input
                    if state.get("conversation_summary"):
                        summary = state["conversation_summary"]
                        # Ensure the summary is properly formatted for context use
                        if summary and not summary.lower().startswith(
                            (
                                "summary:",
                                "context:",
                                "previous conversation:",
                            )
                        ):
                            summary = f"Context from previous conversation: {summary}"

                        prefixed.append(SystemMessage(content=summary))

                    if use_retriever and state.get("retrieval_context"):
                        context = state.get("retrieval_context") or ""
                        base = system_message or (
                            "You are a helpful assistant. Use the following context to answer questions. "
                            "If the context doesn't contain relevant information, say so clearly."
                        )
                        focused_system_message = base + (
                            f"\n\nContext:\n{context}"
                            if context
                            else ""
                        )
                        prefixed.append(
                            SystemMessage(
                                content=focused_system_message
                            )
                        )
                    elif system_message:
                        prefixed.append(
                            SystemMessage(content=system_message)
                        )

                    # Only include the last user message for focused response
                    prefixed.append(last_human_message)
                    return prefixed
                # If no human message found in focus mode, fall through to normal processing

            # Normal processing: include conversation summary if available
            if state.get("conversation_summary"):
                summary = state["conversation_summary"]
                # Ensure the summary is properly formatted for context use
                if summary and not summary.lower().startswith(
                    ("summary:", "context:", "previous conversation:")
                ):
                    summary = (
                        f"Context from previous conversation: {summary}"
                    )

                prefixed.append(SystemMessage(content=summary))

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
                response = await llm_for_call.ainvoke(
                    messages, **kwargs
                )
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

        async def finalize_response(
            state: ConversationState,
        ) -> dict[str, Any]:
            """Generate a final response when tool call limit is reached or recursion detected."""
            try:
                # Extract tool results to provide a meaningful response
                messages = state["messages"]
                tool_results = []
                
                # Find recent tool results
                for msg in messages:
                    if hasattr(msg, "tool_call_id") and hasattr(msg, "content"):
                        tool_results.append(msg.content)
                
                # Get the original user question
                user_question = ""
                for msg in messages:
                    if hasattr(msg, "content") and getattr(msg, "__class__", None).__name__ == "HumanMessage":
                        user_question = msg.content
                        break
                
                # Create a response that incorporates the tool results
                if tool_results and user_question:
                    # Use the LLM without tools to generate a final response
                    try:
                        final_context = (
                            f"Based on the following information gathered from tools:\n"
                            f"{', '.join(tool_results[-3:])}\n\n"  # Use last 3 results
                            f"Please provide a direct and helpful answer to: {user_question}"
                        )
                        
                        final_response = await llm_for_final.ainvoke([
                            HumanMessage(content=final_context)
                        ])
                        
                        return {"messages": [final_response]}
                        
                    except Exception as llm_error:
                        logger.warning(
                            "LLM finalization failed, using template response",
                            error=str(llm_error)
                        )
                        # Fall back to template response
                
                # Fallback response
                tool_count = state.get("tool_call_count", 0)
                
                if tool_results:
                    final_content = (
                        f"Based on the tool results I gathered: {', '.join(tool_results[-2:])}, "
                        f"I have the information needed to answer your question."
                    )
                else:
                    final_content = (
                        f"I have completed using tools (executed {tool_count} tool calls) to help with your request. "
                        "Based on the information gathered, I've done my best to address your question."
                    )

                final_message = AIMessage(content=final_content)
                return {"messages": [final_message]}

            except Exception as e:
                logger.error(
                    "Final response generation failed", error=str(e)
                )
                return {
                    "messages": [
                        AIMessage(
                            content="I've completed my tool usage but encountered an issue generating a final response. Based on the available information, I've done my best to help with your request."
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
            current_tool_count = state.get("tool_call_count", 0)

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

                    # Increment tool call count
                    current_tool_count += 1

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
            return {
                "messages": tool_messages,
                "tool_call_count": current_tool_count,
            }

        def should_continue(state: ConversationState) -> str:
            """If there are tool calls, execute them; otherwise end.
            Also checks tool call limits to prevent infinite recursion.
            """
            last_message = (
                state["messages"][-1] if state["messages"] else None
            )

            # Check if we have tool calls to execute
            has_tool_calls = (
                use_tools
                and last_message
                and hasattr(last_message, "tool_calls")
                and last_message.tool_calls
            )

            if not has_tool_calls:
                return str(END)

            # Check tool call limit to prevent infinite recursion
            current_tool_count = state.get("tool_call_count", 0)
            max_allowed = (
                max_tool_calls or 10
            )  # Default to 10 if not specified

            # Calculate how many tool calls would be executed if we proceed
            pending_tool_calls = (
                len(last_message.tool_calls)
                if last_message.tool_calls
                else 0
            )
            projected_tool_count = (
                current_tool_count + pending_tool_calls
            )

            if projected_tool_count > max_allowed:
                logger.warning(
                    "Tool call limit would be exceeded, ending workflow",
                    current_tool_count=current_tool_count,
                    pending_calls=pending_tool_calls,
                    projected_count=projected_tool_count,
                    max_allowed=max_allowed,
                    user_id=user_id,
                    conversation_id=conversation_id,
                )
                # Instead of ending abruptly, generate a final response
                return "finalize_response"

            # NEW: Check for tool recursion patterns to prevent loops
            # Look for cases where the same tool is being called repeatedly
            # without the LLM providing meaningful responses
            messages = state["messages"]
            if len(messages) >= 4:  # Need at least: Human, AI+tools, Tool, AI+tools
                # Count recent tool calls for the same tool
                recent_tool_calls = []
                tool_results = []
                
                # Look at the last several messages to detect patterns
                for msg in messages[-6:]:  # Look at last 6 messages
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            recent_tool_calls.append(tool_call.get("name"))
                    elif hasattr(msg, "tool_call_id"):  # Tool result message
                        tool_results.append(msg.content)

                # Check if we have multiple calls to the same tool with results
                # but the LLM keeps making more calls instead of using the results
                if recent_tool_calls and tool_results:
                    # Count how many times the same tool appears
                    from collections import Counter
                    tool_counts = Counter(recent_tool_calls)
                    
                    # If any tool has been called more than once and we have results
                    # this suggests the LLM should provide a final answer
                    repeated_tools = [tool for tool, count in tool_counts.items() if count >= 2]
                    
                    if repeated_tools and len(tool_results) >= 1:
                        logger.warning(
                            "Detected tool recursion pattern - forcing final response",
                            repeated_tools=repeated_tools,
                            tool_results_count=len(tool_results),
                            current_tool_count=current_tool_count,
                            user_id=user_id,
                            conversation_id=conversation_id,
                        )
                        return "finalize_response"

            return "execute_tools"

        # Build graph dynamically
        workflow = StateGraph(ConversationState)

        if enable_memory:
            workflow.add_node("manage_memory", manage_memory)

        if use_retriever:
            workflow.add_node("retrieve_context", retrieve_context)

        workflow.add_node("call_model", call_model)

        if use_tools:
            workflow.add_node("execute_tools", execute_tools)
            workflow.add_node("finalize_response", finalize_response)

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
            workflow.add_edge("finalize_response", END)
        else:
            workflow.add_edge("call_model", END)

        # Compile with checkpointer
        await self._ensure_initialized()
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )

        # Configure recursion limit based on max_tool_calls
        # Set recursion limit to be 3x max_tool_calls to account for:
        # - Each tool call involves: call_model -> execute_tools -> call_model
        # - Plus some buffer for memory management and other nodes
        recursion_limit = max((max_tool_calls or 10) * 3 + 10, 25)
        app.recursion_limit = recursion_limit

        logger.debug(
            "Configured workflow recursion limit",
            max_tool_calls=max_tool_calls,
            recursion_limit=recursion_limit,
            enable_retrieval=enable_retrieval,
            enable_tools=enable_tools,
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
        enable_node_tracing: bool = False,
    ) -> Any:
        """Stream workflow execution using astream_events() for real-time updates.

        Args:
            workflow: The LangGraph workflow to execute
            initial_state: Initial conversation state
            thread_id: Optional thread ID for conversation continuity
            enable_llm_streaming: If True, stream token-by-token LLM output
            enable_node_tracing: If True, include node-level tracing events
        """
        if not thread_id:
            thread_id = generate_ulid()

        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Use astream_events for rich event streaming
            async for event in self._stream_with_astream_events(
                workflow,
                initial_state,
                config,
                enable_llm_streaming,
                enable_node_tracing,
            ):
                yield event
        except Exception as e:
            logger.error(
                "Workflow streaming failed",
                error=str(e),
                thread_id=thread_id,
                enable_llm_streaming=enable_llm_streaming,
                enable_node_tracing=enable_node_tracing,
            )
            raise

    async def _stream_with_astream_events(
        self,
        workflow: Pregel,
        initial_state: ConversationState,
        config: dict,
        enable_llm_streaming: bool = False,
        enable_node_tracing: bool = False,
    ) -> Any:
        """Stream workflow using astream_events() for rich event processing.

        Args:
            workflow: The LangGraph workflow to execute
            initial_state: Initial conversation state
            config: Configuration for the workflow
            enable_llm_streaming: If True, stream token-by-token LLM output
            enable_node_tracing: If True, include node-level tracing events
        """
        # Configure event filtering based on requirements
        include_types = []
        include_names = []

        if enable_llm_streaming:
            include_types.append("chat_model")
            # Focus on the final model call for token streaming
            include_names.append("call_model")

        if enable_node_tracing:
            # Include all workflow nodes for development tracing
            include_types.extend(["chain", "tool", "runnable"])

        # If neither specific streaming nor tracing is enabled,
        # fall back to node completion events
        if not include_types:
            include_types = ["chain"]

        try:
            # Build parameters defensively to avoid passing None or problematic values
            stream_params = {
                "config": config,
                "version": "v2",
            }

            # Only add include_types if it has valid entries
            if include_types:
                stream_params["include_types"] = include_types

            # Only add include_names if it has valid entries
            if include_names:
                stream_params["include_names"] = include_names

            async for event in workflow.astream_events(
                initial_state, **stream_params
            ):
                # Convert astream_events to the expected workflow event format
                converted_event = await self._convert_astream_event(
                    event, enable_llm_streaming, enable_node_tracing
                )

                if converted_event:
                    yield converted_event

        except Exception as e:
            logger.error(
                "astream_events streaming failed",
                error=str(e),
                enable_llm_streaming=enable_llm_streaming,
                enable_node_tracing=enable_node_tracing,
            )
            # Fallback to regular astream if astream_events fails
            logger.info("Falling back to regular astream")
            try:
                async for event in workflow.astream(
                    initial_state, config=config
                ):
                    yield event
            except Exception as fallback_error:
                logger.error(
                    "Fallback astream also failed",
                    error=str(fallback_error),
                )
                # Re-raise the original error for better debugging
                raise e from fallback_error

    async def _convert_astream_event(
        self,
        event: dict[str, Any],
        enable_llm_streaming: bool = False,
        enable_node_tracing: bool = False,
    ) -> dict[str, Any] | None:
        """Convert astream_events format to expected workflow event format.

        Args:
            event: Event from astream_events
            enable_llm_streaming: Whether LLM streaming is enabled
            enable_node_tracing: Whether node tracing is enabled

        Returns:
            Converted event or None if event should be filtered
        """
        event_type = event.get("event", "")
        event_name = event.get("name", "")
        event_data = event.get("data", {})

        # Handle LLM streaming events
        if (
            enable_llm_streaming
            and event_type == "on_chat_model_stream"
        ):
            # Extract token content from the streaming chunk
            chunk = event_data.get("chunk")
            if chunk and hasattr(chunk, "content"):
                # Create a token streaming event that mimics the old format
                # but includes token-level data
                return {
                    "_token_stream": {
                        "content": chunk.content,
                        "token": True,
                        "model": event_name,
                        "run_id": event.get("run_id"),
                        "parent_ids": event.get("parent_ids", []),
                    }
                }

        # Handle LLM completion events
        if event_type == "on_chat_model_end":
            # Extract the final message from the model call
            output = event_data.get("output")
            if output and hasattr(output, "content"):
                # Extract usage metadata if available
                usage_metadata = {}
                if (
                    hasattr(output, "usage_metadata")
                    and output.usage_metadata
                ):
                    usage_metadata = {
                        "input_tokens": output.usage_metadata.get(
                            "input_tokens", 0
                        ),
                        "output_tokens": output.usage_metadata.get(
                            "output_tokens", 0
                        ),
                        "total_tokens": output.usage_metadata.get(
                            "total_tokens", 0
                        ),
                    }

                # Create standard workflow event format for final model output
                return {
                    "call_model": {
                        "messages": [output],
                        "run_id": event.get("run_id"),
                        "metadata": {
                            "model": event_name,
                            "parent_ids": event.get("parent_ids", []),
                            "usage": usage_metadata,
                        },
                    }
                }

        # Handle node tracing events
        if enable_node_tracing:
            if event_type == "on_chain_start":
                return {
                    "_node_trace": {
                        "type": "node_start",
                        "node": event_name,
                        "run_id": event.get("run_id"),
                        "parent_ids": event.get("parent_ids", []),
                        "input": event_data.get("input"),
                    }
                }
            elif event_type == "on_chain_end":
                return {
                    "_node_trace": {
                        "type": "node_end",
                        "node": event_name,
                        "run_id": event.get("run_id"),
                        "parent_ids": event.get("parent_ids", []),
                        "output": event_data.get("output"),
                    }
                }
            elif event_type == "on_tool_start":
                return {
                    "_node_trace": {
                        "type": "tool_start",
                        "tool": event_name,
                        "run_id": event.get("run_id"),
                        "parent_ids": event.get("parent_ids", []),
                        "input": event_data.get("input"),
                    }
                }
            elif event_type == "on_tool_end":
                return {
                    "_node_trace": {
                        "type": "tool_end",
                        "tool": event_name,
                        "run_id": event.get("run_id"),
                        "parent_ids": event.get("parent_ids", []),
                        "output": event_data.get("output"),
                    }
                }

        # Handle regular node completion events (fallback)
        if (
            event_type == "on_chain_end"
            and event_name
            and not enable_node_tracing
        ):
            output = event_data.get("output")
            if output:
                return {event_name: output}

        # Filter out events we don't need
        return None

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
        fork_state[
            "parent_conversation_id"
        ] = None  # Forks are independent
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

    async def get_retriever(
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
            embeddings = await embedding_service.get_default_provider()

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

    async def get_tools(
        self, workspace_id: str | None = None
    ) -> list[Any]:
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
                logger.debug(
                    f"Added {len(builtin_tools)} builtin tools"
                )

            # Note: MCP tools are loaded asynchronously in the LLM service
            # when creating workflows, so we don't load them here to avoid
            # blocking synchronous calls
            logger.debug(
                f"Configured tools for workspace: {workspace_id}, total: {len(tools)}"
            )

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
