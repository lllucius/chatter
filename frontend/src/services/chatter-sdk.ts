import {
  Configuration,
  AuthenticationApi,
  ABTestingApi,
  AgentsApi,
  AnalyticsApi,
  ChatApi,
  DataManagementApi,
  DefaultApi,
  DocumentsApi,
  EventsApi,
  HealthApi,
  JobsApi,
  ModelRegistryApi,
  PluginsApi,
  ProfilesApi,
  PromptsApi,
  ToolServersApi,
  UserLogin,
  ToolServerCreate,
  ToolServerUpdate,
  ConversationCreate,
  ConversationUpdate,
} from 'chatter-sdk';

class ChatterSDK {
  private configuration: Configuration;
  private token: string | null = null;
  
  // API instances
  public auth: AuthenticationApi;
  public abTesting: ABTestingApi;
  public agents: AgentsApi;
  public analytics: AnalyticsApi;
  public chat: ChatApi;
  public dataManagement: DataManagementApi;
  public default: DefaultApi;
  public documents: DocumentsApi;
  public events: EventsApi;
  public health: HealthApi;
  public jobs: JobsApi;
  public modelRegistry: ModelRegistryApi;
  public plugins: PluginsApi;
  public profiles: ProfilesApi;
  public prompts: PromptsApi;
  public toolServers: ToolServersApi;

  // Convenience objects for compatibility
  public conversations: {
    listConversationsApiV1ChatConversationsGet: (params?: any) => Promise<any>;
    listConversationsApiV1ConversationsGet: (params?: any) => Promise<any>;
    createConversationApiV1ChatConversationsPost: (params: any) => Promise<any>;
    deleteConversationApiV1ConversationsConversationIdDelete: (params: any) => Promise<any>;
    deleteConversationApiV1ChatConversationsConversationIdDelete: (params: any) => Promise<any>;
    getConversationApiV1ChatConversationsConversationIdGet: (params: any) => Promise<any>;
    getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: (params: any) => Promise<any>;
    updateConversationApiV1ChatConversationsConversationIdPut: (params: any) => Promise<any>;
    chatApiV1ChatChatPost: (params: any) => Promise<any>;
  };

  constructor() {
    this.initializeConfiguration();
    this.initializeAPIs();
    this.loadTokenFromStorage();
    this.initializeConvenienceObjects();
  }

  private initializeConfiguration() {
    this.configuration = new Configuration({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      accessToken: () => this.token || '',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  private initializeAPIs() {
    this.auth = new AuthenticationApi(this.configuration);
    this.abTesting = new ABTestingApi(this.configuration);
    this.agents = new AgentsApi(this.configuration);
    this.analytics = new AnalyticsApi(this.configuration);
    this.chat = new ChatApi(this.configuration);
    this.dataManagement = new DataManagementApi(this.configuration);
    this.default = new DefaultApi(this.configuration);
    this.documents = new DocumentsApi(this.configuration);
    this.events = new EventsApi(this.configuration);
    this.health = new HealthApi(this.configuration);
    this.jobs = new JobsApi(this.configuration);
    this.modelRegistry = new ModelRegistryApi(this.configuration);
    this.plugins = new PluginsApi(this.configuration);
    this.profiles = new ProfilesApi(this.configuration);
    this.prompts = new PromptsApi(this.configuration);
    this.toolServers = new ToolServersApi(this.configuration);
  }

  private initializeConvenienceObjects() {
    // Create conversations object that delegates to chat API for compatibility
    this.conversations = {
      listConversationsApiV1ChatConversationsGet: (params = {}) => this.chat.listConversationsApiV1ChatConversationsGet(params),
      listConversationsApiV1ConversationsGet: (params = {}) => this.chat.listConversationsApiV1ChatConversationsGet(params),
      createConversationApiV1ChatConversationsPost: (params) => this.chat.createConversationApiV1ChatConversationsPost(params),
      deleteConversationApiV1ConversationsConversationIdDelete: (params) => this.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      deleteConversationApiV1ChatConversationsConversationIdDelete: (params) => this.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      getConversationApiV1ChatConversationsConversationIdGet: (params) => this.chat.getConversationApiV1ChatConversationsConversationIdGet(params),
      getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: (params) => this.chat.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(params),
      updateConversationApiV1ChatConversationsConversationIdPut: (params) => this.chat.updateConversationApiV1ChatConversationsConversationIdPut(params),
      chatApiV1ChatChatPost: (params) => this.chat.chatApiV1ChatChatPost(params),
    };
  }

  private loadTokenFromStorage() {
    const storedToken = localStorage.getItem('chatter_access_token');
    if (storedToken) {
      this.setToken(storedToken);
    }
  }

  public getURL(): string | null {
    return this.configuration.basePath;
  }

  public setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_access_token', token);
    
    // Update configuration with new token
    this.configuration = new Configuration({
      ...this.configuration,
      accessToken: () => this.token || '',
    });
    
    // Reinitialize all APIs with new configuration
    this.initializeAPIs();
    this.initializeConvenienceObjects();
  }

  public getToken(): string | null {
    return this.token;
  }

  public clearToken() {
    this.token = null;
    localStorage.removeItem('chatter_access_token');
    localStorage.removeItem('chatter_refresh_token');
    
    // Update configuration to remove token
    this.configuration = new Configuration({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Reinitialize all APIs with new configuration
    this.initializeAPIs();
    this.initializeConvenienceObjects();
  }

  public isAuthenticated(): boolean {
    return !!this.token;
  }

  public async login(username: string, password: string): Promise<void> {
    try {
      const loginData: UserLogin = {
        username,
        password,
      };

      const response = await this.auth.loginApiV1AuthLoginPost({
        userLogin: loginData,
      });

      if (response.accessToken) {
        this.setToken(response.accessToken);
        
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
        await this.auth.logoutApiV1AuthLogoutPost();
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

      const response = await this.auth.refreshTokenApiV1AuthRefreshPost({
        tokenRefresh: { refreshToken },
      });

      if (response.accessToken) {
        this.setToken(response.accessToken);
        
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

  // Convenience methods that match the old API interface
  public async getToolServers() {
    return this.toolServers.listToolServersApiV1ToolServersGet({});
  }

  public async createToolServer(serverData: ToolServerCreate) {
    return this.toolServers.createToolServerApiV1ToolServersPost({
      toolServerCreateRequest: serverData,
    });
  }

  public async updateToolServer(serverId: string, updateData: ToolServerUpdate) {
    return this.toolServers.updateToolServerApiV1ToolServersServerIdPut({
      serverId,
      toolServerUpdateRequest: updateData,
    });
  }

  public async enableToolServer(serverId: string) {
    return this.toolServers.enableToolServerApiV1ToolServersServerIdEnablePost({
      serverId,
    });
  }

  public async disableToolServer(serverId: string) {
    return this.toolServers.disableToolServerApiV1ToolServersServerIdDisablePost({
      serverId,
    });
  }

  public async refreshServerTools(serverId: string) {
    return this.toolServers.refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost({
      serverId,
    });
  }

  public async deleteToolServer(serverId: string) {
    return this.toolServers.deleteToolServerApiV1ToolserversServersServerIdDelete({
      serverId,
    });
  }

  public async enableTool(toolId: string) {
    return this.toolServers.enableToolApiV1ToolserversToolsToolIdEnablePost({
      toolId,
    });
  }

  public async disableTool(toolId: string) {
    return this.toolServers.disableToolApiV1ToolserversToolsToolIdDisablePost({
      toolId,
    });
  }

  public async getAllTools() {
    return this.toolServers.listAllToolsApiV1ToolserversToolsAllGet();
  }

  // Convenience methods for conversations (delegated to chat API)
  public async listConversations(params: any = {}) {
    return this.chat.listConversationsApiV1ChatConversationsGet(params);
  }

  public async createConversation(conversationData: ConversationCreate) {
    return this.chat.createConversationApiV1ChatConversationsPost({
      conversationCreate: conversationData,
    });
  }

  public async deleteConversation(conversationId: string) {
    return this.chat.deleteConversationApiV1ChatConversationsConversationIdDelete({
      conversationId,
    });
  }

  public async getConversation(conversationId: string) {
    return this.chat.getConversationApiV1ChatConversationsConversationIdGet({
      conversationId,
    });
  }

  public async updateConversation(conversationId: string, updateData: ConversationUpdate) {
    return this.chat.updateConversationApiV1ChatConversationsConversationIdPut({
      conversationId,
      conversationUpdate: updateData,
    });
  }
}

// Create and export a singleton instance
export const chatterClient = new ChatterSDK();
