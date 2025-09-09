/**
 * Generated from OpenAPI schema: ABTestResponse
 */
import { MetricType } from './MetricType';
import { TestStatus } from './TestStatus';
import { TestType } from './TestType';
import { TestVariant } from './TestVariant';
import { VariantAllocation } from './VariantAllocation';

export interface ABTestResponse {
  /** Test ID */
  id: string;
  /** Test name */
  name: string;
  /** Test description */
  description: string;
  /** Type of test */
  test_type: TestType;
  /** Test status */
  status: TestStatus;
  /** Allocation strategy */
  allocation_strategy: VariantAllocation;
  /** Test variants */
  variants: TestVariant[];
  /** Metrics being tracked */
  metrics: MetricType[];
  /** Test duration in days */
  duration_days: number;
  /** Minimum sample size */
  min_sample_size: number;
  /** Statistical confidence level */
  confidence_level: number;
  /** Target audience criteria */
  target_audience?: Record<string, unknown> | null;
  /** Percentage of traffic included */
  traffic_percentage: number;
  /** Test start date */
  start_date?: string | null;
  /** Test end date */
  end_date?: string | null;
  /** Number of participants */
  participant_count?: number;
  /** Creation timestamp */
  created_at: string;
  /** Last update timestamp */
  updated_at: string;
  /** Creator */
  created_by: string;
  /** Test tags */
  tags: string[];
  /** Additional metadata */
  metadata: Record<string, unknown>;
}
