/**
 * Generated from OpenAPI schema: BulkToolServerOperation
 */

export interface BulkToolServerOperation {
  /** List of server IDs */
  server_ids: string[];
  /** Operation to perform */
  operation: string;
  /** Operation parameters */
  parameters?: Record<string, unknown> | null;
}
