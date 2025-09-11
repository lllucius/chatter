/**
 * Generated API client for Tool Servers
 */
import { BulkOperationResult, BulkToolServerOperation, RoleToolAccessCreate, RoleToolAccessResponse, ServerStatus, ServerToolsResponse, ToolAccessResult, ToolOperationResponse, ToolPermissionCreate, ToolPermissionResponse, ToolPermissionUpdate, ToolServerCreate, ToolServerDeleteResponse, ToolServerHealthCheck, ToolServerMetrics, ToolServerOperationResponse, ToolServerResponse, ToolServerUpdate, UserToolAccessCheck } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class ToolServersApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Tool Server
   * Create a new tool server.

Args:
    server_data: Server creation data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Created server response
   */
  public async createToolServerApiV1ToolserversServers(data: ToolServerCreate): Promise<ToolServerResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerResponse>;
  }
  /**List Tool Servers
   * List tool servers with optional filtering.

Args:
    request: List request with filter parameters
    current_user: Current authenticated user
    service: Tool server service

Returns:
    List of server responses
   */
  public async listToolServersApiV1ToolserversServers(options?: { status?: ServerStatus | null; includeBuiltin?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ToolServerResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'status': options?.status,
        'include_builtin': options?.includeBuiltin,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerResponse[]>;
  }
  /**Get Tool Server
   * Get a tool server by ID.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Server response
   */
  public async getToolServerApiV1ToolserversServersServerId(serverId: string): Promise<ToolServerResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerResponse>;
  }
  /**Update Tool Server
   * Update a tool server.

Args:
    server_id: Server ID
    update_data: Update data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Updated server response
   */
  public async updateToolServerApiV1ToolserversServersServerId(serverId: string, data: ToolServerUpdate): Promise<ToolServerResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerResponse>;
  }
  /**Delete Tool Server
   * Delete a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Success message
   */
  public async deleteToolServerApiV1ToolserversServersServerId(serverId: string): Promise<ToolServerDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerDeleteResponse>;
  }
  /**Start Tool Server
   * Start a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async startToolServerApiV1ToolserversServersServerIdStart(serverId: string): Promise<ToolServerOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/start`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerOperationResponse>;
  }
  /**Stop Tool Server
   * Stop a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async stopToolServerApiV1ToolserversServersServerIdStop(serverId: string): Promise<ToolServerOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/stop`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerOperationResponse>;
  }
  /**Restart Tool Server
   * Restart a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async restartToolServerApiV1ToolserversServersServerIdRestart(serverId: string): Promise<ToolServerOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/restart`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerOperationResponse>;
  }
  /**Enable Tool Server
   * Enable a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async enableToolServerApiV1ToolserversServersServerIdEnable(serverId: string): Promise<ToolServerOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/enable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerOperationResponse>;
  }
  /**Disable Tool Server
   * Disable a tool server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async disableToolServerApiV1ToolserversServersServerIdDisable(serverId: string): Promise<ToolServerOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/disable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerOperationResponse>;
  }
  /**Get Server Tools
   * Get tools for a specific server.

Args:
    server_id: Server ID
    request: Server tools request with pagination
    current_user: Current authenticated user
    service: Tool server service

Returns:
    List of server tools with pagination
   */
  public async getServerToolsApiV1ToolserversServersServerIdTools(serverId: string, options?: { limit?: number; offset?: number; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ServerToolsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/tools`,
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
    return response.json() as Promise<ServerToolsResponse>;
  }
  /**Enable Tool
   * Enable a specific tool.

Args:
    tool_id: Tool ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async enableToolApiV1ToolserversToolsToolIdEnable(toolId: string): Promise<ToolOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/tools/${toolId}/enable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolOperationResponse>;
  }
  /**Disable Tool
   * Disable a specific tool.

Args:
    tool_id: Tool ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Operation result
   */
  public async disableToolApiV1ToolserversToolsToolIdDisable(toolId: string): Promise<ToolOperationResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/tools/${toolId}/disable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolOperationResponse>;
  }
  /**Get Server Metrics
   * Get analytics for a specific server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Server metrics
   */
  public async getServerMetricsApiV1ToolserversServersServerIdMetrics(serverId: string): Promise<ToolServerMetrics> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/metrics`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerMetrics>;
  }
  /**Check Server Health
   * Perform health check on a server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Health check result
   */
  public async checkServerHealthApiV1ToolserversServersServerIdHealth(serverId: string): Promise<ToolServerHealthCheck> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/health`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolServerHealthCheck>;
  }
  /**Bulk Server Operation
   * Perform bulk operations on multiple servers.

Args:
    operation_data: Bulk operation data
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Bulk operation result
   */
  public async bulkServerOperationApiV1ToolserversServersBulk(data: BulkToolServerOperation): Promise<BulkOperationResult> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/bulk`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<BulkOperationResult>;
  }
  /**List All Tools
   * List all tools across all servers.

Args:
    current_user: Current authenticated user
    tool_server_service: Tool server service

Returns:
    List of all available tools across all servers
   */
  public async listAllToolsApiV1ToolserversToolsAll(): Promise<Record<string, unknown>[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/tools/all`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>[]>;
  }
  /**Test Server Connectivity
   * Test connectivity to an external MCP server.

Args:
    server_id: Tool server ID
    current_user: Current authenticated user
    tool_server_service: Tool server service

Returns:
    Connectivity test results
   */
  public async testServerConnectivityApiV1ToolserversServersServerIdTestConnectivity(serverId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/test-connectivity`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Grant Tool Permission
   * Grant tool permission to a user.

Args:
    permission_data: Permission data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Created permission
   */
  public async grantToolPermissionApiV1ToolserversPermissions(data: ToolPermissionCreate): Promise<ToolPermissionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/permissions`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolPermissionResponse>;
  }
  /**Update Tool Permission
   * Update tool permission.

Args:
    permission_id: Permission ID
    update_data: Update data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Updated permission
   */
  public async updateToolPermissionApiV1ToolserversPermissionsPermissionId(permissionId: string, data: ToolPermissionUpdate): Promise<ToolPermissionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/permissions/${permissionId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolPermissionResponse>;
  }
  /**Revoke Tool Permission
   * Revoke tool permission.

Args:
    permission_id: Permission ID
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Success message
   */
  public async revokeToolPermissionApiV1ToolserversPermissionsPermissionId(permissionId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/permissions/${permissionId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get User Permissions
   * Get all permissions for a user.

Args:
    user_id: User ID
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    List of user permissions
   */
  public async getUserPermissionsApiV1ToolserversUsersUserIdPermissions(userId: string): Promise<ToolPermissionResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/users/${userId}/permissions`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolPermissionResponse[]>;
  }
  /**Create Role Access Rule
   * Create role-based access rule.

Args:
    rule_data: Rule data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Created rule
   */
  public async createRoleAccessRuleApiV1ToolserversRoleAccess(data: RoleToolAccessCreate): Promise<RoleToolAccessResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/role-access`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<RoleToolAccessResponse>;
  }
  /**Get Role Access Rules
   * Get role-based access rules.

Args:
    role: Optional role filter
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    List of access rules
   */
  public async getRoleAccessRulesApiV1ToolserversRoleAccess(options?: { role?: string | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<RoleToolAccessResponse[]> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/role-access`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'role': options?.role,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<RoleToolAccessResponse[]>;
  }
  /**Check Tool Access
   * Check if user has access to a tool.

Args:
    check_data: Access check data
    current_user: Current authenticated user
    access_service: Tool access service

Returns:
    Access check result
   */
  public async checkToolAccessApiV1ToolserversAccessCheck(data: UserToolAccessCheck): Promise<ToolAccessResult> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/access-check`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ToolAccessResult>;
  }
  /**Refresh Server Tools
   * Refresh tools for a remote server.

Args:
    server_id: Server ID
    current_user: Current authenticated user
    service: Tool server service

Returns:
    Refresh result
   */
  public async refreshServerToolsApiV1ToolserversServersServerIdRefreshTools(serverId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/toolservers/servers/${serverId}/refresh-tools`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}