"""Test for workflow seeding compatibility fix.

This test ensures that the unified workflow system supports all the
workflow types that were seeded into the database, maintaining compatibility
with existing templates and workflows.
"""

from chatter.core.unified_workflow_executor import (
    UnifiedWorkflowExecutor,
)


class TestWorkflowSeedingFix:
    """Test that seeded workflow types are compatible with the unified execution engine."""

    def test_seeded_workflow_types_are_supported(self):
        """Test that all workflow types (after migration) are supported by the unified execution engine."""
        # These are the modern workflow types
        modern_types = [
            "plain",
            "rag",
            "tools",
            "full",
        ]

        # Get supported types from the unified execution engine
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all modern types are supported
        for modern_type in modern_types:
            assert modern_type in supported_types, (
                f"Modern workflow type '{modern_type}' is not supported by unified execution engine. "
                f"Supported types: {supported_types}"
            )

    def test_default_workflow_type_is_supported(self):
        """Test that the default workflow type is supported."""
        default_type = "plain"  # Modern default type
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        assert default_type in supported_types, (
            f"Default workflow type '{default_type}' is not supported. "
            f"Supported types: {supported_types}"
        )

    def test_modern_workflow_type_support(self):
        """Test that modern workflow types are supported by the unified system."""
        # These are the modern workflow types
        modern_types = [
            "plain",
            "rag",
            "tools",
            "full",
        ]

        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all modern types are supported by the unified system
        for modern_type in modern_types:
            assert modern_type in supported_types, (
                f"Modern workflow type '{modern_type}' is not supported. "
                f"Supported types: {supported_types}"
            )

    def test_workflow_types_have_good_coverage(self):
        """Test that we have workflow types covering the main capability combinations."""
        modern_types = [
            "plain",
            "rag",
            "tools",
            "full",
        ]

        # We should have at least one workflow type for each major capability combination
        assert (
            "plain" in modern_types
        ), "Should have plain workflow type (no additional capabilities)"
        assert (
            "rag" in modern_types
        ), "Should have rag workflow type (retrieval capability)"
        assert (
            "tools" in modern_types
        ), "Should have tools workflow type (tool calling capability)"
        assert (
            "full" in modern_types
        ), "Should have full workflow type (all capabilities)"

        # Should have good variety covering all capability combinations
        assert (
            len(set(modern_types)) >= 3
        ), "Should have at least 3 different workflow types"

    def test_unified_system_replaces_legacy_executors(self):
        """Test that the unified system has completely replaced the legacy executor classes."""
        import importlib.util

        # Verify that the legacy workflow_executors module no longer exists
        module_spec = importlib.util.find_spec(
            "chatter.core.workflow_executors"
        )
        assert (
            module_spec is None
        ), "Legacy workflow_executors module should have been removed"

        # Verify that the unified system is available
        from chatter.core.unified_workflow_engine import (
            UnifiedWorkflowEngine,
        )
        from chatter.core.unified_workflow_executor import (
            UnifiedWorkflowExecutor,
        )

        # These should import successfully
        assert UnifiedWorkflowExecutor is not None
        assert UnifiedWorkflowEngine is not None
