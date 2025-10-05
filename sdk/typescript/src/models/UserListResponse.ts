/**
 * Generated from OpenAPI schema: UserListResponse
 */
import { UserResponse } from './UserResponse';

export interface UserListResponse {
  /** List of users */
  users: UserResponse[];
  /** Total number of users */
  total: number;
  /** Current page number */
  page: number;
  /** Number of users per page */
  page_size: number;
}
