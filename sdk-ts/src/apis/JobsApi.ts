/**
 * Generated API client for Jobs
 */
import { JobActionResponse, JobCreateRequest, JobListResponse, JobResponse, JobStatsResponse, Record } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

export class JobsApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Job
   * Create a new job.

Args:
    job_data: Job creation data
    current_user: Current authenticated user

Returns:
    Created job data
   */
  public async createJobApiV1Jobs(data: JobCreateRequest): Promise<JobResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<JobResponse>(`/api/v1/jobs/`, requestOptions);
  }
  /**List Jobs
   * List jobs with optional filtering and pagination.

Args:
    request: List request parameters
    current_user: Current authenticated user

Returns:
    List of jobs with pagination info
   */
  public async listJobsApiV1Jobs(data: string[] | null, options?: RequestOptions): Promise<JobListResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'status': options?.status,
        'priority': options?.priority,
        'function_name': options?.functionName,
        'created_after': options?.createdAfter,
        'created_before': options?.createdBefore,
        'search': options?.search,
        'limit': options?.limit,
        'offset': options?.offset,
        'sort_by': options?.sortBy,
        'sort_order': options?.sortOrder,
      },
      body: data,
    };

    return this.request<JobListResponse>(`/api/v1/jobs/`, requestOptions);
  }
  /**Get Job
   * Get job by ID.

Args:
    job_id: Job ID
    current_user: Current authenticated user

Returns:
    Job data
   */
  public async getJobApiV1JobsJobId(jobId: string): Promise<JobResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<JobResponse>(`/api/v1/jobs/${jobId}`, requestOptions);
  }
  /**Cancel Job
   * Cancel a job.

Args:
    job_id: Job ID
    current_user: Current authenticated user

Returns:
    Cancellation result
   */
  public async cancelJobApiV1JobsJobIdCancel(jobId: string): Promise<JobActionResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<JobActionResponse>(`/api/v1/jobs/${jobId}/cancel`, requestOptions);
  }
  /**Get Job Stats
   * Get job queue statistics.

Args:
    current_user: Current authenticated user

Returns:
    Job statistics
   */
  public async getJobStatsApiV1JobsStatsOverview(): Promise<JobStatsResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<JobStatsResponse>(`/api/v1/jobs/stats/overview`, requestOptions);
  }
  /**Cleanup Jobs
   * Clean up old completed jobs to free up memory.

Note: This is a system-wide cleanup operation that affects all users.
Only completed, failed, or cancelled jobs older than 24 hours are removed.

Args:
    force: If True, remove all completed/failed jobs regardless of age
    current_user: Current authenticated user

Returns:
    Cleanup statistics
   */
  public async cleanupJobsApiV1JobsCleanup(options?: RequestOptions): Promise<Record<string, unknown>> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      headers: options?.headers,
      query: {
        'force': options?.force,
      },
    };

    return this.request<Record<string, unknown>>(`/api/v1/jobs/cleanup`, requestOptions);
  }
}