/**
 * Generated from OpenAPI schema: DocumentProcessingRequest
 */
export interface DocumentProcessingRequest {
  /** Force reprocessing */
  reprocess?: boolean;
  /** Override chunk size */
  chunk_size?: number | null;
  /** Override chunk overlap */
  chunk_overlap?: number | null;
  /** Generate embeddings for chunks */
  generate_embeddings?: boolean;
}
