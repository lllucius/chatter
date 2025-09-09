import {
  ChatterSDK,
  UserLogin,
  ToolServerCreate,
  ToolServerUpdate,
  ConversationCreate,
  ConversationUpdate,
} from 'chatter-sdk';

class ChatterSDKWrapper {
  private chatterSDK: ChatterSDK;
  private token: string | null = null;
  
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
    this.chatterSDK = new ChatterSDK({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    });
    this.loadTokenFromStorage();
    this.initializeConvenienceObjects();
  }

  // Expose API instances through getters for compatibility
  public get auth() { return this.chatterSDK.auth; }
  public get abTesting() { return this.chatterSDK.abTesting; }
  public get agents() { return this.chatterSDK.agents; }
  public get analytics() { return this.chatterSDK.analytics; }
  public get chat() { return this.chatterSDK.chat; }
  public get dataManagement() { return this.chatterSDK.dataManagement; }
  public get default() { return this.chatterSDK.default; }
  public get documents() { return this.chatterSDK.documents; }
  public get events() { return this.chatterSDK.events; }
  public get health() { return this.chatterSDK.health; }
  public get jobs() { return this.chatterSDK.jobs; }
  public get modelRegistry() { return this.chatterSDK.models; }
  public get plugins() { return this.chatterSDK.plugins; }
  public get profiles() { return this.chatterSDK.profiles; }
  public get prompts() { return this.chatterSDK.prompts; }
  public get toolServers() { return this.chatterSDK.toolServers; }

  private initializeConvenienceObjects() {
    // Create conversations object that delegates to chat API for compatibility
    this.conversations = {
      listConversationsApiV1ChatConversationsGet: (params = {}) => this.chatterSDK.chat.listConversationsApiV1ChatConversationsGet(params),
      listConversationsApiV1ConversationsGet: (params = {}) => this.chatterSDK.chat.listConversationsApiV1ChatConversationsGet(params),
      createConversationApiV1ChatConversationsPost: (params) => this.chatterSDK.chat.createConversationApiV1ChatConversationsPost(params),
      deleteConversationApiV1ConversationsConversationIdDelete: (params) => this.chatterSDK.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      deleteConversationApiV1ChatConversationsConversationIdDelete: (params) => this.chatterSDK.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      getConversationApiV1ChatConversationsConversationIdGet: (params) => this.chatterSDK.chat.getConversationApiV1ChatConversationsConversationIdGet(params),
      getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: (params) => this.chatterSDK.chat.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(params),
      updateConversationApiV1ChatConversationsConversationIdPut: (params) => this.chatterSDK.chat.updateConversationApiV1ChatConversationsConversationIdPut(params),
      chatApiV1ChatChatPost: (params) => this.chatterSDK.chat.chatApiV1ChatChatPost(params),
    };
  }

  private loadTokenFromStorage() {
    const storedToken = localStorage.getItem('chatter_access_token');
    if (storedToken) {
      this.setToken(storedToken);
    }
  }

  public getURL(): string | null {
    return this.chatterSDK.withConfig({}).basePath || null;
  }

  public setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_access_token', token);
    
    // Create new SDK instance with token
    this.chatterSDK = this.chatterSDK.withAuth(token, 'bearer');
    
    // Reinitialize convenience objects with new SDK instance
    this.initializeConvenienceObjects();
  }

  public getToken(): string | null {
    return this.token;
  }

  public clearToken() {
    this.token = null;
    localStorage.removeItem('chatter_access_token');
    localStorage.removeItem('chatter_refresh_token');
    
    // Create new SDK instance without token
    this.chatterSDK = new ChatterSDK({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    });
    
    // Reinitialize convenience objects
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

      const response = await this.chatterSDK.auth.loginApiV1AuthLoginPost({
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
        await this.chatterSDK.auth.logoutApiV1AuthLogoutPost();
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

      const response = await this.chatterSDK.auth.refreshTokenApiV1AuthRefreshPost({
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
    return this.chatterSDK.toolServers.listToolServersApiV1ToolServersGet({});
  }

  public async createToolServer(serverData: ToolServerCreate) {
    return this.chatterSDK.toolServers.createToolServerApiV1ToolServersPost({
      toolServerCreateRequest: serverData,
    });
  }

  public async updateToolServer(serverId: string, updateData: ToolServerUpdate) {
    return this.chatterSDK.toolServers.updateToolServerApiV1ToolServersServerIdPut({
      serverId,
      toolServerUpdateRequest: updateData,
    });
  }

  public async enableToolServer(serverId: string) {
    return this.chatterSDK.toolServers.enableToolServerApiV1ToolServersServerIdEnablePost({
      serverId,
    });
  }

  public async disableToolServer(serverId: string) {
    return this.chatterSDK.toolServers.disableToolServerApiV1ToolServersServerIdDisablePost({
      serverId,
    });
  }

  public async refreshServerTools(serverId: string) {
    return this.chatterSDK.toolServers.refreshServerToolsApiV1ToolserversServersServerIdRefreshToolsPost({
      serverId,
    });
  }

  public async deleteToolServer(serverId: string) {
    return this.chatterSDK.toolServers.deleteToolServerApiV1ToolserversServersServerIdDelete({
      serverId,
    });
  }

  public async enableTool(toolId: string) {
    return this.chatterSDK.toolServers.enableToolApiV1ToolserversToolsToolIdEnablePost({
      toolId,
    });
  }

  public async disableTool(toolId: string) {
    return this.chatterSDK.toolServers.disableToolApiV1ToolserversToolsToolIdDisablePost({
      toolId,
    });
  }

  public async getAllTools() {
    return this.chatterSDK.toolServers.listAllToolsApiV1ToolserversToolsAllGet();
  }

  // Convenience methods for conversations (delegated to chat API)
  public async listConversations(params: any = {}) {
    return this.chatterSDK.chat.listConversationsApiV1ChatConversationsGet(params);
  }

  public async createConversation(conversationData: ConversationCreate) {
    return this.chatterSDK.chat.createConversationApiV1ChatConversationsPost({
      conversationCreate: conversationData,
    });
  }

  public async deleteConversation(conversationId: string) {
    return this.chatterSDK.chat.deleteConversationApiV1ChatConversationsConversationIdDelete({
      conversationId,
    });
  }

  public async getConversation(conversationId: string) {
    return this.chatterSDK.chat.getConversationApiV1ChatConversationsConversationIdGet({
      conversationId,
    });
  }

  public async updateConversation(conversationId: string, updateData: ConversationUpdate) {
    return this.chatterSDK.chat.updateConversationApiV1ChatConversationsConversationIdPut({
      conversationId,
      conversationUpdate: updateData,
    });
  }
}

// Create and export a singleton instance
export const chatterClient = new ChatterSDKWrapper();
