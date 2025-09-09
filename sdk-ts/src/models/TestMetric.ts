/**
 * Generated from OpenAPI schema: TestMetric
 */
import { MetricType } from './MetricType';


export interface TestMetric {
  /** Type of metric */
  metric_type: MetricType;
  /** Variant name */
  variant_name: string;
  /** Metric value */
  value: number;
  /** Sample size */
  sample_size: number;
  /** 95% confidence interval */
  confidence_interval?: number[] | null;
}
