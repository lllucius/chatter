/**
 * Generated from OpenAPI schema: DocumentListResponse
 */
import { DocumentResponse } from './DocumentResponse';

export interface DocumentListResponse {
  /** List of documents */
  documents: DocumentResponse[];
  /** Total number of documents */
  total_count: number;
  /** Applied limit */
  limit: number;
  /** Applied offset */
  offset: number;
}
