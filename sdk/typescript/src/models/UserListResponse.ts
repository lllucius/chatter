/**
 * Generated from OpenAPI schema: UserListResponse
 */
import { UserResponse } from './UserResponse';

export interface UserListResponse {
  /** List of users */
  users: UserResponse[];
  /** Total number of users */
  total: number;
  /** Number of results skipped */
  offset: number;
  /** Number of results returned */
  limit: number;
}
