/**
 * Authentication service using ChatterSDK directly
 * Manages tokens and provides authenticated SDK instances
 * Uses memory for access tokens and HttpOnly cookies for refresh tokens
 */
import { ChatterSDK, UserLogin } from 'chatter-sdk';
import { handleError } from '../utils/error-handler';

class AuthService {
  private token: string | null = null; // Store access token in memory only
  private baseSDK: ChatterSDK;
  private basePath: string; // Store base path to avoid repeated withConfig calls
  private initialized: boolean = false;
  private refreshInProgress: boolean = false; // Prevent multiple concurrent refresh attempts

  constructor() {
    this.basePath =
      import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    this.baseSDK = new ChatterSDK({
      basePath: this.basePath,
      credentials: 'include', // Include cookies for refresh token
    } as any); // ChatterSDK configuration type mismatch with our needs
    // Don't call initialize() in constructor anymore - it's async now
  }

  /**
   * Initialize the auth service
   * Attempts to restore authentication state from refresh token cookie
   */
  public async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    // Try to restore authentication state from refresh token cookie
    if (!this.token) {
      await this.refreshToken();
    }

    this.initialized = true;
  }

  public isAuthenticated(): boolean {
    return !!this.token;
  }

  public getToken(): string | null {
    return this.token;
  }

  public isInitialized(): boolean {
    return this.initialized;
  }

  public getSDK(): ChatterSDK {
    if (!this.initialized) {
      throw new Error(
        'SDK not initialized. Please wait for initialization to complete.'
      );
    }

    let sdk: ChatterSDK;
    if (this.token) {
      sdk = this.baseSDK.withAuth(this.token, 'bearer');
    } else {
      sdk = this.baseSDK;
    }

    // Verify the SDK is properly constructed with all expected APIs
    if (!sdk || !sdk.conversations || !sdk.workflows) {
      throw new Error('SDK not properly initialized. Please reload the page.');
    }

    return sdk;
  }

  public async login(username: string, password: string): Promise<void> {
    try {
      const loginData: UserLogin = {
        username,
        password,
      };

      const response = await this.baseSDK.auth.authLogin(loginData);

      if (response.access_token) {
        this.token = response.access_token; // Store in memory only
        // Refresh token is automatically stored in HttpOnly cookie by the server
        // No need to manually handle refresh token storage
      } else {
        throw new Error('No access token received');
      }
    } catch (error: unknown) {
      // Use standardized error handling
      handleError(
        error,
        {
          source: 'AuthService.login',
          operation: 'user authentication',
          additionalData: { username },
        },
        {
          showToast: false, // Let the calling component handle the UI
          rethrow: true,
        }
      );
    }
  }

  public async logout(): Promise<void> {
    try {
      if (this.isAuthenticated()) {
        await getSDK().auth.authLogout();
      }
    } catch (error) {
      // Use standardized error handling for logout failures
      handleError(
        error,
        {
          source: 'AuthService.logout',
          operation: 'user logout',
        },
        {
          showToast: false, // Don't interrupt logout flow with error toast
          logToConsole: true,
        }
      );
      // Continue with local logout even if API call fails
    } finally {
      this.clearToken();
    }
  }

  public async refreshToken(): Promise<boolean> {
    if (this.refreshInProgress) {
      // Wait for the current refresh to complete
      return new Promise((resolve) => {
        const checkRefresh = () => {
          if (!this.refreshInProgress) {
            resolve(this.isAuthenticated());
          } else {
            setTimeout(checkRefresh, 100);
          }
        };
        checkRefresh();
      });
    }

    this.refreshInProgress = true;

    try {
      // The actual refresh token is in HttpOnly cookie
      // and will be sent automatically with credentials: 'include'
      const response = await this.baseSDK.auth.refreshTokenApiV1AuthRefresh();

      if (response.access_token) {
        this.token = response.access_token; // Store in memory only

        // New refresh token is automatically set in HttpOnly cookie by server
        return true;
      }

      return false;
    } catch (error) {
      // Use standardized error handling for refresh failures
      handleError(
        error,
        {
          source: 'AuthService.refreshToken',
          operation: 'token refresh',
        },
        {
          showToast: false, // Don't show toast for automatic token refresh failures
          logToConsole: true,
        }
      );
      this.clearToken();
      return false;
    } finally {
      this.refreshInProgress = false;
    }
  }

  private clearToken() {
    this.token = null;
    // No localStorage cleanup needed - tokens are memory-only now
    // HttpOnly refresh token cookie will be cleared by server on logout
  }

  public getURL(): string | null {
    // Return stored base path instead of creating new SDK instance
    return this.basePath;
  }

  /**
   * Get the current SDK configuration (for debugging/inspection)
   */
  public getSDKInfo(): {
    basePath: string | undefined;
    hasToken: boolean;
    initialized: boolean;
  } {
    return {
      basePath: this.basePath,
      hasToken: !!this.token,
      initialized: this.initialized,
    };
  }

  /**
   * Execute an authenticated API request with automatic token refresh
   * This method will automatically refresh the token if the request fails with 401
   */
  public async executeWithAuth<T>(
    apiCall: (sdk: ChatterSDK) => Promise<T>
  ): Promise<T> {
    const sdk = this.getSDK();

    try {
      return await apiCall(sdk);
    } catch (error: unknown) {
      // Check if it's an authentication error (401)
      const isAuthError =
        (error &&
          typeof error === 'object' &&
          'status' in error &&
          error.status === 401) ||
        (error &&
          typeof error === 'object' &&
          'response' in error &&
          error.response &&
          typeof error.response === 'object' &&
          'status' in error.response &&
          error.response.status === 401);

      if (isAuthError) {
        const refreshSuccess = await this.refreshToken();
        if (refreshSuccess) {
          const refreshedSDK = this.getSDK();
          return await apiCall(refreshedSDK);
        } else {
          throw new Error('Authentication failed - please login again');
        }
      }

      // For non-auth errors, use standardized error handling
      handleError(
        error,
        {
          source: 'AuthService.executeWithAuth',
          operation: 'authenticated API call',
        },
        {
          showToast: false, // Let the calling component handle the UI
          rethrow: true,
        }
      );
      // This line should never be reached since handleError with rethrow: true should throw
      throw error;
    }
  }
}

// Create and export a singleton instance
export const authService = new AuthService();

// Export the ChatterSDK instance for direct use
export const getSDK = (): ChatterSDK => authService.getSDK();

// Export initialization check for safe SDK access
export const isSDKInitialized = (): boolean => authService.isInitialized();

// Export initialization function for explicit app setup if needed
export const initializeSDK = async (): Promise<void> => {
  await authService.initialize();
};
