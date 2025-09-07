# chatter_sdk.PromptsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**clone_prompt_api_v1_prompts_prompt_id_clone_post**](PromptsApi.md#clone_prompt_api_v1_prompts_prompt_id_clone_post) | **POST** /api/v1/prompts/{prompt_id}/clone | Clone Prompt
[**create_prompt_api_v1_prompts_post**](PromptsApi.md#create_prompt_api_v1_prompts_post) | **POST** /api/v1/prompts/ | Create Prompt
[**delete_prompt_api_v1_prompts_prompt_id_delete**](PromptsApi.md#delete_prompt_api_v1_prompts_prompt_id_delete) | **DELETE** /api/v1/prompts/{prompt_id} | Delete Prompt
[**get_prompt_api_v1_prompts_prompt_id_get**](PromptsApi.md#get_prompt_api_v1_prompts_prompt_id_get) | **GET** /api/v1/prompts/{prompt_id} | Get Prompt
[**get_prompt_stats_api_v1_prompts_stats_overview_get**](PromptsApi.md#get_prompt_stats_api_v1_prompts_stats_overview_get) | **GET** /api/v1/prompts/stats/overview | Get Prompt Stats
[**list_prompts_api_v1_prompts_get**](PromptsApi.md#list_prompts_api_v1_prompts_get) | **GET** /api/v1/prompts | List Prompts
[**test_prompt_api_v1_prompts_prompt_id_test_post**](PromptsApi.md#test_prompt_api_v1_prompts_prompt_id_test_post) | **POST** /api/v1/prompts/{prompt_id}/test | Test Prompt
[**update_prompt_api_v1_prompts_prompt_id_put**](PromptsApi.md#update_prompt_api_v1_prompts_prompt_id_put) | **PUT** /api/v1/prompts/{prompt_id} | Update Prompt


# **clone_prompt_api_v1_prompts_prompt_id_clone_post**
> PromptResponse clone_prompt_api_v1_prompts_prompt_id_clone_post(prompt_id, prompt_clone_request)

Clone Prompt

Clone an existing prompt.

Args:
    prompt_id: Source prompt ID
    clone_request: Clone request
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Cloned prompt information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_clone_request import PromptCloneRequest
from chatter_sdk.models.prompt_response import PromptResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_id = 'prompt_id_example' # str | 
    prompt_clone_request = chatter_sdk.PromptCloneRequest() # PromptCloneRequest | 

    try:
        # Clone Prompt
        api_response = await api_instance.clone_prompt_api_v1_prompts_prompt_id_clone_post(prompt_id, prompt_clone_request)
        print("The response of PromptsApi->clone_prompt_api_v1_prompts_prompt_id_clone_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->clone_prompt_api_v1_prompts_prompt_id_clone_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_id** | **str**|  | 
 **prompt_clone_request** | [**PromptCloneRequest**](PromptCloneRequest.md)|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

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

# **create_prompt_api_v1_prompts_post**
> PromptResponse create_prompt_api_v1_prompts_post(prompt_create)

Create Prompt

Create a new prompt.

Args:
    prompt_data: Prompt creation data
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Created prompt information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_create import PromptCreate
from chatter_sdk.models.prompt_response import PromptResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_create = chatter_sdk.PromptCreate() # PromptCreate | 

    try:
        # Create Prompt
        api_response = await api_instance.create_prompt_api_v1_prompts_post(prompt_create)
        print("The response of PromptsApi->create_prompt_api_v1_prompts_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->create_prompt_api_v1_prompts_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_create** | [**PromptCreate**](PromptCreate.md)|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

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

# **delete_prompt_api_v1_prompts_prompt_id_delete**
> PromptDeleteResponse delete_prompt_api_v1_prompts_prompt_id_delete(prompt_id)

Delete Prompt

Delete prompt.

Args:
    prompt_id: Prompt ID
    request: Delete request parameters
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Success message

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_delete_response import PromptDeleteResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_id = 'prompt_id_example' # str | 

    try:
        # Delete Prompt
        api_response = await api_instance.delete_prompt_api_v1_prompts_prompt_id_delete(prompt_id)
        print("The response of PromptsApi->delete_prompt_api_v1_prompts_prompt_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->delete_prompt_api_v1_prompts_prompt_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_id** | **str**|  | 

### Return type

[**PromptDeleteResponse**](PromptDeleteResponse.md)

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

# **get_prompt_api_v1_prompts_prompt_id_get**
> PromptResponse get_prompt_api_v1_prompts_prompt_id_get(prompt_id)

Get Prompt

Get prompt details.

Args:
    prompt_id: Prompt ID
    request: Get request parameters
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Prompt information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_response import PromptResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_id = 'prompt_id_example' # str | 

    try:
        # Get Prompt
        api_response = await api_instance.get_prompt_api_v1_prompts_prompt_id_get(prompt_id)
        print("The response of PromptsApi->get_prompt_api_v1_prompts_prompt_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->get_prompt_api_v1_prompts_prompt_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_id** | **str**|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

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

# **get_prompt_stats_api_v1_prompts_stats_overview_get**
> PromptStatsResponse get_prompt_stats_api_v1_prompts_stats_overview_get()

Get Prompt Stats

Get prompt statistics.

Args:
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Prompt statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_stats_response import PromptStatsResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)

    try:
        # Get Prompt Stats
        api_response = await api_instance.get_prompt_stats_api_v1_prompts_stats_overview_get()
        print("The response of PromptsApi->get_prompt_stats_api_v1_prompts_stats_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->get_prompt_stats_api_v1_prompts_stats_overview_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**PromptStatsResponse**](PromptStatsResponse.md)

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

# **list_prompts_api_v1_prompts_get**
> PromptListResponse list_prompts_api_v1_prompts_get(prompt_type=prompt_type, category=category, tags=tags, is_public=is_public, is_chain=is_chain, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)

List Prompts

List user's prompts.

Args:
    prompt_type: Filter by prompt type
    category: Filter by category
    tags: Filter by tags
    is_public: Filter by public status
    is_chain: Filter by chain status
    limit: Maximum number of results
    offset: Number of results to skip
    sort_by: Sort field
    sort_order: Sort order (asc/desc)
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    List of prompts with pagination info

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_category import PromptCategory
from chatter_sdk.models.prompt_list_response import PromptListResponse
from chatter_sdk.models.prompt_type import PromptType
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_type = chatter_sdk.PromptType() # PromptType | Filter by prompt type (optional)
    category = chatter_sdk.PromptCategory() # PromptCategory | Filter by category (optional)
    tags = ['tags_example'] # List[str] | Filter by tags (optional)
    is_public = True # bool | Filter by public status (optional)
    is_chain = True # bool | Filter by chain status (optional)
    limit = 50 # int | Maximum number of results (optional) (default to 50)
    offset = 0 # int | Number of results to skip (optional) (default to 0)
    sort_by = 'created_at' # str | Sort field (optional) (default to 'created_at')
    sort_order = 'desc' # str | Sort order (optional) (default to 'desc')

    try:
        # List Prompts
        api_response = await api_instance.list_prompts_api_v1_prompts_get(prompt_type=prompt_type, category=category, tags=tags, is_public=is_public, is_chain=is_chain, limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order)
        print("The response of PromptsApi->list_prompts_api_v1_prompts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->list_prompts_api_v1_prompts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_type** | [**PromptType**](.md)| Filter by prompt type | [optional] 
 **category** | [**PromptCategory**](.md)| Filter by category | [optional] 
 **tags** | [**List[str]**](str.md)| Filter by tags | [optional] 
 **is_public** | **bool**| Filter by public status | [optional] 
 **is_chain** | **bool**| Filter by chain status | [optional] 
 **limit** | **int**| Maximum number of results | [optional] [default to 50]
 **offset** | **int**| Number of results to skip | [optional] [default to 0]
 **sort_by** | **str**| Sort field | [optional] [default to &#39;created_at&#39;]
 **sort_order** | **str**| Sort order | [optional] [default to &#39;desc&#39;]

### Return type

[**PromptListResponse**](PromptListResponse.md)

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

# **test_prompt_api_v1_prompts_prompt_id_test_post**
> PromptTestResponse test_prompt_api_v1_prompts_prompt_id_test_post(prompt_id, prompt_test_request)

Test Prompt

Test prompt with given variables.

Args:
    prompt_id: Prompt ID
    test_request: Test request
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Test results

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_test_request import PromptTestRequest
from chatter_sdk.models.prompt_test_response import PromptTestResponse
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_id = 'prompt_id_example' # str | 
    prompt_test_request = chatter_sdk.PromptTestRequest() # PromptTestRequest | 

    try:
        # Test Prompt
        api_response = await api_instance.test_prompt_api_v1_prompts_prompt_id_test_post(prompt_id, prompt_test_request)
        print("The response of PromptsApi->test_prompt_api_v1_prompts_prompt_id_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->test_prompt_api_v1_prompts_prompt_id_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_id** | **str**|  | 
 **prompt_test_request** | [**PromptTestRequest**](PromptTestRequest.md)|  | 

### Return type

[**PromptTestResponse**](PromptTestResponse.md)

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

# **update_prompt_api_v1_prompts_prompt_id_put**
> PromptResponse update_prompt_api_v1_prompts_prompt_id_put(prompt_id, prompt_update)

Update Prompt

Update prompt.

Args:
    prompt_id: Prompt ID
    update_data: Update data
    current_user: Current authenticated user
    prompt_service: Prompt service

Returns:
    Updated prompt information

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.prompt_response import PromptResponse
from chatter_sdk.models.prompt_update import PromptUpdate
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
    api_instance = chatter_sdk.PromptsApi(api_client)
    prompt_id = 'prompt_id_example' # str | 
    prompt_update = chatter_sdk.PromptUpdate() # PromptUpdate | 

    try:
        # Update Prompt
        api_response = await api_instance.update_prompt_api_v1_prompts_prompt_id_put(prompt_id, prompt_update)
        print("The response of PromptsApi->update_prompt_api_v1_prompts_prompt_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PromptsApi->update_prompt_api_v1_prompts_prompt_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **prompt_id** | **str**|  | 
 **prompt_update** | [**PromptUpdate**](PromptUpdate.md)|  | 

### Return type

[**PromptResponse**](PromptResponse.md)

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

