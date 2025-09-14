/**
 * Generated from OpenAPI schema: BulkDeletePreviewResponse
 */
import { BulkOperationFilters } from './BulkOperationFilters';
import { EntityType } from './EntityType';

export interface BulkDeletePreviewResponse {
  /** Entity type */
  entity_type: EntityType;
  /** Total items matching filters */
  total_matching: number;
  /** Sample of items that would be deleted (first 10) */
  sample_items: Record<string, unknown>[];
  /** Filters that were applied */
  filters_applied: BulkOperationFilters;
}
