/**
 * Generated from OpenAPI schema: BulkOperationResult
 */
export interface BulkOperationResult {
  /** Total servers requested */
  total_requested: number;
  /** Successfully processed */
  successful: number;
  /** Failed to process */
  failed: number;
  /** Detailed results */
  results: Record<string, unknown>[];
  /** Error messages */
  errors?: string[];
}
