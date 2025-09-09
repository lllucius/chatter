/**
 * Generated from OpenAPI schema: BackupListResponse
 */
import { BackupResponse } from './BackupResponse';


export interface BackupListResponse {
  /** List of backups */
  backups: BackupResponse[];
  /** Total number of backups */
  total: number;
}
