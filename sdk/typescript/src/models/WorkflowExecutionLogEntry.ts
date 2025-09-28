/**
 * Generated from OpenAPI schema: WorkflowExecutionLogEntry
 */
export interface WorkflowExecutionLogEntry {
  /** Log entry timestamp */
  timestamp: string;
  /** Log level (DEBUG, INFO, WARN, ERROR) */
  level: string;
  /** Associated workflow node ID */
  node_id?: string | null;
  /** Execution step name */
  step_name?: string | null;
  /** Log message */
  message: string;
  /** Additional log data */
  data?: Record<string, unknown> | null;
  /** Step execution time */
  execution_time_ms?: number | null;
}
