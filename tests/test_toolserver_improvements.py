"""Tests for toolserver API improvements."""

from unittest.mock import AsyncMock, MagicMock
import asyncio

# Mock the dependencies to test the structure and logic
class MockSettings:
    mcp_enabled = True

# Mock basic imports to test syntax
class MockBaseTool:
    def __init__(self, name):
        self.name = name

class MockSession:
    async def execute(self, query):
        return MagicMock()
    
    async def commit(self):
        pass
    
    async def rollback(self):
        pass
    
    def add(self, obj):
        pass

def test_crypto_utility():
    """Test basic crypto utility functionality."""
    from chatter.utils.security_enhanced import SecretManager, CryptoError
    from cryptography.fernet import Fernet
    
    # Generate a proper Fernet key for testing
    key = Fernet.generate_key().decode()
    secret_manager = SecretManager(key)
    
    # Test encryption/decryption
    secret = "test-secret-data"
    encrypted = secret_manager.encrypt(secret)
    assert encrypted != secret
    
    decrypted = secret_manager.decrypt(encrypted)
    assert decrypted == secret
    
    # Test dictionary encryption
    data = {
        "name": "test",
        "password": "secret123",
        "other": "data"
    }
    
    encrypted_dict = secret_manager.encrypt_dict(data)
    assert encrypted_dict["name"] == "test"  # Not encrypted
    assert encrypted_dict["password"] != "secret123"  # Encrypted
    assert encrypted_dict["password_encrypted"] is True
    
    decrypted_dict = secret_manager.decrypt_dict(encrypted_dict)
    assert decrypted_dict["password"] == "secret123"
    print("✓ Crypto utility tests passed")

def test_rate_limiter():
    """Test rate limiter functionality."""
    import asyncio
    from chatter.utils.unified_rate_limiter import get_unified_rate_limiter, RateLimitExceeded
    
    async def run_test():
        # Create a unified rate limiter instance
        rate_limiter = get_unified_rate_limiter()
        
        # Test basic rate limiting - use the check_rate_limit method
        try:
            # This should succeed
            await rate_limiter.check_rate_limit("test-key", limit=2, window=3600)
            
            # This should also succeed
            await rate_limiter.check_rate_limit("test-key", limit=2, window=3600) 
            
            # This should fail due to rate limiting
            await rate_limiter.check_rate_limit("test-key", limit=2, window=3600)
            assert False, "Should have raised RateLimitExceeded"
        except RateLimitExceeded:
            pass  # Expected
        
        print("✓ Rate limiter tests passed")
    
    asyncio.run(run_test())

def test_mcp_service_validation():
    """Test MCP service argument validation."""
    # Mock the dependencies
    import sys
    from unittest.mock import MagicMock
    
    # Mock langchain modules
    sys.modules['langchain_core'] = MagicMock()
    sys.modules['langchain_core.tools'] = MagicMock()
    sys.modules['langchain_mcp_adapters'] = MagicMock()
    sys.modules['langchain_mcp_adapters.client'] = MagicMock()
    sys.modules['langchain_mcp_adapters.sessions'] = MagicMock()
    
    # Import after mocking
    from chatter.services.mcp import MCPToolService
    
    # Mock settings
    sys.modules['chatter.config'].settings = MockSettings()
    
    service = MCPToolService()
    
    # Test argument sanitization
    try:
        service._sanitize_tool_arguments({'script': '<script>alert(1)</script>'})
        assert False, "Should have caught dangerous content"
    except ValueError as e:
        assert "dangerous content" in str(e).lower()
    
    # Test large arguments
    try:
        service._sanitize_tool_arguments({'data': 'x' * (1024 * 1024 + 1)})
        assert False, "Should have caught large arguments"
    except ValueError as e:
        assert "too large" in str(e).lower()
    
    # Test valid arguments
    valid_args = {'param1': 'value1', 'param2': 123}
    sanitized = service._sanitize_tool_arguments(valid_args)
    assert sanitized == valid_args
    
    print("✓ MCP service validation tests passed")

def test_schema_validation():
    """Test toolserver schema validation."""
    from chatter.schemas.toolserver import ToolServerCreate
    from pydantic import ValidationError
    
    # Test valid server creation
    valid_data = {
        'name': 'test-server',
        'display_name': 'Test Server',
        'base_url': 'https://api.example.com',
        'transport_type': 'http'
    }
    
    server = ToolServerCreate(**valid_data)
    assert server.name == 'test-server'
    assert server.transport_type == 'http'
    
    # Test invalid transport type
    try:
        ToolServerCreate(
            name='test',
            display_name='Test',
            base_url='https://api.example.com',
            transport_type='invalid'
        )
        assert False, "Should have failed validation"
    except ValidationError:
        pass  # Expected
    
    # Test OAuth validation
    oauth_data = valid_data.copy()
    oauth_data['oauth_config'] = {
        'client_id': 'test-id',
        'client_secret': 'test-secret',
        'token_url': 'https://auth.example.com/token'
    }
    
    server_with_oauth = ToolServerCreate(**oauth_data)
    assert server_with_oauth.oauth_config.client_id == 'test-id'
    
    print("✓ Schema validation tests passed")

if __name__ == "__main__":
    print("Running toolserver API improvement tests...")
    
    test_crypto_utility()
    test_rate_limiter()
    test_mcp_service_validation()
    test_schema_validation()
    
    print("\n🎉 All tests passed! The toolserver API improvements are working correctly.")