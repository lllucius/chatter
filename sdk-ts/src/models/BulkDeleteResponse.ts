/**
 * Generated from OpenAPI schema: BulkDeleteResponse
 */

export interface BulkDeleteResponse {
  /** Total number of items requested for deletion */
  total_requested: number;
  /** Number of successful deletions */
  successful_deletions: number;
  /** Number of failed deletions */
  failed_deletions: number;
  /** List of error messages for failed deletions */
  errors: string[];
}
