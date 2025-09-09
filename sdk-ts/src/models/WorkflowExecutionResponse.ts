/**
 * Generated from OpenAPI schema: WorkflowExecutionResponse
 */

export interface WorkflowExecutionResponse {
  /** Execution input data */
  input_data?: Record<string, unknown> | null;
  /** Execution ID */
  id: string;
  /** Workflow definition ID */
  definition_id: string;
  /** Owner user ID */
  owner_id: string;
  /** Execution status */
  status: string;
  /** Execution start time */
  started_at?: string | null;
  /** Execution completion time */
  completed_at?: string | null;
  /** Execution time in milliseconds */
  execution_time_ms?: number | null;
  /** Execution output data */
  output_data?: Record<string, unknown> | null;
  /** Error message if failed */
  error_message?: string | null;
  /** Total tokens used */
  tokens_used?: number;
  /** Total cost */
  cost?: number;
  /** Creation timestamp */
  created_at?: string | null;
  /** Last update timestamp */
  updated_at?: string | null;
}
