/**
 * Generated API client for Prompts
 */
import { PromptCategory, PromptCloneRequest, PromptCreate, PromptDeleteResponse, PromptListResponse, PromptResponse, PromptStatsResponse, PromptTestRequest, PromptTestResponse, PromptType, PromptUpdate } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class PromptsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Prompt
   * Create a new prompt.

Args:
    prompt_data: Prompt creation data
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Created prompt information
   */
  public async createPromptApiV1Prompts(data: PromptCreate): Promise<PromptResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptResponse>;
  }
  /**Get Prompt Stats
   * Get prompt statistics.

Args:
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Prompt statistics
   */
  public async getPromptStatsApiV1PromptsStatsOverview(): Promise<PromptStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/stats/overview`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptStatsResponse>;
  }
  /**List Prompts
   * List user's prompts.

Args:
    prompt_type: Filter by prompt type
    category: Filter by category
    tags: Filter by tags
    is_public: Filter by public status
    is_chain: Filter by chain status
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    List of prompts with pagination info
   */
  public async listPromptsApiV1Prompts(options?: { promptType?: PromptType | null; category?: PromptCategory | null; tags?: string[] | null; isPublic?: boolean | null; isChain?: boolean | null; limit?: number; offset?: number; sortBy?: string; sortOrder?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PromptListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'prompt_type': options?.promptType,
        'category': options?.category,
        'tags': options?.tags,
        'is_public': options?.isPublic,
        'is_chain': options?.isChain,
        'limit': options?.limit,
        'offset': options?.offset,
        'sort_by': options?.sortBy,
        'sort_order': options?.sortOrder,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptListResponse>;
  }
  /**Get Prompt
   * Get prompt details.

Args:
    prompt_id: Prompt ID
    request: Get request parameters
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Prompt information
   */
  public async getPromptApiV1PromptsPromptId(promptId: string): Promise<PromptResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/${promptId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptResponse>;
  }
  /**Update Prompt
   * Update prompt.

Args:
    prompt_id: Prompt ID
    update_data: Update data
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Updated prompt information
   */
  public async updatePromptApiV1PromptsPromptId(promptId: string, data: PromptUpdate): Promise<PromptResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/${promptId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptResponse>;
  }
  /**Delete Prompt
   * Delete prompt.

Args:
    prompt_id: Prompt ID
    request: Delete request parameters
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Success message
   */
  public async deletePromptApiV1PromptsPromptId(promptId: string): Promise<PromptDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/${promptId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptDeleteResponse>;
  }
  /**Test Prompt
   * Test prompt with given variables.

Args:
    prompt_id: Prompt ID
    test_request: Test request
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Test results
   */
  public async testPromptApiV1PromptsPromptIdTest(promptId: string, data: PromptTestRequest): Promise<PromptTestResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/${promptId}/test`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptTestResponse>;
  }
  /**Clone Prompt
   * Clone an existing prompt.

Args:
    prompt_id: Source prompt ID
    clone_request: Clone request
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Cloned prompt information
   */
  public async clonePromptApiV1PromptsPromptIdClone(promptId: string, data: PromptCloneRequest): Promise<PromptResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/prompts/${promptId}/clone`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PromptResponse>;
  }
}