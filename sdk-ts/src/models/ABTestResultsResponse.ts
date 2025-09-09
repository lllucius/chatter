/**
 * Generated from OpenAPI schema: ABTestResultsResponse
 */

export interface ABTestResultsResponse {
  /** Test ID */
  test_id: string;
  /** Test name */
  test_name: string;
  /** Test status */
  status: TestStatus;
  /** Metric results by variant */
  metrics: TestMetric[];
  /** Statistical significance by metric */
  statistical_significance: Record<string, boolean>;
  /** Confidence intervals */
  confidence_intervals: Record<string, Record<string, number[]>>;
  /** Recommended winning variant */
  winning_variant?: string | null;
  /** Action recommendation */
  recommendation: string;
  /** Results generation timestamp */
  generated_at: string;
  /** Total sample size */
  sample_size: number;
  /** Test duration so far */
  duration_days: number;
}
