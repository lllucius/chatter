/**
 * Generated from OpenAPI schema: PluginStatsResponse
 */
export interface PluginStatsResponse {
  /** Total number of plugins */
  total_plugins: number;
  /** Number of active plugins */
  active_plugins: number;
  /** Number of inactive plugins */
  inactive_plugins: number;
  /** Plugin count by type */
  plugin_types: Record<string, number>;
  /** Plugin installation directory */
  plugins_directory: string;
}
