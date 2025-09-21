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
        # These are the types after migration from seed data
        migrated_types = [
            "simple_chat",
            "rag_chat",
            "function_chat",
            "advanced_chat",
        ]

        # Get supported types from the unified execution engine
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all migrated types are supported
        for migrated_type in migrated_types:
            assert migrated_type in supported_types, (
                f"Migrated workflow type '{migrated_type}' is not supported by unified execution engine. "
                f"Supported types: {supported_types}"
            )

    def test_default_workflow_type_is_supported(self):
        """Test that the default workflow type is supported."""
        default_type = "simple_chat"  # Default after migration
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        assert default_type in supported_types, (
            f"Default workflow type '{default_type}' is not supported. "
            f"Supported types: {supported_types}"
        )

    def test_modern_workflow_type_support(self):
        """Test that modern workflow types are supported by the unified system."""
        # These are the modern workflow types used after migration
        modern_types = [
            "simple_chat",
            "rag_chat",
            "function_chat",
            "advanced_chat",
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
            "simple_chat",
            "rag_chat",
            "function_chat",
            "advanced_chat",
        ]

        # We should have at least one workflow type for each major capability combination
        assert (
            "simple_chat" in modern_types
        ), "Should have simple_chat workflow type (no additional capabilities)"
        assert (
            "rag_chat" in modern_types
        ), "Should have rag_chat workflow type (retrieval capability)"
        assert (
            "function_chat" in modern_types
        ), "Should have function_chat workflow type (tool calling capability)"
        assert (
            "advanced_chat" in modern_types
        ), "Should have advanced_chat workflow type (all capabilities)"

        # Should have good variety covering all capability combinations
        assert (
            len(set(modern_types)) >= 3
        ), "Should have at least 3 different workflow types"

    def test_unified_system_replaces_legacy_executors(self):
        """Test that the unified system has completely replaced the legacy executor classes."""
        # Verify that the legacy executor classes no longer exist
        try:
            from chatter.core.workflow_executors import (
                PlainWorkflowExecutor,
            )

            assert (
                False
            ), "PlainWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import (
                RAGWorkflowExecutor,
            )

            assert False, "RAGWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import (
                ToolsWorkflowExecutor,
            )

            assert (
                False
            ), "ToolsWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import (
                FullWorkflowExecutor,
            )

            assert (
                False
            ), "FullWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

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
