/**
 * Generated API client for Agents
 */
import { AgentBulkCreateRequest, AgentBulkCreateResponse, AgentBulkDeleteRequest, AgentCreateRequest, AgentDeleteResponse, AgentHealthResponse, AgentInteractRequest, AgentInteractResponse, AgentListResponse, AgentResponse, AgentStatsResponse, AgentStatus, AgentType, AgentUpdateRequest, Body_list_agents_api_v1_agents__get } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class AgentsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create a new agent
   * Create a new AI agent with specified configuration and capabilities.
   */
  public async createAgentApiV1Agents(data: AgentCreateRequest): Promise<AgentResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentResponse>;
  }
  /**List agents
   * List all agents with optional filtering and pagination. Users can only see their own agents.
   */
  public async listAgentsApiV1Agents(data: Body_list_agents_api_v1_agents__get, options?: { agentType?: AgentType | null; status?: AgentStatus | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<AgentListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/`,
      method: 'GET' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      query: {
        'agent_type': options?.agentType,
        'status': options?.status,
        ...options?.query
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentListResponse>;
  }
  /**Get agent templates
   * Get predefined agent templates for common use cases.
   */
  public async getAgentTemplatesApiV1AgentsTemplates(): Promise<Record<string, unknown>[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/templates`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>[]>;
  }
  /**Get agent statistics
   * Get comprehensive statistics about all agents for the current user.
   */
  public async getAgentStatsApiV1AgentsStatsOverview(): Promise<AgentStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/stats/overview`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentStatsResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/${agentId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/${agentId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/${agentId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentDeleteResponse>;
  }
  /**Interact with agent
   * Send a message to an agent and receive a response. Rate limited per user per agent.
   */
  public async interactWithAgentApiV1AgentsAgentIdInteract(agentId: string, data: AgentInteractRequest): Promise<AgentInteractResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/${agentId}/interact`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentInteractResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/${agentId}/health`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentHealthResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/bulk`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AgentBulkCreateResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/agents/bulk`,
      method: 'DELETE' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}