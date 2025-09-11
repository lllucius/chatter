/**
 * Generated API client for Authentication
 */
import { APIKeyCreate, APIKeyResponse, APIKeyRevokeResponse, AccountDeactivateResponse, LogoutResponse, PasswordChange, PasswordChangeResponse, PasswordResetConfirmResponse, PasswordResetRequestResponse, TokenRefreshResponse, TokenResponse, UserCreate, UserLogin, UserResponse, UserUpdate } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/register`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<TokenResponse>;
  }
  /**Login
   * Authenticate user and return tokens with enhanced security.

Args:
    user_data: User login data
    request: HTTP request for security logging
    response: HTTP response for cookie setting
    auth_service: Authentication service

Returns:
    User data and authentication tokens
   */
  public async authLogin(data: UserLogin): Promise<TokenResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/login`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<TokenResponse>;
  }
  /**Refresh Token
   * Refresh access token with enhanced security validation.

Args:
    request: HTTP request for security logging and cookie reading
    response: HTTP response for setting new refresh token cookie
    auth_service: Authentication service

Returns:
    New access token (refresh token set in HttpOnly cookie)
   */
  public async refreshTokenApiV1AuthRefresh(): Promise<TokenRefreshResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/refresh`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<TokenRefreshResponse>;
  }
  /**Get Current User Info
   * Get current user information.

Args:
    current_user: Current authenticated user

Returns:
    Current user data
   */
  public async getCurrentUserInfoApiV1AuthMe(): Promise<UserResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/me`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<UserResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/me`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<UserResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/change-password`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PasswordChangeResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/api-key`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<APIKeyResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/api-key`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<APIKeyRevokeResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/api-keys`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<APIKeyResponse[]>;
  }
  /**Logout
   * Logout and revoke current token with enhanced security.

Args:
    request: HTTP request for security logging
    response: HTTP response for cookie clearing
    current_user: Current authenticated user
    auth_service: Authentication service

Returns:
    Success message
   */
  public async authLogout(): Promise<LogoutResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/logout`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<LogoutResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/password-reset/request`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'email': options?.email,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PasswordResetRequestResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/password-reset/confirm`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'token': options?.token,
        'new_password': options?.newPassword,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PasswordResetConfirmResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/auth/account`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AccountDeactivateResponse>;
  }
}