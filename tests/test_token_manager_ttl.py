"""Test token manager TTL conversion fix."""

import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

from chatter.core.token_manager import TokenManager
from chatter.config import settings


@pytest.mark.asyncio
async def test_revoke_token_uses_int_ttl():
    """Test that revoke_token converts timedelta to int for cache.set."""
    # Create mock cache
    mock_cache = AsyncMock()
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.delete = AsyncMock(return_value=True)
    
    # Create token manager with mock cache
    token_manager = TokenManager(cache_service=mock_cache)
    
    # Revoke a token
    jti = "test-jti-123"
    result = await token_manager.revoke_token(jti, "test")
    
    assert result is True
    
    # Verify cache.set was called with int TTL, not timedelta
    assert mock_cache.set.call_count == 1
    call_args = mock_cache.set.call_args
    
    # The third argument (ttl) should be an int
    ttl_arg = call_args[0][2]
    assert isinstance(ttl_arg, int), f"Expected int, got {type(ttl_arg)}"
    
    # Verify it's the correct value (days * 24 * 60 * 60)
    expected_ttl = settings.refresh_token_expire_days * 24 * 60 * 60
    assert ttl_arg == expected_ttl


@pytest.mark.asyncio
async def test_store_token_metadata_uses_int_ttl():
    """Test that _store_token_metadata converts timedelta to int for cache.set."""
    # Create mock cache
    mock_cache = AsyncMock()
    mock_cache.set = AsyncMock(return_value=True)
    mock_cache.get = AsyncMock(return_value=[])
    
    # Create token manager with mock cache
    token_manager = TokenManager(cache_service=mock_cache)
    
    # Store token metadata
    jti = "test-jti-456"
    user_id = "user-123"
    session_id = "session-789"
    
    await token_manager._store_token_metadata(jti, user_id, session_id)
    
    # Verify cache.set was called twice (metadata + user_tokens)
    assert mock_cache.set.call_count == 2
    
    # Check both calls use int TTL
    for call in mock_cache.set.call_args_list:
        ttl_arg = call[0][2]
        assert isinstance(ttl_arg, int), f"Expected int, got {type(ttl_arg)}"
        
        # Verify it's the correct value
        expected_ttl = settings.refresh_token_expire_days * 24 * 60 * 60
        assert ttl_arg == expected_ttl


@pytest.mark.asyncio
async def test_add_to_user_tokens_uses_int_ttl():
    """Test that _add_to_user_tokens converts timedelta to int for cache.set."""
    # Create mock cache
    mock_cache = AsyncMock()
    mock_cache.get = AsyncMock(return_value=["old-jti"])
    mock_cache.set = AsyncMock(return_value=True)
    
    # Create token manager with mock cache
    token_manager = TokenManager(cache_service=mock_cache)
    
    # Add token to user's list
    user_id = "user-123"
    jti = "test-jti-789"
    
    await token_manager._add_to_user_tokens(user_id, jti)
    
    # Verify cache.set was called with int TTL
    assert mock_cache.set.call_count == 1
    call_args = mock_cache.set.call_args
    
    # The third argument (ttl) should be an int
    ttl_arg = call_args[0][2]
    assert isinstance(ttl_arg, int), f"Expected int, got {type(ttl_arg)}"
    
    # Verify it's the correct value
    expected_ttl = settings.refresh_token_expire_days * 24 * 60 * 60
    assert ttl_arg == expected_ttl


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
