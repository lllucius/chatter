/**
 * Chatter SDK Wrapper Service
 * 
 * This service wraps the generated OpenAPI client and provides:
 * - Authentication management
 * - Configuration
 * - Error handling
 * - Token management
 */

import {
  Configuration,
  AuthenticationApi,
  AnalyticsApi,
  ChatApi,
  DocumentsApi,
  ProfilesApi,
  PromptsApi,
  AgentsApi,
  ToolServersApi,
  DataManagementApi,
  HealthApi,
  UserLogin,
  UserCreate,
} from '../sdk';

export class ChatterSDK {
  private configuration: Configuration;
  private token: string | null = null;

  // API instances
  public auth: AuthenticationApi;
  public analytics: AnalyticsApi;
  public conversations: ChatApi;
  public documents: DocumentsApi;
  public profiles: ProfilesApi;
  public prompts: PromptsApi;
  public agents: AgentsApi;
  public toolServers: ToolServersApi;
  public dataManagement: DataManagementApi;
  public health: HealthApi;

  constructor(baseURL: string = 'http://localhost:8000') {
    // Load token from localStorage
    const savedToken = localStorage.getItem('chatter_token');
    if (savedToken) {
      this.token = savedToken;
    }

    // Create configuration with auth
    this.configuration = new Configuration({
      basePath: baseURL,
      accessToken: () => this.token || '',
    });

    // Initialize API instances
    this.auth = new AuthenticationApi(this.configuration);
    this.analytics = new AnalyticsApi(this.configuration);
    this.conversations = new ChatApi(this.configuration);
    this.documents = new DocumentsApi(this.configuration);
    this.profiles = new ProfilesApi(this.configuration);
    this.prompts = new PromptsApi(this.configuration);
    this.agents = new AgentsApi(this.configuration);
    this.toolServers = new ToolServersApi(this.configuration);
    this.dataManagement = new DataManagementApi(this.configuration);
    this.health = new HealthApi(this.configuration);
  }

  /**
   * Set authentication token
   */
  setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_token', token);
    
    // Update configuration with new token
    this.configuration = new Configuration({
      basePath: this.configuration.basePath,
      accessToken: () => this.token || '',
    });

    // Reinitialize API instances with new config
    this.updateApiInstances();
  }

  /**
   * Clear authentication token
   */
  logout() {
    this.token = null;
    localStorage.removeItem('chatter_token');
    
    // Update configuration to remove token
    this.configuration = new Configuration({
      basePath: this.configuration.basePath,
      accessToken: () => '',
    });

    // Reinitialize API instances
    this.updateApiInstances();
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.token;
  }

  /**
   * Update all API instances with current configuration
   */
  private updateApiInstances() {
    this.auth = new AuthenticationApi(this.configuration);
    this.analytics = new AnalyticsApi(this.configuration);
    this.conversations = new ChatApi(this.configuration);
    this.documents = new DocumentsApi(this.configuration);
    this.profiles = new ProfilesApi(this.configuration);
    this.prompts = new PromptsApi(this.configuration);
    this.agents = new AgentsApi(this.configuration);
    this.toolServers = new ToolServersApi(this.configuration);
    this.dataManagement = new DataManagementApi(this.configuration);
    this.health = new HealthApi(this.configuration);
  }

  /**
   * Login helper method
   */
  async login(username: string, password: string) {
    try {
      const loginRequest: UserLogin = {
        username,
        password,
      };
      
      const response = await this.auth.loginApiV1AuthLoginPost({ userLogin: loginRequest });
      
      const { access_token, user } = response.data;
      this.setToken(access_token);
      
      return { access_token, user };
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Invalid credentials');
      }
      throw error;
    }
  }

  /**
   * Register helper method
   */
  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }) {
    try {
      const registerRequest: UserCreate = {
        username: userData.username,
        email: userData.email,
        password: userData.password,
        full_name: userData.full_name,
      };
      
      const response = await this.auth.registerApiV1AuthRegisterPost({ userCreate: registerRequest });
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'Registration failed');
      }
      throw error;
    }
  }

  /**
   * Get current user helper method
   */
  async getCurrentUser() {
    try {
      const response = await this.auth.getCurrentUserInfoApiV1AuthMeGet();
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        this.logout();
        window.location.href = '/login';
      }
      throw error;
    }
  }
}

// Create and export a singleton instance
export const chatterSDK = new ChatterSDK();
export default chatterSDK;