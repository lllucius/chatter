/**
 * Generated from OpenAPI schema: WorkflowDebugInfo
 */
export interface WorkflowDebugInfo {
  /** Workflow nodes and edges structure */
  workflow_structure: Record<string, unknown>;
  /** Actual path taken through the workflow */
  execution_path: string[];
  /** Details of each node execution */
  node_executions: Record<string, unknown>[];
  /** Variable states throughout execution */
  variable_states: Record<string, unknown>;
  /** Performance metrics for each step */
  performance_metrics: Record<string, unknown>;
  /** LLM API interactions */
  llm_interactions?: Record<string, unknown>[];
  /** Tool execution details */
  tool_calls?: Record<string, unknown>[];
}
