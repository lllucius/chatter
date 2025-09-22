"""Test enhanced LangGraph streaming support."""

from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest

from chatter.core.langgraph import LangGraphWorkflowManager


class TestLangGraphStreamingEnhancement:
    """Test LangGraph streaming enhancements."""

    @pytest.mark.asyncio
    async def test_langgraph_workflow_manager_has_get_tools_method(
        self,
    ):
        """Test that LangGraphWorkflowManager has the get_tools method."""
        manager = LangGraphWorkflowManager()
        assert hasattr(
            manager, 'get_tools'
        ), "LangGraphWorkflowManager should have get_tools method"

        # Test the method is callable
        tools = await manager.get_tools("test_workspace")
        assert isinstance(tools, list), "get_tools should return a list"

    @pytest.mark.asyncio
    async def test_langgraph_workflow_manager_has_get_retriever_method(
        self,
    ):
        """Test that LangGraphWorkflowManager has the get_retriever method."""
        manager = LangGraphWorkflowManager()
        assert hasattr(
            manager, 'get_retriever'
        ), "LangGraphWorkflowManager should have get_retriever method"

        # Test the method is callable (will return None if no embeddings available)
        retriever = await manager.get_retriever("test_workspace")
        # This can be None if no embeddings service is available, which is fine for this test
        assert retriever is None or hasattr(
            retriever, 'invoke'
        ), "get_retriever should return None or a retriever object"

    @pytest.mark.asyncio
    async def test_langgraph_workflow_streaming_interface_exists(self):
        """Test that LangGraph workflows support the streaming interface."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        # Mock LLM for workflow creation
        mock_llm = MagicMock()
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        # Create a workflow
        workflow = await manager.create_workflow(
            llm=mock_llm,
            mode="plain",
            system_message="Test streaming interface",
        )

        # Test that the workflow has the required streaming interface methods
        assert hasattr(
            workflow, 'astream'
        ), "LangGraph workflow should have astream method for streaming"
        assert hasattr(
            workflow, 'ainvoke'
        ), "LangGraph workflow should have ainvoke method for regular execution"
        assert callable(workflow.astream), "astream should be callable"
        assert callable(workflow.ainvoke), "ainvoke should be callable"

    @pytest.mark.asyncio
    async def test_workflow_manager_supports_all_modes_with_streaming(
        self,
    ):
        """Test that all workflow modes can be created and support streaming."""
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()

        mock_llm = MagicMock()
        mock_llm.bind_tools = MagicMock(return_value=mock_llm)

        # Test all workflow modes support streaming interface
        modes = [
            "plain",
            "rag",
            "tools",
            "full",
        ]

        for mode in modes:
            workflow = await manager.create_workflow(
                llm=mock_llm,
                mode=mode,
                system_message=f"Test mode: {mode}",
                enable_memory=True,
            )

            assert hasattr(
                workflow, 'astream'
            ), f"Workflow mode '{mode}' should support streaming via astream"
            assert hasattr(
                workflow, 'ainvoke'
            ), f"Workflow mode '{mode}' should support regular execution via ainvoke"

    @pytest.mark.asyncio
    async def test_llm_service_workflow_creation_with_streaming_support(
        self,
    ):
        """Test that LLM service creates workflows that support streaming."""
        # Mock the LLM service dependencies
        with (
            mock.patch(
                'chatter.services.llm.get_mcp_service'
            ) as mock_mcp,
            mock.patch(
                'chatter.services.llm.get_builtin_tools'
            ) as mock_tools,
            mock.patch(
                'chatter.core.langgraph.workflow_manager'
            ) as mock_manager,
        ):
            # Setup mocks
            mock_mcp.return_value.get_tools = AsyncMock(return_value=[])
            mock_tools.return_value = []

            # Mock workflow with streaming interface
            mock_workflow = MagicMock()
            mock_workflow.astream = AsyncMock()
            mock_workflow.ainvoke = AsyncMock()
            mock_manager.create_workflow = AsyncMock(
                return_value=mock_workflow
            )

            # Import and test LLM service
            from chatter.services.llm import LLMService

            llm_service = LLMService()

            # Mock provider creation to avoid complex dependency setup
            mock_provider = MagicMock()
            llm_service.get_default_provider = AsyncMock(
                return_value=mock_provider
            )

            # Test workflow creation through LLM service
            workflow = await llm_service.create_langgraph_workflow(
                provider_name=None,
                capabilities="plain",
                system_message="Test streaming workflow",
                enable_memory=True,
                memory_window=10,
            )

            # Verify streaming interface is available
            assert hasattr(
                workflow, 'astream'
            ), "LLM service created workflow should have astream method"
            assert hasattr(
                workflow, 'ainvoke'
            ), "LLM service created workflow should have ainvoke method"

            # Verify the workflow manager was called with correct parameters
            mock_manager.create_workflow.assert_called_once()
            call_args = mock_manager.create_workflow.call_args
            assert call_args[1]['mode'] == 'plain'
            assert call_args[1]['enable_memory']
            assert call_args[1]['memory_window'] == 10

    @pytest.mark.asyncio
    async def test_workflow_manager_get_tools_returns_builtin_tools(
        self,
    ):
        """Test that get_tools properly returns builtin tools."""
        with mock.patch(
            'chatter.core.dependencies.get_builtin_tools'
        ) as mock_builtin:
            mock_builtin.return_value = ['tool1', 'tool2', 'tool3']

            manager = LangGraphWorkflowManager()
            tools = await manager.get_tools("test_workspace")

            # Should have returned the mocked builtin tools
            assert len(tools) == 3
            assert tools == ['tool1', 'tool2', 'tool3']
            mock_builtin.assert_called_once()

    @pytest.mark.asyncio
    async def test_workflow_manager_get_tools_handles_errors_gracefully(
        self,
    ):
        """Test that get_tools handles errors gracefully."""
        with mock.patch(
            'chatter.core.dependencies.get_builtin_tools'
        ) as mock_builtin:
            mock_builtin.side_effect = Exception("Test error")

            manager = LangGraphWorkflowManager()
            tools = await manager.get_tools("test_workspace")

            # Should return empty list on error
            assert tools == []

    @pytest.mark.asyncio
    async def test_workflow_manager_get_retriever_handles_missing_dependencies(
        self,
    ):
        """Test that get_retriever handles missing dependencies gracefully."""
        manager = LangGraphWorkflowManager()

        # Should return None if embeddings service is not available or configured
        retriever = await manager.get_retriever("test_workspace")
        assert (
            retriever is None
        ), "Should return None when embeddings service is not available"
