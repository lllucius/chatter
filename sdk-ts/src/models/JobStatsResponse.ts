/**
 * Generated from OpenAPI schema: JobStatsResponse
 */
export interface JobStatsResponse {
  /** Total number of jobs */
  total_jobs: number;
  /** Number of pending jobs */
  pending_jobs: number;
  /** Number of running jobs */
  running_jobs: number;
  /** Number of completed jobs */
  completed_jobs: number;
  /** Number of failed jobs */
  failed_jobs: number;
  /** Current queue size */
  queue_size: number;
  /** Number of active workers */
  active_workers: number;
}
