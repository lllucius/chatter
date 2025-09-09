/**
 * Generated from OpenAPI schema: PluginInstallRequest
 */

export interface PluginInstallRequest {
  /** Path to plugin file or directory */
  plugin_path: string;
  /** Enable plugin after installation */
  enable_on_install?: boolean;
}
