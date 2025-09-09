/**
 * Generated from OpenAPI schema: PluginResponse
 */
import { PluginStatus } from './PluginStatus';
import { PluginType } from './PluginType';


export interface PluginResponse {
  /** Plugin ID */
  id: string;
  /** Plugin name */
  name: string;
  /** Plugin version */
  version: string;
  /** Plugin description */
  description: string;
  /** Plugin author */
  author: string;
  /** Plugin type */
  plugin_type: PluginType;
  /** Plugin status */
  status: PluginStatus;
  /** Plugin entry point */
  entry_point: string;
  /** Plugin capabilities */
  capabilities: Record<string, unknown>[];
  /** Plugin dependencies */
  dependencies: string[];
  /** Required permissions */
  permissions: string[];
  /** Whether plugin is enabled */
  enabled: boolean;
  /** Error message if any */
  error_message?: string | null;
  /** Installation timestamp */
  installed_at: string;
  /** Last update timestamp */
  updated_at: string;
  /** Additional metadata */
  metadata: Record<string, unknown>;
}
