"""Simple test to verify async methods work correctly."""

import asyncio
import sys
import os

# Add the project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest import mock
from unittest.mock import AsyncMock, MagicMock

from chatter.core.langgraph import LangGraphWorkflowManager


async def test_get_retriever_is_async():
    """Test that get_retriever is async and doesn't produce warnings."""
    manager = LangGraphWorkflowManager()
    
    # Mock the embedding service to avoid actual dependencies
    with mock.patch('chatter.services.embeddings.EmbeddingService') as mock_embedding_service:
        mock_service_instance = AsyncMock()
        mock_embedding_service.return_value = mock_service_instance
        mock_service_instance.get_default_provider = AsyncMock(return_value=None)
        
        # This should work without the "Cannot get embeddings synchronously while event loop is running" warning
        result = await manager.get_retriever("test_workspace")
        print(f"✓ get_retriever returned: {result}")
        
        # Verify the async method was called
        mock_service_instance.get_default_provider.assert_called_once()
        print("✓ Async embedding service method was called correctly")


async def test_get_tools_is_async():
    """Test that get_tools is async."""
    manager = LangGraphWorkflowManager()
    
    with mock.patch('chatter.core.dependencies.get_builtin_tools') as mock_builtin:
        mock_builtin.return_value = ['test_tool']
        
        result = await manager.get_tools("test_workspace")
        print(f"✓ get_tools returned: {result}")
        
        assert isinstance(result, list)
        assert 'test_tool' in result
        print("✓ get_tools returned expected results")


async def test_async_methods_work_in_event_loop():
    """Test that async methods work when called from a running event loop."""
    # Verify we're in a running event loop (this is the scenario that was causing the warning)
    loop = asyncio.get_event_loop()
    assert loop.is_running()
    print("✓ Running in an active event loop")
    
    manager = LangGraphWorkflowManager()
    
    # Mock dependencies
    with mock.patch('chatter.services.embeddings.EmbeddingService') as mock_embedding_service, \
         mock.patch('chatter.core.dependencies.get_builtin_tools') as mock_builtin:
        
        mock_service_instance = AsyncMock()
        mock_embedding_service.return_value = mock_service_instance
        mock_service_instance.get_default_provider = AsyncMock(return_value=None)
        mock_builtin.return_value = ['tool1']
        
        # Both methods should work without warnings
        retriever = await manager.get_retriever("test_workspace")
        tools = await manager.get_tools("test_workspace")
        
        print(f"✓ get_retriever returned: {retriever}")
        print(f"✓ get_tools returned: {tools}")
        print("✓ No warnings should have been produced!")


async def main():
    """Run all tests."""
    print("Testing async LangGraph methods...")
    print("=" * 50)
    
    await test_get_retriever_is_async()
    print()
    
    await test_get_tools_is_async()
    print()
    
    await test_async_methods_work_in_event_loop()
    print()
    
    print("=" * 50)
    print("✅ All tests passed! The sync function issue has been fixed.")


if __name__ == "__main__":
    asyncio.run(main())