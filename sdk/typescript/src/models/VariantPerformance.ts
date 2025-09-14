/**
 * Generated from OpenAPI schema: VariantPerformance
 */
export interface VariantPerformance {
  /** Variant name */
  name: string;
  /** Number of participants */
  participants: number;
  /** Number of conversions */
  conversions: number;
  /** Conversion rate */
  conversion_rate: number;
  /** Total revenue */
  revenue?: number;
  /** Total cost */
  cost?: number;
  /** Return on investment */
  roi?: number;
}
