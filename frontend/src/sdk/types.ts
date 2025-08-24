/**
 * Generated types for Chatter API
 */

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

export interface ChatterConfig {
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
