/**
 * Generated from OpenAPI schema: ABTestUpdateRequest
 */
import { TestStatus } from './TestStatus';

export interface ABTestUpdateRequest {
  /** Test name */
  name?: string | null;
  /** Test description */
  description?: string | null;
  /** Test status */
  status?: TestStatus | null;
  /** Test duration in days */
  duration_days?: number | null;
  /** Minimum sample size */
  min_sample_size?: number | null;
  /** Statistical confidence level */
  confidence_level?: number | null;
  /** Traffic percentage */
  traffic_percentage?: number | null;
  /** Test tags */
  tags?: string[] | null;
  /** Additional metadata */
  metadata?: Record<string, unknown> | null;
}
