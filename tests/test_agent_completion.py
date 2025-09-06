"""Test to verify agent feature completion and functionality."""

from unittest.mock import AsyncMock

import pytest

from chatter.core.agents import AgentManager, AgentType


class TestAgentFeatureCompletion:
    """Test suite to verify agent feature completion."""

    @pytest.mark.asyncio
    async def test_agent_templates_available(self):
        """Test that agent templates are available."""
        manager = AgentManager()
        templates = await manager.get_agent_templates()

        # Should have predefined templates
        assert len(templates) >= 5

        # Check template structure
        for template in templates:
            assert 'id' in template
            assert 'name' in template
            assert 'description' in template
            assert 'agent_type' in template
            assert 'system_message' in template
            assert isinstance(template['agent_type'], AgentType)

    @pytest.mark.asyncio
    async def test_agent_creation_with_fake_llm(self):
        """Test agent creation with mock LLM."""
        manager = AgentManager()

        # Create mock LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=AsyncMock(content="Test response")
        )

        # Create agent
        agent_id = await manager.create_agent(
            name="Test Agent",
            agent_type=AgentType.CONVERSATIONAL,
            description="Test agent for feature completion",
            system_message="You are a test agent",
            llm=mock_llm,
            created_by="test-user",
        )

        assert isinstance(agent_id, str)
        assert len(agent_id) > 0

    @pytest.mark.asyncio
    async def test_agent_retrieval(self):
        """Test agent retrieval after creation."""
        manager = AgentManager()

        # Create mock LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=AsyncMock(content="Test response")
        )

        # Create agent
        agent_id = await manager.create_agent(
            name="Retrieval Test Agent",
            agent_type=AgentType.SPECIALIST,
            description="Agent for testing retrieval",
            system_message="You are a specialist agent",
            llm=mock_llm,
            created_by="test-user",
        )

        # Retrieve agent
        agent = await manager.get_agent(agent_id)

        assert agent is not None
        assert agent.profile.name == "Retrieval Test Agent"
        assert agent.profile.type == AgentType.SPECIALIST
        assert agent.profile.created_by == "test-user"

    @pytest.mark.asyncio
    async def test_agent_listing_and_filtering(self):
        """Test agent listing and filtering functionality."""
        manager = AgentManager()

        # Create mock LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=AsyncMock(content="Test response")
        )

        # Create multiple agents
        await manager.create_agent(
            name="Conversational Agent",
            agent_type=AgentType.CONVERSATIONAL,
            description="Conversational test agent",
            system_message="You are conversational",
            llm=mock_llm,
            created_by="user1",
        )

        await manager.create_agent(
            name="Specialist Agent",
            agent_type=AgentType.SPECIALIST,
            description="Specialist test agent",
            system_message="You are a specialist",
            llm=mock_llm,
            created_by="user2",
        )

        # Test listing all agents
        all_agents, total = await manager.list_agents()
        assert total >= 2
        assert len(all_agents) >= 2

        # Test filtering by type
        conv_agents, conv_total = await manager.list_agents(
            agent_type=AgentType.CONVERSATIONAL
        )
        assert conv_total >= 1

        spec_agents, spec_total = await manager.list_agents(
            agent_type=AgentType.SPECIALIST
        )
        assert spec_total >= 1

        # Test filtering by user
        user1_agents, user1_total = await manager.list_agents(
            user_id="user1"
        )
        assert user1_total >= 1

    @pytest.mark.asyncio
    async def test_agent_interaction(self):
        """Test agent message processing."""
        manager = AgentManager()

        # Create mock LLM that returns predictable responses
        mock_llm = AsyncMock()
        mock_response = AsyncMock()
        mock_response.content = "Hello! I'm a test agent response."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        # Create agent
        agent_id = await manager.create_agent(
            name="Interactive Agent",
            agent_type=AgentType.CONVERSATIONAL,
            description="Agent for interaction testing",
            system_message="You are an interactive test agent",
            llm=mock_llm,
            created_by="test-user",
        )

        # Get agent and test interaction
        agent = await manager.get_agent(agent_id)
        assert agent is not None

        # Test message processing
        response = await agent.process_message(
            message="Hello, how are you?",
            conversation_id="test-conversation",
            context={"user_id": "test-user"},
        )

        assert isinstance(response, str)
        assert len(response) > 0
        # Verify LLM was called
        mock_llm.ainvoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_agent_statistics(self):
        """Test agent statistics functionality."""
        manager = AgentManager()

        # Create mock LLM
        mock_llm = AsyncMock()
        mock_llm.ainvoke = AsyncMock(
            return_value=AsyncMock(content="Test")
        )

        # Create an agent
        await manager.create_agent(
            name="Stats Test Agent",
            agent_type=AgentType.CONVERSATIONAL,
            description="Agent for stats testing",
            system_message="Test agent",
            llm=mock_llm,
            created_by="test-user",
        )

        # Get statistics
        stats = await manager.get_agent_stats()

        assert isinstance(stats, dict)
        assert 'total_agents' in stats
        assert 'active_agents' in stats
        assert 'agent_types' in stats
        assert 'total_interactions' in stats
        assert stats['total_agents'] >= 1

    @pytest.mark.asyncio
    async def test_nonexistent_agent_handling(self):
        """Test handling of non-existent agents."""
        manager = AgentManager()

        # Try to get non-existent agent
        agent = await manager.get_agent("non-existent-agent-id")
        assert agent is None

    def test_agent_executor_fixed(self):
        """Test that AgentExecutor bug is fixed."""
        import inspect

        from chatter.core.agents import AgentExecutor

        executor = AgentExecutor()

        # Check that execute_agent_task method exists and has correct signature
        assert hasattr(executor, 'execute_agent_task')

        sig = inspect.signature(executor.execute_agent_task)
        params = list(sig.parameters.keys())

        # Should have self, agent, task, context parameters
        assert 'agent' in params
        assert 'task' in params
        assert 'context' in params

    def test_agent_manager_class_mapping(self):
        """Test that agent manager has correct agent class mappings."""
        manager = AgentManager()

        # Should have all agent types mapped
        assert AgentType.CONVERSATIONAL in manager.agent_classes
        assert AgentType.TASK_ORIENTED in manager.agent_classes
        assert AgentType.SPECIALIST in manager.agent_classes

        # Each mapping should be a class
        for _agent_type, agent_class in manager.agent_classes.items():
            assert isinstance(agent_class, type)
            assert hasattr(agent_class, 'process_message')
            assert hasattr(agent_class, 'get_capabilities')

    def test_database_models_exist(self):
        """Test that database models exist and are properly defined."""
        from chatter.models.agent_db import AgentDB, AgentInteractionDB

        # Check that models exist
        assert AgentDB is not None
        assert AgentInteractionDB is not None

        # Check key fields exist
        assert hasattr(AgentDB, 'name')
        assert hasattr(AgentDB, 'agent_type')
        assert hasattr(AgentDB, 'system_message')
        assert hasattr(AgentDB, 'created_by')

        assert hasattr(AgentInteractionDB, 'agent_id')
        assert hasattr(AgentInteractionDB, 'user_message')
        assert hasattr(AgentInteractionDB, 'agent_response')
