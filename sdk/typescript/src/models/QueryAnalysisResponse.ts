/**
 * Generated from OpenAPI schema: QueryAnalysisResponse
 */
export interface QueryAnalysisResponse {
  /** Total queries analyzed */
  total_queries_analyzed: number;
  /** Number of slow queries */
  slow_queries_count: number;
  /** Optimization suggestions */
  optimization_suggestions: string[];
  /** Average execution time in milliseconds */
  average_execution_time_ms: number;
  /** Most expensive queries */
  most_expensive_queries: Record<string, unknown>[];
  /** Index recommendations */
  index_recommendations: string[];
}
