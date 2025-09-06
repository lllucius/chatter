# chatter_sdk.ProfilesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**clone_profile_api_v1_profiles_profile_id_clone_post**](ProfilesApi.md#clone_profile_api_v1_profiles_profile_id_clone_post) | **POST** /api/v1/profiles/{profile_id}/clone | Clone Profile
[**create_profile_api_v1_profiles_post**](ProfilesApi.md#create_profile_api_v1_profiles_post) | **POST** /api/v1/profiles/ | Create Profile
[**delete_profile_api_v1_profiles_profile_id_delete**](ProfilesApi.md#delete_profile_api_v1_profiles_profile_id_delete) | **DELETE** /api/v1/profiles/{profile_id} | Delete Profile
[**get_available_providers_api_v1_profiles_providers_available_get**](ProfilesApi.md#get_available_providers_api_v1_profiles_providers_available_get) | **GET** /api/v1/profiles/providers/available | Get Available Providers
[**get_profile_api_v1_profiles_profile_id_get**](ProfilesApi.md#get_profile_api_v1_profiles_profile_id_get) | **GET** /api/v1/profiles/{profile_id} | Get Profile
[**get_profile_stats_api_v1_profiles_stats_overview_get**](ProfilesApi.md#get_profile_stats_api_v1_profiles_stats_overview_get) | **GET** /api/v1/profiles/stats/overview | Get Profile Stats
[**list_profiles_api_v1_profiles_get**](ProfilesApi.md#list_profiles_api_v1_profiles_get) | **GET** /api/v1/profiles | List Profiles
[**test_profile_api_v1_profiles_profile_id_test_post**](ProfilesApi.md#test_profile_api_v1_profiles_profile_id_test_post) | **POST** /api/v1/profiles/{profile_id}/test | Test Profile
[**update_profile_api_v1_profiles_profile_id_put**](ProfilesApi.md#update_profile_api_v1_profiles_profile_id_put) | **PUT** /api/v1/profiles/{profile_id} | Update Profile


# **clone_profile_api_v1_profiles_profile_id_clone_post**
> ProfileResponse clone_profile_api_v1_profiles_profile_id_clone_post(profile_id, profile_clone_request)

Clone Profile

Clone an existing profile.

Args:
    profile_id: Source profile ID
    clone_request: Clone request
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Cloned profile information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_clone_request import ProfileCloneRequest
from chatter_sdk.models.profile_response import ProfileResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_id = 'profile_id_example' # str | 
    profile_clone_request = chatter_sdk.ProfileCloneRequest() # ProfileCloneRequest | 

    try:
        # Clone Profile
        api_response = await api_instance.clone_profile_api_v1_profiles_profile_id_clone_post(profile_id, profile_clone_request)
        print("The response of ProfilesApi->clone_profile_api_v1_profiles_profile_id_clone_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->clone_profile_api_v1_profiles_profile_id_clone_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_id** | **str**|  | 
 **profile_clone_request** | [**ProfileCloneRequest**](ProfileCloneRequest.md)|  | 

### Return type

[**ProfileResponse**](ProfileResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_profile_api_v1_profiles_post**
> ProfileResponse create_profile_api_v1_profiles_post(profile_create)

Create Profile

Create a new LLM profile.

Args:
    profile_data: Profile creation data
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Created profile information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_create import ProfileCreate
from chatter_sdk.models.profile_response import ProfileResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_create = chatter_sdk.ProfileCreate() # ProfileCreate | 

    try:
        # Create Profile
        api_response = await api_instance.create_profile_api_v1_profiles_post(profile_create)
        print("The response of ProfilesApi->create_profile_api_v1_profiles_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->create_profile_api_v1_profiles_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_create** | [**ProfileCreate**](ProfileCreate.md)|  | 

### Return type

[**ProfileResponse**](ProfileResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_profile_api_v1_profiles_profile_id_delete**
> ProfileDeleteResponse delete_profile_api_v1_profiles_profile_id_delete(profile_id)

Delete Profile

Delete profile.

Args:
    profile_id: Profile ID
    request: Delete request parameters
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_delete_response import ProfileDeleteResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_id = 'profile_id_example' # str | 

    try:
        # Delete Profile
        api_response = await api_instance.delete_profile_api_v1_profiles_profile_id_delete(profile_id)
        print("The response of ProfilesApi->delete_profile_api_v1_profiles_profile_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->delete_profile_api_v1_profiles_profile_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_id** | **str**|  | 

### Return type

[**ProfileDeleteResponse**](ProfileDeleteResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_available_providers_api_v1_profiles_providers_available_get**
> AvailableProvidersResponse get_available_providers_api_v1_profiles_providers_available_get()

Get Available Providers

Get available LLM providers.

Args:
    request: Providers request parameters
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Available providers information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.available_providers_response import AvailableProvidersResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)

    try:
        # Get Available Providers
        api_response = await api_instance.get_available_providers_api_v1_profiles_providers_available_get()
        print("The response of ProfilesApi->get_available_providers_api_v1_profiles_providers_available_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->get_available_providers_api_v1_profiles_providers_available_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**AvailableProvidersResponse**](AvailableProvidersResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_profile_api_v1_profiles_profile_id_get**
> ProfileResponse get_profile_api_v1_profiles_profile_id_get(profile_id)

Get Profile

Get profile details.

Args:
    profile_id: Profile ID
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Profile information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_response import ProfileResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_id = 'profile_id_example' # str | 

    try:
        # Get Profile
        api_response = await api_instance.get_profile_api_v1_profiles_profile_id_get(profile_id)
        print("The response of ProfilesApi->get_profile_api_v1_profiles_profile_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->get_profile_api_v1_profiles_profile_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_id** | **str**|  | 

### Return type

[**ProfileResponse**](ProfileResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_profile_stats_api_v1_profiles_stats_overview_get**
> ProfileStatsResponse get_profile_stats_api_v1_profiles_stats_overview_get()

Get Profile Stats

Get profile statistics.

Args:
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Profile statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_stats_response import ProfileStatsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)

    try:
        # Get Profile Stats
        api_response = await api_instance.get_profile_stats_api_v1_profiles_stats_overview_get()
        print("The response of ProfilesApi->get_profile_stats_api_v1_profiles_stats_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->get_profile_stats_api_v1_profiles_stats_overview_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ProfileStatsResponse**](ProfileStatsResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_profiles_api_v1_profiles_get**
> ProfileListResponse list_profiles_api_v1_profiles_get(profile_type=profile_type, llm_provider=llm_provider, tags=tags, is_public=is_public, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

List Profiles

List user's profiles.

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

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_list_response import ProfileListResponse
from chatter_sdk.models.profile_type import ProfileType
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_type = chatter_sdk.ProfileType() # ProfileType | Filter by profile type (optional)
    llm_provider = 'llm_provider_example' # str | Filter by LLM provider (optional)
    tags = ['tags_example'] # List[str] | Filter by tags (optional)
    is_public = True # bool | Filter by public status (optional)
    limit = 50 # int | Maximum number of results (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)
    sort_by = 'created_at' # str | Sort field (optional) (default to 'created_at')
    sort_order = 'desc' # str | Sort order (optional) (default to 'desc')

    try:
        # List Profiles
        api_response = await api_instance.list_profiles_api_v1_profiles_get(profile_type=profile_type, llm_provider=llm_provider, tags=tags, is_public=is_public, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        print("The response of ProfilesApi->list_profiles_api_v1_profiles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->list_profiles_api_v1_profiles_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_type** | [**ProfileType**](.md)| Filter by profile type | [optional] 
 **llm_provider** | **str**| Filter by LLM provider | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by tags | [optional] 
 **is_public** | **bool**| Filter by public status | [optional] 
 **limit** | **int**| Maximum number of results | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]
 **sort_by** | **str**| Sort field | [optional] [default to &#39;created_at&#39;]
 **sort_order** | **str**| Sort order | [optional] [default to &#39;desc&#39;]

### Return type

[**ProfileListResponse**](ProfileListResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **test_profile_api_v1_profiles_profile_id_test_post**
> ProfileTestResponse test_profile_api_v1_profiles_profile_id_test_post(profile_id, profile_test_request)

Test Profile

Test profile with a sample message.

Args:
    profile_id: Profile ID
    test_request: Test request
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Test results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_test_request import ProfileTestRequest
from chatter_sdk.models.profile_test_response import ProfileTestResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_id = 'profile_id_example' # str | 
    profile_test_request = chatter_sdk.ProfileTestRequest() # ProfileTestRequest | 

    try:
        # Test Profile
        api_response = await api_instance.test_profile_api_v1_profiles_profile_id_test_post(profile_id, profile_test_request)
        print("The response of ProfilesApi->test_profile_api_v1_profiles_profile_id_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->test_profile_api_v1_profiles_profile_id_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_id** | **str**|  | 
 **profile_test_request** | [**ProfileTestRequest**](ProfileTestRequest.md)|  | 

### Return type

[**ProfileTestResponse**](ProfileTestResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_profile_api_v1_profiles_profile_id_put**
> ProfileResponse update_profile_api_v1_profiles_profile_id_put(profile_id, profile_update)

Update Profile

Update profile.

Args:
    profile_id: Profile ID
    update_data: Update data
    current_user: Current authenticated user
    profile_service: Profile service

Returns:
    Updated profile information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.profile_response import ProfileResponse
from chatter_sdk.models.profile_update import ProfileUpdate
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: CustomHTTPBearer
configuration = chatter_sdk.Configuration(
    access_token = os.environ["BEARER_TOKEN"]
)

# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.ProfilesApi(api_client)
    profile_id = 'profile_id_example' # str | 
    profile_update = chatter_sdk.ProfileUpdate() # ProfileUpdate | 

    try:
        # Update Profile
        api_response = await api_instance.update_profile_api_v1_profiles_profile_id_put(profile_id, profile_update)
        print("The response of ProfilesApi->update_profile_api_v1_profiles_profile_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ProfilesApi->update_profile_api_v1_profiles_profile_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **profile_id** | **str**|  | 
 **profile_update** | [**ProfileUpdate**](ProfileUpdate.md)|  | 

### Return type

[**ProfileResponse**](ProfileResponse.md)

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

