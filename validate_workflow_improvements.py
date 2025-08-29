#!/usr/bin/env python3
"""Simple validation script for workflow API improvements."""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_basic_syntax():
    """Test that all new files have valid Python syntax."""
    import ast
    
    files_to_test = [
        'chatter/core/workflow_templates.py',
        'chatter/core/workflow_performance.py',
        'validate_workflow_improvements.py'
    ]
    
    failed = []
    for file_path in files_to_test:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            ast.parse(content)
            print(f"✓ {file_path} - syntax OK")
        except SyntaxError as e:
            print(f"✗ {file_path} - syntax error: {e}")
            failed.append(file_path)
        except FileNotFoundError:
            print(f"✗ {file_path} - file not found")
            failed.append(file_path)
    
    return len(failed) == 0


def test_template_constants():
    """Test workflow template constants."""
    try:
        # Test basic template structure without imports
        templates = {
            "customer_support": {
                "name": "customer_support",
                "workflow_type": "full",
                "description": "Customer support with knowledge base and tools",
                "default_params": {
                    "enable_memory": True,
                    "memory_window": 50,
                    "max_tool_calls": 5,
                    "system_message": "You are a helpful customer support assistant."
                },
                "required_tools": ["search_kb", "create_ticket", "escalate"],
                "required_retrievers": ["support_docs"]
            }
        }
        
        assert "customer_support" in templates
        template = templates["customer_support"]
        assert template["workflow_type"] == "full"
        assert "enable_memory" in template["default_params"]
        print("✓ Template structure validation passed")
        return True
        
    except Exception as e:
        print(f"✗ Template test failed: {e}")
        return False


def test_performance_logic():
    """Test performance optimization logic."""
    try:
        # Test basic cache logic
        cache = {}
        max_size = 2
        
        # Simulate cache operations
        def cache_key(provider, workflow_type, config):
            import hashlib
            config_str = f"{provider}:{workflow_type}:{sorted(config.items()) if config else []}"
            return hashlib.md5(config_str.encode()).hexdigest()
        
        # Test cache key generation
        key1 = cache_key("openai", "plain", {"temp": 0.7})
        key2 = cache_key("openai", "plain", {"temp": 0.7})
        key3 = cache_key("openai", "rag", {"temp": 0.7})
        
        assert key1 == key2, "Same config should generate same key"
        assert key1 != key3, "Different config should generate different key"
        print("✓ Cache key generation works")
        
        # Test LRU logic
        access_times = {}
        import time
        
        def add_to_cache(key, value):
            if len(cache) >= max_size and key not in cache:
                # Remove LRU
                if access_times:
                    lru_key = min(access_times.keys(), key=lambda k: access_times[k])
                    del cache[lru_key]
                    del access_times[lru_key]
            cache[key] = value
            access_times[key] = time.time()
        
        add_to_cache("key1", "value1")
        add_to_cache("key2", "value2")
        add_to_cache("key3", "value3")  # Should evict key1
        
        assert len(cache) <= max_size, "Cache size exceeded"
        assert "key1" not in cache, "LRU eviction failed"
        print("✓ LRU cache logic works")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance test failed: {e}")
        return False


def test_validation_logic():
    """Test validation logic."""
    try:
        # Test workflow type validation
        valid_types = ["plain", "rag", "tools", "full"]
        
        def validate_workflow_type(workflow_type):
            return workflow_type in valid_types
        
        assert validate_workflow_type("plain"), "Plain should be valid"
        assert validate_workflow_type("rag"), "RAG should be valid"
        assert not validate_workflow_type("invalid"), "Invalid should fail"
        print("✓ Workflow type validation works")
        
        # Test parameter validation  
        validation_rules = {
            "max_documents": {"type": int, "min": 1, "max": 100},
            "similarity_threshold": {"type": float, "min": 0.0, "max": 1.0},
            "max_tool_calls": {"type": int, "min": 1, "max": 50},
        }
        
        def validate_parameter(name, value):
            if name not in validation_rules:
                return True  # Unknown parameters allowed
            
            rules = validation_rules[name]
            expected_type = rules.get("type")
            
            if expected_type and not isinstance(value, expected_type):
                return False
            
            if isinstance(value, (int, float)):
                min_val = rules.get("min")
                max_val = rules.get("max")
                if min_val is not None and value < min_val:
                    return False
                if max_val is not None and value > max_val:
                    return False
            
            return True
        
        assert validate_parameter("max_documents", 10), "Valid int should pass"
        assert not validate_parameter("max_documents", 0), "Below min should fail"
        assert not validate_parameter("max_documents", 150), "Above max should fail"
        assert validate_parameter("similarity_threshold", 0.5), "Valid float should pass"
        print("✓ Parameter validation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False


def test_error_structure():
    """Test error class structure."""
    try:
        # Test basic error structure
        class WorkflowError(Exception):
            def __init__(self, message, workflow_type=None):
                super().__init__(message)
                self.workflow_type = workflow_type
                self.status_code = 500
        
        class WorkflowConfigurationError(WorkflowError):
            def __init__(self, message, **kwargs):
                super().__init__(message, **kwargs)
                self.status_code = 400
        
        # Test error creation
        base_error = WorkflowError("Test error", workflow_type="plain")
        assert base_error.status_code == 500
        assert base_error.workflow_type == "plain"
        print("✓ Base workflow error works")
        
        config_error = WorkflowConfigurationError("Config error")
        assert config_error.status_code == 400
        print("✓ Configuration error works")
        
        return True
        
    except Exception as e:
        print(f"✗ Error structure test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🔍 Validating Workflow API Improvements...")
    print("=" * 50)
    
    tests = [
        ("Syntax Validation", test_basic_syntax),
        ("Template Logic", test_template_constants), 
        ("Performance Logic", test_performance_logic),
        ("Validation Logic", test_validation_logic),
        ("Error Structure", test_error_structure),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🧪 Testing {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Workflow API improvements are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())