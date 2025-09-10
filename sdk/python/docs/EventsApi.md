# chatter_sdk.EventsApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**admin_events_stream_api_v1_events_admin_stream_get**](EventsApi.md#admin_events_stream_api_v1_events_admin_stream_get) | **GET** /api/v1/events/admin/stream | Admin Events Stream
[**events_stream_api_v1_events_stream_get**](EventsApi.md#events_stream_api_v1_events_stream_get) | **GET** /api/v1/events/stream | Events Stream
[**get_sse_stats_api_v1_events_stats_get**](EventsApi.md#get_sse_stats_api_v1_events_stats_get) | **GET** /api/v1/events/stats | Get Sse Stats
[**trigger_broadcast_test_api_v1_events_broadcast_test_post**](EventsApi.md#trigger_broadcast_test_api_v1_events_broadcast_test_post) | **POST** /api/v1/events/broadcast-test | Trigger Broadcast Test
[**trigger_test_event_api_v1_events_test_event_post**](EventsApi.md#trigger_test_event_api_v1_events_test_event_post) | **POST** /api/v1/events/test-event | Trigger Test Event


# **admin_events_stream_api_v1_events_admin_stream_get**
> object admin_events_stream_api_v1_events_admin_stream_get()

Admin Events Stream

Stream all system events for admin users.

Args:
    request: FastAPI request object
    current_user: Current authenticated admin user

Returns:
    StreamingResponse with SSE format for all events

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
    api_instance = chatter_sdk.EventsApi(api_client)

    try:
        # Admin Events Stream
        api_response = await api_instance.admin_events_stream_api_v1_events_admin_stream_get()
        print("The response of EventsApi->admin_events_stream_api_v1_events_admin_stream_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EventsApi->admin_events_stream_api_v1_events_admin_stream_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/event-stream

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Admin SSE stream for all system events |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **events_stream_api_v1_events_stream_get**
> object events_stream_api_v1_events_stream_get()

Events Stream

Stream real-time events via Server-Sent Events.

Args:
    request: FastAPI request object
    current_user: Current authenticated user

Returns:
    StreamingResponse with SSE format

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
    api_instance = chatter_sdk.EventsApi(api_client)

    try:
        # Events Stream
        api_response = await api_instance.events_stream_api_v1_events_stream_get()
        print("The response of EventsApi->events_stream_api_v1_events_stream_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EventsApi->events_stream_api_v1_events_stream_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[CustomHTTPBearer](../README.md#CustomHTTPBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json, text/event-stream

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Server-Sent Events stream for real-time updates |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_sse_stats_api_v1_events_stats_get**
> SSEStatsResponse get_sse_stats_api_v1_events_stats_get()

Get Sse Stats

Get SSE service statistics.

Args:
    current_user: Current authenticated admin user

Returns:
    SSE service statistics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.sse_stats_response import SSEStatsResponse
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
    api_instance = chatter_sdk.EventsApi(api_client)

    try:
        # Get Sse Stats
        api_response = await api_instance.get_sse_stats_api_v1_events_stats_get()
        print("The response of EventsApi->get_sse_stats_api_v1_events_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EventsApi->get_sse_stats_api_v1_events_stats_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**SSEStatsResponse**](SSEStatsResponse.md)

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

# **trigger_broadcast_test_api_v1_events_broadcast_test_post**
> TestEventResponse trigger_broadcast_test_api_v1_events_broadcast_test_post()

Trigger Broadcast Test

Trigger a broadcast test event for all users.

Args:
    current_user: Current authenticated admin user

Returns:
    Success message with event ID

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.test_event_response import TestEventResponse
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
    api_instance = chatter_sdk.EventsApi(api_client)

    try:
        # Trigger Broadcast Test
        api_response = await api_instance.trigger_broadcast_test_api_v1_events_broadcast_test_post()
        print("The response of EventsApi->trigger_broadcast_test_api_v1_events_broadcast_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EventsApi->trigger_broadcast_test_api_v1_events_broadcast_test_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TestEventResponse**](TestEventResponse.md)

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

# **trigger_test_event_api_v1_events_test_event_post**
> TestEventResponse trigger_test_event_api_v1_events_test_event_post()

Trigger Test Event

Trigger a test event for the current user.

Args:
    current_user: Current authenticated user

Returns:
    Success message with event ID

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.test_event_response import TestEventResponse
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
    api_instance = chatter_sdk.EventsApi(api_client)

    try:
        # Trigger Test Event
        api_response = await api_instance.trigger_test_event_api_v1_events_test_event_post()
        print("The response of EventsApi->trigger_test_event_api_v1_events_test_event_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling EventsApi->trigger_test_event_api_v1_events_test_event_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**TestEventResponse**](TestEventResponse.md)

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

