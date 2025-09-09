/**
 * Generated from OpenAPI schema: DocumentProcessingResponse
 */

export interface DocumentProcessingResponse {
  /** Document ID */
  document_id: string;
  /** Processing status */
  status: DocumentStatus;
  /** Status message */
  message: string;
  /** Processing start time */
  processing_started_at?: string | null;
}
