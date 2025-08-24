/**
 * Generated Chatter API Client
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  User, Profile, Prompt, Document, Conversation, ConversationMessage,
  DashboardData, Agent, ToolServer, ChatterConfig, AuthTokens,
  ApiError
} from './types';

export class ChatterSDK {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(config: ChatterConfig = {}) {
    const { baseURL = 'http://localhost:8000', timeout = 30000 } = config;
    
    this.client = axios.create({
      baseURL,
      timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.logout();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        
        const apiError: ApiError = {
          message: error.message,
          status: error.response?.status,
          code: error.code
        };
        return Promise.reject(apiError);
      }
    );

    // Load token from localStorage if available
    if (typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('chatter_token');
      if (savedToken) {
        this.token = savedToken;
      }
    }
  }

  // Auth methods
  setToken(token: string): void {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatter_token', token);
    }
  }

  logout(): void {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('chatter_token');
    }
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Authentication endpoints
  async login(username: string, password: string): Promise<AuthTokens> {
    const response = await this.client.post('/api/v1/auth/login', {
      username,
      password,
    });
    return response.data;
  }

  async register(userData: {
    username: string;
    email: string;
    password: string;
    full_name?: string;
  }): Promise<User> {
    const response = await this.client.post('/api/v1/auth/register', userData);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get('/api/v1/auth/me');
    return response.data;
  }

  // Dashboard and analytics
  async getDashboardData(): Promise<DashboardData> {
    const response = await this.client.get('/api/v1/analytics/dashboard');
    return response.data;
  }

  // Conversations
  async getConversations(): Promise<Conversation[]> {
    const response = await this.client.get('/api/v1/chat/conversations');
    return response.data;
  }

  async getConversation(id: string): Promise<Conversation> {
    const response = await this.client.get(`/api/v1/chat/conversations/${id}`);
    return response.data;
  }

  async getConversationMessages(id: string): Promise<ConversationMessage[]> {
    const response = await this.client.get(`/api/v1/chat/conversations/${id}/messages`);
    return response.data;
  }

  async createConversation(data: {
    title?: string;
    profile_id?: string;
    prompt_id?: string;
  }): Promise<Conversation> {
    const response = await this.client.post('/api/v1/chat/conversations', data);
    return response.data;
  }

  async updateConversation(id: string, data: Partial<Conversation>): Promise<Conversation> {
    const response = await this.client.put(`/api/v1/chat/conversations/${id}`, data);
    return response.data;
  }

  async deleteConversation(id: string): Promise<void> {
    await this.client.delete(`/api/v1/chat/conversations/${id}`);
  }

  async sendMessage(conversationId: string, content: string): Promise<ConversationMessage> {
    const response = await this.client.post(`/api/v1/chat/${conversationId}`, {
      message: content,
    });
    return response.data;
  }

  // Documents
  async getDocuments(): Promise<Document[]> {
    const response = await this.client.get('/api/v1/documents');
    return response.data;
  }

  async uploadDocument(file: File, title?: string): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);
    if (title) {
      formData.append('title', title);
    }

    const response = await this.client.post('/api/v1/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async deleteDocument(id: string): Promise<void> {
    await this.client.delete(`/api/v1/documents/${id}`);
  }

  async searchDocuments(query: string): Promise<any[]> {
    const response = await this.client.post('/api/v1/documents/search', {
      query,
      limit: 10,
    });
    return response.data;
  }

  // Profiles
  async getProfiles(): Promise<Profile[]> {
    const response = await this.client.get('/api/v1/profiles');
    return response.data;
  }

  async createProfile(profile: Omit<Profile, 'id' | 'created_at' | 'updated_at'>): Promise<Profile> {
    const response = await this.client.post('/api/v1/profiles', profile);
    return response.data;
  }

  async updateProfile(id: string, profile: Partial<Profile>): Promise<Profile> {
    const response = await this.client.put(`/api/v1/profiles/${id}`, profile);
    return response.data;
  }

  async deleteProfile(id: string): Promise<void> {
    await this.client.delete(`/api/v1/profiles/${id}`);
  }

  // Prompts
  async getPrompts(): Promise<Prompt[]> {
    const response = await this.client.get('/api/v1/prompts');
    return response.data;
  }

  async createPrompt(prompt: Omit<Prompt, 'id' | 'created_at' | 'updated_at'>): Promise<Prompt> {
    const response = await this.client.post('/api/v1/prompts', prompt);
    return response.data;
  }

  async updatePrompt(id: string, prompt: Partial<Prompt>): Promise<Prompt> {
    const response = await this.client.put(`/api/v1/prompts/${id}`, prompt);
    return response.data;
  }

  async deletePrompt(id: string): Promise<void> {
    await this.client.delete(`/api/v1/prompts/${id}`);
  }

  // Agents
  async getAgents(): Promise<Agent[]> {
    const response = await this.client.get('/api/v1/agents');
    return response.data;
  }

  async createAgent(agent: Omit<Agent, 'id' | 'created_at' | 'updated_at'>): Promise<Agent> {
    const response = await this.client.post('/api/v1/agents', agent);
    return response.data;
  }

  async updateAgent(id: string, agent: Partial<Agent>): Promise<Agent> {
    const response = await this.client.put(`/api/v1/agents/${id}`, agent);
    return response.data;
  }

  async deleteAgent(id: string): Promise<void> {
    await this.client.delete(`/api/v1/agents/${id}`);
  }

  // Tool Servers
  async getToolServers(): Promise<ToolServer[]> {
    const response = await this.client.get('/api/v1/toolservers');
    return response.data;
  }

  async createToolServer(server: Omit<ToolServer, 'id' | 'created_at' | 'updated_at' | 'health_status' | 'last_health_check'>): Promise<ToolServer> {
    const response = await this.client.post('/api/v1/toolservers', server);
    return response.data;
  }

  async deleteToolServer(id: string): Promise<void> {
    await this.client.delete(`/api/v1/toolservers/${id}`);
  }

  // Health
  async getHealth(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }
}
