/**
 * Generated from OpenAPI schema: TokenRefreshResponse
 */
export interface TokenRefreshResponse {
  /** New access token */
  access_token: string;
  /** New refresh token (may be sent as HttpOnly cookie) */
  refresh_token?: string | null;
  /** Token type */
  token_type?: string;
  /** Token expiration time in seconds */
  expires_in: number;
}
