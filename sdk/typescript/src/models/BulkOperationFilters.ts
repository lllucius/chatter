/**
 * Generated from OpenAPI schema: BulkOperationFilters
 */
import { EntityType } from './EntityType';

export interface BulkOperationFilters {
  /** Type of entity to filter */
  entity_type: EntityType;
  /** Filter items created before this date */
  created_before?: string | null;
  /** Filter items created after this date */
  created_after?: string | null;
  /** Filter by user/owner ID */
  user_id?: string | null;
  /** Filter by status */
  status?: string | null;
  /** Maximum number of items to process */
  limit?: number;
  /** If true, only return count without deleting */
  dry_run?: boolean;
}
