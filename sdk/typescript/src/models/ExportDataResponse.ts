/**
 * Generated from OpenAPI schema: ExportDataResponse
 */
export interface ExportDataResponse {
  /** Export ID */
  export_id: string;
  /** Export status */
  status: string;
  /** Download URL when ready */
  download_url?: string | null;
  /** File size in bytes */
  file_size?: number | null;
  /** Number of records exported */
  record_count?: number | null;
  /** Export creation timestamp */
  created_at: string;
  /** Export completion timestamp */
  completed_at?: string | null;
  /** Download link expiration */
  expires_at?: string | null;
}
