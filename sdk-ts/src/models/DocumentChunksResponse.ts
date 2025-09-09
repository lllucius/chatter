/**
 * Generated from OpenAPI schema: DocumentChunksResponse
 */
import { DocumentChunkResponse } from './DocumentChunkResponse';


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
