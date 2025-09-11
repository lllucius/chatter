/**
 * Generated API client for Profiles
 */
import { AvailableProvidersResponse, ProfileCloneRequest, ProfileCreate, ProfileDeleteResponse, ProfileListResponse, ProfileResponse, ProfileStatsResponse, ProfileTestRequest, ProfileTestResponse, ProfileType, ProfileUpdate } from '../models/index';
import { BaseAPI, Configuration, RequestOpts, HTTPMethod, HTTPQuery, HTTPHeaders } from '../runtime';

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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles`,
      method: 'GET' as HTTPMethod,
      headers: {
        ...options?.headers,
      },
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

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileListResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/${profileId}`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/${profileId}`,
      method: 'PUT' as HTTPMethod,
      headers: {
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/${profileId}`,
      method: 'DELETE' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileDeleteResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/${profileId}/test`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileTestResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/${profileId}/clone`,
      method: 'POST' as HTTPMethod,
      headers: {
        'Content-Type': 'application/json',
      },
      body: data,
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/stats/overview`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<ProfileStatsResponse>;
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
    const requestContext: RequestOpts = {
      path: `/api/v1/profiles/providers/available`,
      method: 'GET' as HTTPMethod,
      headers: {
      },
    };

    const response = await this.request(requestContext);
    return response.json() as Promise<AvailableProvidersResponse>;
  }
}