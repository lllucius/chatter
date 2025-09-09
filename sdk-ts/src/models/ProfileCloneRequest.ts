/**
 * Generated from OpenAPI schema: ProfileCloneRequest
 */

export interface ProfileCloneRequest {
  /** New profile name */
  name: string;
  /** New profile description */
  description?: string | null;
  /** Modifications to apply to cloned profile */
  modifications?: ProfileUpdate | null;
}
