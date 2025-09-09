/**
 * Generated from OpenAPI schema: DocumentResponse
 */
import { DocumentStatus } from './DocumentStatus';


export interface DocumentResponse {
  /** Document title */
  title?: string | null;
  /** Document description */
  description?: string | null;
  /** Document tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Whether document is public */
  is_public?: boolean;
  /** Document ID */
  id: string;
  /** Owner user ID */
  owner_id: string;
  /** Document filename */
  filename: string;
  /** Original filename */
  original_filename: string;
  /** File size in bytes */
  file_size: number;
  /** File hash (SHA-256) */
  file_hash: string;
  /** MIME type */
  mime_type: string;
  /** Document type */
  document_type: DocumentType;
  /** Processing status */
  status: DocumentStatus;
  /** Processing start time */
  processing_started_at?: string | null;
  /** Processing completion time */
  processing_completed_at?: string | null;
  /** Processing error message */
  processing_error?: string | null;
  /** Chunk size */
  chunk_size: number;
  /** Chunk overlap */
  chunk_overlap: number;
  /** Number of chunks */
  chunk_count: number;
  /** Document version */
  version: number;
  /** Parent document ID */
  parent_document_id?: string | null;
  /** View count */
  view_count: number;
  /** Search count */
  search_count: number;
  /** Last access time */
  last_accessed_at?: string | null;
  /** Creation time */
  created_at: string;
  /** Last update time */
  updated_at: string;
}
