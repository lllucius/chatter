/**
 * Generated from OpenAPI schema: EmbeddingSpaceUpdate
 */
import { DistanceMetric } from './DistanceMetric';
import { ReductionStrategy } from './ReductionStrategy';

export interface EmbeddingSpaceUpdate {
  display_name?: string | null;
  description?: string | null;
  reduction_strategy?: ReductionStrategy | null;
  reducer_path?: string | null;
  reducer_version?: string | null;
  normalize_vectors?: boolean | null;
  distance_metric?: DistanceMetric | null;
  index_type?: string | null;
  index_config?: Record<string, unknown> | null;
  is_active?: boolean | null;
  is_default?: boolean | null;
}
