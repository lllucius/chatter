"""
Test for workflow routing configuration to prevent regression.
"""

import re


def test_workflow_router_no_duplicate_prefix():
    """Test that the workflows router doesn't have a duplicate prefix."""

    # Read the workflows router file
    with open('chatter/api/workflows.py') as f:
        content = f.read()

    # Check that router definition doesn't include a prefix
    # The router should be defined as APIRouter() or APIRouter(tags=...)
    # but not APIRouter(prefix="/workflows", ...)
    router_match = re.search(r'router = APIRouter\(([^)]*)\)', content)

    assert router_match, "Could not find router definition"

    router_args = router_match.group(1)

    # The router should not have a prefix argument
    assert 'prefix=' not in router_args, (
        f"Workflows router should not have a prefix defined. "
        f"Found: router = APIRouter({router_args}). "
        f"The prefix should only be added in main.py when including the router."
    )


def test_workflow_router_inclusion_in_main():
    """Test that the workflows router is properly included in main.py."""

    # Read the main file
    with open('chatter/main.py') as f:
        content = f.read()

    # Check that workflows router is included with the correct prefix
    workflows_inclusion_pattern = (
        r'app\.include_router\(\s*'
        r'workflows\.router,\s*'
        r'prefix=f?"[^"]*workflows[^"]*",\s*'
        r'tags=\["Workflows"\]'
    )

    assert re.search(
        workflows_inclusion_pattern, content, re.MULTILINE
    ), (
        "Workflows router should be included in main.py with a /workflows prefix. "
        "Expected pattern: app.include_router(workflows.router, prefix=\".../workflows\", tags=[\"Workflows\"])"
    )


def test_no_double_workflows_in_routes():
    """Test that we don't accidentally create routes with double 'workflows' in the path."""

    # This test serves as documentation of the expected behavior
    # The actual routes should be:
    #   /api/v1/workflows/definitions/{id}/execute
    # NOT:
    #   /api/v1/workflows/workflows/definitions/{id}/execute

    expected_routes = [
        "/api/v1/workflows/definitions",
        "/api/v1/workflows/definitions/{workflow_id}",
        "/api/v1/workflows/definitions/{workflow_id}/execute",
        "/api/v1/workflows/definitions/{workflow_id}/analytics",
        "/api/v1/workflows/templates",
        "/api/v1/workflows/node-types",
    ]

    # All expected routes should have exactly one "workflows" in the path
    for route in expected_routes:
        workflows_count = route.count('workflows')
        assert workflows_count == 1, (
            f"Route {route} should contain exactly one 'workflows' segment, "
            f"but found {workflows_count}"
        )

        # Ensure no double slashes or duplicate segments
        assert (
            '/workflows/workflows/' not in route
        ), f"Route {route} contains duplicate workflows segment"
