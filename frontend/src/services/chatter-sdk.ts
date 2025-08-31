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
  PluginsApi,
  HealthApi,
  JobsApi,
  UserLogin,
  UserCreate,
  ChatRequest,
  ModelRegistryApi,
  ToolServerUpdate,
} from '../sdk';

type StoredAuth = {
  token: string;
  // Optional expiry timestamp in ms since epoch
  expiresAt?: number | null;
  updatedAt: number;
};

const LEGACY_TOKEN_KEY = 'chatter_token';
const STORAGE_KEY = 'chatter_auth';

export class ChatterSDK {
  private configuration: Configuration;
  private token: string | null = null;
  private expiresAt: number | null = null;
  private baseURL: string;

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
  public plugins: PluginsApi;
  public health: HealthApi;
  public jobs: JobsApi;
  public modelRegistry: ModelRegistryApi;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;

    // Load token (supports legacy key and new structured key)
    this.loadFromStorage();

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
    this.plugins = new PluginsApi(this.configuration);
    this.health = new HealthApi(this.configuration);
    this.jobs = new JobsApi(this.configuration);
    this.modelRegistry = new ModelRegistryApi(this.configuration);

    // Keep auth in sync across tabs/windows
    window.addEventListener('storage', this.onStorageChange);
  }

  /**
   * Set authentication token, optionally with expiry.
   * If your backend returns an expiry duration, pass it via options.expiresInSeconds.
   */
  setToken(token: string, options?: { expiresInSeconds?: number }) {
    this.token = token;
    this.expiresAt =
      options?.expiresInSeconds != null
        ? Date.now() + options.expiresInSeconds * 1000
        : null;

    this.persist();

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
    this.expiresAt = null;
    try {
      localStorage.removeItem(LEGACY_TOKEN_KEY);
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore storage errors
    }
    
    // Update configuration to remove token
    this.configuration = new Configuration({
      basePath: this.configuration.basePath,
      accessToken: () => '',
    });

    // Reinitialize API instances
    this.updateApiInstances();
  }

  /**
   * Check if user is authenticated (and token not expired if expiry is set)
   */
  isAuthenticated(): boolean {
    if (!this.token) return false;
    if (this.expiresAt && Date.now() >= this.expiresAt) {
      // Token expired — clear it
      this.logout();
      return false;
    }
    return true;
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
    this.plugins = new PluginsApi(this.configuration);
    this.health = new HealthApi(this.configuration);
    this.jobs = new JobsApi(this.configuration);
    this.modelRegistry = new ModelRegistryApi(this.configuration);
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
      
      const { access_token, user, expires_in } = response.data as any;
      // If backend includes expires_in (seconds), pass it; otherwise token persists until logout
      this.setToken(access_token, { expiresInSeconds: typeof expires_in === 'number' ? expires_in : undefined });
      
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

  /**
   * Chat streaming helper method using native fetch for proper streaming support
   */
  async chatStream(chatRequest: ChatRequest): Promise<ReadableStreamDefaultReader<Uint8Array>> {
    const response = await fetch(`${this.baseURL}/api/v1/chat/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token || ''}`,
      },
      body: JSON.stringify(chatRequest),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body for streaming');
    }

    return response.body.getReader();
  }

  /**
   * Load token from storage (supports legacy key migration).
   */
  private loadFromStorage() {
    try {
      // Prefer new structured storage
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed: StoredAuth = JSON.parse(saved);
        this.token = parsed.token || null;
        this.expiresAt = parsed.expiresAt ?? null;
        return;
      }

      // Migrate from legacy if present
      const legacyToken = localStorage.getItem(LEGACY_TOKEN_KEY);
      if (legacyToken) {
        this.token = legacyToken;
        this.expiresAt = null;
        this.persist(); // write to new format
        // Optionally remove legacy key to avoid duplication
        localStorage.removeItem(LEGACY_TOKEN_KEY);
      }
    } catch {
      // If storage is unavailable or parsing fails, start with no token
      this.token = null;
      this.expiresAt = null;
    }
  }

  /**
   * Persist current token state.
   */
  private persist() {
    try {
      if (this.token) {
        const data: StoredAuth = {
          token: this.token,
          expiresAt: this.expiresAt ?? null,
          updatedAt: Date.now(),
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
      } else {
        localStorage.removeItem(STORAGE_KEY);
      }
    } catch {
      // ignore storage errors
    }
  }

  /**
   * Sync changes across tabs/windows.
   */
  private onStorageChange = (e: StorageEvent) => {
    if (e.key === STORAGE_KEY) {
      // Another tab updated auth — rehydrate
      this.loadFromStorage();

      // Update configuration with new token
      this.configuration = new Configuration({
        basePath: this.baseURL,
        accessToken: () => this.token || '',
      });
      this.updateApiInstances();
    }

    // If legacy key is removed elsewhere, reflect it
    if (e.key === LEGACY_TOKEN_KEY && e.newValue === null) {
      // Nothing to do if we're already on new format; ensure no legacy residue
      try {
        localStorage.removeItem(LEGACY_TOKEN_KEY);
      } catch {
        // ignore
      }
    }
  };

  /**
   * Tool Server convenience methods
   */

  // Get all tool servers
  async getToolServers() {
    return await this.toolServers.listToolServersApiV1ToolserversServersGet({});
  }

  // Get all tools from all servers
  async getAllTools() {
    return await this.toolServers.listAllToolsApiV1ToolserversToolsAllGet({});
  }

  // Create a new tool server
  async createToolServer(serverData: any) {
    return await this.toolServers.createToolServerApiV1ToolserversServersPost({
      toolServerCreate: serverData
    });
  }

  // Enable a tool server
  async enableToolServer(serverId: string) {
    return await this.toolServers.enableToolServerApiV1ToolserversServersServerIdEnablePost({
      serverId
    });
  }

  // Disable a tool server
  async disableToolServer(serverId: string) {
    return await this.toolServers.disableToolServerApiV1ToolserversServersServerIdDisablePost({
      serverId
    });
  }

  // Delete a tool server
  async deleteToolServer(serverId: string) {
    return await this.toolServers.deleteToolServerApiV1ToolserversServersServerIdDelete({
      serverId
    });
  }

  // Update a tool server
  async updateToolServer(serverId: string, updateData: ToolServerUpdate) {
    return await this.toolServers.updateToolServerApiV1ToolserversServersServerIdPut({
      serverId,
      toolServerUpdate: updateData
    });
  }

  // Enable a tool
  async enableTool(toolId: string) {
    return await this.toolServers.enableToolApiV1ToolserversToolsToolIdEnablePost({
      toolId
    });
  }

  // Disable a tool
  async disableTool(toolId: string) {
    return await this.toolServers.disableToolApiV1ToolserversToolsToolIdDisablePost({
      toolId
    });
  }

  // Refresh server tools (get latest tools from server)
  async refreshServerTools(serverId: string) {
    return await this.toolServers.getServerToolsApiV1ToolserversServersServerIdToolsGet({
      serverId
    });
  }

  /**
   * RBAC Permission Management Methods
   */

  // Get user permissions
  async getUserPermissions(userId: string) {
    return await this.toolServers.getUserPermissionsApiV1ToolserversUsersUserIdPermissionsGet({
      userId
    });
  }

  // Grant tool permission
  async grantToolPermission(permissionData: any) {
    return await this.toolServers.grantToolPermissionApiV1ToolserversPermissionsPost({
      toolPermissionCreate: permissionData
    });
  }

  // Update tool permission
  async updateToolPermission(permissionId: string, updateData: any) {
    return await this.toolServers.updateToolPermissionApiV1ToolserversPermissionsPermissionIdPut({
      permissionId,
      toolPermissionUpdate: updateData
    });
  }

  // Revoke tool permission
  async revokeToolPermission(permissionId: string) {
    return await this.toolServers.revokeToolPermissionApiV1ToolserversPermissionsPermissionIdDelete({
      permissionId
    });
  }

  // Create role access rule
  async createRoleAccessRule(ruleData: any) {
    return await this.toolServers.createRoleAccessRuleApiV1ToolserversRoleAccessPost({
      roleToolAccessCreate: ruleData
    });
  }

  // Get role access rules
  async getRoleAccessRules(role?: string) {
    return await this.toolServers.getRoleAccessRulesApiV1ToolserversRoleAccessGet({
      role
    });
  }

  // Check tool access
  async checkToolAccess(checkData: any) {
    return await this.toolServers.checkToolAccessApiV1ToolserversAccessCheckPost({
      userToolAccessCheck: checkData
    });
  }
}

// Create and export a singleton instance
//const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
//export const chatterSDK = new ChatterSDK(API_BASE_URL);
export const chatterSDK = new ChatterSDK();
export default chatterSDK;
