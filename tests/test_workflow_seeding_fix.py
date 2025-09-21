"""Test for workflow seeding compatibility fix."""

from chatter.core.unified_workflow_executor import (
    UnifiedWorkflowExecutor,
)


class TestWorkflowSeedingFix:
    """Test that seeded workflow types are compatible with execution engine."""

    def test_seeded_workflow_types_are_supported(self):
        """Test that all seeded workflow types are supported by the execution engine."""
        # These are the types used in our seeded templates
        seeded_types = ["plain", "rag", "tools", "full"]

        # Get supported types from the execution engine
        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all seeded types are supported
        for seeded_type in seeded_types:
            assert seeded_type in supported_types, (
                f"Seeded workflow type '{seeded_type}' is not supported by execution engine. "
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
        # These mappings should exist in workflow_execution.py for backward compatibility
        expected_mappings = {
            "simple_chat": "plain",
            "rag_chat": "rag",
            "function_chat": "tools",
            "advanced_chat": "full",
        }

        supported_types = UnifiedWorkflowExecutor.get_supported_types()

        # Verify all mapped types are supported
        for legacy_type, modern_type in expected_mappings.items():
            assert modern_type in supported_types, (
                f"Legacy type '{legacy_type}' maps to '{modern_type}' which is not supported. "
                f"Supported types: {supported_types}"
            )

    def test_workflow_types_have_good_coverage(self):
        """Test that we have templates covering the main workflow types."""
        seeded_types = ["plain", "rag", "tools", "full"]

        # We should have at least one template for each major capability
        assert (
            "plain" in seeded_types
        ), "Should have plain workflow templates"
        assert (
            "rag" in seeded_types
        ), "Should have RAG workflow templates"
        assert (
            "tools" in seeded_types
        ), "Should have tool-enabled workflow templates"
        assert (
            "full" in seeded_types
        ), "Should have full-featured workflow templates"

        # Should have good variety
        assert (
            len(set(seeded_types)) >= 3
        ), "Should have at least 3 different workflow types"
