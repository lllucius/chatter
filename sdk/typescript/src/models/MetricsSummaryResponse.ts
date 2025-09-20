/**
 * Generated from OpenAPI schema: MetricsSummaryResponse
 */
export interface MetricsSummaryResponse {
  /** Total number of metrics */
  total_metrics: number;
  /** Number of active metrics */
  active_metrics: number;
  /** Data points collected in last hour */
  data_points_last_hour: number;
  /** Storage size in MB */
  storage_size_mb: number;
  /** Oldest data point timestamp */
  oldest_data_point?: string | null;
  /** Latest data point timestamp */
  latest_data_point?: string | null;
}
