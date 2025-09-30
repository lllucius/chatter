"""Integration test for universal template streaming fix."""

from chatter.core.workflow_node_factory import WorkflowNodeFactory


class TestUniversalTemplateStreamingFix:
    """Integration tests to ensure universal template streaming works without variable_name errors."""

    def test_universal_template_variable_nodes_creation(self):
        """Test that variable nodes can be created without explicit variable_name (universal template scenario)."""
        # Test the exact scenario that was failing in universal template streaming

        # 1. Test capabilities variable node (this was the main failure case)
        capabilities_node = WorkflowNodeFactory.create_node(
            'variable',
            'set_capabilities',
            {
                'operation': 'set',
                'value': {
                    'enable_memory': False,
                    'enable_retrieval': False,
                    'enable_tools': False,
                    'memory_window': 10,
                    'max_tool_calls': 10,
                    'max_documents': 5,
                },
            },
        )

        assert capabilities_node.variable_name == 'var_set_capabilities'
        assert capabilities_node.operation == 'set'
        assert len(capabilities_node.validate_config()) == 0

        # 2. Test empty config variable node
        empty_node = WorkflowNodeFactory.create_node(
            'variable', 'empty_test', {}
        )
        assert empty_node.variable_name == 'var_empty_test'
        assert empty_node.operation == 'set'  # default
        assert len(empty_node.validate_config()) == 0

        # 3. Test minimal config variable node
        minimal_node = WorkflowNodeFactory.create_node(
            'variable', 'minimal_test', {'operation': 'get'}
        )
        assert minimal_node.variable_name == 'var_minimal_test'
        assert minimal_node.operation == 'get'
        assert len(minimal_node.validate_config()) == 0

    def test_no_old_validation_errors_thrown(self):
        """Test that the old 'Variable node must have a variable_name defined' error is no longer thrown."""
        # This should NOT raise ValueError about variable_name being required
        try:
            node = WorkflowNodeFactory.create_node(
                'variable', 'test_node', {}
            )
            errors = node.validate_config()

            # Ensure no errors mention required variable_name
            for error in errors:
                assert (
                    "variable_name" not in error.lower()
                    or "required" not in error.lower()
                ), f"Found old validation error: {error}"

        except ValueError as e:
            error_msg = str(e).lower()
            assert not (
                "variable_name" in error_msg
                and ("required" in error_msg or "defined" in error_msg)
            ), f"Old validation error still present: {str(e)}"

    def test_variable_node_backward_compatibility_maintained(self):
        """Test that existing explicit variable_name configurations still work."""
        # Snake case (preferred)
        node1 = WorkflowNodeFactory.create_node(
            'variable',
            'test1',
            {
                'variable_name': 'my_explicit_var',
                'operation': 'set',
                'value': 'test',
            },
        )
        assert node1.variable_name == 'my_explicit_var'
        assert len(node1.validate_config()) == 0

        # Camel case (legacy)
        node2 = WorkflowNodeFactory.create_node(
            'variable',
            'test2',
            {
                'variableName': 'myLegacyVar',
                'operation': 'set',
                'value': 'test',
            },
        )
        assert node2.variable_name == 'myLegacyVar'
        assert len(node2.validate_config()) == 0

    def test_multiple_variable_nodes_in_workflow(self):
        """Test creating multiple variable nodes like in a universal template workflow."""
        nodes = []

        # Create multiple variable nodes as would appear in universal template
        node_configs = [
            (
                'set_capabilities',
                {'operation': 'set', 'value': {'enable_memory': True}},
            ),
            ('counter', {'operation': 'set', 'value': 0}),
            ('result_collector', {}),  # Empty config
            ('user_state', {'operation': 'get'}),
        ]

        for node_id, config in node_configs:
            node = WorkflowNodeFactory.create_node(
                'variable', node_id, config
            )
            assert node.variable_name.startswith('var_') or config.get(
                'variable_name'
            )
            assert len(node.validate_config()) == 0
            nodes.append(node)

        # Ensure all nodes were created successfully
        assert len(nodes) == 4

        # Ensure all have unique variable names
        var_names = [node.variable_name for node in nodes]
        assert len(set(var_names)) == len(
            var_names
        ), "Variable names should be unique"
