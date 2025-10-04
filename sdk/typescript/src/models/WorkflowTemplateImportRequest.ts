/**
 * Generated from OpenAPI schema: WorkflowTemplateImportRequest
 */
export interface WorkflowTemplateImportRequest {
  /** Template data to import */
  template: Record<string, unknown>;
  /** Optional name override for imported template */
  override_name?: string | null;
  /** Whether to merge with existing template if found */
  merge_with_existing?: boolean;
}
