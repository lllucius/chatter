import { HttpClient } from '../sdk/http-client';
import type { 
  UserLogin,
  ToolServerCreate,
  ToolServerUpdate,
  ConversationCreate,
  ConversationUpdate,
} from '../sdk/data-contracts';

class ChatterSDK extends HttpClient {
  private token: string | null = null;
  
  // API instances - for backwards compatibility, we'll create these as properties
  // API instances - for backwards compatibility, we'll create these as properties
  public auth: ChatterSDK;
  public abTesting: ChatterSDK;
  public agents: ChatterSDK;
  public analytics: ChatterSDK;
  public chat: ChatterSDK;
  public dataManagement: ChatterSDK;
  public default: ChatterSDK;
  public documents: ChatterSDK;
  public events: ChatterSDK;
  public health: ChatterSDK;
  public jobs: ChatterSDK;
  public modelRegistry: ChatterSDK;
  public plugins: ChatterSDK;
  public profiles: ChatterSDK;
  public prompts: ChatterSDK;
  public toolServers: ChatterSDK;

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
    // Initialize the HTTP client with default configuration
    super({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      securityWorker: (securityData) => {
        const token = this.getToken();
        if (token) {
          return {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          };
        }
        return {};
      },
    });

    this.loadTokenFromStorage();
    this.initializeAPIs();
    this.initializeConvenienceObjects();
  }

  private initializeAPIs() {
    // For backwards compatibility, all API instances point to this same instance
    this.auth = this;
    this.abTesting = this;
    this.agents = this;
    this.analytics = this;
    this.chat = this;
    this.dataManagement = this;
    this.default = this;
    this.documents = this;
    this.events = this;
    this.health = this;
    this.jobs = this;
    this.modelRegistry = this;
    this.plugins = this;
    this.profiles = this;
    this.prompts = this;
    this.toolServers = this;
  }

  private initializeConvenienceObjects() {
    // Create conversations object that delegates to chat API for compatibility
    this.conversations = {
      listConversationsApiV1ChatConversationsGet: (params = {}) => this.listConversationsApiV1ChatConversationsGet(params),
      listConversationsApiV1ConversationsGet: (params = {}) => this.listConversationsApiV1ChatConversationsGet(params),
      createConversationApiV1ChatConversationsPost: (params) => this.createConversationApiV1ChatConversationsPost(params),
      deleteConversationApiV1ConversationsConversationIdDelete: (params) => this.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      deleteConversationApiV1ChatConversationsConversationIdDelete: (params) => this.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      getConversationApiV1ChatConversationsConversationIdGet: (params) => this.getConversationApiV1ChatConversationsConversationIdGet(params),
      getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: (params) => this.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(params),
      updateConversationApiV1ChatConversationsConversationIdPut: (params) => this.updateConversationApiV1ChatConversationsConversationIdPut(params),
      chatApiV1ChatChatPost: (params) => this.chatApiV1ChatChatPost(params),
    };
  }

  private loadTokenFromStorage() {
    const storedToken = localStorage.getItem('chatter_access_token');
    if (storedToken) {
      this.setToken(storedToken);
    }
  }

  public getURL(): string | null {
    return this.baseURL || import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }

  public setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_access_token', token);
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

      const response = await this.loginApiV1AuthLoginPost({
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
        await this.logoutApiV1AuthLogoutPost();
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

      const response = await this.refreshTokenApiV1AuthRefreshPost({
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
    return this.request({
      path: '/api/v1/toolservers/servers',
      method: 'GET',
      secure: true,
      format: 'json',
    });
  }

  public async createToolServer(serverData: ToolServerCreate) {
    return this.request({
      path: '/api/v1/toolservers/servers',
      method: 'POST',
      body: serverData,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async updateToolServer(serverId: string, updateData: ToolServerUpdate) {
    return this.request({
      path: `/api/v1/toolservers/servers/${serverId}`,
      method: 'PUT',
      body: updateData,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async deleteToolServer(serverId: string) {
    return this.request({
      path: `/api/v1/toolservers/servers/${serverId}`,
      method: 'DELETE',
      secure: true,
      format: 'json',
    });
  }

  public async enableToolServer(serverId: string) {
    return this.request({
      path: `/api/v1/toolservers/servers/${serverId}/enable`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async disableToolServer(serverId: string) {
    return this.request({
      path: `/api/v1/toolservers/servers/${serverId}/disable`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async refreshServerTools(serverId: string) {
    return this.request({
      path: `/api/v1/toolservers/servers/${serverId}/refresh-tools`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async getAllTools() {
    return this.request({
      path: '/api/v1/toolservers/tools/all',
      method: 'GET',
      secure: true,
      format: 'json',
    });
  }

  public async enableTool(toolId: string) {
    return this.request({
      path: `/api/v1/toolservers/tools/${toolId}/enable`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async disableTool(toolId: string) {
    return this.request({
      path: `/api/v1/toolservers/tools/${toolId}/disable`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  // Convenience methods for conversations (delegated to chat API)
  public async listConversations(params: any = {}) {
    return this.request({
      path: '/api/v1/chat/conversations',
      method: 'GET',
      query: params,
      secure: true,
      format: 'json',
    });
  }

  public async createConversation(conversationData: ConversationCreate) {
    return this.request({
      path: '/api/v1/chat/conversations',
      method: 'POST',
      body: conversationData,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async deleteConversation(conversationId: string) {
    return this.request({
      path: `/api/v1/chat/conversations/${conversationId}`,
      method: 'DELETE',
      secure: true,
      format: 'json',
    });
  }

  public async getConversation(conversationId: string) {
    return this.request({
      path: `/api/v1/chat/conversations/${conversationId}`,
      method: 'GET',
      secure: true,
      format: 'json',
    });
  }

  public async updateConversation(conversationId: string, updateData: ConversationUpdate) {
    return this.request({
      path: `/api/v1/chat/conversations/${conversationId}`,
      method: 'PUT',
      body: updateData,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  // API method implementations to replace the old structure calls
  public async loginApiV1AuthLoginPost(data: { userLogin: UserLogin }) {
    return this.request({
      path: '/api/v1/auth/login',
      method: 'POST',
      body: data.userLogin,
      type: 'application/json',
      format: 'json',
    });
  }

  public async logoutApiV1AuthLogoutPost() {
    return this.request({
      path: '/api/v1/auth/logout',
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async refreshTokenApiV1AuthRefreshPost(data: { tokenRefresh: any }) {
    return this.request({
      path: '/api/v1/auth/refresh',
      method: 'POST',
      body: data.tokenRefresh,
      type: 'application/json',
      format: 'json',
    });
  }

  // Add commonly used API methods
  public async listConversationsApiV1ChatConversationsGet(params: any = {}) {
    return this.listConversations(params);
  }

  public async createConversationApiV1ChatConversationsPost(data: any) {
    return this.createConversation(data.conversationCreate || data);
  }

  public async deleteConversationApiV1ChatConversationsConversationIdDelete(params: any) {
    return this.deleteConversation(params.conversationId);
  }

  public async getConversationApiV1ChatConversationsConversationIdGet(params: any) {
    return this.getConversation(params.conversationId);
  }

  public async getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(params: any) {
    return this.request({
      path: `/api/v1/chat/conversations/${params.conversationId}/messages`,
      method: 'GET',
      query: params,
      secure: true,
      format: 'json',
    });
  }

  public async updateConversationApiV1ChatConversationsConversationIdPut(params: any) {
    return this.updateConversation(params.conversationId, params.conversationUpdate);
  }

  public async chatApiV1ChatChatPost(data: any) {
    return this.request({
      path: '/api/v1/chat/chat',
      method: 'POST',
      body: data,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  // Provider/Model Registry methods
  public async listProvidersApiV1ModelsProvidersGet(params: any = {}) {
    return this.request({
      path: '/api/v1/models/providers',
      method: 'GET',
      query: params,
      secure: true,
      format: 'json',
    });
  }

  public async createProviderApiV1ModelsProvidersPost(data: any) {
    return this.request({
      path: '/api/v1/models/providers',
      method: 'POST',
      body: data,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async updateProviderApiV1ModelsProvidersProviderIdPut(params: any) {
    return this.request({
      path: `/api/v1/models/providers/${params.providerId}`,
      method: 'PUT',
      body: params.providerUpdate,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async deleteProviderApiV1ModelsProvidersProviderIdDelete(params: any) {
    return this.request({
      path: `/api/v1/models/providers/${params.providerId}`,
      method: 'DELETE',
      secure: true,
      format: 'json',
    });
  }

  public async setDefaultProviderApiV1ModelsProvidersProviderIdSetDefaultPost(params: any) {
    return this.request({
      path: `/api/v1/models/providers/${params.providerId}/set-default`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async listModelsApiV1ModelsModelsGet(params: any = {}) {
    return this.request({
      path: '/api/v1/models/models',
      method: 'GET',
      query: params,
      secure: true,
      format: 'json',
    });
  }

  public async createModelApiV1ModelsModelsPost(data: any) {
    return this.request({
      path: '/api/v1/models/models',
      method: 'POST',
      body: data,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async updateModelApiV1ModelsModelsModelIdPut(params: any) {
    return this.request({
      path: `/api/v1/models/models/${params.modelId}`,
      method: 'PUT',
      body: params.modelDefUpdate,
      secure: true,
      type: 'application/json',
      format: 'json',
    });
  }

  public async deleteModelApiV1ModelsModelsModelIdDelete(params: any) {
    return this.request({
      path: `/api/v1/models/models/${params.modelId}`,
      method: 'DELETE',
      secure: true,
      format: 'json',
    });
  }

  public async setDefaultModelApiV1ModelsModelsModelIdSetDefaultPost(params: any) {
    return this.request({
      path: `/api/v1/models/models/${params.modelId}/set-default`,
      method: 'POST',
      secure: true,
      format: 'json',
    });
  }

  public async listToolServersApiV1ToolserversServersGet(params: any = {}) {
    return this.getToolServers();
  }

  public async getAvailableToolsApiV1ChatToolsAvailableGet() {
    return this.request({
      path: '/api/v1/chat/tools/available',
      method: 'GET',
      secure: true,
      format: 'json',
    });
  }

  public async getToolServerAnalyticsApiV1AnalyticsToolserversGet() {
    return this.request({
      path: '/api/v1/analytics/toolservers',
      method: 'GET',
      secure: true,
      format: 'json',
    });
  }
}

// Create and export a singleton instance
export const chatterSDK = new ChatterSDK();
