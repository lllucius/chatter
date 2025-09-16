"""Test for restructured workflow execution flows.

This test validates that the new unified workflow execution system
maintains all the functionality while reducing complexity.
"""

import asyncio
from unittest.mock import Mock, AsyncMock


class TestWorkflowRestructuring:
    """Test the restructured workflow execution system."""

    def test_unified_executor_supported_types(self):
        """Test that unified executor supports all required workflow types."""
        from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
        
        # Test without actual dependencies
        supported_types = UnifiedWorkflowExecutor.get_supported_types()
        
        expected_types = ["plain", "basic", "rag", "tools", "full"]
        assert set(supported_types) == set(expected_types), f"Expected {expected_types}, got {supported_types}"
        print("✓ Unified executor supports all required workflow types")

    def test_simplified_validation_basic_cases(self):
        """Test simplified validation works for basic cases."""
        from chatter.core.simplified_workflow_validation import simplified_workflow_validation_service
        
        # Test valid workflow definition
        valid_definition = {
            "name": "Test Workflow",
            "nodes": [
                {"id": "start1", "type": "start", "data": {}},
                {"id": "model1", "type": "model", "data": {}}
            ],
            "edges": [
                {"id": "edge1", "source": "start1", "target": "model1"}
            ]
        }
        
        result = simplified_workflow_validation_service.validate_workflow_definition(valid_definition)
        assert result.is_valid, f"Valid definition should pass validation. Errors: {result.errors}"
        print("✓ Valid workflow definition passes validation")
        
        # Test invalid workflow definition
        invalid_definition = {
            "name": "",  # Invalid empty name
            "nodes": [],  # No nodes
            "edges": []
        }
        
        result = simplified_workflow_validation_service.validate_workflow_definition(invalid_definition)
        assert not result.is_valid, "Invalid definition should fail validation"
        assert len(result.errors) > 0, "Should have validation errors"
        print("✓ Invalid workflow definition fails validation as expected")

    def test_workflow_config_generation(self):
        """Test workflow configuration generation for different types."""
        from chatter.core.unified_workflow_executor import UnifiedWorkflowExecutor
        
        # Mock dependencies
        executor = UnifiedWorkflowExecutor(
            llm_service=Mock(),
            message_service=Mock(),
            template_manager=Mock()
        )
        
        # Mock conversation and chat request
        conversation = Mock()
        conversation.workspace_id = "test_workspace"
        
        chat_request = Mock()
        chat_request.enable_retrieval = True
        chat_request.document_ids = ["doc1", "doc2"]
        
        # Test plain workflow config
        config = executor._get_workflow_config("plain", conversation, chat_request)
        assert config["memory_window"] == 20
        assert config["tools"] is None
        assert config["retriever"] is None
        print("✓ Plain workflow config is correct")
        
        # Test RAG workflow config  
        config = executor._get_workflow_config("rag", conversation, chat_request)
        assert config["memory_window"] == 30
        assert config["max_documents"] == 10
        print("✓ RAG workflow config is correct")
        
        # Test tools workflow config
        config = executor._get_workflow_config("tools", conversation, chat_request)
        assert config["memory_window"] == 100
        assert config["max_tool_calls"] == 10
        print("✓ Tools workflow config is correct")
        
        # Test full workflow config
        config = executor._get_workflow_config("full", conversation, chat_request)
        assert config["memory_window"] == 50
        assert config["max_tool_calls"] == 5
        assert config["max_documents"] == 10
        print("✓ Full workflow config is correct")

    def test_workflow_execution_service_simplified(self):
        """Test that WorkflowExecutionService maintains its interface."""
        from chatter.services.workflow_execution import WorkflowExecutionService
        
        # Mock dependencies
        llm_service = Mock()
        message_service = Mock()
        session = Mock()
        
        # Create service (should not fail)
        service = WorkflowExecutionService(llm_service, message_service, session)
        
        # Test that it has the unified executor
        assert hasattr(service, 'executor')
        assert service.executor is not None
        print("✓ WorkflowExecutionService creates unified executor")
        
        # Test supported types
        supported_types = service.executor.get_supported_types()
        assert "plain" in supported_types
        assert "rag" in supported_types
        assert "tools" in supported_types
        assert "full" in supported_types
        print("✓ WorkflowExecutionService supports all workflow types")


def main():
    """Run the restructuring tests."""
    print("Testing restructured workflow execution flows...\n")
    
    test = TestWorkflowRestructuring()
    
    try:
        test.test_unified_executor_supported_types()
        test.test_simplified_validation_basic_cases()
        test.test_workflow_config_generation()
        test.test_workflow_execution_service_simplified()
        
        print("\n🎉 All workflow restructuring tests passed!")
        print("\nSummary of changes:")
        print("- ✓ Consolidated 4 separate executors into 1 unified executor")
        print("- ✓ Simplified validation system")
        print("- ✓ Maintained all workflow type support (plain, rag, tools, full)")
        print("- ✓ Preserved public API interfaces")
        print("- ✓ Significantly reduced code duplication")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)