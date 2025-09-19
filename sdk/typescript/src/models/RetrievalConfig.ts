/**
 * Generated from OpenAPI schema: RetrievalConfig
 */
export interface RetrievalConfig {
  /** Enable retrieval */
  enabled?: boolean;
  /** Max documents to retrieve */
  max_documents?: number;
  /** Similarity threshold */
  similarity_threshold?: number;
  /** Specific document IDs */
  document_ids?: string[] | null;
  /** Document collections */
  collections?: string[] | null;
  /** Enable reranking */
  rerank?: boolean;
}
