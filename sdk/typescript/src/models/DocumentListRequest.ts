/**
 * Generated from OpenAPI schema: DocumentListRequest
 */
import { DocumentStatus } from './DocumentStatus';
import { DocumentType } from './DocumentType';

export interface DocumentListRequest {
  /** Filter by status */
  status?: DocumentStatus | null;
  /** Filter by document type */
  document_type?: DocumentType | null;
  /** Filter by tags */
  tags?: string[] | null;
  /** Filter by owner (admin only) */
  owner_id?: string | null;
  /** Maximum number of results */
  limit?: number;
  /** Number of results to skip */
  offset?: number;
  /** Sort field */
  sort_by?: string;
  /** Sort order */
  sort_order?: string;
}
