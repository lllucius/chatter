/**
 * Authentication service using individual API classes
 * Manages tokens and provides authenticated SDK instances
 */
import { 
  Configuration,
  AuthenticationApi,
  AgentsApi,
  ProfilesApi,
  PromptsApi,
  DocumentsApi,
  ToolServersApi,
  ChatApi,
  ModelRegistryApi,
  WorkflowsApi,
  ABTestingApi,
  AnalyticsApi,
  DataManagementApi,
  EventsApi,
  HealthApi,
  JobsApi,
  PluginsApi,
  UserLogin
} from 'chatter-sdk';

// Unified SDK interface that matches the expected structure
interface ChatterSDK {
  auth: AuthenticationApi;
  agents: AgentsApi;
  profiles: ProfilesApi;
  prompts: PromptsApi;
  documents: DocumentsApi;
  toolServers: ToolServersApi;
  chat: ChatApi;
  modelRegistry: ModelRegistryApi;
  workflows: WorkflowsApi;
  abTesting: ABTestingApi;
  analytics: AnalyticsApi;
  dataManagement: DataManagementApi;
  events: EventsApi;
  health: HealthApi;
  jobs: JobsApi;
  plugins: PluginsApi;
}

class AuthService {
  private token: string | null = null;
  private baseConfiguration: Configuration;

  constructor() {
    this.baseConfiguration = new Configuration({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    });
    this.loadTokenFromStorage();
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
    const configuration = this.token
      ? new Configuration({
          ...this.baseConfiguration,
          accessToken: this.token,
        })
      : this.baseConfiguration;

    return {
      auth: new AuthenticationApi(configuration),
      agents: new AgentsApi(configuration),
      profiles: new ProfilesApi(configuration),
      prompts: new PromptsApi(configuration),
      documents: new DocumentsApi(configuration),
      toolServers: new ToolServersApi(configuration),
      chat: new ChatApi(configuration),
      modelRegistry: new ModelRegistryApi(configuration),
      workflows: new WorkflowsApi(configuration),
      abTesting: new ABTestingApi(configuration),
      analytics: new AnalyticsApi(configuration),
      dataManagement: new DataManagementApi(configuration),
      events: new EventsApi(configuration),
      health: new HealthApi(configuration),
      jobs: new JobsApi(configuration),
      plugins: new PluginsApi(configuration),
    };
  }

  public async login(username: string, password: string): Promise<void> {
    try {
      const loginData: UserLogin = {
        username,
        password,
      };

      const response = await this.getSDK().auth.loginApiV1AuthLoginPost({
        userLogin: loginData,
      });

      if (response.accessToken) {
        this.token = response.accessToken;
        localStorage.setItem('chatter_access_token', response.accessToken);
        
        // Store refresh token if available
        if (response.refreshToken) {
          localStorage.setItem('chatter_refresh_token', response.refreshToken);
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
        const sdk = this.getSDK();
        await sdk.auth.logoutApiV1AuthLogoutPost();
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

      const response = await this.getSDK().auth.refreshTokenApiV1AuthRefreshPost({
        tokenRefresh: {
          refresh_token: refreshToken,
        },
      });

      if (response.accessToken) {
        this.token = response.accessToken;
        localStorage.setItem('chatter_access_token', response.accessToken);
        
        // Update refresh token if provided
        if (response.refreshToken) {
          localStorage.setItem('chatter_refresh_token', response.refreshToken);
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
    return this.baseConfiguration.basePath || null;
  }
}

// Create and export a singleton instance
export const authService = new AuthService();

// Export the ChatterSDK type for use in other files
export type { ChatterSDK };

// Export the ChatterSDK instance for direct use
export const getSDK = (): ChatterSDK => authService.getSDK();