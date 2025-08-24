#!/usr/bin/env python3
"""
Script to generate TypeScript SDK from existing API client structure.
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def parse_typescript_interface(content: str, interface_name: str) -> Dict[str, Any]:
    """Parse a TypeScript interface from content."""
    pattern = rf"export interface {interface_name}\s*\{{([^}}]+)\}}"
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return {}
    
    interface_body = match.group(1)
    fields = {}
    
    # Parse fields
    for line in interface_body.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'):
            continue
            
        # Match field: type pattern
        field_match = re.match(r'(\w+)(\?)?\s*:\s*([^;]+);?', line)
        if field_match:
            field_name = field_match.group(1)
            is_optional = field_match.group(2) == '?'
            field_type = field_match.group(3).strip()
            
            fields[field_name] = {
                'type': field_type,
                'optional': is_optional
            }
    
    return fields


def parse_api_methods(content: str) -> List[Dict[str, Any]]:
    """Parse API methods from ChatterAPI class."""
    methods = []
    
    # Find all async methods
    method_pattern = r'async\s+(\w+)\s*\([^)]*\)\s*:\s*Promise<([^>]+)>\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(method_pattern, content, re.DOTALL):
        method_name = match.group(1)
        return_type = match.group(2)
        method_body = match.group(3)
        
        # Extract HTTP method and endpoint
        http_match = re.search(r'this\.client\.(get|post|put|delete|patch)\s*\(\s*[\'"`]([^\'"`]+)', method_body)
        if http_match:
            http_method = http_match.group(1).upper()
            endpoint = http_match.group(2)
            
            methods.append({
                'name': method_name,
                'http_method': http_method,
                'endpoint': endpoint,
                'return_type': return_type
            })
    
    return methods


def generate_typescript_sdk():
    """Generate TypeScript SDK from existing API client."""
    print("🚀 Generating TypeScript SDK...")
    
    # Read existing API client
    api_file = Path(__file__).parent.parent / "frontend" / "src" / "services" / "api.ts"
    if not api_file.exists():
        print(f"❌ API file not found: {api_file}")
        return
    
    content = api_file.read_text()
    
    # Create SDK directory
    sdk_dir = Path(__file__).parent.parent / "frontend" / "src" / "sdk"
    sdk_dir.mkdir(exist_ok=True)
    
    # Generate types file
    generate_types_file(content, sdk_dir)
    
    # Generate API client file
    generate_api_client(content, sdk_dir)
    
    # Generate index file
    generate_index_file(sdk_dir)
    
    # Generate configuration file
    generate_config_file(sdk_dir)
    
    print("✅ TypeScript SDK generated successfully!")
    print(f"📁 SDK location: {sdk_dir}")


def generate_types_file(content: str, sdk_dir: Path):
    """Generate types.ts file with all interfaces."""
    
    # Extract all interfaces
    interfaces = [
        'User', 'Profile', 'Prompt', 'Document', 'Conversation', 
        'ConversationMessage', 'DashboardData', 'Agent', 'ToolServer'
    ]
    
    types_content = '''/**
 * Generated types for Chatter API
 */

'''
    
    for interface_name in interfaces:
        pattern = rf"export interface {interface_name}\s*\{{[^}}]+\}}"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            types_content += match.group(0) + "\n\n"
    
    # Add additional types
    types_content += '''export interface ChatterConfig {
  baseURL?: string;
  timeout?: number;
  retries?: number;
}

export interface AuthTokens {
  access_token: string;
  user: User;
}

export interface ChatMessage {
  message: string;
  profile_id?: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: ConversationMessage;
  conversation_id: string;
}

export interface ApiError {
  message: string;
  code?: string;
  status?: number;
}
'''
    
    (sdk_dir / "types.ts").write_text(types_content)


def generate_api_client(content: str, sdk_dir: Path):
    """Generate the main API client."""
    
    client_content = '''/**
 * Generated Chatter API Client
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  User, Profile, Prompt, Document, Conversation, ConversationMessage,
  DashboardData, Agent, ToolServer, ChatterConfig, AuthTokens,
  ChatMessage, ChatResponse, ApiError
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

  async sendMessage(message: ChatMessage): Promise<ChatResponse> {
    const response = await this.client.post('/api/v1/chat/send', message);
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
'''
    
    (sdk_dir / "client.ts").write_text(client_content)


def generate_index_file(sdk_dir: Path):
    """Generate index.ts file."""
    
    index_content = '''/**
 * Chatter TypeScript SDK
 */

export { ChatterSDK } from './client';
export * from './types';
export { createChatterClient } from './factory';
'''
    
    (sdk_dir / "index.ts").write_text(index_content)


def generate_config_file(sdk_dir: Path):
    """Generate configuration and factory files."""
    
    factory_content = '''/**
 * Factory function for creating Chatter SDK instances
 */
import { ChatterSDK } from './client';
import { ChatterConfig } from './types';

/**
 * Create a new Chatter SDK client instance
 */
export function createChatterClient(config?: ChatterConfig): ChatterSDK {
  return new ChatterSDK(config);
}

/**
 * Create a pre-configured Chatter SDK client with common settings
 */
export function createChatterClientWithDefaults(overrides?: Partial<ChatterConfig>): ChatterSDK {
  const defaultConfig: ChatterConfig = {
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    timeout: 30000,
    retries: 3,
  };

  return new ChatterSDK({ ...defaultConfig, ...overrides });
}
'''
    
    (sdk_dir / "factory.ts").write_text(factory_content)


if __name__ == "__main__":
    generate_typescript_sdk()