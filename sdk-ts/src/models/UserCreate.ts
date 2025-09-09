/**
 * Generated from OpenAPI schema: UserCreate
 */
export interface UserCreate {
  /** User email address */
  email: string;
  /** Username */
  username: string;
  /** Full name */
  full_name?: string | null;
  /** User bio */
  bio?: string | null;
  /** Avatar URL */
  avatar_url?: string | null;
  /** Phone number */
  phone_number?: string | null;
  /** Password */
  password: string;
}
