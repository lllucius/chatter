/**
 * Generated API client for A/B Testing
 */
import { ABTestActionResponse, ABTestCreateRequest, ABTestDeleteResponse, ABTestListResponse, ABTestMetricsResponse, ABTestResponse, ABTestResultsResponse, ABTestUpdateRequest, Record } from '../models/index';
import { BaseAPI, Configuration, RequestOptions } from '../runtime';

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
    const requestOptions: RequestOptions = {
      method: 'POST',
      body: data,
    };

    return this.request<ABTestResponse>(`/api/v1/ab-tests/`, requestOptions);
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
  public async listAbTestsApiV1AbTests(data: string[] | null, options?: RequestOptions): Promise<ABTestListResponse> {
    const requestOptions: RequestOptions = {
      method: 'GET',
      headers: options?.headers,
      query: {
        'status': options?.status,
        'test_type': options?.testType,
      },
      body: data,
    };

    return this.request<ABTestListResponse>(`/api/v1/ab-tests/`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ABTestResponse>(`/api/v1/ab-tests/${testId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'PUT',
      body: data,
    };

    return this.request<ABTestResponse>(`/api/v1/ab-tests/${testId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'DELETE',
    };

    return this.request<ABTestDeleteResponse>(`/api/v1/ab-tests/${testId}`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ABTestActionResponse>(`/api/v1/ab-tests/${testId}/start`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ABTestActionResponse>(`/api/v1/ab-tests/${testId}/pause`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'POST',
    };

    return this.request<ABTestActionResponse>(`/api/v1/ab-tests/${testId}/complete`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ABTestResultsResponse>(`/api/v1/ab-tests/${testId}/results`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<ABTestMetricsResponse>(`/api/v1/ab-tests/${testId}/metrics`, requestOptions);
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
  public async endAbTestApiV1AbTestsTestIdEnd(testId: string, options?: RequestOptions): Promise<ABTestActionResponse> {
    const requestOptions: RequestOptions = {
      method: 'POST',
      headers: options?.headers,
      query: {
        'winner_variant': options?.winnerVariant ?? '',
      },
    };

    return this.request<ABTestActionResponse>(`/api/v1/ab-tests/${testId}/end`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/api/v1/ab-tests/${testId}/performance`, requestOptions);
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
    const requestOptions: RequestOptions = {
      method: 'GET',
    };

    return this.request<Record<string, unknown>>(`/api/v1/ab-tests/${testId}/recommendations`, requestOptions);
  }
}