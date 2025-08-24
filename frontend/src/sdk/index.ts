/**
 * Chatter TypeScript SDK
 * Generated from OpenAPI specification
 */

// Export all APIs
//export * from './api';

// Export all models
//export * from './models';

// Export configuration and base types
export { Configuration } from './configuration';
export type { ConfigurationParameters } from './configuration';
export { BaseAPI } from './base';
export * from './api';

// Type aliases for commonly used response types
export type { AgentResponse as Agent } from './api';
export type { ProfileResponse as Profile } from './api';
export type { PromptResponse as Prompt } from './api';
export type { DocumentResponse as Document } from './api';
export type { ConversationResponse as Conversation } from './api';
export type { ToolServerResponse as ToolServer } from './api';

// Type aliases for request types
export type { AgentCreateRequest as ApiV1AgentsPostRequest } from './api';
export type { AgentUpdateRequest as ApiV1AgentsIdPutRequest } from './api';
export type { ProfileCreate as ApiV1ProfilesPostRequest } from './api';
export type { ProfileUpdate as ApiV1ProfilesIdPutRequest } from './api';
export type { PromptCreate as ApiV1PromptsPostRequest } from './api';
export type { PromptUpdate as ApiV1PromptsIdPutRequest } from './api';

// Additional type aliases
export type { ConversationWithMessages as ConversationMessage } from './api';
export type { ConversationCreate as CreateConversationRequest } from './api';
export type { ChatRequest as SendMessageRequest } from './api';
export type { DashboardResponse as DashboardData } from './api';
