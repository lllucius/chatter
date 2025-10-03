"""Test for workflow template END node fix."""

from chatter.core.workflow_template_generator import WorkflowTemplateGenerator


class MockTemplate:
    """Mock template for testing."""
    
    def __init__(self):
        self.default_params = {
            'system_message': 'You are a helpful assistant.'
        }


class TestWorkflowEndNodeFix:
    """Test that workflow templates use consistent node IDs."""

    def test_universal_chat_workflow_end_node_consistency(self):
        """Test that universal chat workflow uses 'end' (not 'END') consistently."""
        # Create a universal chat workflow
        nodes, edges = WorkflowTemplateGenerator._generate_universal_chat_workflow(
            template=MockTemplate(),
            input_params={
                'enable_memory': False,
                'enable_retrieval': False,
                'enable_tools': True,
                'memory_window': 10,
                'max_tool_calls': 10,
            }
        )
        
        # Find the end node
        end_nodes = [n for n in nodes if n['id'] == 'end']
        assert len(end_nodes) == 1, "Should have exactly one 'end' node"
        
        # Ensure no 'END' node exists
        end_upper_nodes = [n for n in nodes if n['id'] == 'END']
        assert len(end_upper_nodes) == 0, "Should not have 'END' (uppercase) node"
        
        # Check all edges reference 'end' not 'END'
        edges_to_end = [e for e in edges if e['target'] == 'end']
        edges_to_END = [e for e in edges if e['target'] == 'END']
        
        assert len(edges_to_END) == 0, f"No edges should target 'END' (uppercase), found: {edges_to_END}"
        assert len(edges_to_end) > 0, "Some edges should target 'end' (lowercase)"
        
    def test_capability_based_workflow_end_node_consistency(self):
        """Test that capability-based workflow uses 'end' (not 'END') consistently."""
        from chatter.core.workflow_template_generator import WorkflowCapabilities
        
        # Create a simple workflow with tools enabled
        capabilities = WorkflowCapabilities(
            enable_memory=False,
            enable_retrieval=False,
            enable_tools=True,
            max_tool_calls=10,
        )
        
        nodes, edges = WorkflowTemplateGenerator._generate_capability_based_workflow(
            template=None,
            input_params={},
            capabilities=capabilities
        )
        
        # Find the end node
        end_nodes = [n for n in nodes if n['id'] == 'end']
        assert len(end_nodes) == 1, "Should have exactly one 'end' node"
        
        # Ensure no 'END' node exists
        end_upper_nodes = [n for n in nodes if n['id'] == 'END']
        assert len(end_upper_nodes) == 0, "Should not have 'END' (uppercase) node"
        
        # Check all edges reference 'end' not 'END'
        edges_to_END = [e for e in edges if e['target'] == 'END']
        assert len(edges_to_END) == 0, f"No edges should target 'END' (uppercase), found: {edges_to_END}"
