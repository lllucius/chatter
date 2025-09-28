/**
 * Generated from OpenAPI schema: DetailedWorkflowExecutionResponse
 */
import { WorkflowDebugInfo } from './WorkflowDebugInfo';
import { WorkflowExecutionLogEntry } from './WorkflowExecutionLogEntry';

export interface DetailedWorkflowExecutionResponse {
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
  /** Detailed execution log entries */
  execution_log?: Record<string, unknown>[] | null;
  /** Debug information when debug mode enabled */
  debug_info?: Record<string, unknown> | null;
  /** Creation timestamp */
  created_at?: string | null;
  /** Last update timestamp */
  updated_at?: string | null;
  /** Structured execution logs */
  logs?: WorkflowExecutionLogEntry[];
  /** Comprehensive debug information */
  debug_details?: WorkflowDebugInfo | null;
}
