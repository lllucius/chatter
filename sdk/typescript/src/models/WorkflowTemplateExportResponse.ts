/**
 * Chatter API
 * Advanced AI Chatbot Backend API Platform
 */

export interface WorkflowTemplateExportResponse {
  template: Record<string, any>;
  export_format?: string;
  exported_at: string;
}
