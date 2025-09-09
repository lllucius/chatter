/**
 * Generated from OpenAPI schema: RestoreRequest
 */

export interface RestoreRequest {
  /** Backup ID to restore from */
  backup_id: string;
  /** Restore options */
  restore_options?: Record<string, unknown>;
  /** Create backup before restore */
  create_backup_before_restore?: boolean;
  /** Verify backup integrity before restore */
  verify_integrity?: boolean;
}
