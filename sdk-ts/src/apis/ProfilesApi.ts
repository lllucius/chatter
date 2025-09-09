/**
 * Generated API client for Profiles
 */
import { AvailableProvidersResponse, ProfileCloneRequest, ProfileCreate, ProfileDeleteResponse, ProfileListResponse, ProfileResponse, ProfileStatsResponse, ProfileTestRequest, ProfileTestResponse, ProfileType, ProfileUpdate } from '../models/index';
import { BaseAPI, Configuration, HTTPQuery, HTTPHeaders } from '../runtime';

export class ProfilesApi extends BaseAPI {
  constructor(configuration?: Configuration) {
    super(configuration);
  }

  /**Create Profile
   * Create a new LLM profile.

Args:
    profile_data: Profile creation data
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Created profile information
   */
  public async createProfileApiV1Profiles(data: ProfileCreate): Promise<ProfileResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<ProfileResponse>(`/api/v1/profiles/`, requestOptions);
  }
  /**List Profiles
   * List user's profiles.

Args:
    profile_type: Filter by profile type
    llm_provider: Filter by LLM provider
    tags: Filter by tags
    is_public: Filter by public status
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    List of profiles with pagination info
   */
  public async listProfilesApiV1Profiles(options?: { profileType?: ProfileType | null; llmProvider?: string | null; tags?: string[] | null; isPublic?: boolean | null; limit?: number; offset?: number; sortBy?: string; sortOrder?: string; query?: HTTPQuery; headers?: HTTPHeaders; }): Promise<ProfileListResponse> {
    const requestOptions = {
      method: 'GET' as const,
      headers: options?.headers,
      query: {
        'profile_type': options?.profileType,
        'llm_provider': options?.llmProvider,
        'tags': options?.tags,
        'is_public': options?.isPublic,
        'limit': options?.limit,
        'offset': options?.offset,
        'sort_by': options?.sortBy,
        'sort_order': options?.sortOrder,
        ...options?.query
      },
    };

    return this.request<ProfileListResponse>(`/api/v1/profiles`, requestOptions);
  }
  /**Get Profile
   * Get profile details.

Args:
    profile_id: Profile ID
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Profile information
   */
  public async getProfileApiV1ProfilesProfileId(profileId: string): Promise<ProfileResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<ProfileResponse>(`/api/v1/profiles/${profileId}`, requestOptions);
  }
  /**Update Profile
   * Update profile.

Args:
    profile_id: Profile ID
    update_data: Update data
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Updated profile information
   */
  public async updateProfileApiV1ProfilesProfileId(profileId: string, data: ProfileUpdate): Promise<ProfileResponse> {
    const requestOptions = {
      method: 'PUT' as const,
      body: data,
    };

    return this.request<ProfileResponse>(`/api/v1/profiles/${profileId}`, requestOptions);
  }
  /**Delete Profile
   * Delete profile.

Args:
    profile_id: Profile ID
    request: Delete request parameters
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Success message
   */
  public async deleteProfileApiV1ProfilesProfileId(profileId: string): Promise<ProfileDeleteResponse> {
    const requestOptions = {
      method: 'DELETE' as const,
    };

    return this.request<ProfileDeleteResponse>(`/api/v1/profiles/${profileId}`, requestOptions);
  }
  /**Test Profile
   * Test profile with a sample message.

Args:
    profile_id: Profile ID
    test_request: Test request
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Test results
   */
  public async testProfileApiV1ProfilesProfileIdTest(profileId: string, data: ProfileTestRequest): Promise<ProfileTestResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<ProfileTestResponse>(`/api/v1/profiles/${profileId}/test`, requestOptions);
  }
  /**Clone Profile
   * Clone an existing profile.

Args:
    profile_id: Source profile ID
    clone_request: Clone request
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Cloned profile information
   */
  public async cloneProfileApiV1ProfilesProfileIdClone(profileId: string, data: ProfileCloneRequest): Promise<ProfileResponse> {
    const requestOptions = {
      method: 'POST' as const,
      body: data,
    };

    return this.request<ProfileResponse>(`/api/v1/profiles/${profileId}/clone`, requestOptions);
  }
  /**Get Profile Stats
   * Get profile statistics.

Args:
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Profile statistics
   */
  public async getProfileStatsApiV1ProfilesStatsOverview(): Promise<ProfileStatsResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<ProfileStatsResponse>(`/api/v1/profiles/stats/overview`, requestOptions);
  }
  /**Get Available Providers
   * Get available LLM providers.

Args:
    request: Providers request parameters
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Available providers information
   */
  public async getAvailableProvidersApiV1ProfilesProvidersAvailable(): Promise<AvailableProvidersResponse> {
    const requestOptions = {
      method: 'GET' as const,
    };

    return this.request<AvailableProvidersResponse>(`/api/v1/profiles/providers/available`, requestOptions);
  }
}