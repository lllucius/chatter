/**
 * Generated from OpenAPI schema: WorkflowAnalyticsResponse
 */
import { BottleneckInfo } from './BottleneckInfo';
import { ComplexityMetrics } from './ComplexityMetrics';
import { OptimizationSuggestion } from './OptimizationSuggestion';


export interface WorkflowAnalyticsResponse {
  /** Complexity metrics */
  complexity: ComplexityMetrics;
  /** Identified bottlenecks */
  bottlenecks: BottleneckInfo[];
  /** Optimization suggestions */
  optimization_suggestions: OptimizationSuggestion[];
  /** Number of possible execution paths */
  execution_paths: number;
  /** Estimated execution time */
  estimated_execution_time_ms?: number | null;
  /** Identified risk factors */
  risk_factors: string[];
  /** Total execution time */
  total_execution_time_ms: number;
  /** Error message if failed */
  error?: string | null;
  /** Execution start time */
  started_at: string;
  /** Execution completion time */
  completed_at?: string | null;
}
