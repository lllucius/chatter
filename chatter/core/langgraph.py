"""LangGraph workflows for advanced conversation logic."""

from collections.abc import Sequence
from typing import Annotated, Any, TypedDict
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.pregel import Pregel

from chatter.config import settings
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


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


class LangGraphWorkflowManager:
    """Manager for LangGraph conversation workflows."""

    def __init__(self) -> None:
        """Initialize the workflow manager."""
        self.checkpointer = None
        self._setup_checkpointer()

    def _setup_checkpointer(self) -> None:
        """Setup checkpointer for conversation state persistence."""
        try:
            if settings.langgraph_checkpoint_store == "postgres":
                # Use PostgreSQL checkpointer for production
                self.checkpointer = PostgresSaver.from_conn_string(
                    settings.database_url
                )
                logger.info("LangGraph PostgreSQL checkpointer initialized")
            else:
                # Fallback to in-memory checkpointer for development
                self.checkpointer = MemorySaver()
                logger.info("LangGraph Memory checkpointer initialized")
        except Exception as e:
            logger.warning(
                "Failed to initialize PostgreSQL checkpointer, falling back to memory",
                error=str(e)
            )
            # Always fallback to memory checkpointer if PostgreSQL fails
            try:
                self.checkpointer = MemorySaver()
                logger.info("LangGraph Memory checkpointer initialized as fallback")
            except Exception as fallback_error:
                logger.error(
                    "Failed to initialize any checkpointer",
                    error=str(fallback_error)
                )
                self.checkpointer = None

    def create_basic_conversation_workflow(
        self, llm: BaseChatModel, system_message: str | None = None
    ) -> Pregel:
        """Create a basic conversation workflow."""

        async def call_model(
            state: ConversationState
        ) -> dict[str, Any]:
            """Call the language model."""
            messages = state["messages"]

            # Add system message if provided and not already present
            if system_message and not any(
                isinstance(msg, SystemMessage) for msg in messages
            ):
                messages = [
                    SystemMessage(content=system_message)
                ] + list(messages)

            try:
                response = await llm.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call failed", error=str(e))
                error_response = AIMessage(
                    content=f"I'm sorry, I encountered an error: {str(e)}"
                )
                return {"messages": [error_response]}

        # Build workflow
        workflow = StateGraph(ConversationState)
        workflow.add_node("call_model", call_model)
        workflow.set_entry_point("call_model")
        workflow.add_edge("call_model", END)

        # Compile with checkpointer
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )

        return app

    def create_rag_conversation_workflow(
        self,
        llm: BaseChatModel,
        retriever: Any,
        system_message: str | None = None,
    ) -> Pregel:
        """Create a RAG-enabled conversation workflow."""

        async def retrieve_context(
            state: ConversationState
        ) -> dict[str, Any]:
            """Retrieve relevant context for the current query."""
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
                # Retrieve relevant documents
                docs = await retriever.ainvoke(
                    last_human_message.content
                )
                context = "\n\n".join(doc.page_content for doc in docs)
                return {"retrieval_context": context}
            except Exception as e:
                logger.error("Retrieval failed", error=str(e))
                return {"retrieval_context": ""}

        async def call_model_with_context(
            state: ConversationState
        ) -> dict[str, Any]:
            """Call the language model with retrieved context."""
            messages = list(state["messages"])
            context = state.get("retrieval_context", "")

            # Prepare system message with context
            rag_system_message = system_message or (
                "You are a helpful assistant. Use the following context to answer questions. "
                "If the context doesn't contain relevant information, say so clearly."
            )

            if context:
                rag_system_message += f"\n\nContext:\n{context}"

            # Add or update system message
            if messages and isinstance(messages[0], SystemMessage):
                messages[0] = SystemMessage(content=rag_system_message)
            else:
                messages.insert(
                    0, SystemMessage(content=rag_system_message)
                )

            try:
                response = await llm.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error(
                    "Model call with context failed", error=str(e)
                )
                error_response = AIMessage(
                    content=f"I'm sorry, I encountered an error: {str(e)}"
                )
                return {"messages": [error_response]}

        # Build workflow
        workflow = StateGraph(ConversationState)
        workflow.add_node("retrieve_context", retrieve_context)
        workflow.add_node("call_model", call_model_with_context)

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "call_model")
        workflow.add_edge("call_model", END)

        # Compile with checkpointer
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )

        return app

    def create_tool_calling_workflow(
        self,
        llm: BaseChatModel,
        tools: list[Any],
        system_message: str | None = None,
    ) -> Pregel:
        """Create a workflow with tool calling capabilities."""

        # Bind tools to the model
        llm_with_tools = llm.bind_tools(tools)

        async def call_model(
            state: ConversationState
        ) -> dict[str, Any]:
            """Call the language model with tools."""
            messages = state["messages"]

            # Add system message if provided
            if system_message and not any(
                isinstance(msg, SystemMessage) for msg in messages
            ):
                messages = [
                    SystemMessage(content=system_message)
                ] + list(messages)

            try:
                response = await llm_with_tools.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error(
                    "Model call with tools failed", error=str(e)
                )
                error_response = AIMessage(
                    content=f"I'm sorry, I encountered an error: {str(e)}"
                )
                return {"messages": [error_response]}

        async def execute_tools(
            state: ConversationState
        ) -> dict[str, Any]:
            """Execute any tool calls from the model."""
            messages = state["messages"]
            last_message = messages[-1] if messages else None

            if not last_message or not hasattr(
                last_message, "tool_calls"
            ):
                return {}

            tool_results = []
            for tool_call in last_message.tool_calls:
                try:
                    # Find and execute the tool
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    # Execute tool (this is a simplified version)
                    # In a real implementation, you'd have a tool registry
                    result = f"Tool {tool_name} executed with args {tool_args}"
                    tool_results.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "result": result,
                        }
                    )
                except Exception as e:
                    logger.error(
                        "Tool execution failed",
                        tool=tool_call.get("name"),
                        error=str(e),
                    )
                    tool_results.append(
                        {
                            "tool_call_id": tool_call.get("id"),
                            "result": f"Error: {str(e)}",
                        }
                    )

            return {"tool_calls": tool_results}

        def should_continue(state: ConversationState) -> str:
            """Determine if we should continue or end."""
            messages = state["messages"]
            last_message = messages[-1] if messages else None

            if (
                last_message
                and hasattr(last_message, "tool_calls")
                and last_message.tool_calls
            ):
                return "execute_tools"
            end_result: str = str(END)
            return end_result

        # Build workflow
        workflow = StateGraph(ConversationState)
        workflow.add_node("call_model", call_model)
        workflow.add_node("execute_tools", execute_tools)

        workflow.set_entry_point("call_model")
        workflow.add_conditional_edges("call_model", should_continue)
        workflow.add_edge("execute_tools", "call_model")

        # Compile with checkpointer
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
            thread_id = str(uuid4())

        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Run the workflow
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
    ) -> Any:
        """Stream workflow execution for real-time updates."""
        if not thread_id:
            thread_id = str(uuid4())

        config = {"configurable": {"thread_id": thread_id}}

        try:
            async for event in workflow.astream(
                initial_state, config=config
            ):
                yield event
        except Exception as e:
            logger.error(
                "Workflow streaming failed",
                error=str(e),
                thread_id=thread_id,
            )
            raise

    async def get_conversation_history(
        self, workflow: Pregel, thread_id: str
    ) -> ConversationState | None:
        """Get conversation history for a thread."""
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
            new_thread_id = str(uuid4())

        # Get parent conversation state
        parent_state = await self.get_conversation_history(workflow, parent_thread_id)
        if not parent_state:
            raise ValueError(f"Parent conversation {parent_thread_id} not found")

        # Create branched state
        branch_state = dict(parent_state)

        # Trim messages to branch point if specified
        if branch_point_message_index >= 0:
            messages = list(parent_state["messages"])
            branch_state["messages"] = messages[:branch_point_message_index + 1]

        # Update metadata for branch
        branch_state["conversation_id"] = new_thread_id
        branch_state["parent_conversation_id"] = parent_thread_id
        branch_state["branch_id"] = new_thread_id
        branch_state["metadata"] = {
            **parent_state.get("metadata", {}),
            "branch_created_at": str(uuid4()),  # timestamp-like ID
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
            fork_id = str(uuid4())

        # Get source conversation state
        source_state = await self.get_conversation_history(workflow, source_thread_id)
        if not source_state:
            raise ValueError(f"Source conversation {source_thread_id} not found")

        # Create forked state (complete copy)
        fork_state = dict(source_state)
        fork_state["conversation_id"] = fork_id
        fork_state["parent_conversation_id"] = None  # Forks are independent
        fork_state["branch_id"] = fork_id
        fork_state["metadata"] = {
            **source_state.get("metadata", {}),
            "forked_from": source_thread_id,
            "fork_created_at": str(uuid4()),  # timestamp-like ID
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
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages

        # Create summarization prompt
        summary_prompt = "Please provide a concise summary of this conversation:\n\n"
        for msg in recent_messages:
            role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
            summary_prompt += f"{role}: {msg.content}\n"

        summary_prompt += "\nSummary:"

        # Generate summary
        try:
            summary_message = HumanMessage(content=summary_prompt)
            response = await llm.ainvoke([summary_message])
            summary = response.content if hasattr(response, 'content') else str(response)

            # Update conversation state with summary
            config = {"configurable": {"thread_id": thread_id}}
            await workflow.aupdate_state(config, {"conversation_summary": summary})

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

    def create_conversation_workflow_with_memory(
        self,
        llm: BaseChatModel,
        system_message: str | None = None,
        memory_window: int = 20,
    ) -> Pregel:
        """Create a conversation workflow with automatic memory management.

        Args:
            llm: Language model to use
            system_message: Optional system message
            memory_window: Number of messages to keep in active memory

        Returns:
            Compiled LangGraph workflow
        """
        async def manage_memory(state: ConversationState) -> dict[str, Any]:
            """Manage conversation memory by summarizing old messages."""
            messages = state["messages"]

            if len(messages) <= memory_window:
                return {}  # No memory management needed

            # Keep recent messages in active memory
            recent_messages = messages[-memory_window:]

            # Summarize older messages if not already summarized
            if not state.get("conversation_summary"):
                older_messages = messages[:-memory_window]
                summary_prompt = "Summarize this conversation history:\n\n"
                for msg in older_messages:
                    role = "Human" if isinstance(msg, HumanMessage) else "Assistant"
                    summary_prompt += f"{role}: {msg.content}\n"

                try:
                    summary_response = await llm.ainvoke([HumanMessage(content=summary_prompt)])
                    summary = summary_response.content if hasattr(summary_response, 'content') else str(summary_response)

                    return {
                        "messages": recent_messages,
                        "conversation_summary": summary,
                        "memory_context": {"summarized_messages": len(older_messages)},
                    }
                except Exception as e:
                    logger.error("Memory management failed", error=str(e))
                    return {"messages": recent_messages}  # Fallback: just trim messages

            return {"messages": recent_messages}

        async def call_model_with_memory(state: ConversationState) -> dict[str, Any]:
            """Call the language model with memory context."""
            messages = list(state["messages"])

            # Add conversation summary as context if available
            if state.get("conversation_summary"):
                context_msg = SystemMessage(
                    content=f"Previous conversation summary: {state['conversation_summary']}"
                )
                messages = [context_msg] + messages

            # Add system message if provided
            if system_message:
                system_msg = SystemMessage(content=system_message)
                messages = [system_msg] + messages

            try:
                response = await llm.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call failed", error=str(e))
                return {"messages": [AIMessage(content="I apologize, but I encountered an error processing your request.")]}

        # Build workflow
        workflow = StateGraph(ConversationState)
        workflow.add_node("manage_memory", manage_memory)
        workflow.add_node("call_model", call_model_with_memory)

        workflow.set_entry_point("manage_memory")
        workflow.add_edge("manage_memory", "call_model")
        workflow.add_edge("call_model", END)

        # Compile with checkpointer
        app = workflow.compile(
            checkpointer=self.checkpointer,
            interrupt_before=[],
            interrupt_after=[],
        )

        return app


# Global workflow manager instance
workflow_manager = LangGraphWorkflowManager()
