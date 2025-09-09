/**
 * Generated from OpenAPI schema: ABTestCreateRequest
 */
import { TestType } from './TestType';
import { VariantAllocation } from './VariantAllocation';
import { TestVariant } from './TestVariant';
import { MetricType } from './MetricType';

export interface ABTestCreateRequest {
  /** Test name */
  name: string;
  /** Test description */
  description: string;
  /** Type of test */
  test_type: TestType;
  /** Allocation strategy */
  allocation_strategy: VariantAllocation;
  /** Test variants */
  variants: TestVariant[];
  /** Metrics to track */
  metrics: MetricType[];
  /** Test duration in days */
  duration_days?: number;
  /** Minimum sample size */
  min_sample_size?: number;
  /** Statistical confidence level */
  confidence_level?: number;
  /** Target audience criteria */
  target_audience?: Record<string, unknown> | null;
  /** Percentage of traffic to include */
  traffic_percentage?: number;
  /** Test tags */
  tags?: string[];
  /** Additional metadata */
  metadata?: Record<string, unknown>;
}
