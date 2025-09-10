# chatter_sdk.ABTestingApi

All URIs are relative to *http://localhost:8000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**complete_ab_test_api_v1_ab_tests_test_id_complete_post**](ABTestingApi.md#complete_ab_test_api_v1_ab_tests_test_id_complete_post) | **POST** /api/v1/ab-tests/{test_id}/complete | Complete Ab Test
[**create_ab_test_api_v1_ab_tests_post**](ABTestingApi.md#create_ab_test_api_v1_ab_tests_post) | **POST** /api/v1/ab-tests/ | Create Ab Test
[**delete_ab_test_api_v1_ab_tests_test_id_delete**](ABTestingApi.md#delete_ab_test_api_v1_ab_tests_test_id_delete) | **DELETE** /api/v1/ab-tests/{test_id} | Delete Ab Test
[**end_ab_test_api_v1_ab_tests_test_id_end_post**](ABTestingApi.md#end_ab_test_api_v1_ab_tests_test_id_end_post) | **POST** /api/v1/ab-tests/{test_id}/end | End Ab Test
[**get_ab_test_api_v1_ab_tests_test_id_get**](ABTestingApi.md#get_ab_test_api_v1_ab_tests_test_id_get) | **GET** /api/v1/ab-tests/{test_id} | Get Ab Test
[**get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get**](ABTestingApi.md#get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get) | **GET** /api/v1/ab-tests/{test_id}/metrics | Get Ab Test Metrics
[**get_ab_test_performance_api_v1_ab_tests_test_id_performance_get**](ABTestingApi.md#get_ab_test_performance_api_v1_ab_tests_test_id_performance_get) | **GET** /api/v1/ab-tests/{test_id}/performance | Get Ab Test Performance
[**get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get**](ABTestingApi.md#get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get) | **GET** /api/v1/ab-tests/{test_id}/recommendations | Get Ab Test Recommendations
[**get_ab_test_results_api_v1_ab_tests_test_id_results_get**](ABTestingApi.md#get_ab_test_results_api_v1_ab_tests_test_id_results_get) | **GET** /api/v1/ab-tests/{test_id}/results | Get Ab Test Results
[**list_ab_tests_api_v1_ab_tests_get**](ABTestingApi.md#list_ab_tests_api_v1_ab_tests_get) | **GET** /api/v1/ab-tests/ | List Ab Tests
[**pause_ab_test_api_v1_ab_tests_test_id_pause_post**](ABTestingApi.md#pause_ab_test_api_v1_ab_tests_test_id_pause_post) | **POST** /api/v1/ab-tests/{test_id}/pause | Pause Ab Test
[**start_ab_test_api_v1_ab_tests_test_id_start_post**](ABTestingApi.md#start_ab_test_api_v1_ab_tests_test_id_start_post) | **POST** /api/v1/ab-tests/{test_id}/start | Start Ab Test
[**update_ab_test_api_v1_ab_tests_test_id_put**](ABTestingApi.md#update_ab_test_api_v1_ab_tests_test_id_put) | **PUT** /api/v1/ab-tests/{test_id} | Update Ab Test


# **complete_ab_test_api_v1_ab_tests_test_id_complete_post**
> ABTestActionResponse complete_ab_test_api_v1_ab_tests_test_id_complete_post(test_id)

Complete Ab Test

Complete an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_action_response import ABTestActionResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Complete Ab Test
        api_response = await api_instance.complete_ab_test_api_v1_ab_tests_test_id_complete_post(test_id)
        print("The response of ABTestingApi->complete_ab_test_api_v1_ab_tests_test_id_complete_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->complete_ab_test_api_v1_ab_tests_test_id_complete_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestActionResponse**](ABTestActionResponse.md)

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

# **create_ab_test_api_v1_ab_tests_post**
> ABTestResponse create_ab_test_api_v1_ab_tests_post(ab_test_create_request)

Create Ab Test

Create a new A/B test.

Args:
    test_data: A/B test creation data
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Created test data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_create_request import ABTestCreateRequest
from chatter_sdk.models.ab_test_response import ABTestResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    ab_test_create_request = chatter_sdk.ABTestCreateRequest() # ABTestCreateRequest | 

    try:
        # Create Ab Test
        api_response = await api_instance.create_ab_test_api_v1_ab_tests_post(ab_test_create_request)
        print("The response of ABTestingApi->create_ab_test_api_v1_ab_tests_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->create_ab_test_api_v1_ab_tests_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ab_test_create_request** | [**ABTestCreateRequest**](ABTestCreateRequest.md)|  | 

### Return type

[**ABTestResponse**](ABTestResponse.md)

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

# **delete_ab_test_api_v1_ab_tests_test_id_delete**
> ABTestDeleteResponse delete_ab_test_api_v1_ab_tests_test_id_delete(test_id)

Delete Ab Test

Delete an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Deletion result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_delete_response import ABTestDeleteResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Delete Ab Test
        api_response = await api_instance.delete_ab_test_api_v1_ab_tests_test_id_delete(test_id)
        print("The response of ABTestingApi->delete_ab_test_api_v1_ab_tests_test_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->delete_ab_test_api_v1_ab_tests_test_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestDeleteResponse**](ABTestDeleteResponse.md)

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

# **end_ab_test_api_v1_ab_tests_test_id_end_post**
> ABTestActionResponse end_ab_test_api_v1_ab_tests_test_id_end_post(test_id, winner_variant)

End Ab Test

End A/B test and declare winner.

Args:
    test_id: A/B test ID
    winner_variant: Winning variant identifier
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action response

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_action_response import ABTestActionResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 
    winner_variant = 'winner_variant_example' # str | 

    try:
        # End Ab Test
        api_response = await api_instance.end_ab_test_api_v1_ab_tests_test_id_end_post(test_id, winner_variant)
        print("The response of ABTestingApi->end_ab_test_api_v1_ab_tests_test_id_end_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->end_ab_test_api_v1_ab_tests_test_id_end_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 
 **winner_variant** | **str**|  | 

### Return type

[**ABTestActionResponse**](ABTestActionResponse.md)

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

# **get_ab_test_api_v1_ab_tests_test_id_get**
> ABTestResponse get_ab_test_api_v1_ab_tests_test_id_get(test_id)

Get Ab Test

Get A/B test by ID.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    A/B test data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_response import ABTestResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Get Ab Test
        api_response = await api_instance.get_ab_test_api_v1_ab_tests_test_id_get(test_id)
        print("The response of ABTestingApi->get_ab_test_api_v1_ab_tests_test_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->get_ab_test_api_v1_ab_tests_test_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestResponse**](ABTestResponse.md)

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

# **get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get**
> ABTestMetricsResponse get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get(test_id)

Get Ab Test Metrics

Get current A/B test metrics.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Current test metrics

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_metrics_response import ABTestMetricsResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Get Ab Test Metrics
        api_response = await api_instance.get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get(test_id)
        print("The response of ABTestingApi->get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->get_ab_test_metrics_api_v1_ab_tests_test_id_metrics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestMetricsResponse**](ABTestMetricsResponse.md)

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

# **get_ab_test_performance_api_v1_ab_tests_test_id_performance_get**
> Dict[str, object] get_ab_test_performance_api_v1_ab_tests_test_id_performance_get(test_id)

Get Ab Test Performance

Get A/B test performance results by variant.

Args:
    test_id: A/B test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Performance results per variant

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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Get Ab Test Performance
        api_response = await api_instance.get_ab_test_performance_api_v1_ab_tests_test_id_performance_get(test_id)
        print("The response of ABTestingApi->get_ab_test_performance_api_v1_ab_tests_test_id_performance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->get_ab_test_performance_api_v1_ab_tests_test_id_performance_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

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

# **get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get**
> Dict[str, object] get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get(test_id)

Get Ab Test Recommendations

Get comprehensive recommendations for an A/B test.

Args:
    test_id: A/B test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Recommendations and insights for the test

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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Get Ab Test Recommendations
        api_response = await api_instance.get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get(test_id)
        print("The response of ABTestingApi->get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->get_ab_test_recommendations_api_v1_ab_tests_test_id_recommendations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

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

# **get_ab_test_results_api_v1_ab_tests_test_id_results_get**
> ABTestResultsResponse get_ab_test_results_api_v1_ab_tests_test_id_results_get(test_id)

Get Ab Test Results

Get A/B test results and analysis.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Test results and analysis

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_results_response import ABTestResultsResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Get Ab Test Results
        api_response = await api_instance.get_ab_test_results_api_v1_ab_tests_test_id_results_get(test_id)
        print("The response of ABTestingApi->get_ab_test_results_api_v1_ab_tests_test_id_results_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->get_ab_test_results_api_v1_ab_tests_test_id_results_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestResultsResponse**](ABTestResultsResponse.md)

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

# **list_ab_tests_api_v1_ab_tests_get**
> ABTestListResponse list_ab_tests_api_v1_ab_tests_get(status=status, test_type=test_type, request_body=request_body)

List Ab Tests

List A/B tests with optional filtering.

Args:
    request: List request parameters
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    List of A/B tests

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_list_response import ABTestListResponse
from chatter_sdk.models.test_status import TestStatus
from chatter_sdk.models.test_type import TestType
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    status = chatter_sdk.TestStatus() # TestStatus |  (optional)
    test_type = chatter_sdk.TestType() # TestType |  (optional)
    request_body = ['request_body_example'] # List[str] |  (optional)

    try:
        # List Ab Tests
        api_response = await api_instance.list_ab_tests_api_v1_ab_tests_get(status=status, test_type=test_type, request_body=request_body)
        print("The response of ABTestingApi->list_ab_tests_api_v1_ab_tests_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->list_ab_tests_api_v1_ab_tests_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **status** | [**TestStatus**](.md)|  | [optional] 
 **test_type** | [**TestType**](.md)|  | [optional] 
 **request_body** | [**List[str]**](str.md)|  | [optional] 

### Return type

[**ABTestListResponse**](ABTestListResponse.md)

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

# **pause_ab_test_api_v1_ab_tests_test_id_pause_post**
> ABTestActionResponse pause_ab_test_api_v1_ab_tests_test_id_pause_post(test_id)

Pause Ab Test

Pause an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_action_response import ABTestActionResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Pause Ab Test
        api_response = await api_instance.pause_ab_test_api_v1_ab_tests_test_id_pause_post(test_id)
        print("The response of ABTestingApi->pause_ab_test_api_v1_ab_tests_test_id_pause_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->pause_ab_test_api_v1_ab_tests_test_id_pause_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestActionResponse**](ABTestActionResponse.md)

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

# **start_ab_test_api_v1_ab_tests_test_id_start_post**
> ABTestActionResponse start_ab_test_api_v1_ab_tests_test_id_start_post(test_id)

Start Ab Test

Start an A/B test.

Args:
    test_id: Test ID
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Action result

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_action_response import ABTestActionResponse
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 

    try:
        # Start Ab Test
        api_response = await api_instance.start_ab_test_api_v1_ab_tests_test_id_start_post(test_id)
        print("The response of ABTestingApi->start_ab_test_api_v1_ab_tests_test_id_start_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->start_ab_test_api_v1_ab_tests_test_id_start_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 

### Return type

[**ABTestActionResponse**](ABTestActionResponse.md)

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

# **update_ab_test_api_v1_ab_tests_test_id_put**
> ABTestResponse update_ab_test_api_v1_ab_tests_test_id_put(test_id, ab_test_update_request)

Update Ab Test

Update an A/B test.

Args:
    test_id: Test ID
    test_data: Test update data
    current_user: Current authenticated user
    ab_test_manager: A/B test manager instance

Returns:
    Updated test data

### Example

* Bearer Authentication (CustomHTTPBearer):

```python
import chatter_sdk
from chatter_sdk.models.ab_test_response import ABTestResponse
from chatter_sdk.models.ab_test_update_request import ABTestUpdateRequest
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
    api_instance = chatter_sdk.ABTestingApi(api_client)
    test_id = 'test_id_example' # str | 
    ab_test_update_request = chatter_sdk.ABTestUpdateRequest() # ABTestUpdateRequest | 

    try:
        # Update Ab Test
        api_response = await api_instance.update_ab_test_api_v1_ab_tests_test_id_put(test_id, ab_test_update_request)
        print("The response of ABTestingApi->update_ab_test_api_v1_ab_tests_test_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ABTestingApi->update_ab_test_api_v1_ab_tests_test_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **test_id** | **str**|  | 
 **ab_test_update_request** | [**ABTestUpdateRequest**](ABTestUpdateRequest.md)|  | 

### Return type

[**ABTestResponse**](ABTestResponse.md)

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

