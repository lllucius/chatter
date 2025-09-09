/**
 * Generated from OpenAPI schema: UserLogin
 */
export interface UserLogin {
  /** User email address */
  email?: string | null;
  /** Username */
  username?: string | null;
  /** Password */
  password: string;
  /** Remember login */
  remember_me?: boolean;
}
