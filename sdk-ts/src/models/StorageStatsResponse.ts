/**
 * Generated from OpenAPI schema: StorageStatsResponse
 */

export interface StorageStatsResponse {
  /** Total storage used in bytes */
  total_size: number;
  /** Database size in bytes */
  database_size: number;
  /** Uploaded files size in bytes */
  files_size: number;
  /** Backups size in bytes */
  backups_size: number;
  /** Exports size in bytes */
  exports_size: number;
  /** Total number of records */
  total_records: number;
  /** Total number of files */
  total_files: number;
  /** Total number of backups */
  total_backups: number;
  /** Storage usage by data type */
  storage_by_type: Record<string, number>;
  /** Storage usage by user */
  storage_by_user: Record<string, number>;
  /** Storage growth rate in MB per day */
  growth_rate_mb_per_day: number;
  /** Projected size in 30 days */
  projected_size_30_days: number;
  /** Statistics last updated timestamp */
  last_updated: string;
}
