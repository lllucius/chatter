"""Test to reproduce retrieval bug."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from langchain_core.messages import HumanMessage

from chatter.core.langgraph import workflow_manager
from chatter.core.workflow_node_factory import WorkflowNodeContext


async def test_retrieval_node_bug():
    """Test that retrieval node receives documents."""
    
    # Mock LLM
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=MagicMock(content="Test response"))
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    # Mock retriever that returns documents
    mock_doc = MagicMock()
    mock_doc.page_content = "This is test document content"
    mock_retriever = AsyncMock()
    mock_retriever.ainvoke = AsyncMock(return_value=[mock_doc])
    
    # Create workflow with retrieval enabled
    workflow = await workflow_manager.create_workflow(
        llm=mock_llm,
        enable_retrieval=True,
        retriever=mock_retriever,
        enable_tools=False,
        enable_memory=False,
    )
    
    # Create initial state
    initial_state: WorkflowNodeContext = {
        "messages": [HumanMessage(content="What's in the documents?")],
        "user_id": "test_user",
        "conversation_id": "test_conv",
        "retrieval_context": None,
        "conversation_summary": None,
        "tool_call_count": 0,
        "metadata": {},
        "variables": {},
        "loop_state": {},
        "error_state": {},
        "conditional_results": {},
        "execution_history": [],
    }
    
    # Execute workflow
    result = await workflow_manager.run_workflow(
        workflow=workflow,
        initial_state=initial_state,
        thread_id="test_thread",
    )
    
    # Check if retriever was called
    print("Retriever called:", mock_retriever.ainvoke.called)
    print("Retriever call count:", mock_retriever.ainvoke.call_count)
    if mock_retriever.ainvoke.called:
        print("Retriever args:", mock_retriever.ainvoke.call_args)
    
    # Check result
    print("Result keys:", result.keys())
    print("Retrieval context:", result.get("retrieval_context"))
    
    # Check if LLM was called with context
    print("LLM called:", mock_llm.ainvoke.called)
    if mock_llm.ainvoke.called:
        messages = mock_llm.ainvoke.call_args[0][0]
        print("Number of messages passed to LLM:", len(messages))
        for i, msg in enumerate(messages):
            print(f"Message {i} type:", type(msg).__name__)
            print(f"Message {i} content:", msg.content[:200] if hasattr(msg, 'content') else "N/A")
    
    # Assert retriever was called
    assert mock_retriever.ainvoke.called, "Retriever should be called"
    assert result.get("retrieval_context"), "Retrieval context should be set"


if __name__ == "__main__":
    asyncio.run(test_retrieval_node_bug())
