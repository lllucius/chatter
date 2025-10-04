/**
 * Generated from OpenAPI schema: WorkflowTemplateExportResponse
 */
export interface WorkflowTemplateExportResponse {
  /** Complete template data including metadata */
  template: Record<string, unknown>;
  /** Export format version */
  export_format?: string;
  /** Export timestamp */
  exported_at: string;
}
