/**
 * Generated from OpenAPI schema: ExportDataRequest
 */
import { DataFormat } from './DataFormat';
import { ExportScope } from './ExportScope';

export interface ExportDataRequest {
  /** Export scope */
  scope: ExportScope;
  /** Export format */
  format?: DataFormat;
  /** Filter by user ID */
  user_id?: string | null;
  /** Filter by conversation ID */
  conversation_id?: string | null;
  /** Filter from date */
  date_from?: string | null;
  /** Filter to date */
  date_to?: string | null;
  /** Include metadata */
  include_metadata?: boolean;
  /** Compress export file */
  compress?: boolean;
  /** Encrypt export file */
  encrypt?: boolean;
  /** Custom export query */
  custom_query?: Record<string, unknown> | null;
}
