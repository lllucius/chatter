#!/usr/bin/env python3
"""Test the memory management fix to prevent response concatenation."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from chatter.core.langgraph import (
    ConversationState,
    LangGraphWorkflowManager,
)


@pytest.mark.asyncio
async def test_memory_summary_filtering():
    """Test that conversational summary responses are filtered and cleaned."""
    manager = LangGraphWorkflowManager()
    await manager._ensure_initialized()

    # Create mock LLM that returns conversational summary response
    mock_llm = AsyncMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)

    # Mock summary response that looks conversational (problematic case)
    summary_response = AIMessage(
        content="There is no conversation history to summarize. This conversation just started with your first message. What would you like to talk about? I can summarize our conversation at the end if you'd like."
    )
    normal_response = AIMessage(
        content="I don't have a personal name, but I'm happy to play along. If you'd like, you can call me \"Bill\" or any other name you'd like. I'll respond accordingly."
    )

    mock_llm.ainvoke = AsyncMock(
        side_effect=[summary_response, normal_response]
    )

    # Create workflow with memory enabled and small window to trigger memory management
    workflow = await manager.create_workflow(
        llm=mock_llm,
        enable_retrieval=False, enable_tools=False,
        enable_memory=True,
        memory_window=2,
    )

    # Create a conversation state that will trigger memory management
    # Need more than memory_window (2) messages to trigger summarization
    initial_state: ConversationState = {
        'messages': [
            HumanMessage(content="hello"),
            AIMessage(content="How can I assist you today?"),
            HumanMessage(content="what is your name?"),
            AIMessage(content="I'm an AI assistant."),
            HumanMessage(
                content="can I call you bill?"
            ),  # This should trigger memory management
        ],
        'user_id': 'test_user',
        'conversation_id': 'test_conv',
        'retrieval_context': None,
        'tool_calls': [],
        'metadata': {},
        'conversation_summary': None,
        'parent_conversation_id': None,
        'branch_id': None,
        'memory_context': {},
        'workflow_template': None,
        'a_b_test_group': None,
    }

    result = await manager.run_workflow(
        workflow, initial_state, "test_thread"
    )

    # Check that memory management was triggered and created a summary
    assert 'conversation_summary' in result
    summary = result['conversation_summary']

    # The summary should not contain conversational elements
    assert "What would you like to talk about" not in summary
    assert "I can summarize our conversation" not in summary

    # The summary should be properly formatted
    assert summary.startswith("Summary:")

    # The last message should be the normal response, not concatenated
    last_message = result['messages'][-1]
    assert isinstance(last_message, AIMessage)

    # The response should not contain both the summary and normal response
    response_content = last_message.content
    assert "There is no conversation history" not in response_content
    assert "What would you like to talk about" not in response_content

    print(f"Summary created: {summary}")
    print(f"Last response: {response_content}")


@pytest.mark.asyncio
async def test_summary_context_formatting():
    """Test that summaries are properly formatted when used as context."""
    manager = LangGraphWorkflowManager()
    await manager._ensure_initialized()

    # Create a state with an existing summary
    state: ConversationState = {
        'messages': [HumanMessage(content="new question")],
        'user_id': 'test_user',
        'conversation_id': 'test_conv',
        'retrieval_context': None,
        'tool_calls': [],
        'metadata': {},
        'conversation_summary': "User asked about AI capabilities and got basic information",
        'parent_conversation_id': None,
        'branch_id': None,
        'memory_context': {},
        'workflow_template': None,
        'a_b_test_group': None,
    }

    # Create a simple workflow to test context application
    mock_llm = AsyncMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    mock_response = AIMessage(content="Sure, I can help with that.")
    mock_llm.ainvoke = AsyncMock(return_value=mock_response)

    workflow = await manager.create_workflow(
        llm=mock_llm, enable_retrieval=False, enable_tools=False, enable_memory=True
    )

    _result = await manager.run_workflow(workflow, state, "test_thread")

    # Verify the LLM was called with properly formatted context
    call_args = mock_llm.ainvoke.call_args[0][
        0
    ]  # Get the messages passed to LLM

    # Should have a system message with the summary context
    system_messages = [
        msg for msg in call_args if isinstance(msg, SystemMessage)
    ]
    assert len(system_messages) > 0

    summary_context = system_messages[0].content
    print(f"Summary context used: {summary_context}")

    # The context should be properly formatted and not look conversational
    assert (
        "Context from previous conversation:" in summary_context
        or summary_context.startswith("Summary:")
    )


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_memory_summary_filtering())
    asyncio.run(test_summary_context_formatting())
