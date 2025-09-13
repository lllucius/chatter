/**
 * Generated API client for Conversations
 */
import { ConversationCreate, ConversationDeleteResponse, ConversationListResponse, ConversationResponse, ConversationStatus, ConversationUpdate, ConversationWithMessages, MessageDeleteResponse, MessageRatingResponse, MessageRatingUpdate, MessageResponse } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class ConversationsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Conversation
   * Create a new conversation.
   */
  public async createConversationApiV1Conversations(data: ConversationCreate): Promise<ConversationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationResponse>;
  }
  /**List Conversations
   * List conversations for the current user.

Args:
    status: Filter by conversation status
    llm_provider: Filter by LLM provider
    llm_model: Filter by LLM model
    tags: Filter by tags
    enable_retrieval: Filter by retrieval enabled status
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    handler: Conversation resource handler

Returns:
    List of conversations with pagination info
   */
  public async listConversationsApiV1Conversations(options?: { status?: ConversationStatus | null; llmProvider?: string | null; llmModel?: string | null; tags?: string[] | null; enableRetrieval?: boolean | null; limit?: number; offset?: number; sortBy?: string; sortOrder?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ConversationListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'status': options?.status,
        'llm_provider': options?.llmProvider,
        'llm_model': options?.llmModel,
        'tags': options?.tags,
        'enable_retrieval': options?.enableRetrieval,
        'limit': options?.limit,
        'offset': options?.offset,
        'sort_by': options?.sortBy,
        'sort_order': options?.sortOrder,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationListResponse>;
  }
  /**Get Conversation
   * Get conversation details with optional messages.
   */
  public async getConversationApiV1ConversationsConversationId(conversationId: string, options?: { includeMessages?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ConversationWithMessages> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'include_messages': options?.includeMessages,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationWithMessages>;
  }
  /**Update Conversation
   * Update conversation.
   */
  public async updateConversationApiV1ConversationsConversationId(conversationId: string, data: ConversationUpdate): Promise<ConversationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationResponse>;
  }
  /**Delete Conversation
   * Delete conversation.
   */
  public async deleteConversationApiV1ConversationsConversationId(conversationId: string): Promise<ConversationDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ConversationDeleteResponse>;
  }
  /**Get Conversation Messages
   * Get messages from a conversation.
   */
  public async getConversationMessagesApiV1ConversationsConversationIdMessages(conversationId: string, options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<MessageResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}/messages`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<MessageResponse[]>;
  }
  /**Delete Message
   * Delete a message from a conversation.
   */
  public async deleteMessageApiV1ConversationsConversationIdMessagesMessageId(conversationId: string, messageId: string): Promise<MessageDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}/messages/${messageId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<MessageDeleteResponse>;
  }
  /**Update Message Rating
   * Update the rating for a message.
   */
  public async updateMessageRatingApiV1ConversationsConversationIdMessagesMessageIdRating(conversationId: string, messageId: string, data: MessageRatingUpdate): Promise<MessageRatingResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/conversations/${conversationId}/messages/${messageId}/rating`,
      method: 'PATCH' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<MessageRatingResponse>;
  }
}