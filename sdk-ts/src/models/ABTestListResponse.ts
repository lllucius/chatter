/**
 * Generated from OpenAPI schema: ABTestListResponse
 */
import { ABTestResponse } from './ABTestResponse';

export interface ABTestListResponse {
  /** List of tests */
  tests: ABTestResponse[];
  /** Total number of tests */
  total: number;
}
