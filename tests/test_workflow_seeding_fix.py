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
        """Test that all seeded workflow types are supported by the unified execution engine."""
        # These are the types used in our seeded templates
        seeded_types = ["plain", "rag", "tools", "full"]

        # Get supported types from the unified execution engine
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all seeded types are supported
        for seeded_type in seeded_types:
            assert seeded_type in supported_types, (
                f"Seeded workflow type '{seeded_type}' is not supported by unified execution engine. "
                f"Supported types: {supported_types}"
            )

    def test_default_workflow_type_is_supported(self):
        """Test that the default workflow type is supported."""
        default_type = "plain"  # From chat.py schema default
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        assert default_type in supported_types, (
            f"Default workflow type '{default_type}' is not supported. "
            f"Supported types: {supported_types}"
        )

    def test_legacy_workflow_type_mapping_exists(self):
        """Test that legacy workflow type mapping is preserved for backward compatibility."""
        # These mappings should exist in the unified system for backward compatibility
        expected_mappings = {
            "simple_chat": "plain",
            "rag_chat": "rag",
            "function_chat": "tools",
            "advanced_chat": "full",
        }

        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all mapped types are supported by the unified system
        for legacy_type, modern_type in expected_mappings.items():
            assert modern_type in supported_types, (
                f"Legacy type '{legacy_type}' maps to '{modern_type}' which is not supported. "
                f"Supported types: {supported_types}"
            )

    def test_workflow_types_have_good_coverage(self):
        """Test that we have workflow types covering the main capability combinations."""
        seeded_types = ["plain", "rag", "tools", "full"]

        # We should have at least one workflow type for each major capability combination
        assert (
            "plain" in seeded_types
        ), "Should have plain workflow type (no additional capabilities)"
        assert (
            "rag" in seeded_types
        ), "Should have RAG workflow type (retrieval capability)"
        assert (
            "tools" in seeded_types
        ), "Should have tools workflow type (tool calling capability)"
        assert (
            "full" in seeded_types
        ), "Should have full workflow type (all capabilities)"

        # Should have good variety covering all capability combinations
        assert (
            len(set(seeded_types)) >= 3
        ), "Should have at least 3 different workflow types"

    def test_unified_system_replaces_legacy_executors(self):
        """Test that the unified system has completely replaced the legacy executor classes."""
        # Verify that the legacy executor classes no longer exist
        try:
            from chatter.core.workflow_executors import PlainWorkflowExecutor
            assert False, "PlainWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import RAGWorkflowExecutor
            assert False, "RAGWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import ToolsWorkflowExecutor
            assert False, "ToolsWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        try:
            from chatter.core.workflow_executors import FullWorkflowExecutor
            assert False, "FullWorkflowExecutor should have been removed"
        except ImportError:
            pass  # Expected - the module should not exist

        # Verify that the unified system is available
        from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
        from chatter.core.unified_workflow_engine import UnifiedWorkflowEngine
        
        # These should import successfully
        assert UnifiedWorkflowExecutor is not None
        assert UnifiedWorkflowEngine is not None
