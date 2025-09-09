/**
 * Generated API client for Agents
 */
import { AgentBulkCreateRequest, AgentBulkCreateResponse, AgentBulkDeleteRequest, AgentCreateRequest, AgentDeleteResponse, AgentHealthResponse, AgentInteractRequest, AgentInteractResponse, AgentListResponse, AgentResponse, AgentStatsResponse, AgentStatus, AgentType, AgentUpdateRequest, Body_list_agents_api_v1_agents__get } from '../models/index';
import { BaseAPI, Configuration, HTTPQuery, HTTPHeaders } from '../runtime';

export class AgentsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create a new agent
   * Create a new AI agent with specified configuration and capabilities.
   */
  public async createAgentApiV1Agents(data: AgentCreateRequest): Promise<AgentResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<AgentResponse>(`/api/v1/agents/`, requestOptions);
  }
  /**List agents
   * List all agents with optional filtering and pagination. Users can only see their own agents.
   */
  public async listAgentsApiV1Agents(data: Body_list_agents_api_v1_agents__get, options?: { agentType?: AgentType | null; status?: AgentStatus | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<AgentListResponse> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'agent_type': options?.agentType,
        'status': options?.status,
        ...options?.query
      },
      body: data,
    };

    return this.request<AgentListResponse>(`/api/v1/agents/`, requestOptions);
  }
  /**Get agent templates
   * Get predefined agent templates for common use cases.
   */
  public async getAgentTemplatesApiV1AgentsTemplates(): Promise<Record<string, unknown>[]> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<Record<string, unknown>[]>(`/api/v1/agents/templates`, requestOptions);
  }
  /**Get agent statistics
   * Get comprehensive statistics about all agents for the current user.
   */
  public async getAgentStatsApiV1AgentsStatsOverview(): Promise<AgentStatsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<AgentStatsResponse>(`/api/v1/agents/stats/overview`, requestOptions);
  }
  /**Get Agent
   * Get agent by ID.

Args:
    agent_id: Agent ID
    request: Get request parameters
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Agent data
   */
  public async getAgentApiV1AgentsAgentId(agentId: string): Promise<AgentResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<AgentResponse>(`/api/v1/agents/${agentId}`, requestOptions);
  }
  /**Update Agent
   * Update an agent.

Args:
    agent_id: Agent ID
    agent_data: Agent update data
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Updated agent data
   */
  public async updateAgentApiV1AgentsAgentId(agentId: string, data: AgentUpdateRequest): Promise<AgentResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<AgentResponse>(`/api/v1/agents/${agentId}`, requestOptions);
  }
  /**Delete Agent
   * Delete an agent.

Args:
    agent_id: Agent ID
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Deletion result
   */
  public async deleteAgentApiV1AgentsAgentId(agentId: string): Promise<AgentDeleteResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<AgentDeleteResponse>(`/api/v1/agents/${agentId}`, requestOptions);
  }
  /**Interact with agent
   * Send a message to an agent and receive a response. Rate limited per user per agent.
   */
  public async interactWithAgentApiV1AgentsAgentIdInteract(agentId: string, data: AgentInteractRequest): Promise<AgentInteractResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<AgentInteractResponse>(`/api/v1/agents/${agentId}/interact`, requestOptions);
  }
  /**Get Agent Health
   * Get agent health status.

Args:
    agent_id: Agent ID
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Agent health information
   */
  public async getAgentHealthApiV1AgentsAgentIdHealth(agentId: string): Promise<AgentHealthResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<AgentHealthResponse>(`/api/v1/agents/${agentId}/health`, requestOptions);
  }
  /**Bulk Create Agents
   * Create multiple agents in bulk.

Args:
    request: Bulk creation request
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Bulk creation results
   */
  public async bulkCreateAgentsApiV1AgentsBulk(data: AgentBulkCreateRequest): Promise<AgentBulkCreateResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<AgentBulkCreateResponse>(`/api/v1/agents/bulk`, requestOptions);
  }
  /**Bulk Delete Agents
   * Delete multiple agents in bulk.

Args:
    request: Bulk deletion request
    current_user: Current authenticated user
    agent_manager: Agent manager instance

Returns:
    Bulk deletion results
   */
  public async bulkDeleteAgentsApiV1AgentsBulk(data: AgentBulkDeleteRequest): Promise<Record<string, unknown>> {
    const requestOptions = {
      method: 'DELETE' as const,
      body: data,
    };

    return this.request<Record<string, unknown>>(`/api/v1/agents/bulk`, requestOptions);
  }
}