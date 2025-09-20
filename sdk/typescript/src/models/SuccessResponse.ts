/**
 * Generated from OpenAPI schema: SuccessResponse
 */
export interface SuccessResponse {
  /** Success indicator */
  success?: boolean;
  /** Success message */
  message: string;
  /** Response data */
  data?: Record<string, unknown> | null;
}
