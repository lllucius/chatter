/**
 * Generated from OpenAPI schema: TokenResponse
 */
import { UserResponse } from './UserResponse';

export interface TokenResponse {
  /** JWT access token */
  access_token: string;
  /** JWT refresh token */
  refresh_token?: string | null;
  /** Token type */
  token_type?: string;
  /** Token expiration time in seconds */
  expires_in: number;
  /** User information */
  user: UserResponse;
}
