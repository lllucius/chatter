/**
 * Authentication service using ChatterSDK directly
 * Manages tokens and provides authenticated SDK instances
 */
import { ChatterSDK, UserLogin } from 'chatter-sdk';

class AuthService {
  private token: string | null = null;
  private baseSDK: ChatterSDK;
  private initialized: boolean = false;

  constructor() {
    this.baseSDK = new ChatterSDK({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    });
    this.initialize();
  }

  /**
   * Initialize the auth service (automatically called in constructor)
   * Can be called explicitly if needed for testing or re-initialization
   */
  public initialize(): void {
    if (this.initialized) {
      return;
    }
    
    this.loadTokenFromStorage();
    this.initialized = true;
    
    console.log('[AuthService] Initialized with base URL:', this.baseSDK.withConfig({}).basePath);
  }

  private loadTokenFromStorage() {
    const storedToken = localStorage.getItem('chatter_access_token');
    if (storedToken) {
      this.token = storedToken;
    }
  }

  public isAuthenticated(): boolean {
    return !!this.token;
  }

  public getToken(): string | null {
    return this.token;
  }

  public getSDK(): ChatterSDK {
    if (this.token) {
      return this.baseSDK.withAuth(this.token, 'bearer');
    }
    return this.baseSDK;
  }

  public async login(username: string, password: string): Promise<void> {
    try {
      const loginData: UserLogin = {
        username,
        password,
      };

      const response = await this.baseSDK.auth.authLogin(loginData);

      if (response.access_token) {
        this.token = response.access_token;
        localStorage.setItem('chatter_access_token', response.access_token);
        
        // Store refresh token if available
        if (response.refresh_token) {
          localStorage.setItem('chatter_refresh_token', response.refresh_token);
        }
      } else {
        throw new Error('No access token received');
      }
    } catch (error: any) {
      console.error('Login failed:', error);
      
      // Extract error message from the response
      let errorMessage = 'Login failed';
      if (error?.body?.detail) {
        errorMessage = error.body.detail;
      } else if (error?.message) {
        errorMessage = error.message;
      }
      
      throw new Error(errorMessage);
    }
  }

  public async logout(): Promise<void> {
    try {
      if (this.isAuthenticated()) {
        await getSDK().auth.authLogout();
      }
    } catch (error) {
      console.error('Logout API call failed:', error);
      // Continue with local logout even if API call fails
    } finally {
      this.clearToken();
    }
  }

  public async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('chatter_refresh_token');
      if (!refreshToken) {
        return false;
      }

      const response = await this.baseSDK.auth.refreshTokenApiV1AuthRefresh({
        refreshToken: refreshToken,
      });

      if (response.access_token) {
        this.token = response.access_token;
        localStorage.setItem('chatter_access_token', response.access_token);
        
        // Update refresh token if provided
        if (response.refresh_token) {
          localStorage.setItem('chatter_refresh_token', response.refresh_token);
        }
        
        return true;
      }
      
      return false;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearToken();
      return false;
    }
  }

  private clearToken() {
    this.token = null;
    localStorage.removeItem('chatter_access_token');
    localStorage.removeItem('chatter_refresh_token');
  }

  public getURL(): string | null {
    return this.baseSDK.withConfig({}).basePath || null;
  }

  /**
   * Get the current SDK configuration (for debugging/inspection)
   */
  public getSDKInfo(): { basePath: string | undefined; hasToken: boolean } {
    return {
      basePath: this.baseSDK.withConfig({}).basePath,
      hasToken: !!this.token
    };
  }
}

// Create and export a singleton instance
export const authService = new AuthService();

// Export the ChatterSDK instance for direct use
export const getSDK = (): ChatterSDK => authService.getSDK();

// Export initialization function for explicit app setup if needed
export const initializeSDK = (): void => {
  authService.initialize();
  console.log('[SDK] Initialization complete:', authService.getSDKInfo());
};
