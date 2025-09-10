/**
 * Generated from OpenAPI schema: BackupResponse
 */
import { BackupType } from './BackupType';

export interface BackupResponse {
  /** Backup ID */
  id: string;
  /** Backup name */
  name: string;
  /** Backup description */
  description?: string | null;
  /** Backup type */
  backup_type: BackupType;
  /** Backup status */
  status: string;
  /** Backup file size in bytes */
  file_size?: number | null;
  /** Compressed size in bytes */
  compressed_size?: number | null;
  /** Number of records backed up */
  record_count?: number | null;
  /** Backup creation timestamp */
  created_at: string;
  /** Backup completion timestamp */
  completed_at?: string | null;
  /** Backup expiration timestamp */
  expires_at?: string | null;
  /** Whether backup is encrypted */
  encrypted: boolean;
  /** Whether backup is compressed */
  compressed: boolean;
  /** Backup metadata */
  metadata: Record<string, unknown>;
}
