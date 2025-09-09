import {
  ChatterSDK,
  UserLogin,
  ToolServerCreate,
  ToolServerUpdate,
  ConversationCreate,
  ConversationUpdate,
} from 'chatter-sdk';

class ChatterSDKWrapper {
  private sdk: ChatterSDK;
  private token: string | null = null;

  constructor() {
    this.sdk = new ChatterSDK({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
    });
    this.loadTokenFromStorage();
  }

  // Direct access to the new SDK's APIs
  public get auth() { return this.sdk.auth; }
  public get abTesting() { return this.sdk.abTesting; }
  public get agents() { return this.sdk.agents; }
  public get analytics() { return this.sdk.analytics; }
  public get chat() { return this.sdk.chat; }
  public get dataManagement() { return this.sdk.dataManagement; }
  public get default() { return this.sdk.default; }
  public get documents() { return this.sdk.documents; }
  public get events() { return this.sdk.events; }
  public get health() { return this.sdk.health; }
  public get jobs() { return this.sdk.jobs; }
  public get modelRegistry() { return this.sdk.models; } // Note: new SDK uses 'models' instead of 'modelRegistry'
  public get plugins() { return this.sdk.plugins; }
  public get profiles() { return this.sdk.profiles; }
  public get prompts() { return this.sdk.prompts; }
  public get toolServers() { return this.sdk.toolServers; }
  public get workflows() { return this.sdk.workflows; }

  // Convenience objects for compatibility
  public get conversations() {
    return {
      listConversationsApiV1ChatConversationsGet: (params = {}) => this.chat.listConversationsApiV1ChatConversationsGet(params),
      listConversationsApiV1ConversationsGet: (params = {}) => this.chat.listConversationsApiV1ChatConversationsGet(params),
      createConversationApiV1ChatConversationsPost: (params: any) => this.chat.createConversationApiV1ChatConversationsPost(params),
      deleteConversationApiV1ConversationsConversationIdDelete: (params: any) => this.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      deleteConversationApiV1ChatConversationsConversationIdDelete: (params: any) => this.chat.deleteConversationApiV1ChatConversationsConversationIdDelete(params),
      getConversationApiV1ChatConversationsConversationIdGet: (params: any) => this.chat.getConversationApiV1ChatConversationsConversationIdGet(params),
      getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet: (params: any) => this.chat.getConversationMessagesApiV1ChatConversationsConversationIdMessagesGet(params),
      updateConversationApiV1ChatConversationsConversationIdPut: (params: any) => this.chat.updateConversationApiV1ChatConversationsConversationIdPut(params),
      chatApiV1ChatChatPost: (params: any) => this.chat.chatApiV1ChatChatPost(params),
    };
  }

  private loadTokenFromStorage() {
    const storedToken = localStorage.getItem('chatter_access_token');
    if (storedToken) {
      this.setToken(storedToken);
    }
  }

  private updateSDKWithToken() {
    this.sdk = new ChatterSDK({
      basePath: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      bearerToken: this.token || undefined,
    });
  }

  public getURL(): string | null {
    return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  }

  public setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_access_token', token);
    this.updateSDKWithToken();
  }

  public getToken(): string | null {
    return this.token;
  }

  public clearToken() {
    this.token = null;
    localStorage.removeItem('chatter_access_token');
    localStorage.removeItem('chatter_refresh_token');
    this.updateSDKWithToken();
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
export const chatterClient = new ChatterSDKWrapper();
