/**
 * Generated from OpenAPI schema: ABTestMetricsResponse
 */

export interface ABTestMetricsResponse {
  /** Test ID */
  test_id: string;
  /** Current metrics */
  metrics: TestMetric[];
  /** Current participant count */
  participant_count: number;
  /** Last metrics update */
  last_updated: string;
}
