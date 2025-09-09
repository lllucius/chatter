/**
 * Generated from OpenAPI schema: DocumentSearchRequest
 */

export interface DocumentSearchRequest {
  /** Search query */
  query: string;
  /** Maximum number of results */
  limit?: number;
  /** Minimum similarity score */
  score_threshold?: number;
  /** Filter by document types */
  document_types?: DocumentType[] | null;
  /** Filter by tags */
  tags?: string[] | null;
  /** Include document content in results */
  include_content?: boolean;
}
