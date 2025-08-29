"""Integration example showing how to use the new workflow features together."""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from chatter.core.workflow_metrics import workflow_metrics_collector
from chatter.core.workflow_advanced import advanced_workflow_manager
from chatter.core.workflow_security import workflow_security_manager, PermissionLevel
from chatter.core.workflow_performance import workflow_cache, lazy_tool_loader


class EnhancedWorkflowService:
    """Enhanced workflow service that integrates all new features."""
    
    def __init__(self):
        """Initialize enhanced workflow service."""
        self.setup_default_permissions()
        self.setup_performance_optimizations()
    
    def setup_default_permissions(self):
        """Setup default permissions for common tools."""
        # Grant basic permissions to demo users
        common_tools = ["calculator", "file_manager", "web_search"]
        
        for tool_name in common_tools:
            workflow_security_manager.grant_tool_permission(
                user_id="demo_user",
                tool_name=tool_name,
                permission_level=PermissionLevel.READ,
                rate_limit=10,
                expiry=datetime.now() + timedelta(hours=24)
            )
        
        # Grant premium permissions
        workflow_security_manager.grant_tool_permission(
            user_id="premium_user", 
            tool_name="file_manager",
            permission_level=PermissionLevel.WRITE,
            rate_limit=50,
            expiry=datetime.now() + timedelta(days=30)
        )
    
    def setup_performance_optimizations(self):
        """Setup performance optimizations."""
        # Preload common tools
        lazy_tool_loader.preload_tools(["calculator"])
        
        # Setup conditional workflow templates
        advanced_workflow_manager.register_conditional_config(
            "adaptive_support",
            conditions={
                "user_tier": {"in": ["premium", "enterprise"]},
                "query_complexity": {"min": 0.5, "max": 1.0},
                "default": True
            },
            workflow_configs={
                "user_tier": {
                    "mode": "full",
                    "enable_memory": True,
                    "memory_window": 100
                },
                "query_complexity": {
                    "mode": "tools", 
                    "enable_memory": True,
                    "memory_window": 30
                },
                "default": {
                    "mode": "plain",
                    "enable_memory": False,
                    "key": "default"
                }
            }
        )
    
    async def create_enhanced_workflow(
        self,
        llm: Any,
        user_id: str,
        conversation_id: str,
        workflow_type: str = "auto",
        context: Optional[Dict[str, Any]] = None,
        provider_name: str = "openai",
        model_name: str = "gpt-4"
    ) -> Optional[Any]:
        """Create a workflow with all enhancements enabled.
        
        Args:
            llm: Language model instance
            user_id: ID of the user
            conversation_id: ID of the conversation
            workflow_type: Type of workflow or "auto" for conditional
            context: Context for conditional workflows
            provider_name: Name of the LLM provider
            model_name: Name of the model
            
        Returns:
            Enhanced workflow instance or None
        """
        # Check cache first
        cache_config = {
            "workflow_type": workflow_type,
            "user_id": user_id,
            "context": context or {},
            "enable_security": True,
            "enable_metrics": True
        }
        
        cached_workflow = workflow_cache.get(
            provider_name=provider_name,
            workflow_type=workflow_type,
            config=cache_config
        )
        
        if cached_workflow:
            # Start metrics tracking for cached workflow
            workflow_metrics_collector.start_workflow_tracking(
                workflow_type=workflow_type,
                user_id=user_id,
                conversation_id=conversation_id,
                provider_name=provider_name,
                model_name=model_name,
                workflow_config={"cached": True}
            )
            return cached_workflow
        
        try:
            # Determine workflow creation method
            if workflow_type == "auto":
                # Use conditional workflow
                workflow = await advanced_workflow_manager.create_workflow_from_template(
                    llm=llm,
                    template_name="adaptive_support",
                    context=context or {}
                )
            else:
                # Use base workflow manager with enhanced features
                from chatter.core.langgraph import LangGraphWorkflowManager
                
                manager = LangGraphWorkflowManager()
                
                # Get required tools based on workflow type
                required_tools = []
                if workflow_type in ("tools", "full"):
                    # Load tools lazily based on user permissions
                    user_perms = workflow_security_manager.get_user_permissions(user_id)
                    available_tools = list(user_perms.tool_permissions.keys())
                    required_tools = await lazy_tool_loader.get_tools(available_tools)
                
                workflow = manager.create_workflow(
                    llm=llm,
                    mode=workflow_type,
                    tools=required_tools if required_tools else None,
                    enable_memory=True,
                    memory_window=50,
                    user_id=user_id,
                    conversation_id=conversation_id,
                    provider_name=provider_name,
                    model_name=model_name
                )
            
            # Cache the workflow
            if workflow:
                workflow_cache.put(
                    provider_name=provider_name,
                    workflow_type=workflow_type,
                    config=cache_config,
                    workflow=workflow
                )
            
            return workflow
            
        except Exception as e:
            # Log security event for workflow creation failure
            workflow_security_manager.log_event(
                "workflow_creation_failed",
                user_id,
                "",
                workflow_type,
                {"error": str(e)}
            )
            raise
    
    async def execute_workflow_safely(
        self,
        workflow: Any,
        initial_state: Dict[str, Any],
        user_id: str,
        workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute workflow with security and monitoring.
        
        Args:
            workflow: Workflow instance to execute
            initial_state: Initial conversation state
            user_id: ID of the user
            workflow_id: Optional workflow ID for metrics
            
        Returns:
            Workflow execution result
        """
        start_time = datetime.now()
        
        try:
            # Log workflow execution start
            workflow_security_manager.log_event(
                "workflow_execution_started",
                user_id,
                workflow_id or "",
                "unknown",
                {"state_keys": list(initial_state.keys())}
            )
            
            # Execute workflow
            from chatter.core.langgraph import LangGraphWorkflowManager
            manager = LangGraphWorkflowManager()
            
            result = await manager.run_workflow(
                workflow=workflow,
                initial_state=initial_state,
                thread_id=workflow_id
            )
            
            # Log successful execution
            execution_time = (datetime.now() - start_time).total_seconds()
            workflow_security_manager.log_event(
                "workflow_execution_completed",
                user_id,
                workflow_id or "",
                "unknown",
                {
                    "execution_time": execution_time,
                    "message_count": len(result.get("messages", []))
                }
            )
            
            return result
            
        except Exception as e:
            # Log execution failure
            workflow_security_manager.log_event(
                "workflow_execution_failed",
                user_id,
                workflow_id or "",
                "unknown",
                {"error": str(e), "execution_time": (datetime.now() - start_time).total_seconds()}
            )
            raise
    
    def get_user_dashboard(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive dashboard for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Dashboard data with metrics, permissions, and audit info
        """
        # Get workflow metrics
        workflow_stats = workflow_metrics_collector.get_workflow_stats(
            user_id=user_id,
            hours=24
        )
        
        # Get security information
        user_permissions = workflow_security_manager.get_user_permissions(user_id)
        recent_audit = workflow_security_manager.get_audit_log(
            user_id=user_id,
            hours=24,
            limit=10
        )
        
        # Get performance stats
        cache_stats = workflow_cache.get_stats()
        tool_stats = lazy_tool_loader.get_stats()
        
        # Get security stats
        security_stats = workflow_security_manager.get_security_stats(hours=24)
        
        return {
            "user_id": user_id,
            "workflow_metrics": workflow_stats,
            "permissions": {
                "tool_count": len(user_permissions.tool_permissions),
                "global_level": user_permissions.global_permission_level.value,
                "tools": [
                    {
                        "name": name,
                        "level": perm.permission_level.value,
                        "rate_limit": perm.rate_limit,
                        "usage_count": perm.usage_count,
                        "valid": perm.is_valid()
                    }
                    for name, perm in user_permissions.tool_permissions.items()
                ]
            },
            "recent_activity": recent_audit,
            "performance": {
                "cache_stats": cache_stats,
                "tool_stats": tool_stats
            },
            "security": security_stats,
            "generated_at": datetime.now().isoformat()
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health and performance metrics.
        
        Returns:
            System health dashboard
        """
        # Get overall metrics
        overall_workflow_stats = workflow_metrics_collector.get_workflow_stats(hours=24)
        
        # Get performance metrics
        cache_stats = workflow_cache.get_stats()
        tool_stats = lazy_tool_loader.get_stats()
        
        # Get security overview
        security_stats = workflow_security_manager.get_security_stats(hours=24)
        
        # Get recent errors from metrics
        recent_errors = workflow_metrics_collector.get_recent_errors(limit=5)
        
        # Calculate health score
        health_score = self._calculate_health_score(
            overall_workflow_stats,
            cache_stats,
            security_stats
        )
        
        return {
            "health_score": health_score,
            "workflow_metrics": overall_workflow_stats,
            "performance": {
                "cache": cache_stats,
                "tools": tool_stats
            },
            "security": security_stats,
            "recent_errors": recent_errors,
            "generated_at": datetime.now().isoformat()
        }
    
    def _calculate_health_score(
        self,
        workflow_stats: Dict[str, Any],
        cache_stats: Dict[str, Any],
        security_stats: Dict[str, Any]
    ) -> float:
        """Calculate overall system health score.
        
        Args:
            workflow_stats: Workflow performance statistics
            cache_stats: Cache performance statistics  
            security_stats: Security statistics
            
        Returns:
            Health score between 0.0 and 1.0
        """
        score = 1.0
        
        # Workflow success rate impact
        success_rate = workflow_stats.get("success_rate", 1.0)
        score *= success_rate
        
        # Cache hit rate impact
        cache_hit_rate = cache_stats.get("hit_rate", 0.0)
        cache_factor = 0.8 + (0.2 * cache_hit_rate)  # 80% base + 20% from cache performance
        score *= cache_factor
        
        # Security incidents impact
        denied_attempts = security_stats.get("denied_attempts", 0)
        total_events = security_stats.get("total_events", 1)
        security_factor = max(0.5, 1.0 - (denied_attempts / total_events))
        score *= security_factor
        
        return max(0.0, min(1.0, score))


# Example usage
async def example_usage():
    """Example of how to use the enhanced workflow service."""
    
    service = EnhancedWorkflowService()
    
    # Mock LLM for demonstration
    class MockLLM:
        def __init__(self):
            self.name = "mock-gpt-4"
        
        async def ainvoke(self, messages):
            return type('MockResponse', (), {'content': f"Mock response to {len(messages)} messages"})()
    
    llm = MockLLM()
    
    # Create enhanced workflow
    workflow = await service.create_enhanced_workflow(
        llm=llm,
        user_id="demo_user",
        conversation_id="conv_123",
        workflow_type="auto",
        context={
            "user_tier": "premium",
            "query_complexity": 0.8
        }
    )
    
    if workflow:
        print("✅ Enhanced workflow created successfully")
        
        # Execute workflow
        initial_state = {
            "messages": [],
            "user_id": "demo_user",
            "conversation_id": "conv_123",
            "metadata": {}
        }
        
        try:
            result = await service.execute_workflow_safely(
                workflow=workflow,
                initial_state=initial_state,
                user_id="demo_user",
                workflow_id="workflow_123"
            )
            print("✅ Workflow executed successfully")
            
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
    
    # Get user dashboard
    dashboard = service.get_user_dashboard("demo_user")
    print("\n📊 User Dashboard:")
    print(f"- Workflow executions: {dashboard['workflow_metrics']['total_executions']}")
    print(f"- Tool permissions: {dashboard['permissions']['tool_count']}")
    print(f"- Recent activities: {len(dashboard['recent_activity'])}")
    
    # Get system health
    health = service.get_system_health()
    print(f"\n🏥 System Health Score: {health['health_score']:.2f}")
    print(f"- Cache hit rate: {health['performance']['cache']['hit_rate']:.2f}")
    print(f"- Security incidents: {health['security']['denied_attempts']}")


if __name__ == "__main__":
    asyncio.run(example_usage())