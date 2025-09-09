/**
 * Generated API client for Tool Servers
 */
import { BulkOperationResult, BulkToolServerOperation, Record, RoleToolAccessCreate, RoleToolAccessResponse, ServerToolsResponse, ToolAccessResult, ToolOperationResponse, ToolPermissionCreate, ToolPermissionResponse, ToolPermissionUpdate, ToolServerCreate, ToolServerDeleteResponse, ToolServerHealthCheck, ToolServerMetrics, ToolServerOperationResponse, ToolServerResponse, ToolServerUpdate, UserToolAccessCheck } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ToolServerResponse>(`/api/v1/toolservers/servers`, requestOptions);
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
  public async listToolServersApiV1ToolserversServers(options?: RequestOptions): Promise<ToolServerResponse[]> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'status': options?.status,
        'include_builtin': options?.includeBuiltin,
      },
    };

    return this.request<ToolServerResponse[]>(`/api/v1/toolservers/servers`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ToolServerResponse>(`/api/v1/toolservers/servers/${serverId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<ToolServerResponse>(`/api/v1/toolservers/servers/${serverId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<ToolServerDeleteResponse>(`/api/v1/toolservers/servers/${serverId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolServerOperationResponse>(`/api/v1/toolservers/servers/${serverId}/start`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolServerOperationResponse>(`/api/v1/toolservers/servers/${serverId}/stop`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolServerOperationResponse>(`/api/v1/toolservers/servers/${serverId}/restart`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolServerOperationResponse>(`/api/v1/toolservers/servers/${serverId}/enable`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolServerOperationResponse>(`/api/v1/toolservers/servers/${serverId}/disable`, requestOptions);
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
  public async getServerToolsApiV1ToolserversServersServerIdTools(serverId: string, options?: RequestOptions): Promise<ServerToolsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'limit': options?.limit,
        'offset': options?.offset,
      },
    };

    return this.request<ServerToolsResponse>(`/api/v1/toolservers/servers/${serverId}/tools`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolOperationResponse>(`/api/v1/toolservers/tools/${toolId}/enable`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ToolOperationResponse>(`/api/v1/toolservers/tools/${toolId}/disable`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ToolServerMetrics>(`/api/v1/toolservers/servers/${serverId}/metrics`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ToolServerHealthCheck>(`/api/v1/toolservers/servers/${serverId}/health`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<BulkOperationResult>(`/api/v1/toolservers/servers/bulk`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>[]>(`/api/v1/toolservers/tools/all`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<Record<string, unknown>>(`/api/v1/toolservers/servers/${serverId}/test-connectivity`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ToolPermissionResponse>(`/api/v1/toolservers/permissions`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<ToolPermissionResponse>(`/api/v1/toolservers/permissions/${permissionId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<Record<string, unknown>>(`/api/v1/toolservers/permissions/${permissionId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ToolPermissionResponse[]>(`/api/v1/toolservers/users/${userId}/permissions`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<RoleToolAccessResponse>(`/api/v1/toolservers/role-access`, requestOptions);
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
  public async getRoleAccessRulesApiV1ToolserversRoleAccess(options?: RequestOptions): Promise<RoleToolAccessResponse[]> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'role': options?.role,
      },
    };

    return this.request<RoleToolAccessResponse[]>(`/api/v1/toolservers/role-access`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ToolAccessResult>(`/api/v1/toolservers/access-check`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<Record<string, unknown>>(`/api/v1/toolservers/servers/${serverId}/refresh-tools`, requestOptions);
  }
}