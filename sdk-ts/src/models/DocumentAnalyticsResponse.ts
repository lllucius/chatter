/**
 * Generated from OpenAPI schema: DocumentAnalyticsResponse
 */

export interface DocumentAnalyticsResponse {
  /** Total number of documents */
  total_documents: number;
  /** Documents by processing status */
  documents_by_status: Record<string, number>;
  /** Documents by file type */
  documents_by_type: Record<string, number>;
  /** Average processing time */
  avg_processing_time_seconds: number;
  /** Processing success rate */
  processing_success_rate: number;
  /** Total number of chunks */
  total_chunks: number;
  /** Average chunks per document */
  avg_chunks_per_document: number;
  /** Total storage used */
  total_storage_bytes: number;
  /** Average document size */
  avg_document_size_bytes: number;
  /** Storage usage by document type */
  storage_by_type: Record<string, number>;
  /** Total number of searches */
  total_searches: number;
  /** Average search results returned */
  avg_search_results: number;
  /** Popular search terms */
  popular_search_terms: Record<string, number>;
  /** Total document views */
  total_views: number;
  /** Most viewed documents */
  most_viewed_documents: Record<string, unknown>[];
  /** Documents by access level */
  documents_by_access_level: Record<string, number>;
}
