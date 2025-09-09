/**
 * Generated from OpenAPI schema: EmbeddingSpaceCreate
 */

export interface EmbeddingSpaceCreate {
  /** Unique space name */
  name: string;
  /** Human-readable name */
  display_name: string;
  /** Space description */
  description?: string | null;
  /** Original model dimensions */
  base_dimensions: number;
  /** Effective dimensions after reduction */
  effective_dimensions: number;
  /** Reduction strategy */
  reduction_strategy?: ReductionStrategy;
  /** Path to reducer file */
  reducer_path?: string | null;
  /** Reducer version/hash */
  reducer_version?: string | null;
  /** Whether to normalize vectors */
  normalize_vectors?: boolean;
  /** Distance metric */
  distance_metric?: DistanceMetric;
  /** Database table name */
  table_name: string;
  /** Index type */
  index_type?: string;
  /** Index configuration */
  index_config?: Record<string, unknown>;
  /** Whether space is active */
  is_active?: boolean;
  /** Whether this is the default space */
  is_default?: boolean;
  /** Model ID */
  model_id: string;
}
