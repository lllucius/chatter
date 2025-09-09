/**
 * Generated from OpenAPI schema: BottleneckInfo
 */

export interface BottleneckInfo {
  /** Node ID with bottleneck */
  node_id: string;
  /** Node type */
  node_type: string;
  /** Bottleneck reason */
  reason: string;
  /** Bottleneck severity (low/medium/high) */
  severity: string;
  /** Optimization suggestions */
  suggestions: string[];
}
