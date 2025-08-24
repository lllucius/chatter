/**
 * API client for Chatter backend
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// Types for API responses
export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Profile {
  id: string;
  name: string;
  description?: string;
  model_name: string;
  provider: string;
  temperature: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  created_at: string;
  updated_at?: string;
}

export interface Prompt {
  id: string;
  name: string;
  description?: string;
  content: string;
  variables?: string[];
  category: string;
  prompt_type: string;
  created_at: string;
  updated_at?: string;
}

export interface Document {
  id: string;
  title: string;
  filename: string;
  content_type: string;
  file_size: number;
  status: string;
  chunk_count?: number;
  created_at: string;
  updated_at?: string;
}

export interface Conversation {
  id: string;
  title?: string;
  profile_id?: string;
  prompt_id?: string;
  message_count: number;
  total_tokens?: number;
  created_at: string;
  updated_at?: string;
}

export interface ConversationMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tokens?: number;
  created_at: string;
}

export interface DashboardData {
  conversation_stats: {
    total_conversations: number;
    total_messages: number;
    avg_messages_per_conversation: number;
    conversations_today: number;
    conversations_week: number;
  };
  usage_metrics: {
    total_tokens: number;
    tokens_today: number;
    tokens_week: number;
    avg_tokens_per_message: number;
  };
  performance_metrics: {
    avg_response_time: number;
    success_rate: number;
    error_rate: number;
  };
  document_analytics: {
    total_documents: number;
    total_chunks: number;
    documents_processed_today: number;
    avg_chunk_size: number;
  };
  system_health: {
    total_users: number;
    active_users_today: number;
    active_users_week: number;
    storage_usage_bytes: number;
  };
}

export interface Agent {
  id: string;
  name: string;
  description?: string;
  system_prompt?: string;
  agent_type: string;
  config: object;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface ToolServer {
  id: string;
  name: string;
  url: string;
  status: string;
  description?: string;
  health_status: object;
  last_health_check?: string;
  created_at: string;
  updated_at?: string;
}

class ChatterAPI {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
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
      (error) => {
        if (error.response?.status === 401) {
          this.logout();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );

    // Load token from localStorage
    const savedToken = localStorage.getItem('chatter_token');
    if (savedToken) {
      this.token = savedToken;
    }
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('chatter_token', token);
  }

  logout() {
    this.token = null;
    localStorage.removeItem('chatter_token');
  }

  isAuthenticated(): boolean {
    return !!this.token;
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<{ access_token: string; user: User }> {
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

export const api = new ChatterAPI();
export default api;