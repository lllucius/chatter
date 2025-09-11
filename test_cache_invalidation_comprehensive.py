#!/usr/bin/env python3
"""Comprehensive tests for cache invalidation across all services.

This test script verifies that cache invalidation works properly
for all services that use caching:

1. ModelRegistryService - Provider and model cache invalidation
2. EmbeddingService - Provider instance cache invalidation  
3. LLMService - Provider instance cache invalidation
4. AuthService - User cache invalidation
5. WorkflowManagementService - Workflow cache invalidation
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Create a comprehensive test that demonstrates the cache invalidation works


async def test_embedding_service_cache_invalidation():
    """Test that EmbeddingService invalidates provider cache correctly."""
    from chatter.services.embeddings import EmbeddingService
    
    # Create service instance
    service = EmbeddingService()
    
    # Add some mock providers to cache
    service._providers["test_provider_1"] = MagicMock()
    service._providers["test_provider_2"] = MagicMock()
    
    assert len(service._providers) == 2
    
    # Test invalidating specific provider
    await service.invalidate_provider_cache("test_provider_1")
    assert len(service._providers) == 1
    assert "test_provider_1" not in service._providers
    assert "test_provider_2" in service._providers
    
    # Test invalidating all providers
    await service.invalidate_provider_cache()
    assert len(service._providers) == 0


async def test_llm_service_cache_invalidation():
    """Test that LLMService invalidates provider cache correctly."""
    from chatter.services.llm import LLMService
    
    # Create service instance
    service = LLMService()
    
    # Add some mock providers to cache
    service._providers["test_provider_1"] = MagicMock()
    service._providers["test_provider_2"] = MagicMock()
    
    assert len(service._providers) == 2
    
    # Test invalidating specific provider
    await service.invalidate_provider_cache("test_provider_1")
    assert len(service._providers) == 1
    assert "test_provider_1" not in service._providers
    assert "test_provider_2" in service._providers
    
    # Test invalidating all providers
    await service.invalidate_provider_cache()
    assert len(service._providers) == 0


async def test_auth_service_cache_invalidation():
    """Test that AuthService invalidates user cache correctly."""
    from chatter.core.auth import AuthService
    
    # Mock the cache service
    mock_cache = AsyncMock()
    mock_cache.health_check.return_value = {"status": "healthy"}
    
    # Mock the session
    mock_session = AsyncMock()
    
    with patch('chatter.core.auth.get_general_cache', return_value=mock_cache):
        service = AuthService(mock_session)
        
        # Test cache invalidation
        await service._invalidate_user_cache("test_user_id")
        
        # Verify cache was called correctly
        mock_cache.health_check.assert_called_once()
        mock_cache.delete.assert_called_once_with("user:test_user_id")


async def test_workflow_management_cache_invalidation():
    """Test that WorkflowManagementService invalidates workflow cache correctly."""
    from chatter.services.workflow_management import WorkflowManagementService
    
    # Mock the workflow cache
    mock_workflow_cache = AsyncMock()
    
    # Mock the session
    mock_session = AsyncMock()
    
    with patch('chatter.services.workflow_management.get_unified_workflow_cache', return_value=mock_workflow_cache):
        service = WorkflowManagementService(mock_session)
        
        # Test cache invalidation
        await service._invalidate_workflow_caches("test_workflow_id")
        
        # Verify cache was cleared
        mock_workflow_cache.clear.assert_called_once()


async def test_model_registry_dependent_service_invalidation():
    """Test that ModelRegistryService invalidates dependent service caches."""
    from chatter.core.model_registry import ModelRegistryService
    
    # Mock dependent services
    mock_embedding_service = AsyncMock()
    mock_llm_service = AsyncMock()
    
    # Mock the session
    mock_session = AsyncMock()
    
    with patch('chatter.core.model_registry.EmbeddingService', return_value=mock_embedding_service), \
         patch('chatter.core.model_registry.LLMService', return_value=mock_llm_service), \
         patch('chatter.core.model_registry.get_registry_cache'), \
         patch('chatter.core.model_registry.get_performance_metrics'):
        
        service = ModelRegistryService(mock_session)
        
        # Test dependent service cache invalidation
        await service._invalidate_dependent_service_caches("test_provider")
        
        # Verify both services had their caches invalidated
        mock_embedding_service.invalidate_provider_cache.assert_called_once_with("test_provider")
        mock_llm_service.invalidate_provider_cache.assert_called_once_with("test_provider")


async def main():
    """Run all cache invalidation tests."""
    print("Running comprehensive cache invalidation tests...")
    
    try:
        await test_embedding_service_cache_invalidation()
        print("✅ EmbeddingService cache invalidation test passed")
        
        await test_llm_service_cache_invalidation()
        print("✅ LLMService cache invalidation test passed")
        
        await test_auth_service_cache_invalidation()
        print("✅ AuthService cache invalidation test passed")
        
        await test_workflow_management_cache_invalidation()
        print("✅ WorkflowManagementService cache invalidation test passed")
        
        await test_model_registry_dependent_service_invalidation()
        print("✅ ModelRegistryService dependent service invalidation test passed")
        
        print("\n🎉 All cache invalidation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)