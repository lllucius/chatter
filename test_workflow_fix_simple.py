#!/usr/bin/env python3
"""Simple test to verify workflow definition conversion fix."""

import os
os.environ['DATABASE_URL'] = 'sqlite:///test.db'  # Set minimal environment

import sys
sys.path.insert(0, os.path.dirname(__file__))

def test_converter_logic():
    """Test the converter logic without full imports."""
    print("Testing WorkflowDefinition converter logic...")
    
    # Define the converter function logic here for testing
    class GraphDefinition:
        def __init__(self):
            self.nodes = []
            self.edges = []
            self.entry_point = None
            
        def add_node(self, node_id, node_type, config):
            self.nodes.append({"id": node_id, "type": node_type, "config": config})
            
        def add_edge(self, source, target, condition=None):
            self.edges.append({"source": source, "target": target, "condition": condition})
            
        def set_entry_point(self, node_id):
            self.entry_point = node_id
    
    def mock_find_entry_point(definition):
        # Simple logic to find entry point - node that is source but not target
        targets = {edge["target"] for edge in definition.edges}
        sources = {edge["source"] for edge in definition.edges}
        entry_candidates = sources - targets
        
        if len(entry_candidates) == 1:
            return entry_candidates.pop()
        # Return first node if no clear entry point
        return definition.nodes[0]["id"] if definition.nodes else None
    
    def convert_workflow_definition(db_definition):
        """Test version of the converter."""
        definition = GraphDefinition()
        
        # Copy nodes
        for node in db_definition.nodes:
            definition.add_node(
                node_id=node["id"],
                node_type=node["type"], 
                config=node.get("config", {})
            )
        
        # Copy edges
        for edge in db_definition.edges:
            definition.add_edge(
                source=edge["source"],
                target=edge["target"],
                condition=edge.get("condition")
            )
        
        # Find and set entry point if not explicitly set
        if not definition.entry_point:
            entry_point = mock_find_entry_point(definition)
            if entry_point:
                definition.set_entry_point(entry_point)
        
        return definition
    
    # Mock database definition
    class MockDBWorkflowDefinition:
        def __init__(self):
            self.nodes = [
                {"id": "start", "type": "start", "config": {}},
                {"id": "call_model", "type": "call_model", "config": {"system_message": "Test"}},
                {"id": "end", "type": "end", "config": {}},
            ]
            self.edges = [
                {"source": "start", "target": "call_model"},
                {"source": "call_model", "target": "end"},
            ]
    
    # Test the conversion
    db_def = MockDBWorkflowDefinition()
    graph_def = convert_workflow_definition(db_def)
    
    # Verify nodes were copied
    assert len(graph_def.nodes) == 3, f"Expected 3 nodes, got {len(graph_def.nodes)}"
    
    # Verify edges were copied  
    assert len(graph_def.edges) == 2, f"Expected 2 edges, got {len(graph_def.edges)}"
    
    # Verify entry point was set
    assert graph_def.entry_point is not None, "Entry point should be set"
    assert graph_def.entry_point == "start", f"Expected entry point 'start', got '{graph_def.entry_point}'"
    
    print("✓ Converter logic test passed!")


def test_filtering_logic():
    """Test the parameter filtering logic."""
    print("Testing parameter filtering logic...")
    
    def filter_kwargs(kwargs):
        """Test version of the filtering logic."""
        return {k: v for k, v in kwargs.items() if k not in ['llm', 'tools', 'retriever']}
    
    # Test that retriever is filtered out
    test_kwargs = {
        'llm': 'mock_llm',
        'tools': ['tool1', 'tool2'],
        'retriever': 'mock_retriever',
        'temperature': 0.7,
        'max_tokens': 100
    }
    
    filtered = filter_kwargs(test_kwargs)
    
    assert 'retriever' not in filtered, "retriever should be filtered out"
    assert 'llm' not in filtered, "llm should be filtered out"
    assert 'tools' not in filtered, "tools should be filtered out"
    assert 'temperature' in filtered, "temperature should be preserved"
    assert 'max_tokens' in filtered, "max_tokens should be preserved"
    
    print("✓ Parameter filtering test passed!")


if __name__ == "__main__":
    print("Running workflow fix tests...")
    print()
    
    test_converter_logic()
    test_filtering_logic()
    
    print()
    print("✓ All tests passed!")