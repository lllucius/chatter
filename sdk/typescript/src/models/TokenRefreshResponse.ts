/**
 * Generated from OpenAPI schema: TokenRefreshResponse
 */
export interface TokenRefreshResponse {
  /** New access token */
  access_token: string;
  /** New refresh token */
  refresh_token: string;
  /** Token type */
  token_type?: string;
  /** Token expiration time in seconds */
  expires_in: number;
}
