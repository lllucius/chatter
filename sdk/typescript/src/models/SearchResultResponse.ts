/**
 * Generated from OpenAPI schema: SearchResultResponse
 */
export interface SearchResultResponse {
  /** Chunk ID */
  chunk_id: string;
  /** Document ID */
  document_id: string;
  /** Matching content */
  content: string;
  /** Similarity score */
  similarity_score: number;
  /** Document title */
  document_title?: string | null;
  /** Document filename */
  document_filename: string;
  /** Chunk index */
  chunk_index: number;
}
