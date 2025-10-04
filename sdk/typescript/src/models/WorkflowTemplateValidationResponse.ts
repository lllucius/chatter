/**
 * Chatter API
 * Advanced AI Chatbot Backend API Platform
 */

export interface WorkflowTemplateValidationResponse {
  is_valid: boolean;
  errors?: string[];
  warnings?: string[];
  template_info?: Record<string, any> | null;
}
