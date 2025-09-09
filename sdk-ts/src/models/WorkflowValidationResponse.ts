/**
 * Generated from OpenAPI schema: WorkflowValidationResponse
 */
import { ValidationError } from './ValidationError';

export interface WorkflowValidationResponse {
  /** Whether workflow is valid */
  is_valid: boolean;
  /** Validation errors */
  errors: ValidationError[];
  /** Validation warnings */
  warnings: ValidationError[];
  /** Validation suggestions */
  suggestions: string[];
}
