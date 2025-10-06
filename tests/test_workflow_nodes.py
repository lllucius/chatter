"""Tests for workflow node system with BaseWorkflowNode."""

import pytest

from chatter.core.workflow_node_factory import (
    BaseWorkflowNode,
    ConfigParser,
    ConditionalNode,
    DelayNode,
    EndNode,
    ErrorHandlerNode,
    LoopNode,
    MemoryNode,
    ModelNode,
    RetrievalNode,
    StartNode,
    ToolsNode,
    VariableNode,
    WorkflowNodeContext,
)


class TestBaseWorkflowNode:
    """Test shared BaseWorkflowNode functionality."""

    def test_init_with_node_type(self):
        """Test node initialization with node_type."""
        node = BaseWorkflowNode("test_node", {"key": "value"}, "TestNode")
        assert node.node_id == "test_node"
        assert node.config == {"key": "value"}
        assert node.node_type == "TestNode"

    def test_validate_required_fields(self):
        """Test required field validation."""
        node = BaseWorkflowNode("test", {"field1": "value1"}, "TestNode")
        
        # Should pass when all required fields present
        errors = node._validate_required_fields(["field1"])
        assert len(errors) == 0
        
        # Should fail when required field missing
        errors = node._validate_required_fields(["field2"])
        assert len(errors) == 1
        assert "field2" in errors[0]

    def test_validate_field_types(self):
        """Test field type validation."""
        node = BaseWorkflowNode(
            "test", 
            {"count": 5, "name": "test", "flag": True},
            "TestNode"
        )
        
        # Should pass with correct types
        errors = node._validate_field_types({
            "count": int,
            "name": str,
            "flag": bool
        })
        assert len(errors) == 0
        
        # Should fail with incorrect type
        errors = node._validate_field_types({"count": str})
        assert len(errors) == 1
        assert "count" in errors[0]
        assert "str" in errors[0]

    def test_get_config(self):
        """Test safe config value retrieval."""
        node = BaseWorkflowNode("test", {"key": "value"}, "TestNode")
        
        # Should return value if exists
        assert node._get_config("key") == "value"
        
        # Should return default if not exists
        assert node._get_config("missing", "default") == "default"
        assert node._get_config("missing") is None

    def test_get_required_config(self):
        """Test required config value retrieval."""
        node = BaseWorkflowNode("test", {"key": "value"}, "TestNode")
        
        # Should return value if exists
        assert node._get_required_config("key") == "value"
        
        # Should raise KeyError if not exists
        with pytest.raises(KeyError, match="requires 'missing'"):
            node._get_required_config("missing")

    def test_create_error_result(self):
        """Test standardized error result creation."""
        node = BaseWorkflowNode("test_node", {}, "TestNode")
        result = node._create_error_result("Test error message")
        
        assert "error_state" in result
        assert result["error_state"]["has_error"] is True
        assert result["error_state"]["error_message"] == "Test error message"
        assert result["error_state"]["error_node"] == "test_node"


class TestConfigParser:
    """Test ConfigParser utility functions."""

    def test_parse_model_config(self):
        """Test model configuration parsing."""
        config = {
            "provider": "anthropic",
            "model": "claude-3-opus",
            "temperature": 0.5,
            "max_tokens": 2000
        }
        
        parsed = ConfigParser.parse_model_config(config)
        assert parsed["provider"] == "anthropic"
        assert parsed["model"] == "claude-3-opus"
        assert parsed["temperature"] == 0.5
        assert parsed["max_tokens"] == 2000

    def test_parse_model_config_defaults(self):
        """Test model config parsing with defaults."""
        parsed = ConfigParser.parse_model_config({})
        assert parsed["provider"] == "openai"
        assert parsed["model"] == "gpt-4"
        assert parsed["temperature"] == 0.7
        assert parsed["max_tokens"] == 1000

    def test_parse_retry_config(self):
        """Test retry configuration parsing."""
        config = {"max_retries": 5, "retry_delay": 2}
        parsed = ConfigParser.parse_retry_config(config)
        assert parsed["max_retries"] == 5
        assert parsed["retry_delay"] == 2

    def test_parse_timeout_config(self):
        """Test timeout configuration parsing."""
        assert ConfigParser.parse_timeout_config({"timeout": 60}) == 60
        assert ConfigParser.parse_timeout_config({}) == 30

    def test_validate_enum_value(self):
        """Test enum value validation."""
        valid_values = ["option1", "option2", "option3"]
        
        # Should return None for valid value
        error = ConfigParser.validate_enum_value(
            "option1", valid_values, "test_field"
        )
        assert error is None
        
        # Should return error for invalid value
        error = ConfigParser.validate_enum_value(
            "invalid", valid_values, "test_field"
        )
        assert error is not None
        assert "test_field" in error
        assert "invalid" in error


class TestIndividualNodes:
    """Test individual node implementations."""

    def test_memory_node_initialization(self):
        """Test MemoryNode initialization with base class."""
        node = MemoryNode("mem1", {"memory_window": 20})
        assert node.memory_window == 20
        assert node.node_type == "MemoryNode"

    def test_memory_node_defaults(self):
        """Test MemoryNode with default values."""
        node = MemoryNode("mem1", {})
        assert node.memory_window == 10

    def test_retrieval_node_initialization(self):
        """Test RetrievalNode initialization."""
        node = RetrievalNode("ret1", {"max_documents": 3})
        assert node.max_documents == 3
        assert node.node_type == "RetrievalNode"

    def test_conditional_node_validation(self):
        """Test ConditionalNode validation."""
        # Should fail without condition
        node = ConditionalNode("cond1", {})
        errors = node.validate_config()
        assert len(errors) > 0
        assert any("condition" in error for error in errors)
        
        # Should pass with condition
        node = ConditionalNode("cond1", {"condition": "test"})
        errors = node.validate_config()
        assert len(errors) == 0

    def test_loop_node_initialization(self):
        """Test LoopNode initialization."""
        node = LoopNode("loop1", {"max_iterations": 5, "condition": "test"})
        assert node.max_iterations == 5
        assert node.loop_condition == "test"

    def test_loop_node_validation(self):
        """Test LoopNode type validation."""
        node = LoopNode("loop1", {"max_iterations": "invalid"})
        errors = node.validate_config()
        # Should have type validation error
        assert len(errors) > 0

    def test_variable_node_initialization(self):
        """Test VariableNode initialization."""
        node = VariableNode(
            "var1", 
            {
                "operation": "set",
                "variable_name": "my_var",
                "value": "test_value"
            }
        )
        assert node.operation == "set"
        assert node.variable_name == "my_var"
        assert node.value == "test_value"

    def test_variable_node_auto_name(self):
        """Test VariableNode auto-generated variable name."""
        node = VariableNode("var1", {})
        assert node.variable_name == "var_var1"

    def test_variable_node_validation(self):
        """Test VariableNode operation validation."""
        # Invalid operation
        node = VariableNode("var1", {"operation": "invalid"})
        errors = node.validate_config()
        assert len(errors) > 0
        assert any("operation" in error for error in errors)

    def test_error_handler_node_initialization(self):
        """Test ErrorHandlerNode initialization."""
        node = ErrorHandlerNode(
            "err1",
            {"retry_count": 5, "fallback_action": "stop"}
        )
        assert node.retry_count == 5
        assert node.fallback_action == "stop"

    def test_error_handler_node_validation(self):
        """Test ErrorHandlerNode validation."""
        # Invalid fallback action
        node = ErrorHandlerNode("err1", {"fallback_action": "invalid"})
        errors = node.validate_config()
        assert len(errors) > 0
        assert any("fallback_action" in error for error in errors)

    def test_tools_node_initialization(self):
        """Test ToolsNode initialization."""
        node = ToolsNode(
            "tools1",
            {"max_tool_calls": 5, "tool_timeout_ms": 10000}
        )
        assert node.max_tool_calls == 5
        assert node.tool_timeout_ms == 10000

    def test_delay_node_initialization(self):
        """Test DelayNode initialization."""
        node = DelayNode(
            "delay1",
            {
                "delay_type": "random",
                "duration": 500,
                "max_duration": 2000
            }
        )
        assert node.delay_type == "random"
        assert node.duration == 500
        assert node.max_duration == 2000

    def test_delay_node_validation(self):
        """Test DelayNode validation."""
        # Invalid delay type
        node = DelayNode("delay1", {"delay_type": "invalid"})
        errors = node.validate_config()
        assert len(errors) > 0
        assert any("delay_type" in error for error in errors)

    def test_start_node_initialization(self):
        """Test StartNode initialization."""
        node = StartNode("start1", {})
        assert node.node_type == "StartNode"

    def test_end_node_initialization(self):
        """Test EndNode initialization."""
        node = EndNode("end1", {})
        assert node.node_type == "EndNode"


class TestNodeExecution:
    """Test node execution with mocked context."""

    @pytest.fixture
    def mock_context(self):
        """Create a mock WorkflowNodeContext."""
        return WorkflowNodeContext(
            messages=[],
            user_id="test_user",
            conversation_id="test_conv",
            retrieval_context=None,
            conversation_summary=None,
            tool_call_count=0,
            metadata={},
            variables={},
            loop_state={},
            error_state={},
            conditional_results={},
            execution_history=[],
            usage_metadata={}
        )

    @pytest.mark.asyncio
    async def test_start_node_execute(self, mock_context):
        """Test StartNode execution."""
        node = StartNode("start1", {})
        result = await node.execute(mock_context)
        
        assert "metadata" in result
        assert result["metadata"]["workflow_started"] is True

    @pytest.mark.asyncio
    async def test_end_node_execute(self, mock_context):
        """Test EndNode execution."""
        node = EndNode("end1", {})
        result = await node.execute(mock_context)
        
        assert "metadata" in result
        assert result["metadata"]["workflow_completed"] is True

    @pytest.mark.asyncio
    async def test_variable_node_set_operation(self, mock_context):
        """Test VariableNode set operation."""
        node = VariableNode(
            "var1",
            {
                "operation": "set",
                "variable_name": "test_var",
                "value": "test_value"
            }
        )
        result = await node.execute(mock_context)
        
        assert "variables" in result
        assert result["variables"]["test_var"] == "test_value"

    @pytest.mark.asyncio
    async def test_variable_node_increment_operation(self, mock_context):
        """Test VariableNode increment operation."""
        mock_context["variables"]["counter"] = 5
        
        node = VariableNode(
            "var1",
            {
                "operation": "increment",
                "variable_name": "counter"
            }
        )
        result = await node.execute(mock_context)
        
        assert result["variables"]["counter"] == 6

    @pytest.mark.asyncio
    async def test_loop_node_execution(self, mock_context):
        """Test LoopNode execution and iteration tracking."""
        node = LoopNode("loop1", {"max_iterations": 3})
        
        # First execution
        result = await node.execute(mock_context)
        assert result["loop_state"]["loop1"] == 1
        assert result["metadata"]["loop_loop1_continue"] is True
        
        # Update context with loop state
        mock_context["loop_state"] = result["loop_state"]
        
        # Second execution
        result = await node.execute(mock_context)
        assert result["loop_state"]["loop1"] == 2

    @pytest.mark.asyncio
    async def test_error_handler_node_no_errors(self, mock_context):
        """Test ErrorHandlerNode when no errors present."""
        node = ErrorHandlerNode("err1", {"retry_count": 3})
        result = await node.execute(mock_context)
        
        assert "metadata" in result
        assert result["metadata"]["error_handler_err1"] == "no_errors"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
