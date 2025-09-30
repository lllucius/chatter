"""Tests for workflow validation fixes."""

import os

# Set up environment for tests
os.environ['DATABASE_URL'] = 'postgresql://user:pass@localhost/test'
os.environ['REDIS_URL'] = 'redis://localhost:6379'

from chatter.core.validation.context import ValidationContext
from chatter.core.validation.validators import WorkflowValidator


class TestWorkflowValidationFixes:
    """Test class for workflow validation fixes."""

    def test_new_node_types_validation(self):
        """Test that the new node types (memory, retrieval, model) are recognized."""

        definition_data = {
            "name": "test_workflow",
            "description": "Test workflow with new node types",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 50, "y": 200},
                    "data": {"label": "Start"},
                },
                {
                    "id": "memory-1",
                    "type": "memory",
                    "position": {"x": 150, "y": 200},
                    "data": {"label": "Memory"},
                },
                {
                    "id": "retrieval-1",
                    "type": "retrieval",
                    "position": {"x": 250, "y": 200},
                    "data": {"label": "Retrieval"},
                },
                {
                    "id": "model-1",
                    "type": "model",
                    "position": {"x": 350, "y": 200},
                    "data": {"label": "Model"},
                },
                {
                    "id": "end-1",
                    "type": "end",
                    "position": {"x": 450, "y": 200},
                    "data": {"label": "End"},
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start-1",
                    "target": "memory-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e2",
                    "source": "memory-1",
                    "target": "retrieval-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e3",
                    "source": "retrieval-1",
                    "target": "model-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e4",
                    "source": "model-1",
                    "target": "end-1",
                    "type": "custom",
                    "data": {},
                },
            ],
            "metadata": {},
        }

        validator = WorkflowValidator()
        context = ValidationContext()

        result = validator.validate(
            definition_data, "workflow_definition", context
        )

        # Should be valid
        assert (
            result.is_valid
        ), f"Validation should pass. Errors: {[str(e) for e in result.errors]}"

        # Should not have warnings about unknown node types
        unknown_type_warnings = [
            w for w in result.warnings if "unknown type" in w
        ]
        assert (
            len(unknown_type_warnings) == 0
        ), f"Should not have warnings about unknown node types: {unknown_type_warnings}"

    def test_specific_problem_statement_warnings_fixed(self):
        """Test that the specific warnings from the problem statement are fixed:
        - Node 1 has unknown type: variable
        - Node 8 has unknown type: tools
        """

        definition_data = {
            "name": "universal_chat_workflow",
            "description": "Universal chat workflow that was causing warnings",
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "Start"},
                },
                {
                    "id": "set_capabilities",
                    "type": "variable",
                    "position": {"x": 300, "y": 100},
                    "data": {"label": "Set Capabilities"},
                },  # Node 1 - variable type
                {
                    "id": "conditional_memory",
                    "type": "conditional",
                    "position": {"x": 500, "y": 100},
                    "data": {"label": "Memory Check"},
                },
                {
                    "id": "manage_memory",
                    "type": "memory",
                    "position": {"x": 500, "y": 200},
                    "data": {"label": "Manage Memory"},
                },
                {
                    "id": "conditional_retrieval",
                    "type": "conditional",
                    "position": {"x": 700, "y": 100},
                    "data": {"label": "Retrieval Check"},
                },
                {
                    "id": "retrieve_context",
                    "type": "retrieval",
                    "position": {"x": 700, "y": 200},
                    "data": {"label": "Retrieve Context"},
                },
                {
                    "id": "call_model",
                    "type": "llm",
                    "position": {"x": 900, "y": 100},
                    "data": {"label": "Call Model"},
                },
                {
                    "id": "conditional_tools",
                    "type": "conditional",
                    "position": {"x": 1100, "y": 100},
                    "data": {"label": "Tools Check"},
                },
                {
                    "id": "execute_tools",
                    "type": "tools",
                    "position": {"x": 1100, "y": 200},
                    "data": {"label": "Execute Tools"},
                },  # Node 8 - tools type
                {
                    "id": "end",
                    "type": "end",
                    "position": {"x": 1300, "y": 100},
                    "data": {"label": "End"},
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start",
                    "target": "set_capabilities",
                    "type": "default",
                },
                {
                    "id": "e2",
                    "source": "set_capabilities",
                    "target": "conditional_memory",
                    "type": "default",
                },
                {
                    "id": "e3",
                    "source": "conditional_memory",
                    "target": "manage_memory",
                    "type": "conditional",
                },
                {
                    "id": "e4",
                    "source": "conditional_memory",
                    "target": "conditional_retrieval",
                    "type": "conditional",
                },
                {
                    "id": "e5",
                    "source": "manage_memory",
                    "target": "conditional_retrieval",
                    "type": "default",
                },
                {
                    "id": "e6",
                    "source": "conditional_retrieval",
                    "target": "retrieve_context",
                    "type": "conditional",
                },
                {
                    "id": "e7",
                    "source": "conditional_retrieval",
                    "target": "call_model",
                    "type": "conditional",
                },
                {
                    "id": "e8",
                    "source": "retrieve_context",
                    "target": "call_model",
                    "type": "default",
                },
                {
                    "id": "e9",
                    "source": "call_model",
                    "target": "conditional_tools",
                    "type": "default",
                },
                {
                    "id": "e10",
                    "source": "conditional_tools",
                    "target": "execute_tools",
                    "type": "conditional",
                },
                {
                    "id": "e11",
                    "source": "conditional_tools",
                    "target": "end",
                    "type": "conditional",
                },
                {
                    "id": "e12",
                    "source": "execute_tools",
                    "target": "end",
                    "type": "default",
                },
            ],
            "metadata": {},
        }

        validator = WorkflowValidator()
        context = ValidationContext()

        result = validator.validate(
            definition_data, "workflow_definition", context
        )

        # Convert warnings to strings for easier checking
        warning_messages = [str(w) for w in result.warnings]

        # Check that the specific warnings from the problem statement are NOT present
        variable_warning = any(
            "unknown type: variable" in w.lower()
            for w in warning_messages
        )
        tools_warning = any(
            "unknown type: tools" in w.lower() for w in warning_messages
        )

        assert (
            not variable_warning
        ), f"Variable type should be recognized. Warnings: {warning_messages}"
        assert (
            not tools_warning
        ), f"Tools type should be recognized. Warnings: {warning_messages}"

        # Check that these node types are specifically supported
        nodes = definition_data["nodes"]
        variable_node = next(
            (n for n in nodes if n["type"] == "variable"), None
        )
        tools_node = next(
            (n for n in nodes if n["type"] == "tools"), None
        )

        assert (
            variable_node is not None
        ), "Should have a variable node in test data"
        assert (
            tools_node is not None
        ), "Should have a tools node in test data"

    def test_comprehensive_workflow_from_error_log(self):
        """Test validation of the exact workflow from the error log."""

        # This is the actual data from the error log that was failing
        definition_data = {
            "name": "asdf",
            "description": "asdf",
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start",
                    "position": {"x": 50, "y": 200},
                    "data": {
                        "label": "Start",
                        "nodeType": "start",
                        "config": {"isEntryPoint": True},
                    },
                },
                {
                    "id": "memory-1",
                    "type": "memory",
                    "position": {"x": 250, "y": 200},
                    "data": {
                        "label": "Memory Manager",
                        "nodeType": "memory",
                        "config": {"enabled": True, "window": 20},
                    },
                },
                {
                    "id": "retrieval-1",
                    "type": "retrieval",
                    "position": {"x": 450, "y": 200},
                    "data": {
                        "label": "Document Retrieval",
                        "nodeType": "retrieval",
                        "config": {
                            "collection": "knowledge_base",
                            "topK": 5,
                        },
                    },
                },
                {
                    "id": "model-1",
                    "type": "model",
                    "position": {"x": 650, "y": 200},
                    "data": {
                        "label": "Chat Model",
                        "nodeType": "model",
                        "config": {
                            "temperature": 0.7,
                            "maxTokens": 1000,
                            "systemMessage": "Use the retrieved context to answer questions.",
                        },
                    },
                },
                {
                    "id": "conditional-1",
                    "type": "conditional",
                    "position": {"x": 850, "y": 200},
                    "data": {
                        "label": "Tool Decision",
                        "nodeType": "conditional",
                        "config": {
                            "condition": "should_use_tools",
                            "branches": {
                                "true": "tool-1",
                                "false": "end",
                            },
                        },
                    },
                },
                {
                    "id": "tool-1",
                    "type": "tool",
                    "position": {"x": 1050, "y": 100},
                    "data": {
                        "label": "Tool Execution",
                        "nodeType": "tool",
                        "config": {
                            "tools": ["web_search", "calculator"],
                            "parallel": False,
                        },
                    },
                },
            ],
            "edges": [
                {
                    "id": "e1",
                    "source": "start-1",
                    "target": "memory-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e2",
                    "source": "memory-1",
                    "target": "retrieval-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e3",
                    "source": "retrieval-1",
                    "target": "model-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e4",
                    "source": "model-1",
                    "target": "conditional-1",
                    "type": "custom",
                    "data": {},
                },
                {
                    "id": "e5",
                    "source": "conditional-1",
                    "target": "tool-1",
                    "type": "custom",
                    "data": {
                        "label": "needs tools",
                        "condition": "has_tool_calls",
                    },
                    "sourceHandle": "true",
                },
                {
                    "id": "e6",
                    "source": "tool-1",
                    "target": "model-1",
                    "type": "custom",
                    "data": {"label": "tool results"},
                },
            ],
            "metadata": {
                "name": "asdf",
                "description": "asdf",
                "version": "1.0.0",
                "createdAt": "2025-09-28T04:48:16.316Z",
                "updatedAt": "2025-09-28T04:48:16.316Z",
            },
        }

        validator = WorkflowValidator()
        context = ValidationContext()

        result = validator.validate(
            definition_data, "workflow_definition", context
        )

        # Should now be valid after our fixes
        assert (
            result.is_valid
        ), f"Validation should pass after fixes. Errors: {[str(e) for e in result.errors]}"

        # Should not have warnings about unknown node types
        unknown_type_warnings = [
            w for w in result.warnings if "unknown type" in w
        ]
        assert (
            len(unknown_type_warnings) == 0
        ), f"Should not have warnings about unknown node types: {unknown_type_warnings}"

    def test_dictionary_validation_still_works(self):
        """Test that the original dictionary validation still works correctly."""

        # Test that nodes and edges must be dictionaries
        definition_data_with_non_dict_nodes = {
            "name": "test",
            "description": "test",
            "nodes": ["not_a_dict", {"id": "node-1", "type": "start"}],
            "edges": [],
            "metadata": {},
        }

        validator = WorkflowValidator()
        context = ValidationContext()

        result = validator.validate(
            definition_data_with_non_dict_nodes,
            "workflow_definition",
            context,
        )

        # Should be invalid
        assert (
            not result.is_valid
        ), "Validation should fail for non-dictionary nodes"

        # Should have specific error about node being a dictionary
        node_dict_errors = [
            e
            for e in result.errors
            if "Node 0 must be a dictionary" in str(e)
        ]
        assert (
            len(node_dict_errors) == 1
        ), f"Should have error about node being dictionary: {[str(e) for e in result.errors]}"

    def test_edge_dictionary_validation(self):
        """Test that edges must be dictionaries."""

        definition_data_with_non_dict_edges = {
            "name": "test",
            "description": "test",
            "nodes": [
                {
                    "id": "node-1",
                    "type": "start",
                    "position": {"x": 0, "y": 0},
                    "data": {},
                }
            ],
            "edges": ["not_a_dict"],
            "metadata": {},
        }

        validator = WorkflowValidator()
        context = ValidationContext()

        result = validator.validate(
            definition_data_with_non_dict_edges,
            "workflow_definition",
            context,
        )

        # Should be invalid
        assert (
            not result.is_valid
        ), "Validation should fail for non-dictionary edges"

        # Should have specific error about edge being a dictionary
        edge_dict_errors = [
            e
            for e in result.errors
            if "Edge 0 must be a dictionary" in str(e)
        ]
        assert (
            len(edge_dict_errors) == 1
        ), f"Should have error about edge being dictionary: {[str(e) for e in result.errors]}"


if __name__ == "__main__":
    # Run tests directly for manual verification
    test_class = TestWorkflowValidationFixes()

    print("Running workflow validation fix tests...")

    try:
        test_class.test_new_node_types_validation()
        print("✓ New node types test passed")
    except Exception as e:
        print(f"❌ New node types test failed: {e}")

    try:
        test_class.test_comprehensive_workflow_from_error_log()
        print("✓ Comprehensive workflow test passed")
    except Exception as e:
        print(f"❌ Comprehensive workflow test failed: {e}")

    try:
        test_class.test_dictionary_validation_still_works()
        print("✓ Dictionary validation test passed")
    except Exception as e:
        print(f"❌ Dictionary validation test failed: {e}")

    try:
        test_class.test_edge_dictionary_validation()
        print("✓ Edge dictionary validation test passed")
    except Exception as e:
        print(f"❌ Edge dictionary validation test failed: {e}")

    print("All tests completed!")
