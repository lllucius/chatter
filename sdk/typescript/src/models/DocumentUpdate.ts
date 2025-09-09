/**
 * Generated from OpenAPI schema: DocumentUpdate
 */
export interface DocumentUpdate {
  /** Document title */
  title?: string | null;
  /** Document description */
  description?: string | null;
  /** Document tags */
  tags?: string[] | null;
  /** Additional metadata */
  extra_metadata?: Record<string, unknown> | null;
  /** Whether document is public */
  is_public?: boolean | null;
}
