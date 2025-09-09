/**
 * Generated API client for Authentication
 */
import { APIKeyCreate, APIKeyResponse, APIKeyRevokeResponse, AccountDeactivateResponse, LogoutResponse, PasswordChange, PasswordChangeResponse, PasswordResetConfirmResponse, PasswordResetRequestResponse, TokenRefresh, TokenRefreshResponse, TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate } from '../models/index';
import { BaseAPI, Configuration, HTTPQuery, HTTPHeaders } from '../runtime';

export class AuthenticationApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Register
   * Register a new user with enhanced security validation.

Args:
    user_data: User registration data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    User data and authentication tokens
   */
  public async authRegister(data: UserCreate): Promise<TokenResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<TokenResponse>(`/api/v1/auth/register`, requestOptions);
  }
  /**Login
   * Authenticate user and return tokens with enhanced security.

Args:
    user_data: User login data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    User data and authentication tokens
   */
  public async authLogin(data: UserLogin): Promise<TokenResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<TokenResponse>(`/api/v1/auth/login`, requestOptions);
  }
  /**Refresh Token
   * Refresh access token with enhanced security validation.

Args:
    token_data: Refresh token data
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    New access and refresh tokens
   */
  public async refreshTokenApiV1AuthRefresh(data: TokenRefresh): Promise<TokenRefreshResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<TokenRefreshResponse>(`/api/v1/auth/refresh`, requestOptions);
  }
  /**Get Current User Info
   * Get current user information.

Args:
    current_user: Current authenticated user

Returns:
    Current user data
   */
  public async getCurrentUserInfoApiV1AuthMe(): Promise<UserResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<UserResponse>(`/api/v1/auth/me`, requestOptions);
  }
  /**Update Profile
   * Update current user profile.

Args:
    user_data: Profile update data
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Updated user data
   */
  public async updateProfileApiV1AuthMe(data: UserUpdate): Promise<UserResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<UserResponse>(`/api/v1/auth/me`, requestOptions);
  }
  /**Change Password
   * Change user password with enhanced security logging.

Args:
    password_data: Password change data
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message
   */
  public async changePasswordApiV1AuthChangePassword(data: PasswordChange): Promise<PasswordChangeResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<PasswordChangeResponse>(`/api/v1/auth/change-password`, requestOptions);
  }
  /**Create Api Key
   * Create API key for current user with enhanced security.

Args:
    key_data: API key creation data
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Created API key
   */
  public async createApiKeyApiV1AuthApiKey(data: APIKeyCreate): Promise<APIKeyResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<APIKeyResponse>(`/api/v1/auth/api-key`, requestOptions);
  }
  /**Revoke Api Key
   * Revoke current user's API key with security logging.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message
   */
  public async revokeApiKeyApiV1AuthApiKey(): Promise<APIKeyRevokeResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<APIKeyRevokeResponse>(`/api/v1/auth/api-key`, requestOptions);
  }
  /**List Api Keys
   * List user's API keys.

Args:
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    List of API keys
   */
  public async listApiKeysApiV1AuthApiKeys(): Promise<APIKeyResponse[]> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<APIKeyResponse[]>(`/api/v1/auth/api-keys`, requestOptions);
  }
  /**Logout
   * Logout and revoke current token with enhanced security.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message
   */
  public async authLogout(): Promise<LogoutResponse> {
    const requestOptions = {
      method: 'POST' as const,
    };

    return this.request<LogoutResponse>(`/api/v1/auth/logout`, requestOptions);
  }
  /**Request Password Reset
   * Request password reset with enhanced security logging.

Args:
    email: User email
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    Success message
   */
  public async requestPasswordResetApiV1AuthPasswordResetRequest(options?: { email?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PasswordResetRequestResponse> {
    const requestOptions = {
      method: 'POST' as const,
      headers: options?.headers,
      query: {
        'email': options?.email,
        ...options?.query
      },
    };

    return this.request<PasswordResetRequestResponse>(`/api/v1/auth/password-reset/request`, requestOptions);
  }
  /**Confirm Password Reset
   * Confirm password reset with enhanced security logging.

Args:
    token: Reset token
    new_password: New password
    request: HTTP request for security logging
    auth_service: Authentication service

Returns:
    Success message
   */
  public async confirmPasswordResetApiV1AuthPasswordResetConfirm(options?: { token?: string; newPassword?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PasswordResetConfirmResponse> {
    const requestOptions = {
      method: 'POST' as const,
      headers: options?.headers,
      query: {
        'token': options?.token,
        'new_password': options?.newPassword,
        ...options?.query
      },
    };

    return this.request<PasswordResetConfirmResponse>(`/api/v1/auth/password-reset/confirm`, requestOptions);
  }
  /**Deactivate Account
   * Deactivate current user account with enhanced security logging.

Args:
    request: HTTP request for security logging
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message
   */
  public async deactivateAccountApiV1AuthAccount(): Promise<AccountDeactivateResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<AccountDeactivateResponse>(`/api/v1/auth/account`, requestOptions);
  }
}