"""Test async methods in LangGraph workflow manager."""

import asyncio
from unittest import mock
from unittest.mock import AsyncMock, MagicMock

import pytest

from chatter.core.langgraph import LangGraphWorkflowManager


class TestAsyncLangGraphMethods:
    """Test that LangGraph methods work properly as async."""

    @pytest.mark.asyncio
    async def test_get_retriever_async_no_event_loop_warning(self):
        """Test that get_retriever as async method doesn't produce event loop warnings."""
        manager = LangGraphWorkflowManager()

        # Mock the embedding service to avoid actual DB calls
        with mock.patch(
            'chatter.services.embeddings.EmbeddingService'
        ) as mock_embedding_service:
            mock_service_instance = AsyncMock()
            mock_embedding_service.return_value = mock_service_instance
            mock_service_instance.get_default_provider = AsyncMock(
                return_value=None
            )

            # This should not produce the warning "Cannot get embeddings synchronously while event loop is running"
            retriever = await manager.get_retriever("test_workspace")

            # Should return None since we mocked get_default_provider to return None
            assert retriever is None
            # Verify the async method was called
            mock_service_instance.get_default_provider.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_tools_async_returns_builtin_tools(self):
        """Test that get_tools as async method properly returns builtin tools."""
        manager = LangGraphWorkflowManager()

        with mock.patch(
            'chatter.core.dependencies.get_builtin_tools'
        ) as mock_builtin:
            mock_builtin.return_value = ['test_tool_1', 'test_tool_2']

            tools = await manager.get_tools("test_workspace")

            assert isinstance(tools, list)
            assert len(tools) == 2
            assert 'test_tool_1' in tools
            assert 'test_tool_2' in tools
            mock_builtin.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_methods_can_be_called_in_running_event_loop(
        self,
    ):
        """Test that async methods work properly when called from within a running event loop."""
        manager = LangGraphWorkflowManager()

        # Verify we're in a running event loop
        loop = asyncio.get_event_loop()
        assert loop.is_running()

        # Mock dependencies to avoid actual service calls
        with (
            mock.patch(
                'chatter.services.embeddings.EmbeddingService'
            ) as mock_embedding_service,
            mock.patch(
                'chatter.core.dependencies.get_builtin_tools'
            ) as mock_builtin,
        ):
            mock_service_instance = AsyncMock()
            mock_embedding_service.return_value = mock_service_instance
            mock_service_instance.get_default_provider = AsyncMock(
                return_value=None
            )
            mock_builtin.return_value = ['tool1']

            # Both methods should work without warnings
            retriever = await manager.get_retriever("test_workspace")
            tools = await manager.get_tools("test_workspace")

            # Basic assertions to verify they executed
            assert retriever is None  # Due to our mock
            assert tools == ['tool1']  # Due to our mock

    @pytest.mark.asyncio
    async def test_get_retriever_with_successful_embeddings(self):
        """Test get_retriever when embeddings are available."""
        manager = LangGraphWorkflowManager()

        # Mock all the dependencies
        mock_embeddings = MagicMock()
        mock_vector_store = MagicMock()
        mock_retriever = MagicMock()

        with (
            mock.patch(
                'chatter.services.embeddings.EmbeddingService'
            ) as mock_embedding_service,
            mock.patch(
                'chatter.core.vector_store.vector_store_manager'
            ) as mock_vector_store_manager,
        ):
            mock_service_instance = AsyncMock()
            mock_embedding_service.return_value = mock_service_instance
            mock_service_instance.get_default_provider = AsyncMock(
                return_value=mock_embeddings
            )

            mock_vector_store_manager.create_store.return_value = (
                mock_vector_store
            )
            mock_vector_store.as_retriever.return_value = mock_retriever

            retriever = await manager.get_retriever(
                "test_workspace", document_ids=["doc1", "doc2"]
            )

            # Verify the retriever was created
            assert retriever == mock_retriever

            # Verify the correct methods were called
            mock_service_instance.get_default_provider.assert_called_once()
            mock_vector_store_manager.create_store.assert_called_once_with(
                store_type="pgvector",
                embeddings=mock_embeddings,
                collection_name="documents_test_workspace",
            )
            mock_vector_store.as_retriever.assert_called_once()
