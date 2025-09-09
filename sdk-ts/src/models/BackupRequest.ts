/**
 * Generated from OpenAPI schema: BackupRequest
 */

export interface BackupRequest {
  /** Backup type */
  backup_type?: BackupType;
  /** Backup name */
  name?: string | null;
  /** Backup description */
  description?: string | null;
  /** Include uploaded files */
  include_files?: boolean;
  /** Include system logs */
  include_logs?: boolean;
  /** Compress backup */
  compress?: boolean;
  /** Encrypt backup */
  encrypt?: boolean;
  /** Backup retention in days */
  retention_days?: number;
}
