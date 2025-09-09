/**
 * Generated from OpenAPI schema: DocumentSearchResponse
 */

export interface DocumentSearchResponse {
  /** Search results */
  results: DocumentSearchResult[];
  /** Total number of matching results */
  total_results: number;
  /** Original search query */
  query: string;
  /** Applied score threshold */
  score_threshold: number;
}
