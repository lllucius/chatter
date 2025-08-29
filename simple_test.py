#!/usr/bin/env python3
"""Simple test to reproduce the issue with Profile type annotation."""

# Simulate the exact error from the stacktrace
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chatter.models.profile import Profile

class TestService:
    """Test service to reproduce the issue."""
    
    def method_with_profile_annotation(
        self, profile: Profile  # This should cause NameError at runtime
    ) -> str:
        """Method that uses Profile in type annotation."""
        return "test"

if __name__ == "__main__":
    print("Testing direct Profile annotation issue...")
    try:
        service = TestService()
        print("✅ TestService created successfully")
        
        # Try to access the method
        method = getattr(service, 'method_with_profile_annotation')
        print("✅ Method found")
        
        # The error occurs when Python evaluates the type annotation at runtime
        print("Testing method annotations...")
        annotations = method.__annotations__
        print(f"Annotations: {annotations}")
        
    except NameError as e:
        print(f"❌ NameError occurred: {e}")
        print("This confirms the TYPE_CHECKING issue!")
    except Exception as e:
        print(f"❌ Other error: {e}")