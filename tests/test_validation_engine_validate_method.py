"""Test for ValidationEngine validate method fix."""

import pytest
from chatter.core.validation import ValidationEngine, DEFAULT_CONTEXT
from chatter.core.exceptions import ValidationError


class TestValidationEngineValidateMethod:
    """Test the ValidationEngine.validate method that was missing."""
    
    def test_validate_method_exists(self):
        """Test that the validate method exists on ValidationEngine."""
        engine = ValidationEngine()
        assert hasattr(engine, 'validate'), "ValidationEngine should have a validate method"
        
    def test_validate_workflow_definition(self):
        """Test that validate method can validate workflow definitions."""
        engine = ValidationEngine()
        
        # Valid workflow definition
        workflow_data = {
            "name": "test workflow",
            "nodes": [],
            "edges": []
        }
        
        result = engine.validate("workflow", workflow_data, "workflow_definition", DEFAULT_CONTEXT)
        assert result is not None
        assert hasattr(result, 'is_valid')
        assert result.is_valid is True  # Empty lists should be valid
        
    def test_validate_with_invalid_validator(self):
        """Test that validate method raises error for unknown validator."""
        engine = ValidationEngine()
        
        with pytest.raises(ValidationError) as exc_info:
            engine.validate("nonexistent", {}, "rule", DEFAULT_CONTEXT)
            
        assert "Validator 'nonexistent' not found" in str(exc_info.value)
        
    def test_validate_workflow_with_nodes_and_edges(self):
        """Test workflow validation with actual nodes and edges."""
        engine = ValidationEngine()
        
        workflow_data = {
            "name": "test workflow",
            "nodes": [
                {"id": "node1", "type": "start", "data": {"label": "Start"}},
                {"id": "node2", "type": "end", "data": {"label": "End"}}
            ],
            "edges": [
                {"id": "edge1", "source": "node1", "target": "node2"}
            ]
        }
        
        result = engine.validate("workflow", workflow_data, "workflow_definition", DEFAULT_CONTEXT)
        assert result.is_valid is True
        
    def test_validate_missing_required_fields(self):
        """Test workflow validation with missing required fields."""
        engine = ValidationEngine()
        
        # Missing nodes and edges
        workflow_data = {
            "name": "test workflow"
        }
        
        result = engine.validate("workflow", workflow_data, "workflow_definition", DEFAULT_CONTEXT)
        assert result.is_valid is False
        assert len(result.errors) == 2  # Should have errors for missing nodes and edges
        error_messages = [str(error) for error in result.errors]
        assert any("Missing required field: nodes" in msg for msg in error_messages)
        assert any("Missing required field: edges" in msg for msg in error_messages)