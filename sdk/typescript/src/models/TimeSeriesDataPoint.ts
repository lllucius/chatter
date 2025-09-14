/**
 * Generated from OpenAPI schema: TimeSeriesDataPoint
 */
export interface TimeSeriesDataPoint {
  /** Date label (e.g., 'Mon', 'Jan 01') */
  date: string;
  /** Number of conversations */
  conversations?: number | null;
  /** Token usage */
  tokens?: number | null;
  /** Cost */
  cost?: number | null;
  /** Number of workflows */
  workflows?: number | null;
  /** Number of agents */
  agents?: number | null;
  /** Number of A/B tests */
  abTests?: number | null;
}
