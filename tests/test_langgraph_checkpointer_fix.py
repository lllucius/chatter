"""Test for LangGraph checkpointer aget_tuple fix.

This test ensures that the AsyncPostgresSaver properly implements
the aget_tuple method to fix the NotImplementedError that occurred
when using PostgreSQL checkpointer with LangGraph workflows.
"""

import pytest
import asyncio
from unittest.mock import Mock
from langchain_core.runnables import RunnableConfig

from chatter.core.langgraph import AsyncPostgresSaver


class TestAsyncPostgresSaverFix:
    """Test the AsyncPostgresSaver fix for aget_tuple NotImplementedError."""

    def test_async_postgres_saver_has_aget_tuple(self):
        """Test that AsyncPostgresSaver has its own aget_tuple implementation."""
        from langgraph.checkpoint.base import BaseCheckpointSaver
        
        # Our AsyncPostgresSaver should have its own aget_tuple implementation
        assert hasattr(AsyncPostgresSaver, 'aget_tuple')
        assert 'aget_tuple' in AsyncPostgresSaver.__dict__
        
        # It should NOT be the base class implementation that raises NotImplementedError
        assert AsyncPostgresSaver.aget_tuple != BaseCheckpointSaver.aget_tuple

    def test_aget_tuple_is_async(self):
        """Test that aget_tuple is properly async."""
        import inspect
        
        assert inspect.iscoroutinefunction(AsyncPostgresSaver.aget_tuple)

    @pytest.mark.asyncio
    async def test_aget_tuple_calls_get_tuple(self):
        """Test that aget_tuple properly calls get_tuple via asyncio.to_thread."""
        
        # Create a mock instance
        mock_instance = AsyncPostgresSaver.__new__(AsyncPostgresSaver)
        mock_instance.get_tuple = Mock(return_value="test_result")
        
        config = RunnableConfig(configurable={"thread_id": "test"})
        
        # Call aget_tuple - it should work without NotImplementedError
        result = await mock_instance.aget_tuple(config)
        
        # Verify it called the underlying get_tuple method
        mock_instance.get_tuple.assert_called_once_with(config)
        assert result == "test_result"

    def test_inheritance_hierarchy(self):
        """Test that AsyncPostgresSaver properly inherits from PostgresSaver."""
        from langgraph.checkpoint.postgres import PostgresSaver
        
        assert issubclass(AsyncPostgresSaver, PostgresSaver)

    @pytest.mark.asyncio 
    async def test_original_postgres_saver_issue(self):
        """Test that confirms the original PostgresSaver has the issue."""
        from langgraph.checkpoint.postgres import PostgresSaver
        from langgraph.checkpoint.base import BaseCheckpointSaver
        
        # Confirm original PostgresSaver uses base aget_tuple implementation
        assert PostgresSaver.aget_tuple == BaseCheckpointSaver.aget_tuple
        
        # The base implementation should raise NotImplementedError
        mock_instance = Mock(spec=PostgresSaver)
        mock_instance.aget_tuple = BaseCheckpointSaver.aget_tuple.__get__(mock_instance)
        
        config = RunnableConfig(configurable={"thread_id": "test"})
        
        with pytest.raises(NotImplementedError):
            await mock_instance.aget_tuple(config)

    def test_method_source_contains_fix(self):
        """Test that our aget_tuple method contains the expected fix."""
        import inspect
        
        source = inspect.getsource(AsyncPostgresSaver.aget_tuple)
        
        # Should contain our fix using asyncio.to_thread
        assert 'asyncio.to_thread' in source
        assert 'self.get_tuple' in source


class TestLangGraphWorkflowManager:
    """Test LangGraphWorkflowManager with the checkpointer fix."""

    @pytest.mark.asyncio
    async def test_manager_initialization_with_memory(self):
        """Test that workflow manager initializes correctly with memory checkpointer."""
        from chatter.core.langgraph import LangGraphWorkflowManager
        
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        # Should have a working checkpointer
        assert manager.checkpointer is not None
        assert hasattr(manager.checkpointer, 'aget_tuple')
        
        # Test that aget_tuple works
        config = RunnableConfig(configurable={"thread_id": "test"})
        result = await manager.checkpointer.aget_tuple(config)
        # Should return None for non-existent checkpoint, not raise NotImplementedError
        assert result is None

    @pytest.mark.asyncio
    async def test_workflow_creation_works(self):
        """Test that workflow creation works without checkpointer errors."""
        from chatter.core.langgraph import LangGraphWorkflowManager
        from langchain_openai import ChatOpenAI
        
        manager = LangGraphWorkflowManager()
        await manager._ensure_initialized()
        
        # Create a simple LLM (won't actually call OpenAI in tests)
        llm = ChatOpenAI(model="gpt-3.5-turbo", api_key="test", base_url="http://fake")
        
        # This should work without NotImplementedError
        workflow = await manager.create_workflow(llm, mode="plain")
        assert workflow is not None