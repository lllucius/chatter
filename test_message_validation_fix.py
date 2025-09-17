#!/usr/bin/env python3
"""Test script to verify the message validation fix works properly."""

import asyncio
from datetime import datetime
from pydantic import ValidationError

from chatter.schemas.chat import MessageResponse
from chatter.models.conversation import MessageRole


def test_empty_message_validation():
    """Test that empty content messages fail validation as expected."""
    print("Testing empty message validation...")
    
    try:
        # This should fail with ValidationError
        MessageResponse(
            id="test-id",
            conversation_id="test-conv-id",
            role=MessageRole.ASSISTANT,
            content="",  # Empty content
            sequence_number=1,
            created_at=datetime.now()
        )
        print("❌ Empty message validation FAILED - should have raised ValidationError")
        return False
    except ValidationError as e:
        print(f"✅ Empty message validation PASSED - ValidationError raised as expected: {e}")
        return True


def test_placeholder_message_validation():
    """Test that placeholder messages with minimal content pass validation."""
    print("Testing placeholder message validation...")
    
    try:
        # This should pass
        msg = MessageResponse(
            id="test-id",
            conversation_id="test-conv-id", 
            role=MessageRole.ASSISTANT,
            content="...",  # Minimal placeholder content
            sequence_number=1,
            created_at=datetime.now()
        )
        print(f"✅ Placeholder message validation PASSED - content: '{msg.content}'")
        return True
    except ValidationError as e:
        print(f"❌ Placeholder message validation FAILED - should have passed: {e}")
        return False


def test_normal_message_validation():
    """Test that normal messages with content pass validation."""
    print("Testing normal message validation...")
    
    try:
        # This should pass
        msg = MessageResponse(
            id="test-id",
            conversation_id="test-conv-id",
            role=MessageRole.ASSISTANT,
            content="Hello, this is a normal response!",
            sequence_number=1,
            created_at=datetime.now()
        )
        print(f"✅ Normal message validation PASSED - content: '{msg.content}'")
        return True
    except ValidationError as e:
        print(f"❌ Normal message validation FAILED - should have passed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("Running message validation tests...\n")
    
    tests = [
        test_empty_message_validation,
        test_placeholder_message_validation,
        test_normal_message_validation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests PASSED!")
        return 0
    else:
        print("❌ Some tests FAILED!")
        return 1


if __name__ == "__main__":
    exit(main())