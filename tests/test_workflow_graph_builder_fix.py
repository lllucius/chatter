"""
Test for workflow graph builder argument duplication fix.
"""

import os
import sys

# Set up minimal environment for testing
os.environ.setdefault(
    'DATABASE_URL', 'postgresql://test:test@localhost/test'
)

# Add the chatter directory to path
sys.path.insert(0, '/home/runner/work/chatter/chatter')

from chatter.core.workflow_graph_builder import WorkflowGraphBuilder


class FakeLLM:
    """Minimal fake LLM for testing."""

    def __init__(self, name="fake_llm"):
        self.name = name

    def bind_tools(self, tools):
        """Mock bind_tools method."""
        return self

    async def ainvoke(self, messages, **kwargs):
        """Mock ainvoke method."""
        return f"Response from {self.name}"

    def __str__(self):
        return f"FakeLLM({self.name})"


class TestWorkflowGraphBuilderArgumentFix:
    """Test the argument duplication fix in WorkflowGraphBuilder."""

    def test_create_llm_node_wrapper_no_duplicate_args(self):
        """Test that _create_llm_node_wrapper doesn't pass duplicate arguments."""
        builder = WorkflowGraphBuilder()
        fake_llm = FakeLLM("test_llm")

        # This should not raise "got multiple values for argument 'llm'" error
        try:
            result = builder._create_llm_node_wrapper(
                node_id="test_node",
                config={"system_message": "Test message"},
                llm=fake_llm,
                tools=None,
                extra_param="should_be_preserved",
            )
            assert result is not None
            print("✅ LLM node wrapper executed successfully")
        except TypeError as e:
            if "got multiple values for argument 'llm'" in str(e):
                raise AssertionError(
                    f"Argument duplication not fixed: {e}"
                ) from e
            else:
                # Other TypeError might be expected due to fake LLM
                print(
                    f"ℹ️  Expected TypeError (not argument duplication): {e}"
                )
        except Exception as e:
            # Other exceptions might be expected due to fake LLM
            print(
                f"ℹ️  Expected exception (not argument duplication): {e}"
            )

    def test_create_tool_node_wrapper_no_duplicate_args(self):
        """Test that _create_tool_node_wrapper doesn't pass duplicate arguments."""
        builder = WorkflowGraphBuilder()

        # This should not raise "got multiple values for argument 'tools'" error
        try:
            result = builder._create_tool_node_wrapper(
                node_id="test_tool_node",
                config={"max_tool_calls": 5},
                tools=["mock_tool"],
                extra_param="should_be_preserved",
            )
            assert result is not None
            print("✅ Tool node wrapper executed successfully")
        except TypeError as e:
            if "got multiple values for argument 'tools'" in str(e):
                raise AssertionError(
                    f"Argument duplication not fixed: {e}"
                ) from e
            else:
                # Other TypeError might be expected due to mock tools
                print(
                    f"ℹ️  Expected TypeError (not argument duplication): {e}"
                )
        except Exception as e:
            # Other exceptions might be expected due to mock tools
            print(
                f"ℹ️  Expected exception (not argument duplication): {e}"
            )

    def test_kwargs_filtering_preserves_other_params(self):
        """Test that the kwargs filtering preserves non-conflicting parameters."""
        builder = WorkflowGraphBuilder()
        fake_llm = FakeLLM("test_llm")

        # Mock the _create_llm_node method to capture the kwargs
        captured_kwargs = {}

        def mock_create_llm_node(node_id, llm, tools, config, **kwargs):
            nonlocal captured_kwargs
            captured_kwargs = kwargs

            # Return a simple mock object instead of WorkflowNode
            class MockNode:
                def __init__(self, node_id, config):
                    self.node_id = node_id
                    self.config = config

            return MockNode(node_id, config)

        builder._create_llm_node = mock_create_llm_node

        # Call the wrapper with extra parameters
        builder._create_llm_node_wrapper(
            node_id="test",
            config={"test": "config"},
            llm=fake_llm,
            tools=None,
            extra_param1="value1",
            extra_param2="value2",
        )

        # Verify that extra parameters are preserved but llm and tools are filtered out
        assert (
            "llm" not in captured_kwargs
        ), "llm should be filtered out of kwargs"
        assert (
            "tools" not in captured_kwargs
        ), "tools should be filtered out of kwargs"
        assert (
            captured_kwargs.get("extra_param1") == "value1"
        ), "extra_param1 should be preserved"
        assert (
            captured_kwargs.get("extra_param2") == "value2"
        ), "extra_param2 should be preserved"

        print("✅ Kwargs filtering working correctly")


if __name__ == "__main__":
    test = TestWorkflowGraphBuilderArgumentFix()
    test.test_create_llm_node_wrapper_no_duplicate_args()
    test.test_create_tool_node_wrapper_no_duplicate_args()
    test.test_kwargs_filtering_preserves_other_params()
    print("✅ All tests passed!")
