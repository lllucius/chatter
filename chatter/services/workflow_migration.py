"""Migration guide and compatibility layer for workflow system consolidation.

This module provides a compatibility layer to help migrate from the old
multiple execution engines to the new consolidated modern system.
"""

from __future__ import annotations

import warnings
from typing import Any, Dict, List

from chatter.core.modern_langgraph import modern_workflow_manager
from chatter.services.consolidated_workflow_execution import ConsolidatedWorkflowExecutionService
from chatter.utils.logging import get_logger

logger = get_logger(__name__)


class DeprecatedWorkflowEngine:
    """Deprecated workflow engine - use ConsolidatedWorkflowExecutionService instead."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "UnifiedWorkflowEngine is deprecated. Use ConsolidatedWorkflowExecutionService instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._warn_about_deprecation()
        
    def _warn_about_deprecation(self):
        """Warn about deprecation and provide migration guidance."""
        logger.warning(
            "DEPRECATED: UnifiedWorkflowEngine is deprecated. "
            "Please migrate to ConsolidatedWorkflowExecutionService for the modern workflow system."
        )
        
    async def execute_workflow(self, *args, **kwargs):
        """Deprecated method - use ConsolidatedWorkflowExecutionService."""
        raise RuntimeError(
            "UnifiedWorkflowEngine.execute_workflow is deprecated. "
            "Use ConsolidatedWorkflowExecutionService.execute_chat_workflow instead."
        )


class DeprecatedWorkflowExecutor:
    """Deprecated workflow executor - use ConsolidatedWorkflowExecutionService instead."""
    
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "UnifiedWorkflowExecutor is deprecated. Use ConsolidatedWorkflowExecutionService instead.",
            DeprecationWarning,
            stacklevel=2
        )
        self._warn_about_deprecation()
        
    def _warn_about_deprecation(self):
        """Warn about deprecation and provide migration guidance."""
        logger.warning(
            "DEPRECATED: UnifiedWorkflowExecutor is deprecated. "
            "Please migrate to ConsolidatedWorkflowExecutionService for the modern workflow system."
        )
        
    async def execute(self, *args, **kwargs):
        """Deprecated method - use ConsolidatedWorkflowExecutionService."""
        raise RuntimeError(
            "UnifiedWorkflowExecutor.execute is deprecated. "
            "Use ConsolidatedWorkflowExecutionService.execute_chat_workflow instead."
        )


# Compatibility aliases for gradual migration
UnifiedWorkflowEngine = DeprecatedWorkflowEngine
UnifiedWorkflowExecutor = DeprecatedWorkflowExecutor


def migrate_to_modern_system() -> Dict[str, Any]:
    """Get migration information for updating to the modern workflow system."""
    return {
        "migration_guide": {
            "old_system": {
                "LangGraphWorkflowManager": "Limited to hardcoded workflow patterns",
                "UnifiedWorkflowEngine": "Compatibility wrapper (deprecated)",
                "UnifiedWorkflowExecutor": "Streaming executor (deprecated)",
            },
            "new_system": {
                "ModernLangGraphWorkflowManager": "Flexible workflow creation with all node types",
                "ConsolidatedWorkflowExecutionService": "Single execution service for all workflow types",
                "WorkflowNodeFactory": "Extensible node creation system",
                "WorkflowGraphBuilder": "Dynamic graph construction",
                "EnhancedToolExecutor": "Advanced tool execution with recursion detection",
                "EnhancedMemoryManager": "Intelligent memory management",
            },
            "migration_steps": [
                "1. Replace UnifiedWorkflowEngine with ConsolidatedWorkflowExecutionService",
                "2. Replace UnifiedWorkflowExecutor with ConsolidatedWorkflowExecutionService",
                "3. Update workflow creation to use ModernLangGraphWorkflowManager",
                "4. Use WorkflowNodeFactory for custom node types",
                "5. Configure enhanced tool and memory settings",
                "6. Update API endpoints to use modern validation",
            ],
            "breaking_changes": [
                "UnifiedWorkflowEngine.execute_workflow -> ConsolidatedWorkflowExecutionService.execute_chat_workflow",
                "UnifiedWorkflowExecutor.execute -> ConsolidatedWorkflowExecutionService.execute_chat_workflow", 
                "LangGraphWorkflowManager.create_workflow parameters remain compatible",
                "New node types (conditional, loop, variable, error_handler, delay) now supported",
                "Enhanced state schema (WorkflowNodeContext) includes new fields",
            ],
            "benefits": [
                "Support for all defined node types (conditional, loop, variable, error_handler, delay)",
                "Configurable tool recursion detection with multiple strategies",
                "Adaptive memory management with intelligent summarization",
                "Flexible workflow topologies with proper validation",
                "Better error handling and recovery mechanisms",
                "Comprehensive execution tracking and debugging",
            ]
        },
        "compatibility": {
            "backward_compatible_apis": [
                "ModernLangGraphWorkflowManager.create_workflow",
                "Workflow execution endpoints",
                "Basic chat functionality",
            ],
            "deprecated_but_working": [
                "UnifiedWorkflowEngine (with warnings)",
                "UnifiedWorkflowExecutor (with warnings)",
                "Old workflow validation",
            ],
            "removed_features": [
                "Hardcoded workflow patterns",
                "Limited node type support",
                "Simple recursion detection",
                "Fixed memory window sizes",
            ]
        },
        "new_features": {
            "advanced_nodes": {
                "conditional": "Branching logic with condition evaluation",
                "loop": "Iteration control with max iterations and conditions",
                "variable": "State management with operations (set, get, increment, etc.)",
                "error_handler": "Error recovery with retry logic and fallback actions",
                "delay": "Timing control with multiple delay strategies",
            },
            "enhanced_execution": {
                "tool_recursion_detection": "Configurable strategies (strict, adaptive, lenient)",
                "adaptive_memory": "Window sizing based on conversation complexity",
                "summary_caching": "TTL-based caching of conversation summaries",
                "progress_tracking": "Detailed execution history and pattern detection",
            },
            "validation_system": {
                "comprehensive_validation": "All node types and configurations validated",
                "graph_topology_checking": "Cycle detection and connectivity validation",
                "configuration_compatibility": "Node config validation with helpful errors",
            }
        },
        "performance_improvements": [
            "Reduced code duplication (3 engines -> 1 consolidated service)",
            "Better caching for memory summaries",
            "Optimized recursion detection algorithms",
            "Improved error handling with faster recovery",
            "Streamlined graph construction process",
        ]
    }


def check_system_compatibility() -> Dict[str, Any]:
    """Check compatibility of current system with modern workflow architecture."""
    compatibility_status = {
        "modern_system_available": True,
        "deprecated_warnings": [],
        "migration_required": [],
        "feature_gaps": [],
    }
    
    try:
        # Check if modern components are available
        from chatter.core.modern_langgraph import ModernLangGraphWorkflowManager
        from chatter.core.workflow_node_factory import WorkflowNodeFactory
        from chatter.core.workflow_graph_builder import WorkflowGraphBuilder
        from chatter.core.enhanced_tool_executor import EnhancedToolExecutor
        from chatter.core.enhanced_memory_manager import EnhancedMemoryManager
        
        compatibility_status["modern_components_loaded"] = True
        compatibility_status["supported_node_types"] = WorkflowNodeFactory.get_supported_types()
        
    except ImportError as e:
        compatibility_status["modern_system_available"] = False
        compatibility_status["import_errors"] = [str(e)]
        
    # Check for deprecated usage
    import sys
    loaded_modules = sys.modules.keys()
    
    deprecated_modules = [
        "chatter.core.unified_workflow_engine",
        "chatter.core.unified_workflow_executor",
    ]
    
    for module in deprecated_modules:
        if module in loaded_modules:
            compatibility_status["deprecated_warnings"].append(f"Module {module} is deprecated")
            
    return compatibility_status


# Migration helper functions
def create_modern_workflow_service(llm_service, message_service, session):
    """Create modern workflow service with migration logging."""
    logger.info("Creating ConsolidatedWorkflowExecutionService (modern system)")
    
    from chatter.services.consolidated_workflow_execution import ConsolidatedWorkflowExecutionService
    return ConsolidatedWorkflowExecutionService(
        llm_service=llm_service,
        message_service=message_service,
        session=session,
    )


def get_modern_workflow_manager():
    """Get modern workflow manager with migration logging."""
    logger.info("Using ModernLangGraphWorkflowManager (modern system)")
    return modern_workflow_manager


# Export modern components for easy migration
__all__ = [
    "ConsolidatedWorkflowExecutionService",
    "ModernLangGraphWorkflowManager", 
    "WorkflowNodeFactory",
    "WorkflowGraphBuilder",
    "EnhancedToolExecutor",
    "EnhancedMemoryManager",
    "migrate_to_modern_system",
    "check_system_compatibility",
    "create_modern_workflow_service",
    "get_modern_workflow_manager",
    # Deprecated exports (with warnings)
    "DeprecatedWorkflowEngine",
    "DeprecatedWorkflowExecutor",
    "UnifiedWorkflowEngine",  # Alias to deprecated
    "UnifiedWorkflowExecutor",  # Alias to deprecated
]