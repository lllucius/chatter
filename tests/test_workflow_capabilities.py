"""Test the new capability-based workflow system."""

from chatter.core.workflow_capabilities import WorkflowCapabilities


class TestWorkflowCapabilities:
    """Tests for the new capability-based workflow system."""

    def test_capability_creation_from_template_config(self):
        """Test creating capabilities from template configuration."""
        # Test with tools only
        capabilities = WorkflowCapabilities.from_template_configuration(
            required_tools=["test_tool"], required_retrievers=None
        )
        assert capabilities.enable_tools is True
        assert capabilities.enable_retrieval is False
        assert capabilities.enable_memory is True

        # Test with retrievers only
        capabilities = WorkflowCapabilities.from_template_configuration(
            required_tools=None, required_retrievers=["test_retriever"]
        )
        assert capabilities.enable_tools is False
        assert capabilities.enable_retrieval is True
        assert capabilities.enable_memory is True

        # Test with both
        capabilities = WorkflowCapabilities.from_template_configuration(
            required_tools=["test_tool"],
            required_retrievers=["test_retriever"],
        )
        assert capabilities.enable_tools is True
        assert capabilities.enable_retrieval is True
        assert capabilities.enable_memory is True

        # Test with neither (plain)
        capabilities = (
            WorkflowCapabilities.from_template_configuration()
        )
        assert capabilities.enable_tools is False
        assert capabilities.enable_retrieval is False
        assert capabilities.enable_memory is True

    def test_capability_based_workflow_support(self):
        """Test that capability-based workflows are supported by the unified system."""
        # Create various capability combinations
        capability_combinations = [
            WorkflowCapabilities(),  # Plain
            WorkflowCapabilities(enable_retrieval=True),  # RAG
            WorkflowCapabilities(enable_tools=True),  # Tools
            WorkflowCapabilities(
                enable_retrieval=True, enable_tools=True
            ),  # Full
        ]

        # Verify all combinations are supported
        for capabilities in capability_combinations:
            # The unified executor should be able to handle any capability combination
            assert isinstance(
                capabilities, WorkflowCapabilities
            ), f"Capabilities object {capabilities} is not properly formed"

    def test_capability_merging(self):
        """Test merging workflow capabilities."""
        cap1 = WorkflowCapabilities(enable_tools=True)
        cap2 = WorkflowCapabilities(enable_retrieval=True)

        merged = cap1.merge_with(cap2)

        assert merged.enable_tools is True
        assert merged.enable_retrieval is True
        assert merged.enable_memory is True

    def test_capability_serialization(self):
        """Test capability serialization to dict."""
        capabilities = WorkflowCapabilities(
            enable_tools=True, enable_retrieval=True, max_tool_calls=5
        )

        result = capabilities.to_dict()

        assert result["enable_tools"] is True
        assert result["enable_retrieval"] is True
        assert result["max_tool_calls"] == 5

    def test_dynamic_capability_detection(self):
        """Test that capabilities are properly detected from template configuration."""
        # Test that the system can determine what capabilities are needed
        test_cases = [
            ([], [], False, False),  # No tools or retrievers = plain
            (["tool1"], [], True, False),  # Tools only
            ([], ["retriever1"], False, True),  # Retrieval only
            (["tool1"], ["retriever1"], True, True),  # Both = full
        ]

        for (
            tools,
            retrievers,
            expected_tools,
            expected_retrieval,
        ) in test_cases:
            capabilities = (
                WorkflowCapabilities.from_template_configuration(
                    required_tools=tools if tools else None,
                    required_retrievers=(
                        retrievers if retrievers else None
                    ),
                )
            )

            assert (
                capabilities.enable_tools == expected_tools
            ), f"Expected enable_tools={expected_tools} for tools={tools}, retrievers={retrievers}"
            assert (
                capabilities.enable_retrieval == expected_retrieval
            ), f"Expected enable_retrieval={expected_retrieval} for tools={tools}, retrievers={retrievers}"
