/**
 * Generated from OpenAPI schema: StatisticalAnalysis
 */
export interface StatisticalAnalysis {
  /** Confidence level used */
  confidence_level: number;
  /** Is result statistically significant */
  statistical_significance: boolean;
  /** P-value */
  p_value: number;
  /** Effect size */
  effect_size: number;
  /** Statistical power */
  power: number;
  /** Confidence intervals by variant */
  confidence_intervals: Record<string, number[]>;
}
