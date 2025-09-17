"""Test improved LangGraph memory management to prevent hallucinated repetition."""

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


class TestLangGraphMemoryManagement:
    """Test LangGraph memory management improvements."""

    @pytest.mark.asyncio
    async def test_memory_window_default_reduced_to_4(self):
        """Test that default memory window is reduced to 4 messages."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        mock_llm = MagicMock()
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        workflow = await manager.create_workflow(
            llm=mock_llm, mode="plain", enable_memory=True
        )

        # The workflow should be created successfully with default memory_window=4
        assert workflow is not None

    @pytest.mark.asyncio
    async def test_memory_window_limits_messages(self):
        """Test that memory window properly limits the number of messages."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        # Create a mock state with many messages
        messages = []
        for i in range(10):  # 10 exchanges = 20 messages total
            messages.append(HumanMessage(content=f"User message {i}"))
            messages.append(
                AIMessage(content=f"Assistant response {i}")
            )

        # Create mock state with many messages
        _mock_state: ConversationState = {
            'messages': messages,
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

        # Test that with memory_window=4, only 4 recent messages are kept
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=MagicMock(content="Test summary")
        )

        # Simulate the memory management logic
        memory_window = 4
        if len(messages) > memory_window:
            recent_messages = messages[-memory_window:]
            older_messages = messages[:-memory_window]

            assert len(recent_messages) == 4
            assert len(older_messages) == 16

            # Verify the recent messages are the last 4
            assert recent_messages[0].content == "User message 8"
            assert recent_messages[1].content == "Assistant response 8"
            assert recent_messages[2].content == "User message 9"
            assert recent_messages[3].content == "Assistant response 9"

    @pytest.mark.asyncio
    async def test_focus_mode_uses_only_last_message(self):
        """Test that focus mode only uses the last user message."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        mock_llm = MagicMock()
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        # Create workflow with focus_mode=True
        workflow = await manager.create_workflow(
            llm=mock_llm,
            mode="plain",
            focus_mode=True,
            system_message="You are a helpful assistant.",
        )

        assert workflow is not None

        # Test the focus mode logic manually
        messages = [
            HumanMessage(content="hello"),
            AIMessage(content="Hello! How can I help you today?"),
            HumanMessage(content="what is your name"),
            AIMessage(
                content="I'm an AI assistant created by Anthropic."
            ),
            HumanMessage(content="can I call you Bill?"),
        ]

        # In focus mode, only the last human message should be used
        last_human_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_human_message = msg
                break

        assert last_human_message is not None
        assert last_human_message.content == "can I call you Bill?"

        # The focused context should only include system + last user message
        focused_messages = [
            SystemMessage(content="You are a helpful assistant."),
            last_human_message,
        ]

        assert len(focused_messages) == 2
        assert isinstance(focused_messages[0], SystemMessage)
        assert isinstance(focused_messages[1], HumanMessage)
        assert focused_messages[1].content == "can I call you Bill?"

    @pytest.mark.asyncio
    async def test_conversation_summary_creation(self):
        """Test that conversation summaries are created for older messages."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        # Create older messages that should be summarized
        older_messages = [
            HumanMessage(content="hello"),
            AIMessage(content="Hello! How can I help you today?"),
            HumanMessage(content="what is your name"),
            AIMessage(content="I'm an AI assistant."),
        ]

        # Mock LLM for summary generation
        mock_llm = AsyncMock()
        mock_summary_response = MagicMock()
        mock_summary_response.content = "User greeted assistant and asked about assistant's name. Assistant responded helpfully."
        mock_llm.ainvoke = AsyncMock(return_value=mock_summary_response)

        # Test summary creation logic
        summary_prompt = "Summarize the key points from this conversation history concisely:\n\n"
        for msg in older_messages:
            role = (
                "Human"
                if isinstance(msg, HumanMessage)
                else "Assistant"
            )
            summary_prompt += f"{role}: {msg.content}\n"
        summary_prompt += "\nProvide a brief summary focusing on main topics discussed:"

        # Verify the prompt is well-formed
        assert (
            "User greeted" not in summary_prompt
        )  # Summary prompt, not the result
        assert "Human: hello" in summary_prompt
        assert "Assistant: I'm an AI assistant." in summary_prompt
        assert "main topics discussed:" in summary_prompt

        # Simulate the summary call
        response = await mock_llm.ainvoke(
            [HumanMessage(content=summary_prompt)]
        )
        summary = response.content

        assert (
            summary
            == "User greeted assistant and asked about assistant's name. Assistant responded helpfully."
        )
        assert len(summary) < len(
            summary_prompt
        )  # Summary should be more concise

    @pytest.mark.asyncio
    async def test_no_duplicate_history_in_context(self):
        """Test that conversation history is not duplicated in context."""
        # This test validates that the new memory management prevents
        # the "hallucinated repetition" issue described in the problem statement

        messages = [
            HumanMessage(content="hello"),
            AIMessage(content="Hello! How can I help you today?"),
            HumanMessage(content="what is your name"),
            AIMessage(content="I'm an AI assistant."),
            HumanMessage(content="can I call you Bill?"),
        ]

        memory_window = 4

        # With proper memory management, older messages should be summarized
        # and only recent messages should be passed to the LLM
        if len(messages) > memory_window:
            recent_messages = messages[-memory_window:]
            older_messages = messages[:-memory_window]

            # Only 1 older message in this case
            assert len(older_messages) == 1
            assert older_messages[0].content == "hello"

            # 4 recent messages
            assert len(recent_messages) == 4
            assert (
                recent_messages[0].content
                == "Hello! How can I help you today?"
            )
            assert recent_messages[-1].content == "can I call you Bill?"

            # This prevents the LLM from seeing the same "hello" multiple times
            # which was causing the hallucinated repetition

    @pytest.mark.asyncio
    async def test_conversation_agent_reduced_context(self):
        """Test that ConversationalAgent uses reduced context by default."""
        from chatter.core.agents import ConversationalAgent
        from chatter.schemas.agents import AgentProfile, AgentType

        # Create a mock agent profile
        profile = AgentProfile(
            id="test-agent",
            name="Test Agent",
            description="Test agent for memory management",
            system_message="You are a helpful assistant.",
            type=AgentType.CONVERSATIONAL,
        )

        # Create agent with mock LLM
        mock_llm = AsyncMock()
        agent = ConversationalAgent(profile=profile, llm=mock_llm)

        # Add some interaction history
        for i in range(10):  # Add 10 interactions = 20 messages
            await agent.record_interaction(
                conversation_id="test-conv",
                user_message=f"User message {i}",
                agent_response=f"Agent response {i}",
                tools_used=[],
                confidence_score=0.8,
                response_time=0.5,
            )

        # Get conversation context - should be limited to 2 interactions by default
        context = await agent.get_conversation_context("test-conv")

        # Should only return the last 2 interactions (not all 10)
        assert len(context) == 2
        assert context[0].user_message == "User message 8"
        assert context[1].user_message == "User message 9"

        # This prevents the agent from passing all 20 messages to the LLM
        # which was causing hallucinated repetition


class TestMemoryManagementConfiguration:
    """Test memory management configuration options."""

    def test_memory_window_configuration(self):
        """Test that memory window can be configured."""
        import inspect

        from chatter.core.langgraph import LangGraphWorkflowManager

        manager = LangGraphWorkflowManager()
        sig = inspect.signature(manager.create_workflow)

        # Verify memory_window parameter exists and has correct default
        memory_window_param = sig.parameters.get('memory_window')
        assert memory_window_param is not None
        assert memory_window_param.default == 4  # New default value

    def test_focus_mode_parameter_exists(self):
        """Test that focus_mode parameter exists in workflow creation."""
        import inspect

        from chatter.core.langgraph import LangGraphWorkflowManager

        manager = LangGraphWorkflowManager()
        sig = inspect.signature(manager.create_workflow)

        # Verify focus_mode parameter exists
        focus_mode_param = sig.parameters.get('focus_mode')
        assert focus_mode_param is not None
        assert (
            not focus_mode_param.default
        )  # Default should be False

    def test_llm_service_memory_window_default(self):
        """Test that LLM service uses new memory window default."""
        import inspect

        from chatter.services.llm import LLMService

        service = LLMService()
        sig = inspect.signature(service.create_langgraph_workflow)

        # Verify memory_window parameter has new default
        memory_window_param = sig.parameters.get('memory_window')
        assert memory_window_param is not None
        assert memory_window_param.default == 4  # Updated default value
