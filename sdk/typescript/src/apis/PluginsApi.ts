/**
 * Generated API client for Plugins
 */
import { PluginActionResponse, PluginDeleteResponse, PluginHealthCheckResponse, PluginInstallRequest, PluginListResponse, PluginResponse, PluginStatsResponse, PluginStatus, PluginType, PluginUpdateRequest } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class PluginsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Install Plugin
   * Install a new plugin.

Args:
    install_data: Plugin installation data
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Installed plugin data
   */
  public async installPluginApiV1PluginsInstall(data: PluginInstallRequest): Promise<PluginResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/install`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginResponse>;
  }
  /**List Plugins
   * List installed plugins with optional filtering.

Args:
    plugin_type: Filter by plugin type
    status: Filter by status
    enabled: Filter by enabled status
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    List of installed plugins
   */
  public async listPluginsApiV1Plugins(options?: { pluginType?: PluginType | null; status?: PluginStatus | null; enabled?: boolean | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PluginListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'plugin_type': options?.pluginType,
        'status': options?.status,
        'enabled': options?.enabled,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginListResponse>;
  }
  /**Get Plugin
   * Get plugin by ID.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Plugin data
   */
  public async getPluginApiV1PluginsPluginId(pluginId: string): Promise<PluginResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginResponse>;
  }
  /**Update Plugin
   * Update a plugin.

Args:
    plugin_id: Plugin ID
    update_data: Plugin update data
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Updated plugin data
   */
  public async updatePluginApiV1PluginsPluginId(pluginId: string, data: PluginUpdateRequest): Promise<PluginResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginResponse>;
  }
  /**Uninstall Plugin
   * Uninstall a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Uninstall result
   */
  public async uninstallPluginApiV1PluginsPluginId(pluginId: string): Promise<PluginDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginDeleteResponse>;
  }
  /**Enable Plugin
   * Enable a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Action result
   */
  public async enablePluginApiV1PluginsPluginIdEnable(pluginId: string): Promise<PluginActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}/enable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginActionResponse>;
  }
  /**Disable Plugin
   * Disable a plugin.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Action result
   */
  public async disablePluginApiV1PluginsPluginIdDisable(pluginId: string): Promise<PluginActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}/disable`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginActionResponse>;
  }
  /**Health Check Plugins
   * Perform health check on all plugins.

Args:
    auto_disable_unhealthy: Whether to automatically disable unhealthy plugins
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Health check results
   */
  public async healthCheckPluginsApiV1PluginsHealth(options?: { autoDisableUnhealthy?: boolean; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PluginHealthCheckResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/health`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'auto_disable_unhealthy': options?.autoDisableUnhealthy,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginHealthCheckResponse>;
  }
  /**Get Plugin Stats
   * Get plugin system statistics.

Args:
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Plugin system statistics
   */
  public async getPluginStatsApiV1PluginsStats(): Promise<PluginStatsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/stats`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<PluginStatsResponse>;
  }
  /**Check Plugin Dependencies
   * Check plugin dependencies.

Args:
    plugin_id: Plugin ID
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Dependency check results
   */
  public async checkPluginDependenciesApiV1PluginsPluginIdDependencies(pluginId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/${pluginId}/dependencies`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Bulk Enable Plugins
   * Enable multiple plugins.

Args:
    plugin_ids: List of plugin IDs to enable
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Bulk operation results
   */
  public async bulkEnablePluginsApiV1PluginsBulkEnable(data: string[]): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/bulk/enable`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Bulk Disable Plugins
   * Disable multiple plugins.

Args:
    plugin_ids: List of plugin IDs to disable
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    Bulk operation results
   */
  public async bulkDisablePluginsApiV1PluginsBulkDisable(data: string[]): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/plugins/bulk/disable`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}