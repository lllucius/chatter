/**
 * Generated from OpenAPI schema: AnalyticsExportResponse
 */
export interface AnalyticsExportResponse {
  /** Export job ID */
  export_id: string;
  /** Export status */
  status: string;
  /** Download URL when ready */
  download_url?: string | null;
  /** Export creation time */
  created_at: string;
  /** Download expiration time */
  expires_at?: string | null;
}
