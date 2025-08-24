# ProfilesApi

All URIs are relative to *http://localhost:8000*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**cloneProfileApiV1ProfilesProfileIdClonePost**](#cloneprofileapiv1profilesprofileidclonepost) | **POST** /api/v1/profiles/{profile_id}/clone | Clone Profile|
|[**createProfileApiV1ProfilesPost**](#createprofileapiv1profilespost) | **POST** /api/v1/profiles/ | Create Profile|
|[**deleteProfileApiV1ProfilesProfileIdDelete**](#deleteprofileapiv1profilesprofileiddelete) | **DELETE** /api/v1/profiles/{profile_id} | Delete Profile|
|[**getAvailableProvidersApiV1ProfilesProvidersAvailableGet**](#getavailableprovidersapiv1profilesprovidersavailableget) | **GET** /api/v1/profiles/providers/available | Get Available Providers|
|[**getProfileApiV1ProfilesProfileIdGet**](#getprofileapiv1profilesprofileidget) | **GET** /api/v1/profiles/{profile_id} | Get Profile|
|[**getProfileStatsApiV1ProfilesStatsOverviewGet**](#getprofilestatsapiv1profilesstatsoverviewget) | **GET** /api/v1/profiles/stats/overview | Get Profile Stats|
|[**listProfilesApiV1ProfilesGet**](#listprofilesapiv1profilesget) | **GET** /api/v1/profiles | List Profiles|
|[**testProfileApiV1ProfilesProfileIdTestPost**](#testprofileapiv1profilesprofileidtestpost) | **POST** /api/v1/profiles/{profile_id}/test | Test Profile|
|[**updateProfileApiV1ProfilesProfileIdPut**](#updateprofileapiv1profilesprofileidput) | **PUT** /api/v1/profiles/{profile_id} | Update Profile|

# **cloneProfileApiV1ProfilesProfileIdClonePost**
> ProfileResponse cloneProfileApiV1ProfilesProfileIdClonePost(profileCloneRequest)

Clone an existing profile.  Args:     profile_id: Source profile ID     clone_request: Clone request     current_user: Current authenticated user     profile_service: Profile service  Returns:     Cloned profile information

### Example

```typescript
import {
    ProfilesApi,
    Configuration,
    ProfileCloneRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileId: string; // (default to undefined)
let profileCloneRequest: ProfileCloneRequest; //

const { status, data } = await apiInstance.cloneProfileApiV1ProfilesProfileIdClonePost(
    profileId,
    profileCloneRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileCloneRequest** | **ProfileCloneRequest**|  | |
| **profileId** | [**string**] |  | defaults to undefined|


### Return type

**ProfileResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **createProfileApiV1ProfilesPost**
> ProfileResponse createProfileApiV1ProfilesPost(profileCreate)

Create a new LLM profile.  Args:     profile_data: Profile creation data     current_user: Current authenticated user     profile_service: Profile service  Returns:     Created profile information

### Example

```typescript
import {
    ProfilesApi,
    Configuration,
    ProfileCreate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileCreate: ProfileCreate; //

const { status, data } = await apiInstance.createProfileApiV1ProfilesPost(
    profileCreate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileCreate** | **ProfileCreate**|  | |


### Return type

**ProfileResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **deleteProfileApiV1ProfilesProfileIdDelete**
> ProfileDeleteResponse deleteProfileApiV1ProfilesProfileIdDelete()

Delete profile.  Args:     profile_id: Profile ID     request: Delete request parameters     current_user: Current authenticated user     profile_service: Profile service  Returns:     Success message

### Example

```typescript
import {
    ProfilesApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileId: string; // (default to undefined)

const { status, data } = await apiInstance.deleteProfileApiV1ProfilesProfileIdDelete(
    profileId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileId** | [**string**] |  | defaults to undefined|


### Return type

**ProfileDeleteResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getAvailableProvidersApiV1ProfilesProvidersAvailableGet**
> AvailableProvidersResponse getAvailableProvidersApiV1ProfilesProvidersAvailableGet()

Get available LLM providers.  Args:     request: Providers request parameters     current_user: Current authenticated user     profile_service: Profile service  Returns:     Available providers information

### Example

```typescript
import {
    ProfilesApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

const { status, data } = await apiInstance.getAvailableProvidersApiV1ProfilesProvidersAvailableGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**AvailableProvidersResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getProfileApiV1ProfilesProfileIdGet**
> ProfileResponse getProfileApiV1ProfilesProfileIdGet()

Get profile details.  Args:     profile_id: Profile ID     current_user: Current authenticated user     profile_service: Profile service  Returns:     Profile information

### Example

```typescript
import {
    ProfilesApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileId: string; // (default to undefined)

const { status, data } = await apiInstance.getProfileApiV1ProfilesProfileIdGet(
    profileId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileId** | [**string**] |  | defaults to undefined|


### Return type

**ProfileResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getProfileStatsApiV1ProfilesStatsOverviewGet**
> ProfileStatsResponse getProfileStatsApiV1ProfilesStatsOverviewGet()

Get profile statistics.  Args:     current_user: Current authenticated user     profile_service: Profile service  Returns:     Profile statistics

### Example

```typescript
import {
    ProfilesApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

const { status, data } = await apiInstance.getProfileStatsApiV1ProfilesStatsOverviewGet();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**ProfileStatsResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **listProfilesApiV1ProfilesGet**
> ProfileListResponse listProfilesApiV1ProfilesGet()

List user\'s profiles.  Args:     profile_type: Filter by profile type     llm_provider: Filter by LLM provider     tags: Filter by tags     is_public: Filter by public status     limit: Maximum number of results     offset: Number of results to skip     sort_by: Sort field     sort_order: Sort order (asc/desc)     current_user: Current authenticated user     profile_service: Profile service  Returns:     List of profiles with pagination info

### Example

```typescript
import {
    ProfilesApi,
    Configuration
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileType: ProfileType; //Filter by profile type (optional) (default to undefined)
let llmProvider: string; //Filter by LLM provider (optional) (default to undefined)
let tags: Array<string>; //Filter by tags (optional) (default to undefined)
let isPublic: boolean; //Filter by public status (optional) (default to undefined)
let limit: number; //Maximum number of results (optional) (default to 50)
let offset: number; //Number of results to skip (optional) (default to 0)
let sortBy: string; //Sort field (optional) (default to 'created_at')
let sortOrder: string; //Sort order (optional) (default to 'desc')

const { status, data } = await apiInstance.listProfilesApiV1ProfilesGet(
    profileType,
    llmProvider,
    tags,
    isPublic,
    limit,
    offset,
    sortBy,
    sortOrder
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileType** | **ProfileType** | Filter by profile type | (optional) defaults to undefined|
| **llmProvider** | [**string**] | Filter by LLM provider | (optional) defaults to undefined|
| **tags** | **Array&lt;string&gt;** | Filter by tags | (optional) defaults to undefined|
| **isPublic** | [**boolean**] | Filter by public status | (optional) defaults to undefined|
| **limit** | [**number**] | Maximum number of results | (optional) defaults to 50|
| **offset** | [**number**] | Number of results to skip | (optional) defaults to 0|
| **sortBy** | [**string**] | Sort field | (optional) defaults to 'created_at'|
| **sortOrder** | [**string**] | Sort order | (optional) defaults to 'desc'|


### Return type

**ProfileListResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **testProfileApiV1ProfilesProfileIdTestPost**
> ProfileTestResponse testProfileApiV1ProfilesProfileIdTestPost(profileTestRequest)

Test profile with a sample message.  Args:     profile_id: Profile ID     test_request: Test request     current_user: Current authenticated user     profile_service: Profile service  Returns:     Test results

### Example

```typescript
import {
    ProfilesApi,
    Configuration,
    ProfileTestRequest
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileId: string; // (default to undefined)
let profileTestRequest: ProfileTestRequest; //

const { status, data } = await apiInstance.testProfileApiV1ProfilesProfileIdTestPost(
    profileId,
    profileTestRequest
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileTestRequest** | **ProfileTestRequest**|  | |
| **profileId** | [**string**] |  | defaults to undefined|


### Return type

**ProfileTestResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **updateProfileApiV1ProfilesProfileIdPut**
> ProfileResponse updateProfileApiV1ProfilesProfileIdPut(profileUpdate)

Update profile.  Args:     profile_id: Profile ID     update_data: Update data     current_user: Current authenticated user     profile_service: Profile service  Returns:     Updated profile information

### Example

```typescript
import {
    ProfilesApi,
    Configuration,
    ProfileUpdate
} from 'chatter-sdk';

const configuration = new Configuration();
const apiInstance = new ProfilesApi(configuration);

let profileId: string; // (default to undefined)
let profileUpdate: ProfileUpdate; //

const { status, data } = await apiInstance.updateProfileApiV1ProfilesProfileIdPut(
    profileId,
    profileUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **profileUpdate** | **ProfileUpdate**|  | |
| **profileId** | [**string**] |  | defaults to undefined|


### Return type

**ProfileResponse**

### Authorization

[HTTPBearer](../README.md#HTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

