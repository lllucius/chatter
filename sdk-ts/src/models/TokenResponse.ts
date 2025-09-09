/**
 * Generated from OpenAPI schema: TokenResponse
 */

export interface TokenResponse {
  /** JWT access token */
  access_token: string;
  /** JWT refresh token */
  refresh_token: string;
  /** Token type */
  token_type?: string;
  /** Token expiration time in seconds */
  expires_in: number;
  /** User information */
  user: UserResponse;
}
