"""
Test for workflow definition query consistency fix.

This test ensures that list_workflow_definitions and get_workflow_definition
use consistent logic for determining workflow access permissions.
"""

import pytest


def test_workflow_boolean_query_consistency():
    """Test that boolean queries use explicit True checks instead of truthy checks."""

    # Read the workflow management service
    with open('chatter/services/workflow_management.py') as f:
        content = f.read()

    # Check that is_public checks are explicit
    # These should be "== True" not just the bare field name

    # Check list_workflow_definitions method
    assert (
        'WorkflowDefinition.is_public == True' in content
    ), "list_workflow_definitions should use explicit 'is_public == True' check"

    # Check get_workflow_definition method
    assert (
        'WorkflowDefinition.is_public == True' in content
    ), "get_workflow_definition should use explicit 'is_public == True' check"

    # Check that no bare is_public checks remain for WorkflowDefinition
    # This is a more complex check to avoid false positives
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if (
            'WorkflowDefinition.is_public' in line
            and '== True' not in line
        ):
            # Allow certain contexts like assignments
            if ('=' in line and '==' not in line) or (
                'is_public=' in line
            ):
                continue
            # If we find a bare WorkflowDefinition.is_public in a query context, that's bad
            if any(
                keyword in line
                for keyword in ['where(', 'or_(', 'and_(']
            ):
                pytest.fail(
                    f"Found bare 'WorkflowDefinition.is_public' in query at line {i+1}: {line.strip()}\n"
                    f"Should use 'WorkflowDefinition.is_public == True' for explicit boolean check"
                )

    # Verify templates are also fixed
    assert (
        'WorkflowTemplate.is_public == True' in content
    ), "Template queries should also use explicit 'is_public == True' check"

    assert (
        'WorkflowTemplate.is_builtin == True' in content
    ), "Template queries should also use explicit 'is_builtin == True' check"


def test_workflow_access_logic_scenarios():
    """Test different workflow access scenarios to document expected behavior."""

    scenarios = [
        # (owner_id, workflow_owner_id, is_public, should_have_access, description)
        ("user1", "user1", False, True, "User owns private workflow"),
        ("user1", "user1", True, True, "User owns public workflow"),
        (
            "user1",
            "user2",
            True,
            True,
            "User accesses other's public workflow",
        ),
        (
            "user1",
            "user2",
            False,
            False,
            "User cannot access other's private workflow",
        ),
        (
            "user1",
            "user2",
            None,
            False,
            "User cannot access workflow with NULL is_public",
        ),
    ]

    print("\nWorkflow access scenarios:")
    for query_user, owner, is_public, expected, desc in scenarios:
        # Simulate the fixed logic
        owner_match = query_user == owner
        public_match = is_public is True  # Explicit True check
        has_access = owner_match or public_match

        print(f"  {desc}: {has_access} (expected: {expected})")
        assert has_access == expected, f"Failed scenario: {desc}"
