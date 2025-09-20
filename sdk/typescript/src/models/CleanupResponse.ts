/**
 * Generated from OpenAPI schema: CleanupResponse
 */
export interface CleanupResponse {
  /** Cleanup operation type */
  operation: string;
  /** Number of items cleaned */
  items_cleaned: number;
  /** Storage freed in MB */
  storage_freed_mb: number;
  /** Operation duration in seconds */
  duration_seconds: number;
  /** Operation result message */
  message: string;
}
