/**
 * Generated from OpenAPI schema: PluginListResponse
 */
import { PluginResponse } from './PluginResponse';

export interface PluginListResponse {
  /** List of plugins */
  plugins: PluginResponse[];
  /** Total number of plugins */
  total: number;
}
