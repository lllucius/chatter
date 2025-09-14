# chatter_sdk.AnalyticsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**analyze_query_performance_api_v1_analytics_database_analyze_queries_post**](AnalyticsApi.md#analyze_query_performance_api_v1_analytics_database_analyze_queries_post) | **POST** /api/v1/analytics/database/analyze-queries | Analyze Query Performance
[**cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post**](AnalyticsApi.md#cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post) | **POST** /api/v1/analytics/real-time/real-time/cleanup | Cleanup Inactive Tasks
[**export_analytics_api_v1_analytics_export_post**](AnalyticsApi.md#export_analytics_api_v1_analytics_export_post) | **POST** /api/v1/analytics/export | Export Analytics
[**get_analytics_health_api_v1_analytics_health_get**](AnalyticsApi.md#get_analytics_health_api_v1_analytics_health_get) | **GET** /api/v1/analytics/health | Get Analytics Health
[**get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get**](AnalyticsApi.md#get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get) | **GET** /api/v1/analytics/metrics/summary | Get Analytics Metrics Summary
[**get_cache_warming_status_api_v1_analytics_cache_status_get**](AnalyticsApi.md#get_cache_warming_status_api_v1_analytics_cache_status_get) | **GET** /api/v1/analytics/cache/status | Get Cache Warming Status
[**get_conversation_stats_api_v1_analytics_conversations_get**](AnalyticsApi.md#get_conversation_stats_api_v1_analytics_conversations_get) | **GET** /api/v1/analytics/conversations | Get Conversation Stats
[**get_dashboard_api_v1_analytics_dashboard_get**](AnalyticsApi.md#get_dashboard_api_v1_analytics_dashboard_get) | **GET** /api/v1/analytics/dashboard | Get Dashboard
[**get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get**](AnalyticsApi.md#get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get) | **GET** /api/v1/analytics/dashboard/chart-data | Get Dashboard Chart Data
[**get_database_health_metrics_api_v1_analytics_database_health_get**](AnalyticsApi.md#get_database_health_metrics_api_v1_analytics_database_health_get) | **GET** /api/v1/analytics/database/health | Get Database Health Metrics
[**get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get**](AnalyticsApi.md#get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get) | **GET** /api/v1/analytics/performance/detailed | Get Detailed Performance Metrics
[**get_document_analytics_api_v1_analytics_documents_get**](AnalyticsApi.md#get_document_analytics_api_v1_analytics_documents_get) | **GET** /api/v1/analytics/documents | Get Document Analytics
[**get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get**](AnalyticsApi.md#get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get) | **GET** /api/v1/analytics/dashboard/integrated | Get Integrated Dashboard Stats
[**get_performance_metrics_api_v1_analytics_performance_get**](AnalyticsApi.md#get_performance_metrics_api_v1_analytics_performance_get) | **GET** /api/v1/analytics/performance | Get Performance Metrics
[**get_system_analytics_api_v1_analytics_system_get**](AnalyticsApi.md#get_system_analytics_api_v1_analytics_system_get) | **GET** /api/v1/analytics/system | Get System Analytics
[**get_tool_server_analytics_api_v1_analytics_toolservers_get**](AnalyticsApi.md#get_tool_server_analytics_api_v1_analytics_toolservers_get) | **GET** /api/v1/analytics/toolservers | Get Tool Server Analytics
[**get_trending_content_api_v1_analytics_real_time_search_trending_get**](AnalyticsApi.md#get_trending_content_api_v1_analytics_real_time_search_trending_get) | **GET** /api/v1/analytics/real-time/search/trending | Get Trending Content
[**get_usage_metrics_api_v1_analytics_usage_get**](AnalyticsApi.md#get_usage_metrics_api_v1_analytics_usage_get) | **GET** /api/v1/analytics/usage | Get Usage Metrics
[**get_user_analytics_api_v1_analytics_users_user_id_get**](AnalyticsApi.md#get_user_analytics_api_v1_analytics_users_user_id_get) | **GET** /api/v1/analytics/users/{user_id} | Get User Analytics
[**get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get**](AnalyticsApi.md#get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get) | **GET** /api/v1/analytics/real-time/user-behavior/{user_id} | Get User Behavior Analytics
[**intelligent_search_api_v1_analytics_real_time_search_intelligent_get**](AnalyticsApi.md#intelligent_search_api_v1_analytics_real_time_search_intelligent_get) | **GET** /api/v1/analytics/real-time/search/intelligent | Intelligent Search
[**invalidate_stale_cache_api_v1_analytics_cache_invalidate_post**](AnalyticsApi.md#invalidate_stale_cache_api_v1_analytics_cache_invalidate_post) | **POST** /api/v1/analytics/cache/invalidate | Invalidate Stale Cache
[**optimize_cache_performance_api_v1_analytics_cache_optimize_post**](AnalyticsApi.md#optimize_cache_performance_api_v1_analytics_cache_optimize_post) | **POST** /api/v1/analytics/cache/optimize | Optimize Cache Performance
[**send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post**](AnalyticsApi.md#send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post) | **POST** /api/v1/analytics/real-time/real-time/system-health | Send System Health Update
[**send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post**](AnalyticsApi.md#send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post) | **POST** /api/v1/analytics/real-time/real-time/workflow/{workflow_id}/update | Send Workflow Update
[**start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post**](AnalyticsApi.md#start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post) | **POST** /api/v1/analytics/real-time/real-time/dashboard/start | Start Real Time Dashboard
[**stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post**](AnalyticsApi.md#stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post) | **POST** /api/v1/analytics/real-time/real-time/dashboard/stop | Stop Real Time Dashboard
[**warm_analytics_cache_api_v1_analytics_cache_warm_post**](AnalyticsApi.md#warm_analytics_cache_api_v1_analytics_cache_warm_post) | **POST** /api/v1/analytics/cache/warm | Warm Analytics Cache


# **analyze_query_performance_api_v1_analytics_database_analyze_queries_post**
> Dict[str, object] analyze_query_performance_api_v1_analytics_database_analyze_queries_post(query_type=query_type)

Analyze Query Performance

Analyze performance of analytics database queries.

Args:
    query_type: Specific query type to analyze (optional)
    current_user: Current authenticated user
    db_optimization_service: Database optimization service
    
Returns:
    Query performance analysis and optimization recommendations

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    query_type = 'query_type_example' # str |  (optional)

    try:
        # Analyze Query Performance
        api_response = await api_instance.analyze_query_performance_api_v1_analytics_database_analyze_queries_post(query_type=query_type)
        print("The response of AnalyticsApi->analyze_query_performance_api_v1_analytics_database_analyze_queries_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->analyze_query_performance_api_v1_analytics_database_analyze_queries_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_type** | **str**|  | [optional] 

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Cleanup Inactive Tasks
        api_response = await api_instance.cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post()
        print("The response of AnalyticsApi->cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->cleanup_inactive_tasks_api_v1_analytics_real_time_real_time_cleanup_post: %s\n" % e)
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

# **export_analytics_api_v1_analytics_export_post**
> object export_analytics_api_v1_analytics_export_post(metrics, format=format, start_date=start_date, end_date=end_date, period=period)

Export Analytics

Export analytics reports.

Args:
    format: Export format
    metrics: List of metrics to export
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Exported analytics report

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    metrics = ['metrics_example'] # List[str] | List of metrics to export
    format = 'json' # str | Export format (json, csv, xlsx) (optional) (default to 'json')
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Export Analytics
        api_response = await api_instance.export_analytics_api_v1_analytics_export_post(metrics, format=format, start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->export_analytics_api_v1_analytics_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->export_analytics_api_v1_analytics_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **metrics** | [**List[str]**](str.md)| List of metrics to export | 
 **format** | **str**| Export format (json, csv, xlsx) | [optional] [default to &#39;json&#39;]
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

**object**

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

# **get_analytics_health_api_v1_analytics_health_get**
> Dict[str, object] get_analytics_health_api_v1_analytics_health_get()

Get Analytics Health

Get analytics system health status.

Returns:
    Health check results for analytics system

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Analytics Health
        api_response = await api_instance.get_analytics_health_api_v1_analytics_health_get()
        print("The response of AnalyticsApi->get_analytics_health_api_v1_analytics_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_analytics_health_api_v1_analytics_health_get: %s\n" % e)
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

# **get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get**
> Dict[str, object] get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get()

Get Analytics Metrics Summary

Get summary of key analytics metrics for monitoring.

Returns:
    Summary of analytics metrics

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Analytics Metrics Summary
        api_response = await api_instance.get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get()
        print("The response of AnalyticsApi->get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get: %s\n" % e)
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

# **get_cache_warming_status_api_v1_analytics_cache_status_get**
> Dict[str, object] get_cache_warming_status_api_v1_analytics_cache_status_get()

Get Cache Warming Status

Get cache warming status and performance metrics.

Args:
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache warming status and metrics

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Cache Warming Status
        api_response = await api_instance.get_cache_warming_status_api_v1_analytics_cache_status_get()
        print("The response of AnalyticsApi->get_cache_warming_status_api_v1_analytics_cache_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_cache_warming_status_api_v1_analytics_cache_status_get: %s\n" % e)
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

# **get_conversation_stats_api_v1_analytics_conversations_get**
> ConversationStatsResponse get_conversation_stats_api_v1_analytics_conversations_get(start_date=start_date, end_date=end_date, period=period)

Get Conversation Stats

Get conversation statistics.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Conversation statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.conversation_stats_response import ConversationStatsResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Conversation Stats
        api_response = await api_instance.get_conversation_stats_api_v1_analytics_conversations_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_conversation_stats_api_v1_analytics_conversations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_conversation_stats_api_v1_analytics_conversations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**ConversationStatsResponse**](ConversationStatsResponse.md)

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

# **get_dashboard_api_v1_analytics_dashboard_get**
> DashboardResponse get_dashboard_api_v1_analytics_dashboard_get(start_date=start_date, end_date=end_date, period=period)

Get Dashboard

Get comprehensive dashboard data.

Args:
    request: Dashboard request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Complete dashboard data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.dashboard_response import DashboardResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Dashboard
        api_response = await api_instance.get_dashboard_api_v1_analytics_dashboard_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_dashboard_api_v1_analytics_dashboard_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_dashboard_api_v1_analytics_dashboard_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**DashboardResponse**](DashboardResponse.md)

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

# **get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get**
> ChartReadyAnalytics get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get(start_date=start_date, end_date=end_date, period=period)

Get Dashboard Chart Data

Get chart-ready analytics data for dashboard visualization.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics  
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Chart-ready analytics data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.chart_ready_analytics import ChartReadyAnalytics
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Dashboard Chart Data
        api_response = await api_instance.get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_dashboard_chart_data_api_v1_analytics_dashboard_chart_data_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**ChartReadyAnalytics**](ChartReadyAnalytics.md)

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

# **get_database_health_metrics_api_v1_analytics_database_health_get**
> Dict[str, object] get_database_health_metrics_api_v1_analytics_database_health_get()

Get Database Health Metrics

Get comprehensive database health metrics for analytics.

Args:
    current_user: Current authenticated user
    db_optimization_service: Database optimization service
    
Returns:
    Database health metrics and recommendations

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Database Health Metrics
        api_response = await api_instance.get_database_health_metrics_api_v1_analytics_database_health_get()
        print("The response of AnalyticsApi->get_database_health_metrics_api_v1_analytics_database_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_database_health_metrics_api_v1_analytics_database_health_get: %s\n" % e)
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

# **get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get**
> Dict[str, object] get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get()

Get Detailed Performance Metrics

Get detailed performance metrics for analytics service.

Args:
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Detailed performance metrics

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Detailed Performance Metrics
        api_response = await api_instance.get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get()
        print("The response of AnalyticsApi->get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_detailed_performance_metrics_api_v1_analytics_performance_detailed_get: %s\n" % e)
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

# **get_document_analytics_api_v1_analytics_documents_get**
> DocumentAnalyticsResponse get_document_analytics_api_v1_analytics_documents_get(start_date=start_date, end_date=end_date, period=period)

Get Document Analytics

Get document analytics.

Args:
    request: Document analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Document analytics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.document_analytics_response import DocumentAnalyticsResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Document Analytics
        api_response = await api_instance.get_document_analytics_api_v1_analytics_documents_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_document_analytics_api_v1_analytics_documents_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_document_analytics_api_v1_analytics_documents_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**DocumentAnalyticsResponse**](DocumentAnalyticsResponse.md)

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

# **get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get**
> IntegratedDashboardStats get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get()

Get Integrated Dashboard Stats

Get integrated dashboard statistics.

Args:
    current_user: Current authenticated user
    analytics_service: Analytics service
    
Returns:
    Integrated dashboard statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.integrated_dashboard_stats import IntegratedDashboardStats
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get Integrated Dashboard Stats
        api_response = await api_instance.get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get()
        print("The response of AnalyticsApi->get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_integrated_dashboard_stats_api_v1_analytics_dashboard_integrated_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**IntegratedDashboardStats**](IntegratedDashboardStats.md)

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

# **get_performance_metrics_api_v1_analytics_performance_get**
> PerformanceMetricsResponse get_performance_metrics_api_v1_analytics_performance_get(start_date=start_date, end_date=end_date, period=period)

Get Performance Metrics

Get performance metrics.

Args:
    request: Performance metrics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Performance metrics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.performance_metrics_response import PerformanceMetricsResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Performance Metrics
        api_response = await api_instance.get_performance_metrics_api_v1_analytics_performance_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_performance_metrics_api_v1_analytics_performance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_performance_metrics_api_v1_analytics_performance_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**PerformanceMetricsResponse**](PerformanceMetricsResponse.md)

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

# **get_system_analytics_api_v1_analytics_system_get**
> SystemAnalyticsResponse get_system_analytics_api_v1_analytics_system_get()

Get System Analytics

Get system analytics.

Args:
    request: System analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    System analytics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.system_analytics_response import SystemAnalyticsResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Get System Analytics
        api_response = await api_instance.get_system_analytics_api_v1_analytics_system_get()
        print("The response of AnalyticsApi->get_system_analytics_api_v1_analytics_system_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_system_analytics_api_v1_analytics_system_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**SystemAnalyticsResponse**](SystemAnalyticsResponse.md)

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

# **get_tool_server_analytics_api_v1_analytics_toolservers_get**
> Dict[str, object] get_tool_server_analytics_api_v1_analytics_toolservers_get(start_date=start_date, end_date=end_date, period=period)

Get Tool Server Analytics

Get tool server analytics.

Args:
    request: Tool server analytics request parameters
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Tool server analytics data

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Tool Server Analytics
        api_response = await api_instance.get_tool_server_analytics_api_v1_analytics_toolservers_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_tool_server_analytics_api_v1_analytics_toolservers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_tool_server_analytics_api_v1_analytics_toolservers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    limit = 10 # int |  (optional) (default to 10)

    try:
        # Get Trending Content
        api_response = await api_instance.get_trending_content_api_v1_analytics_real_time_search_trending_get(limit=limit)
        print("The response of AnalyticsApi->get_trending_content_api_v1_analytics_real_time_search_trending_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_trending_content_api_v1_analytics_real_time_search_trending_get: %s\n" % e)
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

# **get_usage_metrics_api_v1_analytics_usage_get**
> UsageMetricsResponse get_usage_metrics_api_v1_analytics_usage_get(start_date=start_date, end_date=end_date, period=period)

Get Usage Metrics

Get usage metrics.

Args:
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    Usage metrics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.usage_metrics_response import UsageMetricsResponse
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get Usage Metrics
        api_response = await api_instance.get_usage_metrics_api_v1_analytics_usage_get(start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_usage_metrics_api_v1_analytics_usage_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_usage_metrics_api_v1_analytics_usage_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

### Return type

[**UsageMetricsResponse**](UsageMetricsResponse.md)

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

# **get_user_analytics_api_v1_analytics_users_user_id_get**
> Dict[str, object] get_user_analytics_api_v1_analytics_users_user_id_get(user_id, start_date=start_date, end_date=end_date, period=period)

Get User Analytics

Get per-user analytics.

Args:
    user_id: User ID
    start_date: Start date for analytics
    end_date: End date for analytics
    period: Predefined period
    current_user: Current authenticated user
    analytics_service: Analytics service

Returns:
    User-specific analytics

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    user_id = 'user_id_example' # str | 
    start_date = '2013-10-20T19:20:30+01:00' # datetime | Start date for analytics (optional)
    end_date = '2013-10-20T19:20:30+01:00' # datetime | End date for analytics (optional)
    period = '7d' # str | Predefined period (1h, 24h, 7d, 30d, 90d) (optional) (default to '7d')

    try:
        # Get User Analytics
        api_response = await api_instance.get_user_analytics_api_v1_analytics_users_user_id_get(user_id, start_date=start_date, end_date=end_date, period=period)
        print("The response of AnalyticsApi->get_user_analytics_api_v1_analytics_users_user_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_user_analytics_api_v1_analytics_users_user_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **str**|  | 
 **start_date** | **datetime**| Start date for analytics | [optional] 
 **end_date** | **datetime**| End date for analytics | [optional] 
 **period** | **str**| Predefined period (1h, 24h, 7d, 30d, 90d) | [optional] [default to &#39;7d&#39;]

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    user_id = 'user_id_example' # str | 

    try:
        # Get User Behavior Analytics
        api_response = await api_instance.get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get(user_id)
        print("The response of AnalyticsApi->get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->get_user_behavior_analytics_api_v1_analytics_real_time_user_behavior_user_id_get: %s\n" % e)
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    query = 'query_example' # str | 
    search_type = 'documents' # str |  (optional) (default to 'documents')
    limit = 10 # int |  (optional) (default to 10)
    include_recommendations = True # bool |  (optional) (default to True)

    try:
        # Intelligent Search
        api_response = await api_instance.intelligent_search_api_v1_analytics_real_time_search_intelligent_get(query, search_type=search_type, limit=limit, include_recommendations=include_recommendations)
        print("The response of AnalyticsApi->intelligent_search_api_v1_analytics_real_time_search_intelligent_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->intelligent_search_api_v1_analytics_real_time_search_intelligent_get: %s\n" % e)
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

# **invalidate_stale_cache_api_v1_analytics_cache_invalidate_post**
> Dict[str, object] invalidate_stale_cache_api_v1_analytics_cache_invalidate_post(max_age_hours=max_age_hours)

Invalidate Stale Cache

Invalidate stale cache entries to free up memory.

Args:
    max_age_hours: Maximum age in hours for cache entries to keep
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache invalidation results

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    max_age_hours = 24 # int |  (optional) (default to 24)

    try:
        # Invalidate Stale Cache
        api_response = await api_instance.invalidate_stale_cache_api_v1_analytics_cache_invalidate_post(max_age_hours=max_age_hours)
        print("The response of AnalyticsApi->invalidate_stale_cache_api_v1_analytics_cache_invalidate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->invalidate_stale_cache_api_v1_analytics_cache_invalidate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **max_age_hours** | **int**|  | [optional] [default to 24]

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

# **optimize_cache_performance_api_v1_analytics_cache_optimize_post**
> Dict[str, object] optimize_cache_performance_api_v1_analytics_cache_optimize_post()

Optimize Cache Performance

Analyze and optimize cache performance automatically.

Args:
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Optimization results and recommendations

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Optimize Cache Performance
        api_response = await api_instance.optimize_cache_performance_api_v1_analytics_cache_optimize_post()
        print("The response of AnalyticsApi->optimize_cache_performance_api_v1_analytics_cache_optimize_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->optimize_cache_performance_api_v1_analytics_cache_optimize_post: %s\n" % e)
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    request_body = None # Dict[str, object] | 

    try:
        # Send System Health Update
        api_response = await api_instance.send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post(request_body)
        print("The response of AnalyticsApi->send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->send_system_health_update_api_v1_analytics_real_time_real_time_system_health_post: %s\n" % e)
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    workflow_id = 'workflow_id_example' # str | 
    update_type = 'update_type_example' # str | 
    request_body = None # Dict[str, object] | 

    try:
        # Send Workflow Update
        api_response = await api_instance.send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post(workflow_id, update_type, request_body)
        print("The response of AnalyticsApi->send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->send_workflow_update_api_v1_analytics_real_time_real_time_workflow_workflow_id_update_post: %s\n" % e)
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Start Real Time Dashboard
        api_response = await api_instance.start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post()
        print("The response of AnalyticsApi->start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->start_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_start_post: %s\n" % e)
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
    api_instance = chatter_sdk.AnalyticsApi(api_client)

    try:
        # Stop Real Time Dashboard
        api_response = await api_instance.stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post()
        print("The response of AnalyticsApi->stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->stop_real_time_dashboard_api_v1_analytics_real_time_real_time_dashboard_stop_post: %s\n" % e)
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

# **warm_analytics_cache_api_v1_analytics_cache_warm_post**
> Dict[str, object] warm_analytics_cache_api_v1_analytics_cache_warm_post(force_refresh=force_refresh)

Warm Analytics Cache

Warm analytics cache to improve performance.

Args:
    force_refresh: Force refresh of existing cache entries
    current_user: Current authenticated user
    cache_warming_service: Cache warming service
    
Returns:
    Cache warming results

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
    api_instance = chatter_sdk.AnalyticsApi(api_client)
    force_refresh = False # bool |  (optional) (default to False)

    try:
        # Warm Analytics Cache
        api_response = await api_instance.warm_analytics_cache_api_v1_analytics_cache_warm_post(force_refresh=force_refresh)
        print("The response of AnalyticsApi->warm_analytics_cache_api_v1_analytics_cache_warm_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnalyticsApi->warm_analytics_cache_api_v1_analytics_cache_warm_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **force_refresh** | **bool**|  | [optional] [default to False]

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

