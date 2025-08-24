/**
 * Updated API service using the generated TypeScript SDK
 */

import { createChatterClientWithDefaults } from '../sdk';

// Create and export a configured SDK instance
export const api = createChatterClientWithDefaults({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000,
});

// Export the SDK class for type checking and advanced usage
export { ChatterSDK, createChatterClient } from '../sdk';

// Re-export all types for convenience
export type {
  User, Profile, Prompt, Document, Conversation, ConversationMessage,
  DashboardData, Agent, ToolServer, ChatterConfig, AuthTokens,
  ChatMessage, ChatResponse, ApiError
} from '../sdk/types';