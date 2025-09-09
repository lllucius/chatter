/**
 * Generated from OpenAPI schema: JobCreateRequest
 */
import { JobPriority } from './JobPriority';


export interface JobCreateRequest {
  /** Job name */
  name: string;
  /** Function to execute */
  function_name: string;
  /** Function arguments */
  args?: Record<string, unknown>[];
  /** Function keyword arguments */
  kwargs?: Record<string, unknown>;
  /** Job priority */
  priority?: JobPriority;
  /** Maximum retry attempts */
  max_retries?: number;
  /** Schedule job for later execution */
  schedule_at?: string | null;
}
