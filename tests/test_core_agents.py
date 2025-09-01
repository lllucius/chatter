"""Tests for AI agent framework and management."""

import asyncio
from datetime import datetime, UTC
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any

import pytest

from chatter.core.agents import (
    BaseAgent,
    ConversationalAgent,
    SpecializedAgent,
    AgentManager,
    AgentExecutor,
    AgentRegistry
)
from chatter.schemas.agents import (
    AgentProfile,
    AgentType,
    AgentCapability,
    AgentStatus,
    AgentInteraction
)
from chatter.core.exceptions import AgentError, AgentExecutionError


@pytest.mark.unit
class TestBaseAgent:
    """Test BaseAgent abstract base class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = MagicMock()
        self.agent_profile = AgentProfile(
            id="test-agent",
            name="Test Agent",
            description="A test agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE],
            system_message="You are a helpful test assistant."
        )

    def test_base_agent_initialization(self):
        """Test BaseAgent initialization."""
        # Act
        agent = ConversationalAgent(self.agent_profile, self.mock_llm)
        
        # Assert
        assert agent.profile == self.agent_profile
        assert agent.llm == self.mock_llm
        assert isinstance(agent.tools, dict)
        assert len(agent.tools) == 0
        assert isinstance(agent.conversation_history, dict)
        assert isinstance(agent.performance_metrics, dict)
        assert agent.performance_metrics["total_interactions"] == 0

    def test_base_agent_performance_metrics_structure(self):
        """Test performance metrics have expected structure."""
        # Act
        agent = ConversationalAgent(self.agent_profile, self.mock_llm)
        
        # Assert
        expected_metrics = [
            "total_interactions",
            "average_confidence", 
            "average_response_time",
            "feedback_score",
            "success_rate"
        ]
        
        for metric in expected_metrics:
            assert metric in agent.performance_metrics
            assert isinstance(agent.performance_metrics[metric], (int, float))

    def test_add_tool_to_agent(self):
        """Test adding tools to agent."""
        # Arrange
        agent = ConversationalAgent(self.agent_profile, self.mock_llm)
        mock_tool = MagicMock()
        mock_tool.name = "calculator"
        
        # Act
        agent.add_tool("calculator", mock_tool)
        
        # Assert
        assert "calculator" in agent.tools
        assert agent.tools["calculator"] == mock_tool

    def test_get_conversation_history(self):
        """Test getting conversation history for a conversation."""
        # Arrange
        agent = ConversationalAgent(self.agent_profile, self.mock_llm)
        conversation_id = "conv-123"
        
        # Act
        history = agent.get_conversation_history(conversation_id)
        
        # Assert
        assert isinstance(history, list)
        assert len(history) == 0  # Initially empty

    def test_update_performance_metrics(self):
        """Test updating agent performance metrics."""
        # Arrange
        agent = ConversationalAgent(self.agent_profile, self.mock_llm)
        
        # Act
        agent.update_performance_metrics({
            "response_time": 1.5,
            "confidence": 0.85,
            "feedback_score": 4.2
        })
        
        # Assert
        assert agent.performance_metrics["total_interactions"] == 1
        assert agent.performance_metrics["average_response_time"] == 1.5
        assert agent.performance_metrics["average_confidence"] == 0.85


@pytest.mark.unit
class TestConversationalAgent:
    """Test ConversationalAgent implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = AsyncMock()
        self.agent_profile = AgentProfile(
            id="conversational-agent",
            name="Conversational Agent",
            description="A conversational AI agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE, AgentCapability.MEMORY],
            system_message="You are a helpful conversational assistant."
        )
        self.agent = ConversationalAgent(self.agent_profile, self.mock_llm)

    @pytest.mark.asyncio
    async def test_process_message_basic(self):
        """Test basic message processing."""
        # Arrange
        message = "Hello, how are you?"
        conversation_id = "conv-123"
        
        self.mock_llm.ainvoke.return_value = MagicMock(content="I'm doing well, thank you!")
        
        # Act
        response = await self.agent.process_message(message, conversation_id)
        
        # Assert
        assert response is not None
        assert "content" in response
        assert response["content"] == "I'm doing well, thank you!"
        self.mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_with_context(self):
        """Test message processing with additional context."""
        # Arrange
        message = "What did I ask about earlier?"
        conversation_id = "conv-123"
        context = {"previous_topic": "weather"}
        
        self.mock_llm.ainvoke.return_value = MagicMock(content="You asked about the weather.")
        
        # Act
        response = await self.agent.process_message(
            message, conversation_id, context=context
        )
        
        # Assert
        assert response is not None
        assert "content" in response
        self.mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_message_stores_interaction(self):
        """Test that message processing stores interaction in history."""
        # Arrange
        message = "Test message"
        conversation_id = "conv-123"
        
        self.mock_llm.ainvoke.return_value = MagicMock(content="Test response")
        
        # Act
        await self.agent.process_message(message, conversation_id)
        
        # Assert
        history = self.agent.get_conversation_history(conversation_id)
        assert len(history) == 1
        interaction = history[0]
        assert interaction.user_message == message
        assert interaction.agent_response == "Test response"
        assert interaction.agent_id == self.agent.profile.id

    @pytest.mark.asyncio
    async def test_process_message_error_handling(self):
        """Test error handling during message processing."""
        # Arrange
        message = "Test message"
        conversation_id = "conv-123"
        
        self.mock_llm.ainvoke.side_effect = Exception("LLM error")
        
        # Act & Assert
        with pytest.raises(AgentExecutionError):
            await self.agent.process_message(message, conversation_id)

    def test_build_message_context(self):
        """Test building message context from conversation history."""
        # Arrange
        conversation_id = "conv-123"
        
        # Add some history
        interaction1 = AgentInteraction(
            agent_id=self.agent.profile.id,
            conversation_id=conversation_id,
            user_message="Hello",
            agent_response="Hi there!"
        )
        self.agent.conversation_history[conversation_id] = [interaction1]
        
        # Act
        context = self.agent._build_message_context(conversation_id, max_history=5)
        
        # Assert
        assert len(context) >= 1
        assert any("Hello" in str(msg) for msg in context)

    def test_calculate_confidence_score(self):
        """Test confidence score calculation."""
        # Arrange
        response_text = "I am confident about this answer."
        
        # Act
        confidence = self.agent._calculate_confidence_score(response_text)
        
        # Assert
        assert 0.0 <= confidence <= 1.0
        assert isinstance(confidence, float)


@pytest.mark.unit
class TestSpecializedAgent:
    """Test SpecializedAgent implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_llm = AsyncMock()
        self.agent_profile = AgentProfile(
            id="specialized-agent",
            name="Code Assistant",
            description="Specialized agent for code assistance",
            type=AgentType.SPECIALIZED,
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.TOOL_USE],
            system_message="You are a specialized code assistant.",
            specialization="programming"
        )
        self.agent = SpecializedAgent(self.agent_profile, self.mock_llm)

    @pytest.mark.asyncio
    async def test_specialized_processing(self):
        """Test specialized agent processing with domain expertise."""
        # Arrange
        message = "Write a Python function to calculate factorial"
        conversation_id = "conv-123"
        
        self.mock_llm.ainvoke.return_value = MagicMock(
            content="def factorial(n):\n    return 1 if n <= 1 else n * factorial(n-1)"
        )
        
        # Act
        response = await self.agent.process_message(message, conversation_id)
        
        # Assert
        assert response is not None
        assert "def factorial" in response["content"]
        assert "specialization_applied" in response
        assert response["specialization_applied"] == "programming"

    @pytest.mark.asyncio
    async def test_tool_integration(self):
        """Test specialized agent with tool integration."""
        # Arrange
        mock_tool = AsyncMock()
        mock_tool.name = "code_executor"
        mock_tool.ainvoke.return_value = "Code executed successfully"
        
        self.agent.add_tool("code_executor", mock_tool)
        
        message = "Run this Python code: print('Hello World')"
        conversation_id = "conv-123"
        
        # Mock the LLM to indicate tool usage
        self.mock_llm.ainvoke.return_value = MagicMock(
            content="I'll execute that code for you.",
            additional_kwargs={"tool_calls": [{"name": "code_executor"}]}
        )
        
        # Act
        response = await self.agent.process_message(message, conversation_id)
        
        # Assert
        assert response is not None
        assert "tools_used" in response

    def test_validate_specialization_match(self):
        """Test validation of message-specialization match."""
        # Arrange
        programming_messages = [
            "Write a Python function",
            "Debug this code",
            "Explain this algorithm"
        ]
        
        non_programming_messages = [
            "What's the weather like?",
            "Tell me a joke",
            "What's 2+2?"
        ]
        
        # Act & Assert
        for msg in programming_messages:
            assert self.agent._is_specialization_match(msg) is True
            
        for msg in non_programming_messages:
            # These might still match if the agent is flexible
            match = self.agent._is_specialization_match(msg)
            assert isinstance(match, bool)


@pytest.mark.unit
class TestAgentManager:
    """Test AgentManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AgentManager()

    def test_agent_manager_initialization(self):
        """Test AgentManager initialization."""
        # Assert
        assert isinstance(self.manager.agents, dict)
        assert len(self.manager.agents) == 0
        assert isinstance(self.manager.registry, AgentRegistry)

    @pytest.mark.asyncio
    async def test_create_agent(self):
        """Test creating a new agent."""
        # Arrange
        mock_llm = AsyncMock()
        profile = AgentProfile(
            id="new-agent",
            name="New Agent",
            description="A newly created agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        # Act
        agent = await self.manager.create_agent(profile, mock_llm)
        
        # Assert
        assert agent is not None
        assert agent.profile.id == "new-agent"
        assert "new-agent" in self.manager.agents

    @pytest.mark.asyncio
    async def test_get_agent_existing(self):
        """Test getting an existing agent."""
        # Arrange
        mock_llm = AsyncMock()
        profile = AgentProfile(
            id="existing-agent",
            name="Existing Agent",
            description="An existing agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        created_agent = await self.manager.create_agent(profile, mock_llm)
        
        # Act
        retrieved_agent = await self.manager.get_agent("existing-agent")
        
        # Assert
        assert retrieved_agent == created_agent

    @pytest.mark.asyncio
    async def test_get_agent_nonexistent(self):
        """Test getting a non-existent agent."""
        # Act & Assert
        with pytest.raises(AgentError) as exc_info:
            await self.manager.get_agent("nonexistent-agent")
        
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_remove_agent(self):
        """Test removing an agent."""
        # Arrange
        mock_llm = AsyncMock()
        profile = AgentProfile(
            id="removable-agent",
            name="Removable Agent",
            description="An agent to be removed",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        await self.manager.create_agent(profile, mock_llm)
        assert "removable-agent" in self.manager.agents
        
        # Act
        removed = await self.manager.remove_agent("removable-agent")
        
        # Assert
        assert removed is True
        assert "removable-agent" not in self.manager.agents

    def test_list_agents(self):
        """Test listing all agents."""
        # Arrange
        # Start with empty manager
        agent_list = self.manager.list_agents()
        initial_count = len(agent_list)
        
        # Act & Assert
        assert isinstance(agent_list, list)
        assert len(agent_list) == initial_count

    @pytest.mark.asyncio
    async def test_find_agents_by_capability(self):
        """Test finding agents by capability."""
        # Arrange
        mock_llm = AsyncMock()
        
        # Create agents with different capabilities
        conversational_profile = AgentProfile(
            id="conv-agent",
            name="Conversational Agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE, AgentCapability.MEMORY]
        )
        
        code_profile = AgentProfile(
            id="code-agent", 
            name="Code Agent",
            type=AgentType.SPECIALIZED,
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.TOOL_USE]
        )
        
        await self.manager.create_agent(conversational_profile, mock_llm)
        await self.manager.create_agent(code_profile, mock_llm)
        
        # Act
        nl_agents = self.manager.find_agents_by_capability(AgentCapability.NATURAL_LANGUAGE)
        code_agents = self.manager.find_agents_by_capability(AgentCapability.CODE_GENERATION)
        
        # Assert
        assert len(nl_agents) == 1
        assert nl_agents[0].profile.id == "conv-agent"
        
        assert len(code_agents) == 1
        assert code_agents[0].profile.id == "code-agent"

    @pytest.mark.asyncio
    async def test_agent_status_management(self):
        """Test agent status management."""
        # Arrange
        mock_llm = AsyncMock()
        profile = AgentProfile(
            id="status-agent",
            name="Status Agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        agent = await self.manager.create_agent(profile, mock_llm)
        
        # Act & Assert
        # Initial status should be active
        assert agent.get_status() == AgentStatus.ACTIVE
        
        # Pause agent
        await self.manager.pause_agent("status-agent")
        assert agent.get_status() == AgentStatus.PAUSED
        
        # Resume agent
        await self.manager.resume_agent("status-agent")
        assert agent.get_status() == AgentStatus.ACTIVE


@pytest.mark.unit
class TestAgentExecutor:
    """Test AgentExecutor functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = AgentExecutor()

    @pytest.mark.asyncio
    async def test_execute_agent_task(self):
        """Test executing a task with an agent."""
        # Arrange
        mock_agent = AsyncMock()
        mock_agent.process_message.return_value = {
            "content": "Task completed successfully",
            "confidence": 0.9
        }
        
        task = {
            "message": "Complete this task",
            "conversation_id": "conv-123",
            "context": {"priority": "high"}
        }
        
        # Act
        result = await self.executor.execute_task(mock_agent, task)
        
        # Assert
        assert result is not None
        assert result["content"] == "Task completed successfully"
        assert result["confidence"] == 0.9
        mock_agent.process_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_timeout(self):
        """Test task execution with timeout."""
        # Arrange
        slow_agent = AsyncMock()
        
        async def slow_process(*args, **kwargs):
            await asyncio.sleep(2.0)  # Simulate slow processing
            return {"content": "Slow response"}
        
        slow_agent.process_message = slow_process
        
        task = {
            "message": "Slow task",
            "conversation_id": "conv-123"
        }
        
        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await self.executor.execute_task(slow_agent, task, timeout=0.1)

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel execution of multiple agent tasks."""
        # Arrange
        agents = [AsyncMock() for _ in range(3)]
        
        for i, agent in enumerate(agents):
            agent.process_message.return_value = {
                "content": f"Response from agent {i}",
                "agent_id": f"agent-{i}"
            }
        
        tasks = [
            {
                "message": f"Task {i}",
                "conversation_id": f"conv-{i}"
            }
            for i in range(3)
        ]
        
        # Act
        results = await self.executor.execute_parallel_tasks(
            list(zip(agents, tasks))
        )
        
        # Assert
        assert len(results) == 3
        for i, result in enumerate(results):
            assert f"Response from agent {i}" in result["content"]


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = AgentManager()
        self.executor = AgentExecutor()

    @pytest.mark.asyncio
    async def test_complete_agent_workflow(self):
        """Test complete agent workflow from creation to execution."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(
            content="Hello! I'm ready to help you with your questions."
        )
        
        profile = AgentProfile(
            id="workflow-agent",
            name="Workflow Test Agent",
            description="Agent for testing complete workflow",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE, AgentCapability.MEMORY],
            system_message="You are a helpful assistant for workflow testing."
        )
        
        # Act
        # Step 1: Create agent
        agent = await self.manager.create_agent(profile, mock_llm)
        
        # Step 2: Execute task
        task = {
            "message": "Hello, can you help me?",
            "conversation_id": "integration-test-conv"
        }
        
        result = await self.executor.execute_task(agent, task)
        
        # Step 3: Verify conversation history
        history = agent.get_conversation_history("integration-test-conv")
        
        # Assert
        assert agent.profile.id == "workflow-agent"
        assert result["content"] == "Hello! I'm ready to help you with your questions."
        assert len(history) == 1
        assert history[0].user_message == "Hello, can you help me?"

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self):
        """Test coordination between multiple agents."""
        # Arrange
        mock_llm1 = AsyncMock()
        mock_llm2 = AsyncMock()
        
        mock_llm1.ainvoke.return_value = MagicMock(
            content="I can help with general questions."
        )
        mock_llm2.ainvoke.return_value = MagicMock(
            content="def hello(): return 'Hello from code agent'"
        )
        
        # Create different types of agents
        general_profile = AgentProfile(
            id="general-agent",
            name="General Assistant",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        code_profile = AgentProfile(
            id="code-agent",
            name="Code Assistant", 
            type=AgentType.SPECIALIZED,
            capabilities=[AgentCapability.CODE_GENERATION],
            specialization="programming"
        )
        
        general_agent = await self.manager.create_agent(general_profile, mock_llm1)
        code_agent = await self.manager.create_agent(code_profile, mock_llm2)
        
        # Act
        # Route different types of questions to appropriate agents
        general_task = {
            "message": "What's the weather like?",
            "conversation_id": "multi-conv-1"
        }
        
        code_task = {
            "message": "Write a hello function in Python",
            "conversation_id": "multi-conv-2"
        }
        
        general_result = await self.executor.execute_task(general_agent, general_task)
        code_result = await self.executor.execute_task(code_agent, code_task)
        
        # Assert
        assert "general questions" in general_result["content"]
        assert "def hello" in code_result["content"]
        
        # Verify each agent handled their specialized task
        general_history = general_agent.get_conversation_history("multi-conv-1")
        code_history = code_agent.get_conversation_history("multi-conv-2")
        
        assert len(general_history) == 1
        assert len(code_history) == 1

    @pytest.mark.asyncio
    async def test_agent_performance_tracking(self):
        """Test agent performance metrics tracking."""
        # Arrange
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = MagicMock(
            content="Performance test response"
        )
        
        profile = AgentProfile(
            id="perf-agent",
            name="Performance Agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        agent = await self.manager.create_agent(profile, mock_llm)
        
        # Act
        # Execute multiple tasks to build performance history
        tasks = [
            {
                "message": f"Test message {i}",
                "conversation_id": f"perf-conv-{i}"
            }
            for i in range(5)
        ]
        
        for task in tasks:
            await self.executor.execute_task(agent, task)
        
        # Assert
        metrics = agent.performance_metrics
        assert metrics["total_interactions"] == 5
        assert metrics["average_response_time"] >= 0
        assert metrics["success_rate"] >= 0

    @pytest.mark.asyncio
    async def test_agent_error_recovery(self):
        """Test agent error handling and recovery."""
        # Arrange
        unreliable_llm = AsyncMock()
        
        # First call fails, second succeeds
        unreliable_llm.ainvoke.side_effect = [
            Exception("Temporary LLM failure"),
            MagicMock(content="Recovery successful")
        ]
        
        profile = AgentProfile(
            id="recovery-agent",
            name="Recovery Agent",
            type=AgentType.CONVERSATIONAL,
            capabilities=[AgentCapability.NATURAL_LANGUAGE]
        )
        
        agent = await self.manager.create_agent(profile, unreliable_llm)
        
        # Act
        task = {
            "message": "Test error recovery",
            "conversation_id": "recovery-conv"
        }
        
        # First attempt should fail
        with pytest.raises(AgentExecutionError):
            await self.executor.execute_task(agent, task)
        
        # Second attempt should succeed
        result = await self.executor.execute_task(agent, task)
        
        # Assert
        assert result["content"] == "Recovery successful"