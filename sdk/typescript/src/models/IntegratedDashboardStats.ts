/**
 * Generated from OpenAPI schema: IntegratedDashboardStats
 */
export interface IntegratedDashboardStats {
  /** Workflow statistics */
  workflows: Record<string, unknown>;
  /** Agent statistics */
  agents: Record<string, unknown>;
  /** A/B testing statistics */
  ab_testing: Record<string, unknown>;
  /** System statistics */
  system: Record<string, unknown>;
}
