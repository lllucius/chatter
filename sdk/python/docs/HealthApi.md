# chatter_sdk.HealthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_correlation_trace_trace_correlation_id_get**](HealthApi.md#get_correlation_trace_trace_correlation_id_get) | **GET** /trace/{correlation_id} | Get Correlation Trace
[**get_metrics_metrics_get**](HealthApi.md#get_metrics_metrics_get) | **GET** /metrics | Get Metrics
[**health_check_endpoint_healthz_get**](HealthApi.md#health_check_endpoint_healthz_get) | **GET** /healthz | Health Check Endpoint
[**liveness_check_live_get**](HealthApi.md#liveness_check_live_get) | **GET** /live | Liveness Check
[**readiness_check_readyz_get**](HealthApi.md#readiness_check_readyz_get) | **GET** /readyz | Readiness Check


# **get_correlation_trace_trace_correlation_id_get**
> CorrelationTraceResponse get_correlation_trace_trace_correlation_id_get(correlation_id)

Get Correlation Trace

Get trace of all requests for a correlation ID.

Args:
    correlation_id: The correlation ID to trace

Returns:
    List of requests associated with the correlation ID

### Example


```python
import chatter_sdk
from chatter_sdk.models.correlation_trace_response import CorrelationTraceResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.HealthApi(api_client)
    correlation_id = 'correlation_id_example' # str | 

    try:
        # Get Correlation Trace
        api_response = await api_instance.get_correlation_trace_trace_correlation_id_get(correlation_id)
        print("The response of HealthApi->get_correlation_trace_trace_correlation_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->get_correlation_trace_trace_correlation_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **correlation_id** | **str**|  | 

### Return type

[**CorrelationTraceResponse**](CorrelationTraceResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |
**422** | Validation Error |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_metrics_metrics_get**
> MetricsResponse get_metrics_metrics_get()

Get Metrics

Get application metrics and monitoring data.

Returns:
    Application metrics including performance and health data

### Example


```python
import chatter_sdk
from chatter_sdk.models.metrics_response import MetricsResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.HealthApi(api_client)

    try:
        # Get Metrics
        api_response = await api_instance.get_metrics_metrics_get()
        print("The response of HealthApi->get_metrics_metrics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->get_metrics_metrics_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**MetricsResponse**](MetricsResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **health_check_endpoint_healthz_get**
> HealthCheckResponse health_check_endpoint_healthz_get()

Health Check Endpoint

Basic health check endpoint.

Returns:
    Health status

### Example


```python
import chatter_sdk
from chatter_sdk.models.health_check_response import HealthCheckResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.HealthApi(api_client)

    try:
        # Health Check Endpoint
        api_response = await api_instance.health_check_endpoint_healthz_get()
        print("The response of HealthApi->health_check_endpoint_healthz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->health_check_endpoint_healthz_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthCheckResponse**](HealthCheckResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **liveness_check_live_get**
> HealthCheckResponse liveness_check_live_get()

Liveness Check

Liveness check endpoint for Kubernetes.

This is a simple liveness probe that checks if the application process
is running and responding. It should NOT check external dependencies.

Returns:
    Health status indicating the application is alive

### Example


```python
import chatter_sdk
from chatter_sdk.models.health_check_response import HealthCheckResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.HealthApi(api_client)

    try:
        # Liveness Check
        api_response = await api_instance.liveness_check_live_get()
        print("The response of HealthApi->liveness_check_live_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->liveness_check_live_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**HealthCheckResponse**](HealthCheckResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **readiness_check_readyz_get**
> ReadinessCheckResponse readiness_check_readyz_get()

Readiness Check

Readiness check endpoint with database connectivity.

This checks that the application is ready to serve traffic by validating
that all external dependencies (database, etc.) are available.

Args:
    session: Database session

Returns:
    Readiness status with detailed checks.
    Returns 200 if ready, 503 if not ready.

### Example


```python
import chatter_sdk
from chatter_sdk.models.readiness_check_response import ReadinessCheckResponse
from chatter_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = chatter_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
async with chatter_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = chatter_sdk.HealthApi(api_client)

    try:
        # Readiness Check
        api_response = await api_instance.readiness_check_readyz_get()
        print("The response of HealthApi->readiness_check_readyz_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->readiness_check_readyz_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**ReadinessCheckResponse**](ReadinessCheckResponse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  * x-correlation-id - Request correlation ID for tracing <br>  * X-RateLimit-Limit-Minute - Requests allowed per minute <br>  * X-RateLimit-Limit-Hour - Requests allowed per hour <br>  * X-RateLimit-Remaining-Minute - Requests remaining this minute <br>  * X-RateLimit-Remaining-Hour - Requests remaining this hour <br>  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

