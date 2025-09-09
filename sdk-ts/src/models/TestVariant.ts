/**
 * Generated from OpenAPI schema: TestVariant
 */

export interface TestVariant {
  /** Variant name */
  name: string;
  /** Variant description */
  description: string;
  /** Variant configuration */
  configuration: Record<string, unknown>;
  /** Variant weight for allocation */
  weight?: number;
}
