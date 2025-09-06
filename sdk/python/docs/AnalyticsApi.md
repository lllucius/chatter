# chatter_sdk.AnalyticsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_analytics_api_v1_analytics_export_post**](AnalyticsApi.md#export_analytics_api_v1_analytics_export_post) | **POST** /api/v1/analytics/export | Export Analytics
[**get_analytics_health_api_v1_analytics_health_get**](AnalyticsApi.md#get_analytics_health_api_v1_analytics_health_get) | **GET** /api/v1/analytics/health | Get Analytics Health
[**get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get**](AnalyticsApi.md#get_analytics_metrics_summary_api_v1_analytics_metrics_summary_get) | **GET** /api/v1/analytics/metrics/summary | Get Analytics Metrics Summary
[**get_conversation_stats_api_v1_analytics_conversations_get**](AnalyticsApi.md#get_conversation_stats_api_v1_analytics_conversations_get) | **GET** /api/v1/analytics/conversations | Get Conversation Stats
[**get_dashboard_api_v1_analytics_dashboard_get**](AnalyticsApi.md#get_dashboard_api_v1_analytics_dashboard_get) | **GET** /api/v1/analytics/dashboard | Get Dashboard
[**get_document_analytics_api_v1_analytics_documents_get**](AnalyticsApi.md#get_document_analytics_api_v1_analytics_documents_get) | **GET** /api/v1/analytics/documents | Get Document Analytics
[**get_performance_metrics_api_v1_analytics_performance_get**](AnalyticsApi.md#get_performance_metrics_api_v1_analytics_performance_get) | **GET** /api/v1/analytics/performance | Get Performance Metrics
[**get_system_analytics_api_v1_analytics_system_get**](AnalyticsApi.md#get_system_analytics_api_v1_analytics_system_get) | **GET** /api/v1/analytics/system | Get System Analytics
[**get_tool_server_analytics_api_v1_analytics_toolservers_get**](AnalyticsApi.md#get_tool_server_analytics_api_v1_analytics_toolservers_get) | **GET** /api/v1/analytics/toolservers | Get Tool Server Analytics
[**get_usage_metrics_api_v1_analytics_usage_get**](AnalyticsApi.md#get_usage_metrics_api_v1_analytics_usage_get) | **GET** /api/v1/analytics/usage | Get Usage Metrics
[**get_user_analytics_api_v1_analytics_users_user_id_get**](AnalyticsApi.md#get_user_analytics_api_v1_analytics_users_user_id_get) | **GET** /api/v1/analytics/users/{user_id} | Get User Analytics


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

