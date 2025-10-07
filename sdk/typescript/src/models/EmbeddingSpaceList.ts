/**
 * Generated from OpenAPI schema: EmbeddingSpaceList
 */
import { EmbeddingSpaceWithModel } from './EmbeddingSpaceWithModel';

export interface EmbeddingSpaceList {
  spaces: EmbeddingSpaceWithModel[];
  total: number;
  limit: number;
  offset: number;
}
