# chatter_sdk.RealTimeAnalyticsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post**](RealTimeAnalyticsApi.md#cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post) | **POST** /api/v1/analytics/real-time/real-time/cleanup | Cleanup Inactive Tasks
[**get_trending_content_api_v1_analytics_real_time_search_trending_get**](RealTimeAnalyticsApi.md#get_trending_content_api_v1_analytics_real_time_search_trending_get) | **GET** /api/v1/analytics/real-time/search/trending | Get Trending Content
[**get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get**](RealTimeAnalyticsApi.md#get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get) | **GET** /api/v1/analytics/real-time/user-behavior/{user_id} | Get User Behavior Analytics
[**intelligent_search_api_v1_analytics_real_time_search_intelligent_get**](RealTimeAnalyticsApi.md#intelligent_search_api_v1_analytics_real_time_search_intelligent_get) | **GET** /api/v1/analytics/real-time/search/intelligent | Intelligent Search
[**send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post**](RealTimeAnalyticsApi.md#send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post) | **POST** /api/v1/analytics/real-time/real-time/system-health | Send System Health Update
[**send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post**](RealTimeAnalyticsApi.md#send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post) | **POST** /api/v1/analytics/real-time/real-time/workflow/{workflow_id}/update | Send Workflow Update
[**start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post**](RealTimeAnalyticsApi.md#start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post) | **POST** /api/v1/analytics/real-time/real-time/dashboard/start | Start Real Time Dashboard
[**stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post**](RealTimeAnalyticsApi.md#stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post) | **POST** /api/v1/analytics/real-time/real-time/dashboard/stop | Stop Real Time Dashboard


# **cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post**
> Dict[str, object] cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post()

Cleanup Inactive Tasks

Clean up inactive real-time tasks.

This endpoint is admin-only and performs maintenance on the
real-time analytics service.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)

    try:
        # Cleanup Inactive Tasks
        api_response = await api_instance.cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post()
        print("The response of RealTimeAnalyticsApi->cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

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

# **get_trending_content_api_v1_analytics_real_time_search_trending_get**
> Dict[str, object] get_trending_content_api_v1_analytics_real_time_search_trending_get(limit=limit)

Get Trending Content

Get trending content personalized for the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)
    limit = 10 # int |  (optional) (default to 10)

    try:
        # Get Trending Content
        api_response = await api_instance.get_trending_content_api_v1_analytics_real_time_search_trending_get(limit=limit)
        print("The response of RealTimeAnalyticsApi->get_trending_content_api_v1_analytics_real_time_search_trending_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->get_trending_content_api_v1_analytics_real_time_search_trending_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 10]

### Return type

**Dict[str, object]**

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

# **get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get**
> Dict[str, object] get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get(user_id)

Get User Behavior Analytics

Get personalized behavior analytics for a user.

Users can only access their own analytics unless they are admin.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)
    user_id = 'user_id_example' # str | 

    try:
        # Get User Behavior Analytics
        api_response = await api_instance.get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get(user_id)
        print("The response of RealTimeAnalyticsApi->get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 

### Return type

**Dict[str, object]**

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

# **intelligent_search_api_v1_analytics_real_time_search_intelligent_get**
> Dict[str, object] intelligent_search_api_v1_analytics_real_time_search_intelligent_get(query, search_type=search_type, limit=limit, include_recommendations=include_recommendations)

Intelligent Search

Perform intelligent semantic search with personalized results.

Args:
    query: Search query string
    search_type: Type of content to search ("documents", "conversations", "prompts")
    limit: Maximum number of results to return
    include_recommendations: Whether to include search recommendations

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)
    query = 'query_example' # str | 
    search_type = 'documents' # str |  (optional) (default to 'documents')
    limit = 10 # int |  (optional) (default to 10)
    include_recommendations = True # bool |  (optional) (default to True)

    try:
        # Intelligent Search
        api_response = await api_instance.intelligent_search_api_v1_analytics_real_time_search_intelligent_get(query, search_type=search_type, limit=limit, include_recommendations=include_recommendations)
        print("The response of RealTimeAnalyticsApi->intelligent_search_api_v1_analytics_real_time_search_intelligent_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->intelligent_search_api_v1_analytics_real_time_search_intelligent_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**|  | 
 **search_type** | **str**|  | [optional] [default to &#39;documents&#39;]
 **limit** | **int**|  | [optional] [default to 10]
 **include_recommendations** | **bool**|  | [optional] [default to True]

### Return type

**Dict[str, object]**

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

# **send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post**
> Dict[str, object] send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post(request_body)

Send System Health Update

Send system health update to all admin users.

This endpoint is admin-only and broadcasts health information
to all connected administrators.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)
    request_body = None # Dict[str, object] | 

    try:
        # Send System Health Update
        api_response = await api_instance.send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post(request_body)
        print("The response of RealTimeAnalyticsApi->send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request_body** | [**Dict[str, object]**](object.md)|  | 

### Return type

**Dict[str, object]**

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

# **send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post**
> Dict[str, object] send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post(workflow_id, update_type, request_body)

Send Workflow Update

Send a real-time workflow update to the user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)
    workflow_id = 'workflow_id_example' # str | 
    update_type = 'update_type_example' # str | 
    request_body = None # Dict[str, object] | 

    try:
        # Send Workflow Update
        api_response = await api_instance.send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post(workflow_id, update_type, request_body)
        print("The response of RealTimeAnalyticsApi->send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **workflow_id** | **str**|  | 
 **update_type** | **str**|  | 
 **request_body** | [**Dict[str, object]**](object.md)|  | 

### Return type

**Dict[str, object]**

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

# **start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post**
> Dict[str, object] start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post()

Start Real Time Dashboard

Start real-time dashboard updates for the current user.

This endpoint initiates a background task that streams analytics data
to the user via Server-Sent Events (SSE).

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)

    try:
        # Start Real Time Dashboard
        api_response = await api_instance.start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post()
        print("The response of RealTimeAnalyticsApi->start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

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

# **stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post**
> Dict[str, object] stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post()

Stop Real Time Dashboard

Stop real-time dashboard updates for the current user.

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8000
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost:8000"
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
    api_instance = chatter_sdk.RealTimeAnalyticsApi(api_client)

    try:
        # Stop Real Time Dashboard
        api_response = await api_instance.stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post()
        print("The response of RealTimeAnalyticsApi->stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealTimeAnalyticsApi->stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, object]**

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

