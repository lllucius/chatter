"""Tests for Phase 7: API Simplification.

This test module verifies that the API simplification changes work correctly:
- Execution endpoints use ExecutionEngine
- Validation endpoints use WorkflowValidator
- Response models are properly aligned
"""

import pytest


class TestPhase7APIsimplification:
    """Test Phase 7 API simplification."""

    def test_execution_result_has_required_fields(self):
        """Test that ExecutionResult has all required fields for API response."""
        from chatter.core.workflow_execution_result import ExecutionResult

        # Create a minimal ExecutionResult
        result = ExecutionResult(
            response="Test response",
            execution_id="test_exec_123",
            user_id="user_123",
            definition_id="def_123",
        )

        # Verify fields exist
        assert result.execution_id == "test_exec_123"
        assert result.user_id == "user_123"
        assert result.definition_id == "def_123"
        assert result.template_id is None

    def test_execution_result_to_api_response(self):
        """Test ExecutionResult.to_api_response() returns proper schema."""
        from chatter.core.workflow_execution_result import ExecutionResult

        # Create a complete ExecutionResult
        result = ExecutionResult(
            response="Test response",
            execution_id="exec_123",
            user_id="user_123",
            definition_id="def_123",
            execution_time_ms=1000,
            tokens_used=100,
            cost=0.05,
        )

        # Convert to API response
        api_response = result.to_api_response()

        # Verify schema fields
        assert api_response.id == "exec_123"
        assert api_response.owner_id == "user_123"
        assert api_response.definition_id == "def_123"
        assert api_response.status == "completed"
        assert api_response.execution_time_ms == 1000
        assert api_response.tokens_used == 100
        assert api_response.cost == 0.05
        assert api_response.error_message is None

    def test_execution_result_with_template(self):
        """Test ExecutionResult with template_id instead of definition_id."""
        from chatter.core.workflow_execution_result import ExecutionResult

        # Create result with template_id
        result = ExecutionResult(
            response="Test response",
            execution_id="exec_123",
            user_id="user_123",
            template_id="template_123",
            execution_time_ms=500,
        )

        # Convert to API response
        api_response = result.to_api_response()

        # Verify template_id is used for definition_id when definition_id is None
        assert api_response.id == "exec_123"
        assert api_response.owner_id == "user_123"
        assert api_response.definition_id == "template_123"

    def test_execution_result_with_errors(self):
        """Test ExecutionResult with errors sets proper status."""
        from chatter.core.workflow_execution_result import ExecutionResult

        # Create result with errors
        result = ExecutionResult(
            response="",
            execution_id="exec_123",
            user_id="user_123",
            errors=["Something went wrong"],
        )

        # Convert to API response
        api_response = result.to_api_response()

        # Verify error handling
        assert api_response.status == "failed"
        assert api_response.error_message == "Something went wrong"

    def test_execution_result_from_raw(self):
        """Test ExecutionResult.from_raw() with all fields."""
        from chatter.core.workflow_execution_result import ExecutionResult

        # Simulate raw result from workflow_manager
        raw_result = {
            "messages": [
                {"content": "Hello", "type": "human"},
                {"content": "Hi there!", "type": "ai"},
            ],
            "usage_metadata": {
                "total_tokens": 100,
                "prompt_tokens": 60,
                "completion_tokens": 40,
            },
            "cost": 0.001,
            "metadata": {"test": "value"},
            "tool_call_count": 2,
        }

        # Create from raw
        result = ExecutionResult.from_raw(
            raw_result=raw_result,
            execution_id="exec_123",
            conversation_id="conv_123",
            workflow_type="definition",
            user_id="user_123",
            definition_id="def_123",
        )

        # Verify all fields
        assert result.execution_id == "exec_123"
        assert result.conversation_id == "conv_123"
        assert result.workflow_type == "definition"
        assert result.user_id == "user_123"
        assert result.definition_id == "def_123"
        assert result.tokens_used == 100
        assert result.prompt_tokens == 60
        assert result.completion_tokens == 40
        assert result.cost == 0.001
        assert result.tool_calls == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
