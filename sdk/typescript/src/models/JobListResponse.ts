/**
 * Generated from OpenAPI schema: JobListResponse
 */
import { JobResponse } from './JobResponse';

export interface JobListResponse {
  /** List of jobs */
  jobs: JobResponse[];
  /** Total number of jobs */
  total: number;
  /** Maximum results per page */
  limit: number;
  /** Number of results skipped */
  offset: number;
  /** Whether more results exist */
  has_more: boolean;
}
