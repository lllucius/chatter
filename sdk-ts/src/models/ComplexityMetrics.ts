/**
 * Generated from OpenAPI schema: ComplexityMetrics
 */

export interface ComplexityMetrics {
  /** Overall complexity score */
  score: number;
  /** Number of nodes */
  node_count: number;
  /** Number of edges */
  edge_count: number;
  /** Maximum path depth */
  depth: number;
  /** Average branching factor */
  branching_factor: number;
  /** Loop complexity score */
  loop_complexity?: number;
  /** Conditional complexity score */
  conditional_complexity?: number;
}
