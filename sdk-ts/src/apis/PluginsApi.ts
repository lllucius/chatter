/**
 * Generated API client for Plugins
 */
import { PluginActionResponse, PluginDeleteResponse, PluginHealthCheckResponse, PluginInstallRequest, PluginListResponse, PluginResponse, PluginStatsResponse, PluginStatus, PluginType, PluginUpdateRequest } from '../models/index';
import { BaseAPI, Configuration, HTTPQuery, HTTPHeaders } from '../runtime';

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
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<PluginResponse>(`/api/v1/plugins/install`, requestOptions);
  }
  /**List Plugins
   * List installed plugins with optional filtering.

Args:
    request: List request parameters
    current_user: Current authenticated user
    plugin_manager: Plugin manager instance

Returns:
    List of installed plugins
   */
  public async listPluginsApiV1Plugins(options?: { pluginType?: PluginType | null; status?: PluginStatus | null; enabled?: boolean | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<PluginListResponse> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'plugin_type': options?.pluginType,
        'status': options?.status,
        'enabled': options?.enabled,
        ...options?.query
      },
    };

    return this.request<PluginListResponse>(`/api/v1/plugins/`, requestOptions);
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
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<PluginResponse>(`/api/v1/plugins/${pluginId}`, requestOptions);
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
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<PluginResponse>(`/api/v1/plugins/${pluginId}`, requestOptions);
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
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<PluginDeleteResponse>(`/api/v1/plugins/${pluginId}`, requestOptions);
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
    const requestOptions = {
      method: 'POST' as const,
    };

    return this.request<PluginActionResponse>(`/api/v1/plugins/${pluginId}/enable`, requestOptions);
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
    const requestOptions = {
      method: 'POST' as const,
    };

    return this.request<PluginActionResponse>(`/api/v1/plugins/${pluginId}/disable`, requestOptions);
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
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'auto_disable_unhealthy': options?.autoDisableUnhealthy,
        ...options?.query
      },
    };

    return this.request<PluginHealthCheckResponse>(`/api/v1/plugins/health`, requestOptions);
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
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<PluginStatsResponse>(`/api/v1/plugins/stats`, requestOptions);
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
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<Record<string, unknown>>(`/api/v1/plugins/${pluginId}/dependencies`, requestOptions);
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
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<Record<string, unknown>>(`/api/v1/plugins/bulk/enable`, requestOptions);
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
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<Record<string, unknown>>(`/api/v1/plugins/bulk/disable`, requestOptions);
  }
}