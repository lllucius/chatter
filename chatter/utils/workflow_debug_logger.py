"""Workflow debug logger for capturing detailed execution information."""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class WorkflowDebugLogger:
    """Logger for capturing detailed workflow execution information."""
    
    def __init__(self, debug_mode: bool = False):
        """Initialize the debug logger.
        
        Args:
            debug_mode: Whether debug logging is enabled
        """
        self.debug_mode = debug_mode
        self.logs: List[Dict[str, Any]] = []
        self.node_executions: List[Dict[str, Any]] = []
        self.variable_states: Dict[str, Any] = {}
        self.execution_path: List[str] = []
        self.performance_metrics: Dict[str, Any] = {}
        self.llm_interactions: List[Dict[str, Any]] = []
        self.tool_calls: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    def log_entry(
        self, 
        level: str,
        message: str,
        node_id: Optional[str] = None,
        step_name: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        execution_time_ms: Optional[int] = None
    ) -> None:
        """Add a log entry.
        
        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR)
            message: Log message
            node_id: Associated workflow node ID
            step_name: Execution step name
            data: Additional log data
            execution_time_ms: Step execution time
        """
        if not self.debug_mode and level == "DEBUG":
            return
            
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "message": message,
            "node_id": node_id,
            "step_name": step_name,
            "data": data or {},
            "execution_time_ms": execution_time_ms,
        }
        self.logs.append(log_entry)
        
    def log_node_execution(
        self,
        node_id: str,
        node_type: str,
        input_data: Any = None,
        output_data: Any = None,
        execution_time_ms: Optional[int] = None,
        status: str = "completed",
        error: Optional[str] = None
    ) -> None:
        """Log the execution of a workflow node.
        
        Args:
            node_id: Node identifier
            node_type: Type of node
            input_data: Input data to the node
            output_data: Output data from the node
            execution_time_ms: Execution time in milliseconds
            status: Execution status
            error: Error message if failed
        """
        if not self.debug_mode:
            return
            
        node_execution = {
            "node_id": node_id,
            "node_type": node_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "input_data": self._sanitize_data(input_data),
            "output_data": self._sanitize_data(output_data),
            "execution_time_ms": execution_time_ms,
            "status": status,
            "error": error,
        }
        self.node_executions.append(node_execution)
        
        # Add to execution path
        self.execution_path.append(node_id)
        
    def log_llm_interaction(
        self,
        provider: str,
        model: str,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None,
        cost: Optional[float] = None,
        response_time_ms: Optional[int] = None,
        status: str = "completed",
        error: Optional[str] = None
    ) -> None:
        """Log LLM API interactions.
        
        Args:
            provider: LLM provider
            model: Model used
            input_tokens: Input token count
            output_tokens: Output token count
            cost: API call cost
            response_time_ms: Response time in milliseconds
            status: Interaction status
            error: Error message if failed
        """
        if not self.debug_mode:
            return
            
        interaction = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "response_time_ms": response_time_ms,
            "status": status,
            "error": error,
        }
        self.llm_interactions.append(interaction)
        
    def log_tool_call(
        self,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        result: Optional[Any] = None,
        execution_time_ms: Optional[int] = None,
        status: str = "completed",
        error: Optional[str] = None
    ) -> None:
        """Log tool execution details.
        
        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            result: Tool execution result
            execution_time_ms: Execution time in milliseconds
            status: Execution status
            error: Error message if failed
        """
        if not self.debug_mode:
            return
            
        tool_call = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool_name": tool_name,
            "parameters": self._sanitize_data(parameters),
            "result": self._sanitize_data(result),
            "execution_time_ms": execution_time_ms,
            "status": status,
            "error": error,
        }
        self.tool_calls.append(tool_call)
        
    def update_variable_state(self, variable_name: str, value: Any) -> None:
        """Update variable state tracking.
        
        Args:
            variable_name: Name of the variable
            value: Variable value
        """
        if not self.debug_mode:
            return
            
        self.variable_states[variable_name] = {
            "value": self._sanitize_data(value),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        
    def add_performance_metric(self, metric_name: str, value: Any) -> None:
        """Add a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if not self.debug_mode:
            return
            
        self.performance_metrics[metric_name] = value
        
    def get_debug_info(self, workflow_nodes: List[Dict[str, Any]], workflow_edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get comprehensive debug information.
        
        Args:
            workflow_nodes: Workflow nodes structure
            workflow_edges: Workflow edges structure
            
        Returns:
            Debug information dictionary
        """
        if not self.debug_mode:
            return {}
            
        total_time = (time.time() - self.start_time) * 1000  # Convert to ms
        
        return {
            "workflow_structure": {
                "nodes": workflow_nodes,
                "edges": workflow_edges,
            },
            "execution_path": self.execution_path,
            "node_executions": self.node_executions,
            "variable_states": self.variable_states,
            "performance_metrics": {
                **self.performance_metrics,
                "total_execution_time_ms": total_time,
                "nodes_executed": len(self.node_executions),
                "llm_calls": len(self.llm_interactions),
                "tool_calls": len(self.tool_calls),
            },
            "llm_interactions": self.llm_interactions,
            "tool_calls": self.tool_calls,
        }
        
    def get_structured_logs(self) -> List[Dict[str, Any]]:
        """Get structured log entries.
        
        Returns:
            List of log entries
        """
        return self.logs.copy()
        
    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data for logging (remove sensitive info, limit size).
        
        Args:
            data: Data to sanitize
            
        Returns:
            Sanitized data
        """
        if data is None:
            return None
            
        # Convert to string and limit length to prevent huge logs
        str_data = str(data)
        if len(str_data) > 1000:
            return str_data[:1000] + "... (truncated)"
            
        return str_data