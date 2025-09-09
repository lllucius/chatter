/**
 * Generated from OpenAPI schema: OptimizationSuggestion
 */

export interface OptimizationSuggestion {
  /** Suggestion type */
  type: string;
  /** Suggestion description */
  description: string;
  /** Expected impact (low/medium/high) */
  impact: string;
  /** Affected node IDs */
  node_ids?: string[] | null;
}
