/**
 * Generated from OpenAPI schema: UserResponse
 */

export interface UserResponse {
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
  /** User ID */
  id: string;
  /** Is user active */
  is_active: boolean;
  /** Is user email verified */
  is_verified: boolean;
  /** Is user a superuser */
  is_superuser: boolean;
  /** Default LLM provider */
  default_llm_provider?: string | null;
  /** Default profile ID */
  default_profile_id?: string | null;
  /** Daily message limit */
  daily_message_limit?: number | null;
  /** Monthly message limit */
  monthly_message_limit?: number | null;
  /** Max file size in MB */
  max_file_size_mb?: number | null;
  /** API key name */
  api_key_name?: string | null;
  /** Account creation date */
  created_at: string;
  /** Last update date */
  updated_at: string;
  /** Last login date */
  last_login_at?: string | null;
}
