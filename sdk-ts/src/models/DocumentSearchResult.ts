/**
 * Generated from OpenAPI schema: DocumentSearchResult
 */

export interface DocumentSearchResult {
  /** Document ID */
  document_id: string;
  /** Chunk ID */
  chunk_id: string;
  /** Similarity score */
  score: number;
  /** Matching content */
  content: string;
  /** Chunk metadata */
  metadata?: Record<string, unknown> | null;
  /** Document information */
  document: DocumentResponse;
}
