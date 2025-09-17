#!/usr/bin/env python3
"""Test script to reproduce the conversation issue described in the problem statement."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from chatter.core.langgraph import LangGraphWorkflowManager, ConversationState


async def test_conversation_issue():
    """Reproduce the conversation issue where summary gets mixed with response."""
    manager = LangGraphWorkflowManager()
    await manager._ensure_initialized()
    
    # Create a mock LLM that returns specific responses
    mock_llm = MagicMock()
    mock_llm.bind_tools = MagicMock(return_value=mock_llm)
    
    # Set up responses for the conversation sequence
    responses = [
        AIMessage(content="How can I assist you today?"),
        AIMessage(content="I don't have a personal name, but I'm an AI designed to assist and communicate with users. I'm often referred to as a \"language model\" or a \"chatbot.\" You can think of me as a computer program designed to understand and respond to human language."),
        AIMessage(content="Denver is the capital and largest city of the state of Colorado in the United States. It is located in the western part of the country, at the confluence of the South Platte River and Cherry Creek. Denver is situated in the Rocky Mountain foothills, about 1,300 miles (2,100 km) west of the Mississippi River."),
        AIMessage(content="There is no conversation history to summarize. This conversation just started with your first message. What would you like to talk about? I can summarize our conversation at the end if you'd like."),  # Summary response
        AIMessage(content="I don't have a personal name, but I'm happy to play along. If you'd like, you can call me \"Bill\" or any other name you'd like. I'll respond accordingly.")  # Actual response
    ]
    
    # Create an async mock that returns the responses in sequence
    async_responses = [AsyncMock(return_value=response) for response in responses]
    mock_llm.ainvoke = MagicMock(side_effect=async_responses)
    
    # Create the workflow with memory enabled
    workflow = await manager.create_workflow(
        llm=mock_llm,
        mode="plain",
        enable_memory=True,
        memory_window=2  # Small window to trigger memory management sooner
    )
    
    # Simulate the conversation sequence from the problem statement
    thread_id = "test_thread"
    
    # First exchange: "hello" -> "How can I assist you today?"
    initial_state: ConversationState = {
        'messages': [HumanMessage(content="hello")],
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
    
    result1 = await manager.run_workflow(workflow, initial_state, thread_id)
    print(f"Exchange 1 - Messages: {len(result1['messages'])}")
    for i, msg in enumerate(result1['messages']):
        print(f"  {i}: {msg.content}")
    
    # Second exchange: "what is your name?"
    state2: ConversationState = {
        **result1,
        'messages': [*result1['messages'], HumanMessage(content="what is your name?")]
    }
    
    result2 = await manager.run_workflow(workflow, state2, thread_id)
    print(f"\nExchange 2 - Messages: {len(result2['messages'])}")
    for i, msg in enumerate(result2['messages']):
        print(f"  {i}: {msg.content}")
    
    # Third exchange: "where is denver"
    state3: ConversationState = {
        **result2,
        'messages': [*result2['messages'], HumanMessage(content="where is denver")]
    }
    
    result3 = await manager.run_workflow(workflow, state3, thread_id)
    print(f"\nExchange 3 - Messages: {len(result3['messages'])}")
    for i, msg in enumerate(result3['messages']):
        print(f"  {i}: {msg.content}")
    
    # Fourth exchange: "can I call you bill?" - This should trigger memory management
    state4: ConversationState = {
        **result3,
        'messages': [*result3['messages'], HumanMessage(content="can I call you bill?")]
    }
    
    result4 = await manager.run_workflow(workflow, state4, thread_id)
    print(f"\nExchange 4 - Messages: {len(result4['messages'])}")
    for i, msg in enumerate(result4['messages']):
        print(f"  {i}: {type(msg).__name__}: {msg.content}")
    
    # Check if the last message has the concatenated content issue
    last_message = result4['messages'][-1]
    print(f"\nLast message content: {last_message.content}")
    
    # Check if memory management was triggered
    if 'conversation_summary' in result4:
        print(f"\nConversation summary created: {result4['conversation_summary']}")
    
    return result4


if __name__ == "__main__":
    asyncio.run(test_conversation_issue())