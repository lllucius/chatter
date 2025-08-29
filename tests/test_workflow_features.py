"""Tests for the new workflow features: metrics, advanced workflows, and security."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from chatter.core.workflow_metrics import (
    WorkflowMetrics,
    WorkflowMetricsCollector,
    workflow_metrics_collector
)
from chatter.core.workflow_advanced import (
    AdvancedWorkflowManager,
    ConditionalWorkflowConfig,
    CompositeWorkflowConfig,
    advanced_workflow_manager
)
from chatter.core.workflow_security import (
    WorkflowSecurityManager,
    PermissionLevel,
    ToolPermission,
    UserPermissions,
    workflow_security_manager
)


class TestWorkflowMetrics:
    """Test workflow metrics functionality."""
    
    def test_workflow_metrics_creation(self):
        """Test creating workflow metrics."""
        metrics = WorkflowMetrics(
            workflow_type="rag",
            user_id="test_user",
            conversation_id="test_conv",
            provider_name="openai",
            model_name="gpt-4"
        )
        
        assert metrics.workflow_type == "rag"
        assert metrics.user_id == "test_user"
        assert metrics.conversation_id == "test_conv"
        assert metrics.provider_name == "openai"
        assert metrics.model_name == "gpt-4"
        assert metrics.success is True
        assert metrics.execution_time == 0.0
    
    def test_metrics_token_usage(self):
        """Test token usage tracking."""
        metrics = WorkflowMetrics()
        
        metrics.add_token_usage("openai", 100)
        metrics.add_token_usage("openai", 50)
        metrics.add_token_usage("anthropic", 75)
        
        assert metrics.token_usage["openai"] == 150
        assert metrics.token_usage["anthropic"] == 75
    
    def test_metrics_error_handling(self):
        """Test error tracking."""
        metrics = WorkflowMetrics()
        
        metrics.add_error("Tool execution failed")
        metrics.add_error("Rate limit exceeded")
        
        assert len(metrics.errors) == 2
        assert "Tool execution failed" in metrics.errors
        assert metrics.success is False
    
    def test_metrics_finalization(self):
        """Test metrics finalization."""
        metrics = WorkflowMetrics()
        start_time = metrics.start_time
        
        # Simulate some processing time
        import time
        time.sleep(0.1)
        
        metrics.finalize()
        
        assert metrics.end_time is not None
        assert metrics.execution_time > 0
        assert metrics.end_time > start_time


class TestWorkflowMetricsCollector:
    """Test workflow metrics collector."""
    
    def setup_method(self):
        """Setup test environment."""
        self.collector = WorkflowMetricsCollector(max_history=100)
    
    def test_start_workflow_tracking(self):
        """Test starting workflow tracking."""
        workflow_id = self.collector.start_workflow_tracking(
            workflow_type="tools",
            user_id="user123",
            conversation_id="conv456",
            provider_name="anthropic",
            model_name="claude-3"
        )
        
        assert workflow_id in self.collector.active_workflows
        metrics = self.collector.active_workflows[workflow_id]
        assert metrics.workflow_type == "tools"
        assert metrics.user_id == "user123"
        assert metrics.conversation_id == "conv456"
    
    def test_update_workflow_metrics(self):
        """Test updating workflow metrics."""
        workflow_id = self.collector.start_workflow_tracking(
            workflow_type="rag",
            user_id="user123",
            conversation_id="conv456"
        )
        
        self.collector.update_workflow_metrics(
            workflow_id,
            token_usage={"openai": 100},
            tool_calls=2,
            retrieval_context_size=1500,
            memory_usage_mb=50.5
        )
        
        metrics = self.collector.active_workflows[workflow_id]
        assert metrics.token_usage["openai"] == 100
        assert metrics.tool_calls == 2
        assert metrics.retrieval_context_size == 1500
        assert metrics.memory_usage_mb == 50.5
    
    def test_finish_workflow_tracking(self):
        """Test finishing workflow tracking."""
        workflow_id = self.collector.start_workflow_tracking(
            workflow_type="full",
            user_id="user123",
            conversation_id="conv456"
        )
        
        # Update some metrics
        self.collector.update_workflow_metrics(
            workflow_id,
            tool_calls=3
        )
        
        # Finish tracking
        final_metrics = self.collector.finish_workflow_tracking(
            workflow_id,
            user_satisfaction=0.9
        )
        
        assert final_metrics is not None
        assert final_metrics.user_satisfaction == 0.9
        assert final_metrics.execution_time > 0
        assert workflow_id not in self.collector.active_workflows
        assert final_metrics in self.collector.metrics_history
    
    def test_workflow_stats(self):
        """Test getting workflow statistics."""
        # Create some test data
        for i in range(5):
            workflow_id = self.collector.start_workflow_tracking(
                workflow_type="rag" if i % 2 == 0 else "tools",
                user_id=f"user{i}",
                conversation_id=f"conv{i}",
                provider_name="openai"
            )
            self.collector.update_workflow_metrics(
                workflow_id,
                token_usage={"openai": 100 + i * 10},
                tool_calls=i
            )
            self.collector.finish_workflow_tracking(workflow_id)
        
        stats = self.collector.get_workflow_stats()
        
        assert stats["total_executions"] == 5
        assert stats["success_rate"] == 1.0
        assert stats["avg_execution_time"] > 0
        assert stats["total_tokens"] > 0
        assert "rag" in stats["workflow_types"]
        assert "tools" in stats["workflow_types"]


class TestAdvancedWorkflows:
    """Test advanced workflow features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.manager = AdvancedWorkflowManager()
    
    def test_conditional_workflow_config(self):
        """Test conditional workflow configuration."""
        conditions = {
            "query_complexity": {"min": 0.7, "max": 1.0},
            "user_type": "premium"
        }
        workflow_configs = {
            "query_complexity": {"mode": "full"},
            "user_type": {"mode": "tools"}
        }
        
        config = ConditionalWorkflowConfig(conditions, workflow_configs)
        
        # Test high complexity condition
        result = config.evaluate_conditions({"query_complexity": 0.8})
        assert result == "query_complexity"
        
        # Test user type condition
        result = config.evaluate_conditions({"user_type": "premium"})
        assert result == "user_type"
        
        # Test no match
        result = config.evaluate_conditions({"query_complexity": 0.5})
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_conditional_workflow(self):
        """Test creating conditional workflows."""
        # Mock LLM
        mock_llm = Mock()
        
        conditions = {
            "complexity": "high",
            "default": True
        }
        workflow_configs = {
            "complexity": {"mode": "full", "enable_memory": True},
            "default": {"mode": "plain", "key": "default"}
        }
        
        with patch.object(self.manager.base_manager, 'create_workflow') as mock_create:
            mock_create.return_value = Mock()
            
            # Test matching condition
            workflow = await self.manager.create_conditional_workflow(
                llm=mock_llm,
                conditions=conditions,
                workflow_configs=workflow_configs,
                context={"complexity": "high"}
            )
            
            assert workflow is not None
            mock_create.assert_called_once()
            call_args = mock_create.call_args[1]
            assert call_args["mode"] == "full"
            assert call_args["enable_memory"] is True
    
    @pytest.mark.asyncio
    async def test_composite_workflow(self):
        """Test composite workflow creation."""
        # Mock workflows
        mock_workflows = [Mock() for _ in range(3)]
        
        config = await self.manager.create_composite_workflow(
            workflows=mock_workflows,
            execution_strategy="sequential"
        )
        
        assert isinstance(config, CompositeWorkflowConfig)
        assert len(config.workflows) == 3
        assert config.execution_strategy == "sequential"
        assert config.workflow_id in self.manager.composite_configs


class TestWorkflowSecurity:
    """Test workflow security features."""
    
    def setup_method(self):
        """Setup test environment."""
        self.security_manager = WorkflowSecurityManager()
    
    def test_tool_permission_creation(self):
        """Test creating tool permissions."""
        permission = ToolPermission(
            tool_name="file_reader",
            permission_level=PermissionLevel.READ,
            allowed_methods={"read", "list"},
            rate_limit=10
        )
        
        assert permission.tool_name == "file_reader"
        assert permission.permission_level == PermissionLevel.READ
        assert "read" in permission.allowed_methods
        assert permission.rate_limit == 10
        assert permission.is_valid()
    
    def test_expired_permission(self):
        """Test expired permissions."""
        expiry = datetime.now() - timedelta(hours=1)  # Expired 1 hour ago
        permission = ToolPermission(
            tool_name="expired_tool",
            permission_level=PermissionLevel.WRITE,
            expiry=expiry
        )
        
        assert not permission.is_valid()
        assert not permission.can_execute()
    
    def test_user_permissions(self):
        """Test user permission management."""
        user_perms = UserPermissions("user123")
        
        # Add permission
        permission = ToolPermission(
            tool_name="calculator",
            permission_level=PermissionLevel.READ,
            allowed_methods={"add", "subtract"}
        )
        user_perms.add_tool_permission(permission)
        
        # Test permission checks
        assert user_perms.can_use_tool("calculator", "add")
        assert user_perms.can_use_tool("calculator", "subtract")
        assert not user_perms.can_use_tool("calculator", "multiply")  # Not allowed
        assert not user_perms.can_use_tool("nonexistent_tool")
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        permission = ToolPermission(
            tool_name="api_tool",
            permission_level=PermissionLevel.WRITE,
            rate_limit=2  # Only 2 calls per hour
        )
        
        # First two calls should succeed
        assert permission.record_usage()
        assert permission.record_usage()
        
        # Third call should fail due to rate limit
        assert not permission.record_usage()
    
    def test_tool_authorization(self):
        """Test tool execution authorization."""
        user_id = "user123"
        
        # Grant permission
        self.security_manager.grant_tool_permission(
            user_id=user_id,
            tool_name="file_manager",
            permission_level=PermissionLevel.WRITE,
            allowed_methods={"create", "delete"},
            rate_limit=5
        )
        
        # Test authorization
        authorized = self.security_manager.authorize_tool_execution(
            user_id=user_id,
            workflow_id="workflow123",
            workflow_type="tools",
            tool_name="file_manager",
            method="create",
            parameters={"filename": "test.txt"}
        )
        
        assert authorized
        
        # Test unauthorized tool
        unauthorized = self.security_manager.authorize_tool_execution(
            user_id=user_id,
            workflow_id="workflow123",
            workflow_type="tools",
            tool_name="unauthorized_tool",
            method="execute"
        )
        
        assert not unauthorized
    
    def test_sensitive_content_detection(self):
        """Test sensitive content detection."""
        # Test with sensitive content
        sensitive_data = {
            "api_key": "sk-1234567890abcdef",
            "message": "Please use this password: secret123"
        }
        
        assert self.security_manager.contains_sensitive_content(sensitive_data)
        
        # Test with clean content
        clean_data = {
            "message": "Hello world",
            "number": 42
        }
        
        assert not self.security_manager.contains_sensitive_content(clean_data)
    
    def test_audit_logging(self):
        """Test audit logging functionality."""
        # Grant permission (should create audit log)
        self.security_manager.grant_tool_permission(
            user_id="user123",
            tool_name="test_tool",
            permission_level=PermissionLevel.READ
        )
        
        # Check audit log
        audit_entries = self.security_manager.get_audit_log(
            user_id="user123",
            event_type="permission_granted"
        )
        
        assert len(audit_entries) > 0
        entry = audit_entries[0]
        assert entry["event_type"] == "permission_granted"
        assert entry["user_id"] == "user123"
        assert "test_tool" in str(entry["details"])
    
    def test_security_stats(self):
        """Test security statistics."""
        user_id = "test_user"
        
        # Create some test events
        self.security_manager.log_event(
            "tool_execution_authorized",
            user_id,
            "workflow1",
            "tools",
            {"tool_name": "calculator"}
        )
        
        self.security_manager.log_event(
            "tool_access_denied",
            user_id,
            "workflow2",
            "tools",
            {"tool_name": "file_manager", "reason": "insufficient_permissions"}
        )
        
        stats = self.security_manager.get_security_stats()
        
        assert stats["total_events"] >= 2
        assert stats["authorized_executions"] >= 1
        assert stats["denied_attempts"] >= 1
        assert len(stats["top_users"]) > 0
        assert len(stats["top_events"]) > 0


if __name__ == "__main__":
    pytest.main([__file__])