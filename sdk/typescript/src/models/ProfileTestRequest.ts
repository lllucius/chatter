/**
 * Generated from OpenAPI schema: ProfileTestRequest
 */
export interface ProfileTestRequest {
  /** Test message */
  test_message: string;
  /** Include retrieval in test */
  include_retrieval?: boolean;
  /** Include tools in test */
  include_tools?: boolean;
}
