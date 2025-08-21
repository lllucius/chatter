"""LangGraph workflows for advanced conversation logic."""

from collections.abc import Sequence
from typing import Annotated, Any, TypedDict
from uuid import uuid4

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.pregel import Pregel

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


class LangGraphWorkflowManager:
    """Manager for LangGraph conversation workflows."""

    def __init__(self):
        """Initialize the workflow manager."""
        self.checkpointer = None
        self._setup_checkpointer()

    def _setup_checkpointer(self) -> None:
        """Setup checkpointer for conversation state persistence."""
        try:
            # For now, use in-memory checkpointer
            # TODO: Implement PostgreSQL checkpointer when available
            self.checkpointer = MemorySaver()
            logger.info("LangGraph Memory checkpointer initialized")
        except Exception as e:
            logger.warning("Failed to initialize checkpointer", error=str(e))
            self.checkpointer = None

    def create_basic_conversation_workflow(
        self,
        llm: BaseChatModel,
        system_message: str | None = None
    ) -> Pregel:
        """Create a basic conversation workflow."""

        async def call_model(state: ConversationState) -> dict[str, Any]:
            """Call the language model."""
            messages = state["messages"]

            # Add system message if provided and not already present
            if system_message and not any(isinstance(msg, SystemMessage) for msg in messages):
                messages = [SystemMessage(content=system_message)] + list(messages)

            try:
                response = await llm.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call failed", error=str(e))
                error_response = AIMessage(content=f"I'm sorry, I encountered an error: {str(e)}")
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
            interrupt_after=[]
        )

        return app

    def create_rag_conversation_workflow(
        self,
        llm: BaseChatModel,
        retriever: Any,
        system_message: str | None = None
    ) -> Pregel:
        """Create a RAG-enabled conversation workflow."""

        async def retrieve_context(state: ConversationState) -> dict[str, Any]:
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
                docs = await retriever.ainvoke(last_human_message.content)
                context = "\n\n".join(doc.page_content for doc in docs)
                return {"retrieval_context": context}
            except Exception as e:
                logger.error("Retrieval failed", error=str(e))
                return {"retrieval_context": ""}

        async def call_model_with_context(state: ConversationState) -> dict[str, Any]:
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
                messages.insert(0, SystemMessage(content=rag_system_message))

            try:
                response = await llm.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call with context failed", error=str(e))
                error_response = AIMessage(content=f"I'm sorry, I encountered an error: {str(e)}")
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
            interrupt_after=[]
        )

        return app

    def create_tool_calling_workflow(
        self,
        llm: BaseChatModel,
        tools: list[Any],
        system_message: str | None = None
    ) -> Pregel:
        """Create a workflow with tool calling capabilities."""

        # Bind tools to the model
        llm_with_tools = llm.bind_tools(tools)

        async def call_model(state: ConversationState) -> dict[str, Any]:
            """Call the language model with tools."""
            messages = state["messages"]

            # Add system message if provided
            if system_message and not any(isinstance(msg, SystemMessage) for msg in messages):
                messages = [SystemMessage(content=system_message)] + list(messages)

            try:
                response = await llm_with_tools.ainvoke(messages)
                return {"messages": [response]}
            except Exception as e:
                logger.error("Model call with tools failed", error=str(e))
                error_response = AIMessage(content=f"I'm sorry, I encountered an error: {str(e)}")
                return {"messages": [error_response]}

        async def execute_tools(state: ConversationState) -> dict[str, Any]:
            """Execute any tool calls from the model."""
            messages = state["messages"]
            last_message = messages[-1] if messages else None

            if not last_message or not hasattr(last_message, 'tool_calls'):
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
                    tool_results.append({
                        "tool_call_id": tool_call["id"],
                        "result": result
                    })
                except Exception as e:
                    logger.error("Tool execution failed", tool=tool_call.get("name"), error=str(e))
                    tool_results.append({
                        "tool_call_id": tool_call.get("id"),
                        "result": f"Error: {str(e)}"
                    })

            return {"tool_calls": tool_results}

        def should_continue(state: ConversationState) -> str:
            """Determine if we should continue or end."""
            messages = state["messages"]
            last_message = messages[-1] if messages else None

            if last_message and hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                return "execute_tools"
            return END

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
            interrupt_after=[]
        )

        return app

    async def run_workflow(
        self,
        workflow: Pregel,
        initial_state: ConversationState,
        thread_id: str | None = None
    ) -> ConversationState:
        """Run a workflow with state management."""
        if not thread_id:
            thread_id = str(uuid4())

        config = {"configurable": {"thread_id": thread_id}}

        try:
            # Run the workflow
            result = await workflow.ainvoke(initial_state, config=config)
            return result
        except Exception as e:
            logger.error("Workflow execution failed", error=str(e), thread_id=thread_id)
            raise

    async def stream_workflow(
        self,
        workflow: Pregel,
        initial_state: ConversationState,
        thread_id: str | None = None
    ):
        """Stream workflow execution for real-time updates."""
        if not thread_id:
            thread_id = str(uuid4())

        config = {"configurable": {"thread_id": thread_id}}

        try:
            async for event in workflow.astream(initial_state, config=config):
                yield event
        except Exception as e:
            logger.error("Workflow streaming failed", error=str(e), thread_id=thread_id)
            raise

    async def get_conversation_history(
        self,
        workflow: Pregel,
        thread_id: str
    ) -> ConversationState | None:
        """Get conversation history for a thread."""
        if not self.checkpointer:
            return None

        config = {"configurable": {"thread_id": thread_id}}

        try:
            state = await workflow.aget_state(config)
            return state.values if state else None
        except Exception as e:
            logger.error("Failed to get conversation history", error=str(e), thread_id=thread_id)
            return None


# Global workflow manager instance
workflow_manager = LangGraphWorkflowManager()
