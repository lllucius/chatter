/**
 * Generated from OpenAPI schema: ABTestActionResponse
 */

export interface ABTestActionResponse {
  /** Whether action was successful */
  success: boolean;
  /** Action result message */
  message: string;
  /** Test ID */
  test_id: string;
  /** New test status */
  new_status: TestStatus;
}
