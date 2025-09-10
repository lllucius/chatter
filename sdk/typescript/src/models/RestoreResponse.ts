/**
 * Generated from OpenAPI schema: RestoreResponse
 */
export interface RestoreResponse {
  /** Restore operation ID */
  restore_id: string;
  /** Source backup ID */
  backup_id: string;
  /** Restore status */
  status: string;
  /** Restore progress percentage */
  progress?: number;
  /** Number of records restored */
  records_restored?: number;
  /** Restore start timestamp */
  started_at: string;
  /** Restore completion timestamp */
  completed_at?: string | null;
  /** Error message if failed */
  error_message?: string | null;
}
