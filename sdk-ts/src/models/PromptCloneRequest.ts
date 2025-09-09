/**
 * Generated from OpenAPI schema: PromptCloneRequest
 */

export interface PromptCloneRequest {
  /** New prompt name */
  name: string;
  /** New prompt description */
  description?: string | null;
  /** Modifications to apply */
  modifications?: Record<string, unknown> | null;
}
