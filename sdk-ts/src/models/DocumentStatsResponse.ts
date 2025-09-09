/**
 * Generated from OpenAPI schema: DocumentStatsResponse
 */

export interface DocumentStatsResponse {
  /** Total number of documents */
  total_documents: number;
  /** Total number of chunks */
  total_chunks: number;
  /** Total size in bytes */
  total_size_bytes: number;
  /** Documents grouped by status */
  documents_by_status: Record<string, number>;
  /** Documents grouped by type */
  documents_by_type: Record<string, number>;
  /** Processing statistics */
  processing_stats: Record<string, unknown>;
}
