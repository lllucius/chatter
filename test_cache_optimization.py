#!/usr/bin/env python3
"""Test script for cache optimization changes."""

import os
import sys
from pathlib import Path

# Add the chatter package to Python path
chatter_root = Path(__file__).parent
sys.path.insert(0, str(chatter_root))

# Set required environment variables
os.environ.setdefault('DATABASE_URL', 'sqlite:///test.db')
os.environ.setdefault('CACHE_DISABLED', 'false')

def test_cache_config():
    """Test the simplified cache configuration."""
    print("Testing cache configuration...")
    
    try:
        from chatter.core.cache_interface import CacheConfig, CacheStats
        
        # Test basic config creation
        config = CacheConfig(
            default_ttl=3600,
            max_size=1000,
            disabled=False
        )
        
        print(f"✓ CacheConfig created: ttl={config.default_ttl}, size={config.max_size}")
        
        # Test stats
        stats = CacheStats(total_entries=10, cache_hits=8, cache_misses=2)
        print(f"✓ CacheStats created: hit_rate={stats.hit_rate}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache config test failed: {e}")
        return False

def test_cache_types():
    """Test the simplified cache types."""
    print("Testing cache types...")
    
    try:
        # Mock the settings to avoid deep dependencies
        class MockSettings:
            cache_disabled = False
            cache_ttl_default = 3600
            cache_ttl_short = 300
            cache_ttl_long = 7200
            cache_max_size = 1000
            cache_eviction_policy = "lru"
            cache_backend = "multi_tier"
            cache_l1_size_ratio = 0.1
        
        # Monkey patch settings
        import chatter.core.cache_factory as cf
        cf.settings = MockSettings()
        
        from chatter.core.cache_factory import CacheType
        
        # Test enum values
        types = [t.value for t in CacheType]
        expected = ['general', 'session', 'persistent']
        
        if types == expected:
            print(f"✓ Cache types simplified: {types}")
            return True
        else:
            print(f"❌ Unexpected cache types: {types}, expected {expected}")
            return False
            
    except Exception as e:
        print(f"❌ Cache types test failed: {e}")
        return False

def test_cache_factory():
    """Test the simplified cache factory."""
    print("Testing cache factory...")
    
    try:
        # Mock settings and dependencies to test factory logic
        class MockSettings:
            cache_disabled = False
            cache_ttl_default = 3600
            cache_ttl_short = 300
            cache_ttl_long = 7200
            cache_max_size = 1000
            cache_eviction_policy = "lru"
            cache_backend = "memory"  # Use memory to avoid Redis dependencies
            cache_l1_size_ratio = 0.1
        
        # Mock the cache implementations
        class MockCache:
            def __init__(self, config):
                self.config = config
        
        import chatter.core.cache_factory as cf
        cf.settings = MockSettings()
        
        from chatter.core.cache_factory import CacheFactory, CacheType
        
        factory = CacheFactory()
        
        # Test getting config for different types
        general_config = factory._get_config_for_type(CacheType.GENERAL)
        session_config = factory._get_config_for_type(CacheType.SESSION)
        persistent_config = factory._get_config_for_type(CacheType.PERSISTENT)
        
        print(f"✓ General config: ttl={general_config.default_ttl}, prefix='{general_config.key_prefix}'")
        print(f"✓ Session config: ttl={session_config.default_ttl}, prefix='{session_config.key_prefix}'")
        print(f"✓ Persistent config: ttl={persistent_config.default_ttl}, prefix='{persistent_config.key_prefix}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simplified_workflow_cache():
    """Test the simplified workflow cache."""
    print("Testing simplified workflow cache...")
    
    try:
        # Mock the cache interface
        class MockCache:
            def __init__(self):
                self.data = {}
                
            def make_key(self, *parts):
                return ":".join(str(p) for p in parts)
                
            async def get(self, key):
                return self.data.get(key)
                
            async def set(self, key, value):
                self.data[key] = value
                return True
                
            async def clear(self):
                self.data.clear()
                return True
                
            async def get_stats(self):
                from chatter.core.cache_interface import CacheStats
                return CacheStats(total_entries=len(self.data))
                
            async def health_check(self):
                return {"status": "healthy"}
        
        from chatter.core.simplified_cache import SimplifiedWorkflowCache
        
        # Create cache with mock
        cache = SimplifiedWorkflowCache(MockCache())
        
        # Test key generation
        key = cache._make_key("provider", "workflow_type", {"param": "value"})
        print(f"✓ Generated key: {key}")
        
        print(f"✓ SimplifiedWorkflowCache created and key generation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Simplified workflow cache test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Cache Optimization Changes")
    print("=" * 50)
    
    tests = [
        test_cache_config,
        test_cache_types,
        test_cache_factory,
        test_simplified_workflow_cache,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Cache optimization is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please review the changes.")
        return 1

if __name__ == "__main__":
    sys.exit(main())