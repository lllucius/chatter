/**
 * Generated from OpenAPI schema: ABTestAnalyticsResponse
 */
import { StatisticalAnalysis } from './StatisticalAnalysis';
import { TestStatus } from './TestStatus';
import { VariantPerformance } from './VariantPerformance';

export interface ABTestAnalyticsResponse {
  /** Test ID */
  test_id: string;
  /** Test name */
  test_name: string;
  /** Test status */
  status: TestStatus;
  /** Total participants */
  total_participants: number;
  /** Variant performance data */
  variants: VariantPerformance[];
  /** Statistical analysis results */
  statistical_analysis: StatisticalAnalysis;
  /** Winning variant */
  winner?: string | null;
  /** Improvement percentage */
  improvement?: number | null;
  /** Recommendation */
  recommendation: string;
  /** Days test has been running */
  duration_days: number;
  /** Days remaining */
  remaining_days?: number | null;
  /** Test progress percentage */
  progress_percentage: number;
  /** Analytics generation timestamp */
  generated_at: string;
  /** Last data update */
  last_updated: string;
}
