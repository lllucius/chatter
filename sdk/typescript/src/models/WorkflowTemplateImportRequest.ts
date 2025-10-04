/**
 * Chatter API
 * Advanced AI Chatbot Backend API Platform
 */

export interface WorkflowTemplateImportRequest {
  template: Record<string, any>;
  override_name?: string | null;
  merge_with_existing?: boolean;
}
