/**
 * Generated from OpenAPI schema: DocumentChunkResponse
 */
export interface DocumentChunkResponse {
  /** Chunk ID */
  id: string;
  /** Document ID */
  document_id: string;
  /** Chunk content */
  content: string;
  /** Chunk index */
  chunk_index: number;
  /** Start character position */
  start_char?: number | null;
  /** End character position */
  end_char?: number | null;
  /** Chunk metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Token count */
  token_count?: number | null;
  /** Detected language */
  language?: string | null;
  /** Embedding model used */
  embedding_model?: string | null;
  /** Embedding provider */
  embedding_provider?: string | null;
  /** Embedding creation time */
  embedding_created_at?: string | null;
  /** Content hash */
  content_hash: string;
  /** Creation time */
  created_at: string;
  /** Last update time */
  updated_at: string;
}
