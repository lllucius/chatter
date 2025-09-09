/**
 * Generated from OpenAPI schema: JobResponse
 */

export interface JobResponse {
  /** Job ID */
  id: string;
  /** Job name */
  name: string;
  /** Function name */
  function_name: string;
  /** Job priority */
  priority: JobPriority;
  /** Job status */
  status: JobStatus;
  /** Creation timestamp */
  created_at: string;
  /** Start timestamp */
  started_at?: string | null;
  /** Completion timestamp */
  completed_at?: string | null;
  /** Scheduled execution time */
  scheduled_at?: string | null;
  /** Number of retry attempts */
  retry_count: number;
  /** Maximum retry attempts */
  max_retries: number;
  /** Error message if failed */
  error_message?: string | null;
  /** Job result if completed */
  result?: Record<string, unknown> | null;
  /** Job progress percentage */
  progress?: number;
  /** Progress message */
  progress_message?: string | null;
}
