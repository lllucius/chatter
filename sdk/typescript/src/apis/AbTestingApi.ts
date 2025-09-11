/**
 * Generated API client for A/B Testing
 */
import { ABTestActionResponse, ABTestCreateRequest, ABTestDeleteResponse, ABTestListResponse, ABTestMetricsResponse, ABTestResponse, ABTestResultsResponse, ABTestUpdateRequest, TestStatus, TestType } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

export class AbTestingApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Ab Test
   * Create a new A/B test.

Args:
    test_data: A/B test creation data
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Created test data
   */
  public async createAbTestApiV1AbTests(data: ABTestCreateRequest): Promise<ABTestResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestResponse>;
  }
  /**List Ab Tests
   * List A/B tests with optional filtering.

Args:
    request: List request parameters
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    List of A/B tests
   */
  public async listAbTestsApiV1AbTests(data: string[] | null, options?: { status?: TestStatus | null; testType?: TestType | null; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ABTestListResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/`,
      method: 'GET' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      query: {
        'status': options?.status,
        'test_type': options?.testType,
        ...options?.query
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestListResponse>;
  }
  /**Get Ab Test
   * Get A/B test by ID.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    A/B test data
   */
  public async getAbTestApiV1AbTestsTestId(testId: string): Promise<ABTestResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestResponse>;
  }
  /**Update Ab Test
   * Update an A/B test.

Args:
    test_id: Test ID
    test_data: Test update data
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Updated test data
   */
  public async updateAbTestApiV1AbTestsTestId(testId: string, data: ABTestUpdateRequest): Promise<ABTestResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestResponse>;
  }
  /**Delete Ab Test
   * Delete an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Deletion result
   */
  public async deleteAbTestApiV1AbTestsTestId(testId: string): Promise<ABTestDeleteResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestDeleteResponse>;
  }
  /**Start Ab Test
   * Start an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result
   */
  public async startAbTestApiV1AbTestsTestIdStart(testId: string): Promise<ABTestActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/start`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestActionResponse>;
  }
  /**Pause Ab Test
   * Pause an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result
   */
  public async pauseAbTestApiV1AbTestsTestIdPause(testId: string): Promise<ABTestActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/pause`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestActionResponse>;
  }
  /**Complete Ab Test
   * Complete an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result
   */
  public async completeAbTestApiV1AbTestsTestIdComplete(testId: string): Promise<ABTestActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/complete`,
      method: 'POST' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestActionResponse>;
  }
  /**Get Ab Test Results
   * Get A/B test results and analysis.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Test results and analysis
   */
  public async getAbTestResultsApiV1AbTestsTestIdResults(testId: string): Promise<ABTestResultsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/results`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestResultsResponse>;
  }
  /**Get Ab Test Metrics
   * Get current A/B test metrics.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Current test metrics
   */
  public async getAbTestMetricsApiV1AbTestsTestIdMetrics(testId: string): Promise<ABTestMetricsResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/metrics`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestMetricsResponse>;
  }
  /**End Ab Test
   * End A/B test and declare winner.

Args:
    test_id: A/B test ID
    winner_variant: Winning variant identifier
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action response
   */
  public async endAbTestApiV1AbTestsTestIdEnd(testId: string, options?: { winnerVariant?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ABTestActionResponse> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/end`,
      method: 'POST' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
      query: {
        'winner_variant': options?.winnerVariant,
        ...options?.query
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ABTestActionResponse>;
  }
  /**Get Ab Test Performance
   * Get A/B test performance results by variant.

Args:
    test_id: A/B test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Performance results per variant
   */
  public async getAbTestPerformanceApiV1AbTestsTestIdPerformance(testId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/performance`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
  /**Get Ab Test Recommendations
   * Get comprehensive recommendations for an A/B test.

Args:
    test_id: A/B test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Recommendations and insights for the test
   */
  public async getAbTestRecommendationsApiV1AbTestsTestIdRecommendations(testId: string): Promise<Record<string, unknown>> {
    const requestContext: RequestOpts = {
      path: `/api/v1/ab-tests/${testId}/recommendations`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<Record<string, unknown>>;
  }
}