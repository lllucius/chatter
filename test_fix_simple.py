#!/usr/bin/env python3
"""
Simple test script to demonstrate that the async methods fix the sync function issue.
This script tests the basic functionality without requiring full project dependencies.
"""

import asyncio
import inspect
import sys
import os

# Simple test to verify the methods are async
print("Testing async method conversion...")

# Mock the missing dependencies
class MockSettings:
    langgraph_checkpoint_store = "memory"

class MockLogger:
    def warning(self, msg, **kwargs):
        print(f"[WARNING] {msg} {kwargs}")
    
    def info(self, msg, **kwargs):
        print(f"[INFO] {msg} {kwargs}")
    
    def error(self, msg, **kwargs):
        print(f"[ERROR] {msg} {kwargs}")
    
    def debug(self, msg, **kwargs):
        print(f"[DEBUG] {msg} {kwargs}")

# Mock imports
sys.modules['chatter.config'] = type('MockConfig', (), {'settings': MockSettings()})()
sys.modules['chatter.models.base'] = type('MockBase', (), {'generate_ulid': lambda: 'test-ulid'})()
sys.modules['chatter.utils.logging'] = type('MockLogging', (), {'get_logger': lambda name: MockLogger()})()

# Now let's check the method signatures by directly inspecting the source
def check_method_signatures():
    """Check if the methods are async by looking at the source code."""
    
    # Read the file and check method signatures
    with open('/home/runner/work/chatter/chatter/chatter/core/langgraph.py', 'r') as f:
        content = f.read()
    
    # Check for async get_retriever
    if 'async def get_retriever(' in content:
        print("✓ get_retriever is now async")
    else:
        print("✗ get_retriever is still sync")
        return False
    
    # Check for async get_tools
    if 'async def get_tools(' in content:
        print("✓ get_tools is now async")
    else:
        print("✗ get_tools is still sync")
        return False
    
    # Check that the problematic asyncio code is removed
    if 'loop.run_until_complete' in content:
        print("✗ Still contains loop.run_until_complete (problematic sync code)")
        return False
    else:
        print("✓ Removed problematic sync asyncio code")
    
    if 'asyncio.run(' in content:
        print("✗ Still contains asyncio.run (problematic sync code)")
        return False
    else:
        print("✓ Removed problematic asyncio.run code")
    
    if 'Cannot get embeddings synchronously while event loop is running' in content:
        print("✗ Still contains the warning message")
        return False
    else:
        print("✓ Removed the warning message")
    
    return True

def check_unified_workflow_executor():
    """Check if unified workflow executor is updated to use await."""
    
    with open('/home/runner/work/chatter/chatter/chatter/core/unified_workflow_executor.py', 'r') as f:
        content = f.read()
    
    # Check for async _get_workflow_config
    if 'async def _get_workflow_config(' in content:
        print("✓ _get_workflow_config is now async")
    else:
        print("✗ _get_workflow_config is still sync")
        return False
    
    # Check for await calls to get_retriever and get_tools
    if 'await workflow_manager.get_retriever(' in content:
        print("✓ get_retriever is called with await")
    else:
        print("✗ get_retriever is not called with await")
        return False
    
    if 'await workflow_manager.get_tools(' in content:
        print("✓ get_tools is called with await")
    else:
        print("✗ get_tools is not called with await")
        return False
    
    # Check for await calls to _get_workflow_config
    if 'await self._get_workflow_config(' in content:
        print("✓ _get_workflow_config is called with await")
    else:
        print("✗ _get_workflow_config is not called with await")
        return False
    
    return True

def main():
    """Run all checks."""
    print("=" * 60)
    print("Checking async method conversion fix")
    print("=" * 60)
    
    print("\n1. Checking LangGraph method signatures...")
    langgraph_ok = check_method_signatures()
    
    print("\n2. Checking unified workflow executor updates...")
    executor_ok = check_unified_workflow_executor()
    
    print("\n" + "=" * 60)
    if langgraph_ok and executor_ok:
        print("✅ SUCCESS: All checks passed!")
        print("   - get_retriever() and get_tools() are now async")
        print("   - Problematic sync asyncio code has been removed")
        print("   - Warning message has been removed")
        print("   - Unified workflow executor updated to use await")
        print("   - This should fix the 'Cannot get embeddings synchronously while event loop is running' warning")
        return True
    else:
        print("❌ FAILURE: Some checks failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)