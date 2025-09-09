/**
 * Generated from OpenAPI schema: DocumentChunksResponse
 */

export interface DocumentChunksResponse {
  /** List of document chunks */
  chunks: DocumentChunkResponse[];
  /** Total number of chunks */
  total_count: number;
  /** Applied limit */
  limit: number;
  /** Applied offset */
  offset: number;
}
