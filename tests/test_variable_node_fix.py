"""Test for variable node validation fix."""

import pytest
from unittest.mock import Mock

from chatter.core.workflow_node_factory import VariableNode, WorkflowNodeFactory


class TestVariableNodeFix:
    """Test that variable node validation issues are fixed."""

    def test_variable_node_without_variable_name(self):
        """Test that VariableNode works without variable_name."""
        # This should work now and not raise validation errors
        node = VariableNode('test_node', {})
        
        # Should have auto-generated variable name
        assert node.variable_name == 'var_test_node'
        
        # Should not have validation errors
        errors = node.validate_config()
        assert len(errors) == 0

    def test_variable_node_with_explicit_variable_name(self):
        """Test that VariableNode works with explicit variable_name."""
        node = VariableNode('test_node', {'variable_name': 'my_variable'})
        
        # Should use explicit variable name
        assert node.variable_name == 'my_variable'
        
        # Should not have validation errors
        errors = node.validate_config()
        assert len(errors) == 0

    def test_variable_node_with_invalid_operation(self):
        """Test that VariableNode still validates operations."""
        node = VariableNode('test_node', {'operation': 'invalid_op'})
        
        # Should have auto-generated variable name
        assert node.variable_name == 'var_test_node'
        
        # Should have validation error for invalid operation
        errors = node.validate_config()
        assert len(errors) == 1
        assert 'Invalid operation: invalid_op' in errors[0]

    def test_variable_node_factory_creation(self):
        """Test that WorkflowNodeFactory can create variable nodes without errors."""
        # This should not raise an exception anymore
        node = WorkflowNodeFactory.create_node(
            node_type='variable',
            node_id='test_variable',
            config={}
        )
        
        assert isinstance(node, VariableNode)
        assert node.variable_name == 'var_test_variable'

    def test_variable_node_factory_creation_with_config(self):
        """Test WorkflowNodeFactory with proper config."""
        node = WorkflowNodeFactory.create_node(
            node_type='variable',
            node_id='test_variable',
            config={'variable_name': 'my_var', 'operation': 'set', 'value': 'test'}
        )
        
        assert isinstance(node, VariableNode)
        assert node.variable_name == 'my_var'
        assert node.operation == 'set'
        assert node.value == 'test'

    def test_variable_node_warning_logged_for_auto_generated_names(self, caplog):
        """Test that warnings are logged for auto-generated variable names."""
        import logging
        
        with caplog.at_level(logging.WARNING):
            node = VariableNode('test_node', {})
            node.validate_config()
        
        # Should log a warning about auto-generated variable name
        warning_messages = [record.message for record in caplog.records if record.levelname == 'WARNING']
        assert any('auto-generated variable name' in msg for msg in warning_messages)

    async def test_variable_node_execution(self):
        """Test that variable node execution still works correctly."""
        from chatter.core.workflow_node_factory import WorkflowNodeContext
        
        # Test set operation
        node = VariableNode('test_node', {'operation': 'set', 'value': 'test_value'})
        
        context: WorkflowNodeContext = {
            'messages': [],
            'user_id': 'test_user',
            'conversation_id': 'test_conv',
            'retrieval_context': None,
            'conversation_summary': None,
            'tool_call_count': 0,
            'metadata': {},
            'variables': {},
            'loop_state': {},
            'error_state': {},
            'conditional_results': {},
            'execution_history': []
        }
        
        result = await node.execute(context)
        
        # Should set the variable
        assert 'variables' in result
        assert result['variables']['var_test_node'] == 'test_value'