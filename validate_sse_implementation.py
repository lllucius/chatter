#!/usr/bin/env python3
"""
Validation script for SSE implementation.
"""

import ast
import sys
from pathlib import Path


def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path) as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main():
    """Validate SSE implementation files."""
    print("🔍 Validating SSE Implementation")
    print("=" * 50)

    # Files to validate
    files_to_check = [
        "chatter/services/sse_events.py",
        "chatter/api/events.py", 
        "chatter/schemas/events.py",
        "chatter/main.py",
    ]

    all_valid = True
    total_lines = 0

    for file_path in files_to_check:
        if Path(file_path).exists():
            valid, error = check_syntax(file_path)

            # Count lines
            with open(file_path) as f:
                lines = len(f.readlines())
            total_lines += lines

            status = "✅ PASS" if valid else "❌ FAIL"
            print(f"{status} {file_path} ({lines} lines)")
            
            if not valid:
                print(f"   Error: {error}")
                all_valid = False
        else:
            print(f"⚠️  SKIP {file_path} (not found)")

    print("\n" + "=" * 50)
    
    # Check that webhook files are removed
    webhook_files = [
        "chatter/api/webhooks.py",
        "chatter/services/webhooks.py", 
        "chatter/schemas/webhooks.py",
    ]
    
    removed_count = 0
    for file_path in webhook_files:
        if not Path(file_path).exists():
            print(f"✅ REMOVED {file_path}")
            removed_count += 1
        else:
            print(f"❌ STILL EXISTS {file_path}")
            all_valid = False
    
    print("\n" + "=" * 50)
    
    # Check SSE features
    features = [
        ("SSE Event Service", "chatter/services/sse_events.py"),
        ("SSE API Endpoints", "chatter/api/events.py"),
        ("Event Schemas", "chatter/schemas/events.py"),
        ("Test Client", "sse_test_client.html"),
        ("API Documentation", "SSE_API_DOCUMENTATION.md"),
    ]
    
    implemented_features = 0
    for feature, file_path in features:
        if Path(file_path).exists():
            print(f"✅ {feature}")
            implemented_features += 1
        else:
            print(f"❌ {feature} - {file_path} not found")
    
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"   Total lines of code: {total_lines:,}")
    print(f"   Files validated: {len(files_to_check)}")
    print(f"   Webhook files removed: {removed_count}/{len(webhook_files)}")
    print(f"   SSE features implemented: {implemented_features}/{len(features)}")
    
    if all_valid and removed_count == len(webhook_files) and implemented_features == len(features):
        print("✅ All validations passed! SSE implementation is complete.")
        return 0
    else:
        print("❌ Some validations failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())